"""
NOVARYX - Scroll Animations
Scroll-triggered reveal components.
"""

from typing import Dict, Any

def generate_scroll_reveal_component(animation_config: Dict[str, Any] = None) -> str:
    """Generate ScrollReveal wrapper component"""
    
    cfg = animation_config or {}
    scroll_props = cfg.get("scroll_reveal", {}).get("props", {})
    
    initial = scroll_props.get("initial", {"opacity": 0, "y": 40})
    while_in_view = scroll_props.get("whileInView", {"opacity": 1, "y": 0})
    viewport = scroll_props.get("viewport", {"once": True, "margin": "-80px"})
    transition = scroll_props.get("transition", {"duration": 0.6, "ease": "easeOut"})
    
    return f'''import React from "react";
import {{ motion, Variants }} from "framer-motion";

interface ScrollRevealProps {{
  children: React.ReactNode;
  variants?: Variants;
  className?: string;
  delay?: number;
  duration?: number;
  direction?: "up" | "down" | "left" | "right" | "none";
  distance?: number;
  once?: boolean;
}}

export function ScrollReveal({{
  children,
  className = "",
  delay = 0,
  duration = 0.6,
  direction = "up",
  distance = 40,
  once = true,
}}: ScrollRevealProps) {{
  
  const directionMap = {{
    up: {{ y: distance }},
    down: {{ y: -distance }},
    left: {{ x: distance }},
    right: {{ x: -distance }},
    none: {{}},
  }};

  const variants: Variants = {{
    hidden: {{
      opacity: 0,
      ...directionMap[direction],
    }},
    visible: {{
      opacity: 1,
      x: 0,
      y: 0,
      transition: {{
        duration,
        delay,
        ease: [0.25, 0.1, 0.25, 1],
      }},
    }},
  }};

  return (
    <motion.div
      variants={{variants}}
      initial="hidden"
      whileInView="visible"
      viewport={{{{ once, margin: "-60px" }}}}
      className={{className}}
    >
      {{children}}
    </motion.div>
  );
}}

// Stagger container for lists/grids
interface StaggerContainerProps {{
  children: React.ReactNode;
  className?: string;
  staggerDelay?: number;
  delayChildren?: number;
}}

export function StaggerContainer({{
  children,
  className = "",
  staggerDelay = 0.08,
  delayChildren = 0,
}}: StaggerContainerProps) {{
  
  const containerVariants: Variants = {{
    hidden: {{}},
    visible: {{
      transition: {{
        staggerChildren: staggerDelay,
        delayChildren,
      }},
    }},
  }};

  return (
    <motion.div
      variants={{containerVariants}}
      initial="hidden"
      whileInView="visible"
      viewport={{{{ once: true, margin: "-50px" }}}}
      className={{className}}
    >
      {{children}}
    </motion.div>
  );
}}

// Stagger item (child of StaggerContainer)
interface StaggerItemProps {{
  children: React.ReactNode;
  className?: string;
}}

export function StaggerItem({{ children, className = "" }}: StaggerItemProps) {{
  const itemVariants: Variants = {{
    hidden: {{
      opacity: 0,
      y: 24,
    }},
    visible: {{
      opacity: 1,
      y: 0,
      transition: {{
        duration: 0.5,
        ease: [0.25, 0.1, 0.25, 1],
      }},
    }},
  }};

  return (
    <motion.div variants={{itemVariants}} className={{className}}>
      {{children}}
    </motion.div>
  );
}}
'''