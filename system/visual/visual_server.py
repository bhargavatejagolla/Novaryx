"""
NOVARYX - Visual Builder Server
Serves the visual builder web interface and API endpoints.

Provides:
  - Web-based visual builder UI
  - REST API for component CRUD
  - Theme customization endpoints
  - Preview proxy
  - Component inspection API
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger("novaryx.visual_server")


class VisualBuilderServer:
    """
    Visual builder server that provides the web UI and API.
    
    Endpoints:
      GET  /api/components          - List all components
      GET  /api/components/:id      - Get component details
      POST /api/components/:id      - Update component
      GET  /api/theme               - Get current theme
      POST /api/theme               - Update theme
      GET  /api/preview/status      - Get preview status
      POST /api/generate            - Trigger generation
    """
    
    def __init__(self, host: str = "localhost", port: int = 5000):
        self.host = host
        self.port = port
        self.running = False
        
        # Connected systems
        self.component_editor = ComponentEditor()
        self.theme_customizer = ThemeCustomizer()
        self.preview_panel = PreviewPanel()
        self.component_inspector = ComponentInspector()
        
        logger.info(f"Visual Builder Server configured: {host}:{port}")
    
    def start(self):
        """Start the visual builder server"""
        self.running = True
        logger.info(f"Visual Builder running at http://{self.host}:{self.port}")
        print(f"\n🎨 Visual Builder: http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        logger.info("Visual Builder stopped")
    
    def get_components_list(self) -> List[Dict]:
        """API: Get all available components"""
        return self.component_editor.list_components()
    
    def get_component(self, component_id: str) -> Optional[Dict]:
        """API: Get component details"""
        return self.component_editor.get_component(component_id)
    
    def update_component(self, component_id: str, updates: Dict) -> Dict:
        """API: Update a component"""
        return self.component_editor.update_component(component_id, updates)
    
    def get_theme(self) -> Dict:
        """API: Get current theme"""
        return self.theme_customizer.get_current_theme()
    
    def update_theme(self, theme_updates: Dict) -> Dict:
        """API: Update theme"""
        return self.theme_customizer.apply_theme(theme_updates)
    
    def get_preview_status(self) -> Dict:
        """API: Get preview status"""
        return self.preview_panel.get_status()
    
    def generate_html(self) -> str:
        """Generate the visual builder HTML page"""
        return self._build_html()
    
    def _build_html(self) -> str:
        """Build the complete visual builder HTML"""
        return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NOVARYX - Visual Builder</title>
  <style>
    :root {{
      --bg: #0f0f1a;
      --surface: #1e1e32;
      --border: rgba(255,255,255,0.08);
      --text: #f1f1f6;
      --text-secondary: #a0a0b8;
      --primary: #6366f1;
      --accent: #06b6d4;
      --radius: 12px;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'Inter', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      height: 100vh;
      display: flex;
      overflow: hidden;
    }}
    
    /* Sidebar */
    .sidebar {{
      width: 280px;
      background: var(--surface);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      overflow-y: auto;
    }}
    .sidebar-header {{
      padding: 20px;
      border-bottom: 1px solid var(--border);
    }}
    .sidebar-header h1 {{
      font-size: 20px;
      font-weight: 700;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .sidebar-nav {{
      padding: 12px;
      flex: 1;
    }}
    .nav-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      border-radius: var(--radius);
      cursor: pointer;
      transition: all 0.2s;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }}
    .nav-item:hover, .nav-item.active {{
      background: rgba(99,102,241,0.1);
      color: var(--text);
    }}
    .nav-item .icon {{ font-size: 18px; }}
    
    /* Main Content */
    .main {{
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}
    .toolbar {{
      padding: 12px 20px;
      border-bottom: 1px solid var(--border);
      display: flex;
      gap: 10px;
      align-items: center;
    }}
    .btn {{
      padding: 8px 18px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text);
      cursor: pointer;
      font-size: 13px;
      transition: all 0.2s;
    }}
    .btn:hover {{ border-color: var(--primary); }}
    .btn-primary {{
      background: var(--primary);
      border-color: var(--primary);
      color: white;
    }}
    .btn-primary:hover {{ opacity: 0.9; }}
    
    /* Content Area */
    .content {{
      flex: 1;
      display: flex;
      overflow: hidden;
    }}
    
    /* Canvas */
    .canvas {{
      flex: 1;
      padding: 30px;
      overflow-y: auto;
      display: flex;
      align-items: flex-start;
      justify-content: center;
    }}
    .preview-frame {{
      width: 100%;
      max-width: 1200px;
      min-height: 600px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
    }}
    .preview-frame iframe {{
      width: 100%;
      height: 100%;
      min-height: 600px;
      border: none;
    }}
    
    /* Inspector Panel */
    .inspector {{
      width: 320px;
      background: var(--surface);
      border-left: 1px solid var(--border);
      overflow-y: auto;
      padding: 20px;
    }}
    .inspector-section {{
      margin-bottom: 24px;
    }}
    .inspector-section h3 {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-secondary);
      margin-bottom: 12px;
    }}
    .field {{
      margin-bottom: 12px;
    }}
    .field label {{
      display: block;
      font-size: 12px;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }}
    .field input, .field select {{
      width: 100%;
      padding: 8px 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: var(--bg);
      color: var(--text);
      font-size: 13px;
    }}
    .field input:focus, .field select:focus {{
      outline: none;
      border-color: var(--primary);
    }}
    .color-input {{
      display: flex;
      gap: 8px;
      align-items: center;
    }}
    .color-input input[type="color"] {{
      width: 36px;
      height: 36px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }}
    
    /* Status Bar */
    .status-bar {{
      padding: 8px 20px;
      border-top: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: var(--text-secondary);
    }}
    .status-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      display: inline-block;
      margin-right: 6px;
    }}
    .status-dot.connected {{ background: #10b981; }}
    .status-dot.generating {{ background: #f59e0b; animation: pulse 1s infinite; }}
    @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}
    
    /* Component List */
    .component-list {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 10px;
    }}
    .component-card {{
      padding: 14px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      cursor: pointer;
      transition: all 0.2s;
      text-align: center;
    }}
    .component-card:hover {{
      border-color: var(--primary);
      background: rgba(99,102,241,0.05);
    }}
    .component-card .comp-icon {{
      font-size: 28px;
      margin-bottom: 8px;
    }}
    .component-card .comp-name {{
      font-size: 12px;
      font-weight: 500;
    }}
  </style>
</head>
<body>
  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-header">
      <h1>🚀 NOVARYX</h1>
      <p style="font-size:11px;color:var(--text-secondary);margin-top:4px;">Visual Builder</p>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-item active" data-panel="components">
        <span class="icon">🧩</span> Components
      </div>
      <div class="nav-item" data-panel="theme">
        <span class="icon">🎨</span> Theme
      </div>
      <div class="nav-item" data-panel="pages">
        <span class="icon">📄</span> Pages
      </div>
      <div class="nav-item" data-panel="preview">
        <span class="icon">👁️</span> Preview
      </div>
      <div class="nav-item" data-panel="settings">
        <span class="icon">⚙️</span> Settings
      </div>
    </nav>
    <div style="padding:12px;border-top:1px solid var(--border);">
      <button class="btn btn-primary" style="width:100%;" onclick="generateProject()">
        ⚡ Generate Project
      </button>
    </div>
  </aside>

  <!-- Main -->
  <main class="main">
    <div class="toolbar">
      <input type="text" id="promptInput" 
             placeholder="Describe what you want to build..." 
             style="flex:1;padding:8px 14px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:14px;"
             value="Build a dark purple SaaS dashboard with analytics">
      <button class="btn btn-primary" onclick="generateProject()">Generate</button>
      <button class="btn">Save</button>
      <button class="btn">Export</button>
    </div>

    <div class="content">
      <!-- Canvas / Preview -->
      <div class="canvas" id="canvas">
        <div class="preview-frame">
          <div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--text-secondary);flex-direction:column;gap:12px;">
            <div style="font-size:64px;">🚀</div>
            <p>Enter a prompt and click Generate</p>
            <p style="font-size:12px;">Your project preview will appear here</p>
          </div>
        </div>
      </div>

      <!-- Inspector -->
      <div class="inspector" id="inspector">
        <div class="inspector-section">
          <h3>📊 Generation Status</h3>
          <div id="generationStatus">
            <p style="color:var(--text-secondary);font-size:13px;">Ready to generate</p>
          </div>
        </div>
        <div class="inspector-section">
          <h3>🎨 Quick Theme</h3>
          <div class="field">
            <label>Primary Color</label>
            <div class="color-input">
              <input type="color" id="primaryColor" value="#6366f1" onchange="updateTheme()">
              <input type="text" id="primaryColorText" value="#6366f1" onchange="updateTheme()">
            </div>
          </div>
          <div class="field">
            <label>Mode</label>
            <select id="colorMode" onchange="updateTheme()">
              <option value="dark">Dark</option>
              <option value="light">Light</option>
            </select>
          </div>
          <div class="field">
            <label>Font</label>
            <select id="fontFamily" onchange="updateTheme()">
              <option value="Inter">Inter</option>
              <option value="Poppins">Poppins</option>
              <option value="Roboto">Roboto</option>
              <option value="mono">JetBrains Mono</option>
            </select>
          </div>
        </div>
        <div class="inspector-section">
          <h3>📁 Recent Files</h3>
          <div id="recentFiles" style="font-size:12px;color:var(--text-secondary);">
            No files generated yet
          </div>
        </div>
      </div>
    </div>

    <div class="status-bar">
      <span>
        <span class="status-dot connected" id="statusDot"></span>
        <span id="statusText">Ready</span>
      </span>
      <span id="projectInfo"></span>
    </div>
  </main>

  <script>
    // State
    let currentTheme = {{
      primary: '#6366f1',
      mode: 'dark',
      font: 'Inter'
    }};
    
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {{
      item.addEventListener('click', function() {{
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
      }});
    }});
    
    // Theme updates
    function updateTheme() {{
      currentTheme.primary = document.getElementById('primaryColor').value;
      currentTheme.mode = document.getElementById('colorMode').value;
      currentTheme.font = document.getElementById('fontFamily').value;
      document.getElementById('primaryColorText').value = currentTheme.primary;
      document.getElementById('primaryColor').value = currentTheme.primary;
      
      document.documentElement.style.setProperty('--primary', currentTheme.primary);
      
      fetch('/api/theme', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify(currentTheme)
      }});
    }}
    
    // Generate project
    function generateProject() {{
      const prompt = document.getElementById('promptInput').value;
      if (!prompt) return;
      
      const statusDot = document.getElementById('statusDot');
      const statusText = document.getElementById('statusText');
      const genStatus = document.getElementById('generationStatus');
      
      statusDot.className = 'status-dot generating';
      statusText.textContent = 'Generating...';
      genStatus.innerHTML = '<p style="color:#f59e0b;">⚡ Generation started...</p>';
      
      fetch('/api/generate', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{prompt: prompt, theme: currentTheme}})
      }})
      .then(r => r.json())
      .then(data => {{
        statusDot.className = 'status-dot connected';
        statusText.textContent = 'Ready';
        genStatus.innerHTML = `<p style="color:#10b981;">Project generated!</p>
          <p style="font-size:12px;color:var(--text-secondary);">${{data.files}} files created</p>
          <p style="font-size:12px;color:var(--text-secondary);">${{data.components}} components</p>`;
        
        document.getElementById('projectInfo').textContent = 
          `Project: ${{data.project}} | Files: ${{data.files}}`;
        
        // Update recent files
        if (data.recent_files) {{
          document.getElementById('recentFiles').innerHTML = 
            data.recent_files.map(f => `<div>${{f}}</div>`).join('');
        }}
      }})
      .catch(err => {{
        statusDot.className = 'status-dot connected';
        statusText.textContent = 'Error';
        genStatus.innerHTML = `<p style="color:#ef4444;">Error: ${{err.message}}</p>`;
      }});
    }}
    
    // Keyboard shortcut
    document.addEventListener('keydown', function(e) {{
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {{
        generateProject();
      }}
    }});
    
    console.log('🚀 NOVARYX Visual Builder ready');
    console.log('   Press Ctrl+Enter to generate');
  </script>
</body>
</html>"""