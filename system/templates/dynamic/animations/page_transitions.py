"""
NOVARYX - Page Transitions
AnimatePresence wrappers for page-level transitions.
"""

from typing import Dict, Any

def generate_page_transition_wrapper(animation_config: Dict[str, Any] = None) -> str:
    """Generate the PageTransition wrapper component"""
    
    cfg = animation_config or {}
    page_props = cfg.get("page_transition", {}).get("props", {})
    
    initial = page_props.get("initial", {"opacity": 0, "y": 20})
    animate = page_props.get("animate", {"opacity": 1, "y": 0})
    exit_props = page_props.get("exit", {"opacity": 0, "y": -20})
    transition = page_props.get("transition", {"duration": 0.35, "ease": "easeInOut"})
    
    return f'''import React from "react";
import {{ motion, AnimatePresence }} from "framer-motion";
import {{ useRouter }} from "next/router";

interface PageTransitionProps {{
  children: React.ReactNode;
  locationKey?: string;
}}

const pageVariants = {{
  initial: {repr(initial)},
  animate: {repr(animate)},
  exit: {repr(exit_props)},
}};

const pageTransition = {repr(transition)};

export function PageTransition({{ children, locationKey }}: PageTransitionProps) {{
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={{locationKey}}
        variants={{pageVariants}}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={{pageTransition}}
        style={{{{ width: "100%" }}}}
      >
        {{children}}
      </motion.div>
    </AnimatePresence>
  );
}}

// Usage in _app.tsx or layout:
// <PageTransition locationKey={{router.asPath}}>
//   <Component {{...pageProps}} />
// </PageTransition>
'''