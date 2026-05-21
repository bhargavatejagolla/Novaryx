"""
NOVARYX - 3D Tilt Card
Card with perspective tilt following mouse movement.

Parameters:
  - tilt_amount: float (degrees)
  - glare_enabled: bool
  - glare_opacity: float
  - scale_on_hover: float
  - layers: int (1-5)
  - border_glow: bool
"""

def generate_card_3d_tsx(config: dict = None) -> str:
    cfg = config or {}
    tilt_amount = cfg.get("tilt_amount", 15)
    glare_enabled = cfg.get("glare_enabled", True)
    glare_opacity = cfg.get("glare_opacity", 0.15)
    scale_on_hover = cfg.get("scale_on_hover", 1.03)
    border_glow = cfg.get("border_glow", True)
    
    return f'''import React, {{ useRef, useState }} from "react";
import {{ motion, useMotionValue, useSpring, useTransform }} from "framer-motion";

interface Card3DProps {{
  children?: React.ReactNode;
  tiltAmount?: number;
  glareEnabled?: boolean;
  glareOpacity?: number;
  scaleOnHover?: number;
  borderGlow?: boolean;
  primaryColor?: string;
  className?: string;
  onClick?: () => void;
}}

export function Card3D({{
  children,
  tiltAmount = {tilt_amount},
  glareEnabled = {str(glare_enabled).lower()},
  glareOpacity = {glare_opacity},
  scaleOnHover = {scale_on_hover},
  borderGlow = {str(border_glow).lower()},
  primaryColor,
  className = "",
  onClick,
}}: Card3DProps) {{
  const ref = useRef<HTMLDivElement>(null);
  const [hovering, setHovering] = useState(false);

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [tiltAmount, -tiltAmount]), {{
    stiffness: 300,
    damping: 30,
  }});
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-tiltAmount, tiltAmount]), {{
    stiffness: 300,
    damping: 30,
  }});

  const handleMouseMove = (e: React.MouseEvent) => {{
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    mouseX.set(x);
    mouseY.set(y);
  }};

  const handleMouseEnter = () => setHovering(true);
  const handleMouseLeave = () => {{
    setHovering(false);
    mouseX.set(0);
    mouseY.set(0);
  }};

  return (
    <motion.div
      ref={{ref}}
      onMouseMove={{handleMouseMove}}
      onMouseEnter={{handleMouseEnter}}
      onMouseLeave={{handleMouseLeave}}
      onClick={{onClick}}
      style={{{{
        rotateX,
        rotateY,
        transformStyle: "preserve-3d",
        perspective: 1000,
      }}}}
      animate={{{{
        scale: hovering ? scaleOnHover : 1,
      }}}}
      transition={{{{ duration: 0.3 }}}}
      className={{`relative rounded-2xl bg-[var(--surface)] border border-[var(--border)] overflow-hidden ${{className}} ${{onClick ? "cursor-pointer" : ""}}`}}
    >
      {{/* Glare effect */}}
      {{glareEnabled && hovering && (
        <motion.div
          className="absolute inset-0 pointer-events-none z-10"
          style={{{{
            background: `radial-gradient(circle at ${{mouseX.get() * 100 + 50}}% ${{mouseY.get() * 100 + 50}}%, rgba(255,255,255,${{glareOpacity}}), transparent 60%)`,
          }}}}
        />
      )}}

      {{/* Border glow */}}
      {{borderGlow && hovering && (
        <motion.div
          className="absolute inset-0 rounded-2xl pointer-events-none z-0"
          animate={{{{ opacity: 1 }}}}
          initial={{{{ opacity: 0 }}}}
          style={{{{
            boxShadow: `0 0 30px ${{primaryColor || "var(--primary)"}}30`,
          }}}}
        />
      )}}

      {{/* Content */}}
      <div className="relative z-20" style={{{{ transform: "translateZ(30px)" }}}}>
        {{children}}
      </div>
    </motion.div>
  );
}}
'''