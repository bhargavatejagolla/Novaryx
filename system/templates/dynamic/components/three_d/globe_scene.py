"""
NOVARYX - 3D Globe Scene
Rotating Earth globe with markers, arcs, and atmosphere.

Parameters (AI configurable):
  - rotation_speed: float
  - marker_count: int
  - arc_count: int
  - atmosphere_enabled: bool
  - globe_scale: float
  - primary_color: hex string
  - accent_color: hex string
"""

from typing import Dict, Any, List

def generate_globe_tsx(config: dict = None) -> str:
    """Generate the Globe component TSX with given config"""
    
    cfg = config or {}
    rotation_speed = cfg.get("rotation_speed", 0.3)
    marker_count = cfg.get("marker_count", 20)
    arc_count = cfg.get("arc_count", 5)
    atmosphere = cfg.get("atmosphere_enabled", True)
    globe_scale = cfg.get("globe_scale", 1.0)
    primary = cfg.get("primary_color", "#6366f1")
    accent = cfg.get("accent_color", "#06b6d4")
    
    return f'''import React, {{ useRef, useMemo }} from "react";
import {{ Canvas, useFrame }} from "@react-three/fiber";
import {{ OrbitControls, Sphere, useTexture, Text }} from "@react-three/drei";
import * as THREE from "three";

interface GlobeProps {{
  rotationSpeed?: number;
  markerCount?: number;
  arcCount?: number;
  atmosphereEnabled?: boolean;
  scale?: number;
  primaryColor?: string;
  accentColor?: string;
  markers?: Array<{{ lat: number; lng: number; label?: string }}>;
  className?: string;
}}

// Generate random points on sphere surface
function generateSpherePoints(count: number, radius: number = 1.0): THREE.Vector3[] {{
  const points: THREE.Vector3[] = [];
  for (let i = 0; i < count; i++) {{
    const phi = Math.acos(2 * Math.random() - 1);
    const theta = 2 * Math.PI * Math.random();
    points.push(new THREE.Vector3(
      radius * Math.sin(phi) * Math.cos(theta),
      radius * Math.cos(phi),
      radius * Math.sin(phi) * Math.sin(theta)
    ));
  }}
  return points;
}}

function GlobeMesh({{ rotationSpeed = {rotation_speed}, markerCount = {marker_count}, arcCount = {arc_count}, atmosphereEnabled = {str(atmosphere).lower()}, scale = {globe_scale}, primaryColor = "{primary}", accentColor = "{accent}", markers = [] }}: GlobeProps) {{
  const groupRef = useRef<THREE.Group>(null!);
  const markerPoints = useMemo(() => markers.length > 0 
    ? markers.map(m => {{
        const phi = (90 - m.lat) * (Math.PI / 180);
        const theta = (m.lng + 180) * (Math.PI / 180);
        return new THREE.Vector3(
          -Math.sin(phi) * Math.cos(theta),
          Math.cos(phi),
          Math.sin(phi) * Math.sin(theta)
        );
      }})
    : generateSpherePoints(markerCount)
  , [markers, markerCount]);

  useFrame((_, delta) => {{
    if (groupRef.current) {{
      groupRef.current.rotation.y += delta * rotationSpeed * 0.1;
    }}
  }});

  return (
    <group ref={{groupRef}} scale={{scale}}>
      {{/* Earth sphere */}}
      <Sphere args={{[1, 64, 64]}}>
        <meshPhongMaterial
          color={{primaryColor}}
          emissive={{primaryColor}}
          emissiveIntensity={{0.1}}
          specular="#ffffff"
          shininess={{10}}
          wireframe={{false}}
        />
      </Sphere>

      {{/* Wireframe overlay */}}
      <Sphere args={{[1.01, 32, 32]}}>
        <meshBasicMaterial
          color={{accentColor}}
          wireframe={{true}}
          transparent
          opacity={{0.08}}
        />
      </Sphere>

      {{/* Atmosphere glow */}}
      {{atmosphereEnabled && (
        <Sphere args={{[1.15, 64, 64]}}>
          <meshBasicMaterial
            color={{primaryColor}}
            transparent
            opacity={{0.06}}
            side={{THREE.BackSide}}
          />
        </Sphere>
      )}}

      {{/* Markers */}}
      {{markerPoints.map((point, i) => (
        <group key={{i}} position={{point.multiplyScalar(1.02)}}>
          <Sphere args={{[0.02, 8, 8]}}>
            <meshBasicMaterial color={{accentColor}} />
          </Sphere>
          <Sphere args={{[0.04, 8, 8]}}>
            <meshBasicMaterial
              color={{accentColor}}
              transparent
              opacity={{0.3}}
            />
          </Sphere>
        </group>
      ))}}

      {{/* Connection arcs */}}
      {{Array.from({{ length: arcCount }}).map((_, i) => {{
        const start = markerPoints[Math.floor(Math.random() * markerPoints.length)];
        const end = markerPoints[Math.floor(Math.random() * markerPoints.length)];
        const mid = start.clone().add(end).multiplyScalar(0.5).normalize().multiplyScalar(1.4);
        const curve = new THREE.QuadraticBezierCurve3(start.clone(), mid, end.clone());
        
        return (
          <mesh key={{`arc-${{i}}`}}>
            <tubeGeometry args={{[curve, 64, 0.005, 8, false]}} />
            <meshBasicMaterial color={{accentColor}} transparent opacity={{0.5}} />
          </mesh>
        );
      }})}}
    </group>
  );
}}

export function GlobeScene({{ className = "", ...props }}: GlobeProps & {{ className?: string }}) {{
  const [webglSupported, setWebglSupported] = React.useState(true);

  React.useEffect(() => {{
    try {{
      const canvas = document.createElement("canvas");
      const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
      setWebglSupported(!!gl);
    }} catch {{
      setWebglSupported(false);
    }}
  }}, []);

  if (!webglSupported) {{
    return (
      <div className="flex items-center justify-center h-full bg-gradient-to-br from-[var(--primary)]/20 to-[var(--accent)]/20 rounded-xl">
        <div className="text-center text-[var(--text-secondary)]">
          <div className="text-6xl mb-4">🌍</div>
          <p className="text-sm">3D Globe</p>
          <p className="text-xs text-[var(--text-tertiary)]">WebGL not supported</p>
        </div>
      </div>
    );
  }}

  return (
    <div className={{`w-full h-full min-h-[400px] ${{className}}`}}>
      <Canvas
        camera={{{{ position: [0, 0.5, 3], fov: 45 }}}}
        gl={{{{ antialias: true, alpha: true }}}}
        dpr={{[1, 2]}}
      >
        <ambientLight intensity={{0.3}} />
        <pointLight position={{[5, 5, 5]}} intensity={{0.8}} />
        <pointLight position={{[-3, -2, -3]}} intensity={{0.4}} color={{props.accentColor || "{accent}"}} />
        <GlobeMesh {{...props}} />
        <OrbitControls
          enableZoom={{true}}
          enablePan={{false}}
          minDistance={{2}}
          maxDistance={{6}}
          autoRotate={{true}}
          autoRotateSpeed={{0.2}}
        />
      </Canvas>
    </div>
  );
}}
'''


def generate_globe_config(prompt: str, theme_colors: dict = None) -> dict:
    """Generate globe configuration from prompt and theme"""
    config = {
        "rotation_speed": 0.3,
        "marker_count": 20,
        "arc_count": 5,
        "atmosphere_enabled": True,
        "globe_scale": 1.0,
    }
    
    prompt_lower = prompt.lower()
    
    if "fast" in prompt_lower or "quick" in prompt_lower:
        config["rotation_speed"] = 0.8
    if "slow" in prompt_lower:
        config["rotation_speed"] = 0.1
    if "many" in prompt_lower or "lot" in prompt_lower:
        config["marker_count"] = 50
        config["arc_count"] = 10
    if "simple" in prompt_lower or "minimal" in prompt_lower:
        config["marker_count"] = 8
        config["arc_count"] = 2
        config["atmosphere_enabled"] = False
    
    if theme_colors:
        config["primary_color"] = theme_colors.get("primary", "#6366f1")
        config["accent_color"] = theme_colors.get("accent", "#06b6d4")
    
    return config