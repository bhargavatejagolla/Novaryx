"""
NOVARYX - Particle Field
Interactive 3D particle network with mouse interaction.

Parameters:
  - particle_count: int (100-2000)
  - connection_distance: float
  - particle_size: float
  - speed: float
  - mouse_interaction: bool
  - primary_color: hex
  - accent_color: hex
"""

from typing import Dict, Any, List

def generate_particle_field_tsx(config: dict = None) -> str:
    cfg = config or {}
    particle_count = cfg.get("particle_count", 500)
    connection_distance = cfg.get("connection_distance", 2.0)
    particle_size = cfg.get("particle_size", 0.05)
    speed = cfg.get("speed", 0.2)
    mouse_interaction = cfg.get("mouse_interaction", True)
    primary = cfg.get("primary_color", "#6366f1")
    accent = cfg.get("accent_color", "#06b6d4")
    
    return f'''import React, {{ useRef, useMemo }} from "react";
import {{ Canvas, useFrame, useThree }} from "@react-three/fiber";
import * as THREE from "three";

interface ParticleFieldProps {{
  particleCount?: number;
  connectionDistance?: number;
  particleSize?: number;
  speed?: number;
  mouseInteraction?: boolean;
  primaryColor?: string;
  accentColor?: string;
  className?: string;
}}

function Particles({{
  particleCount = {particle_count},
  connectionDistance = {connection_distance},
  particleSize = {particle_size},
  speed = {speed},
  mouseInteraction = {str(mouse_interaction).lower()},
  primaryColor = "{primary}",
  accentColor = "{accent}",
}}: ParticleFieldProps) {{
  const meshRef = useRef<THREE.Points>(null!);
  const linesRef = useRef<THREE.LineSegments>(null!);
  const {{ mouse }} = useThree();
  const mousePos = useRef(new THREE.Vector3(0, 0, 0));

  const {{ positions, velocities, lineGeometry }} = useMemo(() => {{
    const count = particleCount;
    const pos = new Float32Array(count * 3);
    const vel = new Float32Array(count * 3);
    
    for (let i = 0; i < count; i++) {{
      pos[i * 3] = (Math.random() - 0.5) * 10;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 6;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 4;
      vel[i * 3] = (Math.random() - 0.5) * 0.01;
      vel[i * 3 + 1] = (Math.random() - 0.5) * 0.01;
      vel[i * 3 + 2] = (Math.random() - 0.5) * 0.01;
    }}

    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    
    const lineGeo = new THREE.BufferGeometry();
    lineGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(count * 6 * 3), 3));

    return {{ positions: pos, velocities: vel, lineGeometry: lineGeo }};
  }}, [particleCount]);

  useFrame((_, delta) => {{
    if (!meshRef.current) return;

    // Update mouse position
    if (mouseInteraction) {{
      mousePos.current.lerp(
        new THREE.Vector3(mouse.x * 5, mouse.y * 3, 0),
        0.05
      );
    }}

    const pos = meshRef.current.geometry.attributes.position.array as Float32Array;
    const linePositions = new Float32Array(particleCount * 6 * 3);
    let lineIdx = 0;

    for (let i = 0; i < particleCount; i++) {{
      // Update position
      pos[i * 3] += velocities[i * 3] * delta * speed * 10;
      pos[i * 3 + 1] += velocities[i * 3 + 1] * delta * speed * 10;
      pos[i * 3 + 2] += velocities[i * 3 + 2] * delta * speed * 10;

      // Bounce off boundaries
      for (let axis = 0; axis < 3; axis++) {{
        const bound = axis === 0 ? 5 : axis === 1 ? 3 : 2;
        if (Math.abs(pos[i * 3 + axis]) > bound) {{
          velocities[i * 3 + axis] *= -1;
          pos[i * 3 + axis] = Math.sign(pos[i * 3 + axis]) * bound;
        }}
      }}

      // Mouse repulsion
      if (mouseInteraction) {{
        const dx = pos[i * 3] - mousePos.current.x;
        const dy = pos[i * 3 + 1] - mousePos.current.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 2) {{
          velocities[i * 3] += (dx / dist) * 0.02;
          velocities[i * 3 + 1] += (dy / dist) * 0.02;
        }}
      }}

      // Connection lines
      for (let j = i + 1; j < Math.min(i + 20, particleCount); j++) {{
        const dx = pos[i * 3] - pos[j * 3];
        const dy = pos[i * 3 + 1] - pos[j * 3 + 1];
        const dz = pos[i * 3 + 2] - pos[j * 3 + 2];
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
        
        if (dist < connectionDistance) {{
          const alpha = 1 - dist / connectionDistance;
          linePositions[lineIdx * 3] = pos[i * 3];
          linePositions[lineIdx * 3 + 1] = pos[i * 3 + 1];
          linePositions[lineIdx * 3 + 2] = pos[i * 3 + 2];
          linePositions[lineIdx * 3 + 3] = pos[j * 3];
          linePositions[lineIdx * 3 + 4] = pos[j * 3 + 1];
          linePositions[lineIdx * 3 + 5] = pos[j * 3 + 2];
          lineIdx++;
        }}
      }}
    }}

    meshRef.current.geometry.attributes.position.needsUpdate = true;

    // Update lines
    if (linesRef.current && lineIdx > 0) {{
      const lineGeo = new THREE.BufferGeometry();
      lineGeo.setAttribute("position", new THREE.BufferAttribute(linePositions.slice(0, lineIdx * 6), 3));
      linesRef.current.geometry.dispose();
      linesRef.current.geometry = lineGeo;
    }}
  }});

  return (
    <>
      <points ref={{meshRef}} geometry={{new THREE.BufferGeometry().copy(meshRef.current?.geometry || new THREE.BufferGeometry())}}>
        <pointsMaterial
          size={{particleSize}}
          color={{primaryColor}}
          blending={{THREE.AdditiveBlending}}
          depthWrite={{false}}
          transparent
          opacity={{0.8}}
        />
      </points>
      <lineSegments ref={{linesRef}}>
        <lineBasicMaterial
          color={{accentColor}}
          transparent
          opacity={{0.15}}
          blending={{THREE.AdditiveBlending}}
          depthWrite={{false}}
        />
      </lineSegments>
    </>
  );
}}

export function ParticleField({{ className = "", ...props }}: ParticleFieldProps & {{ className?: string }}) {{
  return (
    <div className={{`w-full h-full min-h-[400px] ${{className}}`}}>
      <Canvas
        camera={{{{ position: [0, 0, 8], fov: 60 }}}}
        gl={{{{ antialias: true, alpha: true }}}}
        dpr={{[1, 2]}}
      >
        <Particles {{...props}} />
      </Canvas>
    </div>
  );
}}
'''


def generate_particle_config(prompt: str, theme_colors: dict = None) -> dict:
    """Generate particle field config from prompt"""
    config = {
        "particle_count": 500,
        "connection_distance": 2.0,
        "particle_size": 0.05,
        "speed": 0.2,
        "mouse_interaction": True,
    }
    
    prompt_lower = prompt.lower()
    
    if "dense" in prompt_lower or "many" in prompt_lower:
        config["particle_count"] = 1200
        config["connection_distance"] = 1.5
    if "sparse" in prompt_lower or "few" in prompt_lower:
        config["particle_count"] = 150
        config["connection_distance"] = 3.0
    if "fast" in prompt_lower:
        config["speed"] = 0.5
    
    if theme_colors:
        config["primary_color"] = theme_colors.get("primary", "#6366f1")
        config["accent_color"] = theme_colors.get("accent", "#06b6d4")
    
    return config