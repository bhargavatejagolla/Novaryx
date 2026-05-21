"""
NOVARYX - State Monitor
Monitors system health during generation:
- Memory usage
- Timeout detection
- Error rate tracking
- Performance metrics
"""

import time
import threading
import logging
import psutil
import os
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from .state_machine import NovaryxStateMachine
from .state_definitions import GenerationState, TERMINAL_STATES

logger = logging.getLogger("novaryx.state_monitor")


class StateMonitor:
    """
    Background monitor for the state machine.
    
    Watches for:
    - State timeouts
    - Memory pressure
    - Excessive errors
    - Stuck states
    """
    
    def __init__(
        self,
        state_machine: NovaryxStateMachine,
        check_interval_seconds: float = 5.0,
        memory_warning_threshold_mb: float = 14000,  # 14GB for 16GB system
        memory_critical_threshold_mb: float = 15000
    ):
        self.state_machine = state_machine
        self.check_interval = check_interval_seconds
        self.memory_warning_threshold = memory_warning_threshold_mb
        self.memory_critical_threshold = memory_critical_threshold_mb
        
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False
        self._paused = False
        
        self.alerts: list = []
        self.metrics: Dict[str, list] = {
            "memory_usage_mb": [],
            "cpu_percent": [],
            "state_durations": []
        }
        
        # Callbacks
        self.on_timeout: Optional[Callable] = None
        self.on_memory_warning: Optional[Callable] = None
        self.on_memory_critical: Optional[Callable] = None
        self.on_error_limit: Optional[Callable] = None
        
        logger.info("StateMonitor initialized")
    
    def start(self):
        """Start background monitoring"""
        if self._running:
            logger.warning("Monitor already running")
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="novaryx-monitor"
        )
        self._monitor_thread.start()
        logger.info("StateMonitor started")
    
    def stop(self):
        """Stop background monitoring"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=10)
        logger.info("StateMonitor stopped")
    
    def pause(self):
        """Pause monitoring"""
        self._paused = True
    
    def resume(self):
        """Resume monitoring"""
        self._paused = False
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._running:
            if not self._paused:
                try:
                    self._check_timeout()
                    self._check_memory()
                    self._check_errors()
                    self._collect_metrics()
                except Exception as e:
                    logger.error(f"Monitor error: {e}")
            
            time.sleep(self.check_interval)
    
    def _check_timeout(self):
        """Check if current state has timed out"""
        if self.state_machine.check_timeout():
            self.alerts.append({
                "type": "timeout",
                "state": self.state_machine.state.current_state.value,
                "timestamp": datetime.now().isoformat()
            })
            if self.on_timeout:
                self.on_timeout(self.state_machine.state)
    
    def _check_memory(self):
        """Check system memory usage"""
        try:
            memory = psutil.virtual_memory()
            used_mb = memory.used / (1024 * 1024)
            
            self.metrics["memory_usage_mb"].append(used_mb)
            
            # Keep only last 100 readings
            if len(self.metrics["memory_usage_mb"]) > 100:
                self.metrics["memory_usage_mb"] = self.metrics["memory_usage_mb"][-100:]
            
            # Check thresholds
            if used_mb > self.memory_critical_threshold:
                logger.critical(f"Memory critical: {used_mb:.0f}MB")
                self.alerts.append({
                    "type": "memory_critical",
                    "usage_mb": used_mb,
                    "threshold_mb": self.memory_critical_threshold,
                    "timestamp": datetime.now().isoformat()
                })
                if self.on_memory_critical:
                    self.on_memory_critical(used_mb)
                    
            elif used_mb > self.memory_warning_threshold:
                logger.warning(f"Memory warning: {used_mb:.0f}MB")
                if self.on_memory_warning:
                    self.on_memory_warning(used_mb)
                    
        except Exception as e:
            logger.debug(f"Memory check failed: {e}")
    
    def _check_errors(self):
        """Check error count"""
        if self.state_machine.state.has_exceeded_error_limit():
            logger.critical(
                f"Error limit exceeded: {self.state_machine.state.error_count}"
            )
            self.alerts.append({
                "type": "error_limit",
                "error_count": self.state_machine.state.error_count,
                "timestamp": datetime.now().isoformat()
            })
            if self.on_error_limit:
                self.on_error_limit(self.state_machine.state.error_count)
    
    def _collect_metrics(self):
        """Collect performance metrics"""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            self.metrics["cpu_percent"].append(cpu)
            
            if len(self.metrics["cpu_percent"]) > 100:
                self.metrics["cpu_percent"] = self.metrics["cpu_percent"][-100:]
                
        except Exception:
            pass
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            memory = psutil.virtual_memory()
            return {
                "memory_used_mb": memory.used / (1024 * 1024),
                "memory_available_mb": memory.available / (1024 * 1024),
                "memory_percent": memory.percent,
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "process_memory_mb": psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024),
                "timestamp": datetime.now().isoformat()
            }
        except Exception:
            return {}
    
    def get_average_metrics(self) -> Dict[str, Any]:
        """Get average metrics over monitoring period"""
        avg = {}
        
        if self.metrics["memory_usage_mb"]:
            avg["avg_memory_mb"] = sum(self.metrics["memory_usage_mb"]) / len(self.metrics["memory_usage_mb"])
            avg["max_memory_mb"] = max(self.metrics["memory_usage_mb"])
            avg["min_memory_mb"] = min(self.metrics["memory_usage_mb"])
        
        if self.metrics["cpu_percent"]:
            avg["avg_cpu"] = sum(self.metrics["cpu_percent"]) / len(self.metrics["cpu_percent"])
        
        return avg
    
    def get_alert_count(self) -> int:
        """Get total alert count"""
        return len(self.alerts)
    
    def get_recent_alerts(self, count: int = 5) -> list:
        """Get recent alerts"""
        return self.alerts[-count:]
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
    
    def display_health(self):
        """Display current health status"""
        metrics = self.get_current_metrics()
        avg = self.get_average_metrics()
        
        print("\n" + "=" * 50)
        print("💓 SYSTEM HEALTH")
        print("=" * 50)
        
        if metrics:
            print(f"   Memory: {metrics.get('memory_used_mb', 0):.0f}MB used / "
                  f"{metrics.get('memory_available_mb', 0):.0f}MB available "
                  f"({metrics.get('memory_percent', 0)}%)")
            print(f"   CPU: {metrics.get('cpu_percent', 0)}%")
            print(f"   Process Memory: {metrics.get('process_memory_mb', 0):.0f}MB")
        
        if avg:
            if "avg_memory_mb" in avg:
                print(f"   Avg Memory: {avg['avg_memory_mb']:.0f}MB "
                      f"(max: {avg.get('max_memory_mb', 0):.0f}MB)")
        
        print(f"   Alerts: {len(self.alerts)}")
        print(f"   Monitor: {'🟢 Running' if self._running else '🔴 Stopped'}")
        print("=" * 50 + "\n")


# ---- Test ----

def test_monitor():
    """Test the state monitor"""
    from .state_machine import NovaryxStateMachine
    
    print("\n" + "=" * 60)
    print("🧪 STATE MONITOR TEST")
    print("=" * 60)
    
    sm = NovaryxStateMachine()
    sm.transition(GenerationState.INITIALIZING, "Startup")
    sm.transition(GenerationState.READY, "Ready")
    
    monitor = StateMonitor(sm, check_interval_seconds=2)
    
    # Set up alerts
    monitor.on_memory_warning = lambda mb: print(f"⚠️ Memory warning: {mb:.0f}MB")
    monitor.on_timeout = lambda state: print(f"⏰ Timeout in state: {state.current_state.value}")
    
    # Start monitoring
    monitor.start()
    
    # Simulate some work
    print("\n📊 Monitoring for 5 seconds...")
    time.sleep(5)
    
    # Transition to a state with timeout
    sm.transition(GenerationState.PARSING_PROMPT, "Testing timeout")
    
    print("\n📊 Monitoring with timeout state...")
    time.sleep(5)
    
    monitor.display_health()
    
    # Stop
    monitor.stop()
    
    print("✅ Monitor test complete")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_monitor()