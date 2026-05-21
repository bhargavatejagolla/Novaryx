"""
NOVARYX - 3D Hero Scene
Full hero background with animated geometry.

Parameters:
  - geometry_type: "torus" | "sphere" | "cube" | "icosahedron"
  - rotation_speed: float
  - primary_color: hex
  - accent_color: hex
"""

from typing import Dict, Any, List

def generate_hero_scene_tsx(config: dict = None) -> str:
    cfg = config or {}
    rotation_speed = cfg.get("rotation_speed", 0.5)
    primary = cfg.get("primary_color", "#6366f1")
    accent = cfg.get("accent_color", "#06b6d4")
    
    return f'''import React, {{ useRef }} from "react";
import {{ Canvas, useFrame }} from "@react-three/fiber";
import * as THREE from "three";

interface HeroSceneProps {{
  rotationSpeed?: number;
  primaryColor?: string;
  accentColor?: string;
  className?: string;
}}

function AnimatedGeometry({{ rotationSpeed = {rotation_speed}, primaryColor = "{primary}", accentColor = "{accent}" }}: HeroSceneProps) {{
  const groupRef = useRef<THREE.Group>(null!);
  const torusRef = useRef<THREE.Mesh>(null!);
  const sphereRef = useRef<THREE.Mesh>(null!);

  useFrame((state, delta) => {{
    if (groupRef.current) {{
      groupRef.current.rotation.y += delta * rotationSpeed * 0.2;
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.3) * 0.2;
    }}
    if (torusRef.current) {{
      torusRef.current.rotation.x += delta * 0.3;
      torusRef.current.rotation.y += delta * 0.2;
    }}
    if (sphereRef.current) {{
      sphereRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.5;
    }}
  }});

  return (
    <group ref={{groupRef}}>
      {{/* Main torus knot */}}
      <mesh ref={{torusRef}}>
        <torusKnotGeometry args={{[1.2, 0.3, 128, 32]}} />
        <meshPhongMaterial
          color={{primaryColor}}
          emissive={{primaryColor}}
          emissiveIntensity={{0.2}}
          wireframe={{true}}
          transparent
          opacity={{0.6}}
        />
      </mesh>

      {{/* Inner sphere */}}
      <mesh ref={{sphereRef}}>
        <sphereGeometry args={{[0.5, 32, 32]}} />
        <meshPhongMaterial
          color={{accentColor}}
          emissive={{accentColor}}
          emissiveIntensity={{0.3}}
          transparent
          opacity={{0.4}}
        />
      </mesh>

      {{/* Orbiting particles */}}
      {{Array.from({{ length: 30 }}).map((_, i) => {{
        const angle = (i / 30) * Math.PI * 2;
        const radius = 1.8;
        return (
          <mesh
            key={{i}}
            position={{[
              Math.cos(angle) * radius,
              Math.sin(angle + Date.now() * 0.001) * 0.5,
              Math.sin(angle) * radius,
            ]}}
          >
            <sphereGeometry args={{[0.03, 8, 8]}} />
            <meshBasicMaterial color={{i % 2 === 0 ? primaryColor : accentColor}} />
          </mesh>
        );
      }})}}
    </group>
  );
}}

export function HeroScene({{ className = "", ...props }}: HeroSceneProps & {{ className?: string }}) {{
  return (
    <div className={{`w-full h-full min-h-[500px] ${{className}}`}}>
      <Canvas
        camera={{{{ position: [0, 0, 4], fov: 50 }}}}
        gl={{{{ antialias: true, alpha: true }}}}
        dpr={{[1, 2]}}
      >
        <ambientLight intensity={{0.3}} />
        <pointLight position={{[10, 10, 10]}} intensity={{0.5}} />
        <pointLight position={{[-5, -5, -5]}} intensity={{0.3}} color={{props.accentColor || "{accent}"}} />
        <AnimatedGeometry {{...props}} />
      </Canvas>
    </div>
  );
}}
'''
