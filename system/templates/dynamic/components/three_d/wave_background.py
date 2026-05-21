"""
NOVARYX - Wave Background
Animated 3D wave mesh for subtle background effects.

Parameters:
  - wave_count: int
  - amplitude: float
  - frequency: float
  - speed: float
  - primary_color: hex
  - wireframe: bool
"""

from typing import Dict, Any

def generate_wave_background_tsx(config: Dict[str, Any] = None) -> str:
    cfg = config or {}
    wave_count = cfg.get("wave_count", 5)
    amplitude = cfg.get("amplitude", 1.0)
    frequency = cfg.get("frequency", 0.5)
    speed = cfg.get("speed", 0.3)
    primary = cfg.get("primary_color", "#6366f1")
    wireframe = cfg.get("wireframe", False)
    
    return f'''import React, {{ useRef, useMemo }} from "react";
import {{ Canvas, useFrame }} from "@react-three/fiber";
import * as THREE from "three";

interface WaveBackgroundProps {{
  waveCount?: number;
  amplitude?: number;
  frequency?: number;
  speed?: number;
  primaryColor?: string;
  wireframe?: boolean;
  className?: string;
}}

function WaveMesh({{
  waveCount = {wave_count},
  amplitude = {amplitude},
  frequency = {frequency},
  speed = {speed},
  primaryColor = "{primary}",
  wireframe = {str(wireframe).lower()},
}}: WaveBackgroundProps) {{
  const meshRef = useRef<THREE.Mesh>(null!);

  const geometry = useMemo(() => {{
    const geo = new THREE.PlaneGeometry(12, 8, 64, 64);
    geo.rotateX(-Math.PI / 3);
    return geo;
  }}, []);

  useFrame((state) => {{
    if (!meshRef.current) return;
    const positions = (meshRef.current.geometry as THREE.PlaneGeometry)
      .attributes.position.array as Float32Array;

    for (let i = 0; i < positions.length; i += 3) {{
      const x = positions[i];
      const y = positions[i + 1];
      positions[i + 2] =
        Math.sin(x * frequency + state.clock.elapsedTime * speed) *
        Math.cos(y * frequency * 0.7 + state.clock.elapsedTime * speed * 0.6) *
        amplitude;
    }}

    meshRef.current.geometry.attributes.position.needsUpdate = true;
    meshRef.current.geometry.computeVertexNormals();
  }});

  return (
    <mesh ref={{meshRef}} geometry={{geometry}}>
      <meshPhongMaterial
        color={{primaryColor}}
        emissive={{primaryColor}}
        emissiveIntensity={{0.15}}
        wireframe={{wireframe}}
        transparent
        opacity={{0.6}}
        side={{THREE.DoubleSide}}
      />
    </mesh>
  );
}}

export function WaveBackground({{ className = "", ...props }}: WaveBackgroundProps & {{ className?: string }}) {{
  return (
    <div className={{`w-full h-full min-h-[300px] ${{className}}`}}>
      <Canvas
        camera={{{{ position: [0, 2, 5], fov: 50 }}}}
        gl={{{{ antialias: true, alpha: true }}}}
        dpr={{[1, 2]}}
      >
        <ambientLight intensity={{0.4}} />
        <pointLight position={{[0, 5, 5]}} intensity={{0.6}} />
        <WaveMesh {{...props}} />
      </Canvas>
    </div>
  );
}}
'''