"""
NOVARYX - Micro Interactions
Hover, tap, focus, and loading animations for components.
"""

from typing import Dict, Any

def generate_micro_interactions_utility(animation_config: Dict[str, Any] = None) -> str:
    """Generate utility hooks and components for micro-interactions"""
    
    cfg = animation_config or {}
    micro_props = cfg.get("micro_interaction", {}).get("props", {})
    loader_css = cfg.get("loader", {}).get("css", "animate-pulse bg-[var(--surface-raised)] rounded")
    
    return f'''import React from "react";
import {{ motion, HTMLMotionProps }} from "framer-motion";

// ---- Interactive Wrapper (applies hover/tap from config) ----

interface InteractiveProps extends HTMLMotionProps<"div"> {{
  children: React.ReactNode;
  hoverEffect?: "lift" | "glow" | "scale" | "none";
  as?: "div" | "button" | "span";
}}

export function Interactive({{
  children,
  hoverEffect = "lift",
  as = "div",
  className = "",
  ...props
}}: InteractiveProps) {{
  
  const effects = {{
    lift: {{
      whileHover: {{ y: -4, boxShadow: "0 12px 30px rgba(0,0,0,0.25)" }},
      whileTap: {{ y: 0, scale: 0.98 }},
    }},
    glow: {{
      whileHover: {{ boxShadow: "0 0 25px var(--primary)" }},
      whileTap: {{ scale: 0.98 }},
    }},
    scale: {{
      whileHover: {{ scale: 1.05 }},
      whileTap: {{ scale: 0.97 }},
    }},
    none: {{}},
  }};

  const effectProps = effects[hoverEffect] || effects.lift;

  const Component = motion[as];

  return (
    <Component
      className={{className}}
      transition={{{{ type: "spring", stiffness: 400, damping: 25 }}}}
      {{...effectProps}}
      {{...props}}
    >
      {{children}}
    </Component>
  );
}}

// ---- Loading Spinner ----

interface SpinnerProps {{
  size?: number;
  color?: string;
  className?: string;
}}

export function Spinner({{ size = 24, color, className = "" }}: SpinnerProps) {{
  return (
    <motion.div
      className={{`border-2 border-[var(--border)] border-t-[var(--primary)] rounded-full ${{className}}`}}
      style={{{{ width: size, height: size, borderTopColor: color || undefined }}}}
      animate={{{{ rotate: 360 }}}}
      transition={{{{ repeat: Infinity, duration: 0.8, ease: "linear" }}}}
    />
  );
}}

// ---- Skeleton Loader ----

interface SkeletonProps {{
  variant?: "text" | "circular" | "rectangular" | "card";
  width?: string | number;
  height?: string | number;
  className?: string;
}}

export function Skeleton({{
  variant = "text",
  width,
  height,
  className = "",
}}: SkeletonProps) {{
  
  const baseClass = "{loader_css}";
  
  const variants = {{
    text: "h-4 w-full",
    circular: "rounded-full",
    rectangular: "rounded-lg",
    card: "rounded-xl h-32 w-full",
  }};

  return (
    <div
      className={{`${baseClass} ${{variants[variant]}} ${{className}}`}}
      style={{{{ width, height }}}}
    />
  );
}}

// ---- Fade In (simple entrance animation) ----

interface FadeInProps {{
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  className?: string;
}}

export function FadeIn({{
  children,
  delay = 0,
  duration = 0.4,
  className = "",
}}: FadeInProps) {{
  return (
    <motion.div
      initial={{{{ opacity: 0, y: 8 }}}}
      animate={{{{ opacity: 1, y: 0 }}}}
      transition={{{{ duration, delay, ease: "easeOut" }}}}
      className={{className}}
    >
      {{children}}
    </motion.div>
  );
}}

// ---- Count Up (animated number) ----

interface CountUpProps {{
  from?: number;
  to: number;
  duration?: number;
  className?: string;
}}

export function CountUp({{ from = 0, to, duration = 1.5, className = "" }}: CountUpProps) {{
  return (
    <motion.span
      initial={{{{ opacity: 0 }}}}
      animate={{{{ opacity: 1 }}}}
      className={{className}}
    >
      <motion.span
        initial={{{{ count: from }}}}
        animate={{{{ count: to }}}}
        transition={{{{ duration, ease: "easeOut" }}}}
      >
        {{({{ count }}) => Math.round(count as number).toLocaleString()}}
      </motion.span>
    </motion.span>
  );
}}
'''