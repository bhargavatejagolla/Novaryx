"""
NOVARYX - Smart Defaults (Phase 11)
Injects production-grade defaults automatically without user prompt.
Includes Auth wrappers, dark mode, responsive layouts, SEO.
"""

from typing import Dict, Any

class SmartDefaultsInjector:
    """Injects smart defaults into the project spec or blueprint."""
    
    @staticmethod
    def inject_defaults(blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhances the blueprint with production-grade defaults.
        """
        if "smart_defaults" not in blueprint:
            blueprint["smart_defaults"] = {}
            
        # SEO Defaults
        blueprint["smart_defaults"]["seo"] = {
            "generate_sitemap": True,
            "generate_robots": True,
            "default_meta_tags": True,
            "open_graph_setup": True
        }
        
        # UX Defaults
        blueprint["smart_defaults"]["ux"] = {
            "dark_mode_toggle": True,
            "toast_notifications": True,
            "skeleton_loaders": True,
            "error_boundaries": True,
            "not_found_page": True
        }
        
        # Accessibility
        blueprint["smart_defaults"]["a11y"] = {
            "aria_labels_required": True,
            "keyboard_navigation": True
        }
        
        # Infrastructure
        blueprint["smart_defaults"]["infra"] = {
            "dockerfile": True,
            "github_actions_ci": True,
            "env_example": True
        }
        
        return blueprint
        
    @staticmethod
    def get_boilerplate_files() -> Dict[str, str]:
        """Returns standard boilerplate content that should be in every project."""
        return {
            "src/components/ErrorBoundary.tsx": """
'use client';
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props { children: ReactNode; fallback?: ReactNode; }
interface State { hasError: bool; error?: Error; }

export class ErrorBoundary extends Component<Props, State> {
  public state: State = { hasError: false };
  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }
  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }
  public render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 border border-red-500 bg-red-50 text-red-900 rounded-md">
            <h2>Something went wrong.</h2>
            <details className="whitespace-pre-wrap">{this.state.error?.toString()}</details>
        </div>
      );
    }
    return this.props.children;
  }
}
"""
        }
