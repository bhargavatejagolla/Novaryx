"""
NOVARYX - Component Library Batch 2
Forms, Auth, Modals, Search, Notifications, Empty States, Error Boundaries, Loading Skeletons.

Each component uses design tokens, has all states, and is production-ready.
"""


# =====================================================================
# COMPONENT REGISTRY ENTRIES (add to ComponentRegistry.COMPONENTS)
# =====================================================================

BATCH2_COMPONENTS = """
    # Add these to ComponentRegistry.COMPONENTS dict:

    "search_bar": ComponentMeta(
        component_id="search_bar",
        name="Search Bar",
        description="Animated search input with icon, clear button, keyboard shortcut, and suggestions dropdown",
        component_type="search_bar",
        allowed_layouts=["dashboard", "admin", "ecommerce", "landing"],
        allowed_slots=["header", "navbar"],
        keywords=["search", "find", "lookup", "search bar", "search input", "filter"],
        complexity="medium"
    ),
    
    "notification_bell": ComponentMeta(
        component_id="notification_bell",
        name="Notification Bell",
        description="Notification bell icon with unread badge and dropdown panel",
        component_type="notification_bell",
        allowed_layouts=["dashboard", "admin"],
        allowed_slots=["header"],
        keywords=["notification", "bell", "alert", "notify", "inbox"],
        complexity="medium"
    ),
    
    "modal": ComponentMeta(
        component_id="modal",
        name="Modal Dialog",
        description="Animated modal overlay with title, content, actions, and keyboard dismiss",
        component_type="modal",
        allowed_layouts=["dashboard", "admin", "landing", "ecommerce", "portfolio"],
        allowed_slots=["drawer", "main", "content"],
        keywords=["modal", "dialog", "popup", "overlay", "lightbox"],
        complexity="medium"
    ),
    
    "auth_form": ComponentMeta(
        component_id="auth_form",
        name="Authentication Form",
        description="Login/Register form with email, password, validation, social buttons, and loading state",
        component_type="auth_form",
        allowed_layouts=["dashboard", "landing", "ecommerce", "admin"],
        allowed_slots=["main", "content", "hero"],
        keywords=["login", "register", "sign up", "sign in", "auth", "authentication", "email password"],
        complexity="complex"
    ),
    
    "empty_state": ComponentMeta(
        component_id="empty_state",
        name="Empty State",
        description="Illustrated empty state with icon, title, description, and action button",
        component_type="empty_state",
        allowed_layouts=["dashboard", "admin", "ecommerce", "landing", "portfolio"],
        allowed_slots=["main", "content", "stats", "panels"],
        keywords=["empty", "no data", "nothing", "blank", "placeholder", "zero state"],
        complexity="simple"
    ),
    
    "error_boundary": ComponentMeta(
        component_id="error_boundary",
        name="Error Boundary",
        description="React error boundary with fallback UI, error details, and retry button",
        component_type="error_boundary",
        allowed_layouts=["dashboard", "admin", "ecommerce", "landing", "portfolio"],
        allowed_slots=["main", "content"],
        keywords=["error", "crash", "boundary", "fallback", "something went wrong"],
        complexity="simple"
    ),
    
    "skeleton_loader": ComponentMeta(
        component_id="skeleton_loader",
        name="Skeleton Loader",
        description="Configurable skeleton loading placeholder with pulse animation",
        component_type="skeleton_loader",
        allowed_layouts=["dashboard", "admin", "ecommerce", "landing", "portfolio"],
        allowed_slots=["main", "content", "stats", "panels"],
        keywords=["skeleton", "loading", "placeholder", "shimmer", "pulse loader"],
        complexity="simple"
    ),
    
    "toast_notification": ComponentMeta(
        component_id="toast_notification",
        name="Toast Notification",
        description="Slide-in toast notification with icon, message, action, and auto-dismiss",
        component_type="toast_notification",
        allowed_layouts=["dashboard", "admin", "ecommerce", "landing", "portfolio"],
        allowed_slots=["main", "content", "header"],
        keywords=["toast", "notification", "snackbar", "alert", "message", "popup message"],
        complexity="medium"
    ),
"""


# =====================================================================
# TSX GENERATORS
# =====================================================================

def generate_search_bar_tsx() -> str:
    return '''import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  suggestions?: string[];
  shortcut?: string;
  className?: string;
}

export function SearchBar({
  placeholder = "Search...",
  onSearch,
  suggestions = [],
  shortcut = "⌘K",
  className = "",
}: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [focused, setFocused] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const filteredSuggestions = query
    ? suggestions.filter((s) => s.toLowerCase().includes(query.toLowerCase()))
    : suggestions;

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if (e.key === "Escape") {
        inputRef.current?.blur();
        setShowSuggestions(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch?.(query);
    setShowSuggestions(false);
  };

  return (
    <div className={`relative ${className}`}>
      <form onSubmit={handleSubmit}>
        <div
          className={`flex items-center gap-2 px-4 py-2 rounded-xl border transition-all duration-200 ${
            focused
              ? "border-[var(--border-focus)] shadow-sm bg-[var(--surface-raised)]"
              : "border-[var(--border)] bg-[var(--background)]"
          }`}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--text-tertiary)] flex-shrink-0">
            <circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" />
          </svg>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setShowSuggestions(true);
            }}
            onFocus={() => { setFocused(true); setShowSuggestions(true); }}
            onBlur={() => { setFocused(false); setTimeout(() => setShowSuggestions(false), 200); }}
            placeholder={placeholder}
            className="flex-1 bg-transparent text-sm text-[var(--text-primary)] placeholder-[var(--text-tertiary)] outline-none"
          />
          {query && (
            <button
              type="button"
              onClick={() => { setQuery(""); inputRef.current?.focus(); }}
              className="text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors"
            >
              ✕
            </button>
          )}
          {!focused && !query && (
            <kbd className="hidden sm:inline-block px-2 py-0.5 text-xs rounded-md bg-[var(--surface-raised)] text-[var(--text-tertiary)] border border-[var(--border)]">
              {shortcut}
            </kbd>
          )}
        </div>
      </form>

      {/* Suggestions Dropdown */}
      <AnimatePresence>
        {showSuggestions && filteredSuggestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="absolute top-full left-0 right-0 mt-2 p-2 rounded-xl bg-[var(--surface)] border border-[var(--border)] shadow-lg z-50"
          >
            {filteredSuggestions.map((suggestion, i) => (
              <button
                key={i}
                onClick={() => {
                  setQuery(suggestion);
                  onSearch?.(suggestion);
                  setShowSuggestions(false);
                }}
                className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-[var(--surface-raised)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
'''


def generate_notification_bell_tsx() -> str:
    return '''import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Notification {
  id: string;
  title: string;
  description: string;
  time: string;
  read: boolean;
  icon?: React.ReactNode;
}

interface NotificationBellProps {
  notifications?: Notification[];
  onMarkAllRead?: () => void;
  onNotificationClick?: (notification: Notification) => void;
  className?: string;
}

export function NotificationBell({
  notifications = [],
  onMarkAllRead,
  onNotificationClick,
  className = "",
}: NotificationBellProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const unreadCount = notifications.filter((n) => !n.read).length;

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={ref} className={`relative ${className}`}>
      <button
        onClick={() => setOpen(!open)}
        className="relative p-2 rounded-xl hover:bg-[var(--surface-raised)] transition-colors"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--text-secondary)]">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
        {unreadCount > 0 && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-0.5 -right-0.5 w-5 h-5 rounded-full bg-[var(--error)] text-white text-xs flex items-center justify-center font-medium"
          >
            {unreadCount > 9 ? "9+" : unreadCount}
          </motion.span>
        )}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            className="absolute right-0 top-full mt-2 w-80 rounded-xl bg-[var(--surface)] border border-[var(--border)] shadow-xl z-50 overflow-hidden"
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)]">
              <h4 className="text-sm font-semibold">Notifications</h4>
              {unreadCount > 0 && (
                <button
                  onClick={onMarkAllRead}
                  className="text-xs text-[var(--primary)] hover:underline"
                >
                  Mark all read
                </button>
              )}
            </div>
            <div className="max-h-72 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-sm text-[var(--text-tertiary)]">
                  No notifications yet
                </div>
              ) : (
                notifications.map((notif) => (
                  <button
                    key={notif.id}
                    onClick={() => {
                      onNotificationClick?.(notif);
                      setOpen(false);
                    }}
                    className={`w-full text-left px-4 py-3 flex gap-3 hover:bg-[var(--surface-raised)] transition-colors ${
                      !notif.read ? "bg-[var(--primary)]/5" : ""
                    }`}
                  >
                    <div className="w-8 h-8 rounded-full bg-[var(--primary)]/10 flex items-center justify-center text-xs flex-shrink-0 mt-0.5">
                      {notif.icon || "📢"}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-[var(--text-primary)] truncate">
                        {notif.title}
                      </p>
                      <p className="text-xs text-[var(--text-secondary)] truncate mt-0.5">
                        {notif.description}
                      </p>
                      <p className="text-xs text-[var(--text-tertiary)] mt-1">
                        {notif.time}
                      </p>
                    </div>
                    {!notif.read && (
                      <div className="w-2 h-2 rounded-full bg-[var(--primary)] flex-shrink-0 mt-2" />
                    )}
                  </button>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
'''


def generate_modal_tsx() -> str:
    return '''import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children?: React.ReactNode;
  footer?: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl" | "full";
  closeOnOverlay?: boolean;
  className?: string;
}

const sizeMap = {
  sm: "max-w-sm",
  md: "max-w-md",
  lg: "max-w-lg",
  xl: "max-w-xl",
  full: "max-w-4xl",
};

export function Modal({
  open,
  onClose,
  title,
  children,
  footer,
  size = "md",
  closeOnOverlay = true,
  className = "",
}: ModalProps) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (open) {
      document.addEventListener("keydown", handleEsc);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEsc);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[var(--z-modal)] flex items-center justify-center p-4">
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeOnOverlay ? onClose : undefined}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className={`relative w-full ${sizeMap[size]} rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-2xl ${className}`}
          >
            {/* Header */}
            {title && (
              <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
                <h3 className="text-lg font-semibold text-[var(--text-primary)]">{title}</h3>
                <button
                  onClick={onClose}
                  className="p-1 rounded-lg hover:bg-[var(--surface-raised)] text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors"
                >
                  ✕
                </button>
              </div>
            )}

            {/* Body */}
            <div className="px-6 py-4 max-h-[70vh] overflow-y-auto">
              {children}
            </div>

            {/* Footer */}
            {footer && (
              <div className="flex justify-end gap-3 px-6 py-4 border-t border-[var(--border)]">
                {footer}
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
'''


def generate_auth_form_tsx() -> str:
    return '''import React, { useState } from "react";
import { motion } from "framer-motion";

interface AuthFormProps {
  mode?: "login" | "register";
  onSubmit?: (data: { email: string; password: string; name?: string }) => void;
  onSocialLogin?: (provider: string) => void;
  loading?: boolean;
  error?: string;
  className?: string;
}

export function AuthForm({
  mode = "login",
  onSubmit,
  onSocialLogin,
  loading = false,
  error,
  className = "",
}: AuthFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit?.({ email, password, ...(mode === "register" ? { name } : {}) });
  };

  const isLogin = mode === "login";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`w-full max-w-md mx-auto p-8 rounded-2xl bg-[var(--surface)] border border-[var(--border)] ${className}`}
    >
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-[var(--text-primary)] mb-2">
          {isLogin ? "Welcome back" : "Create account"}
        </h2>
        <p className="text-sm text-[var(--text-secondary)]">
          {isLogin ? "Sign in to your account" : "Get started with your free account"}
        </p>
      </div>

      {/* Social Buttons */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        {["Google", "GitHub"].map((provider) => (
          <button
            key={provider}
            type="button"
            onClick={() => onSocialLogin?.(provider.toLowerCase())}
            className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-[var(--border)] text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--surface-raised)] transition-colors"
          >
            {provider}
          </button>
        ))}
      </div>

      <div className="relative mb-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-[var(--divider)]" />
        </div>
        <div className="relative flex justify-center text-xs">
          <span className="px-2 bg-[var(--surface)] text-[var(--text-tertiary)]">or continue with email</span>
        </div>
      </div>

      {/* Error */}
      {error && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="p-3 mb-4 rounded-lg bg-[var(--error)]/10 border border-[var(--error)]/20 text-sm text-[var(--error)]"
        >
          {error}
        </motion.div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {!isLogin && (
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-4 py-2.5 rounded-xl bg-[var(--background)] border border-[var(--border)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:border-[var(--border-focus)] focus:outline-none transition-colors"
              placeholder="John Doe"
            />
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-4 py-2.5 rounded-xl bg-[var(--background)] border border-[var(--border)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:border-[var(--border-focus)] focus:outline-none transition-colors"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className="w-full px-4 py-2.5 rounded-xl bg-[var(--background)] border border-[var(--border)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:border-[var(--border-focus)] focus:outline-none transition-colors"
            placeholder="••••••••"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-4 rounded-xl bg-[var(--primary)] text-white font-medium hover:shadow-[var(--shadow-glow)] transition-shadow disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              {isLogin ? "Signing in..." : "Creating account..."}
            </span>
          ) : (
            isLogin ? "Sign in" : "Create account"
          )}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-[var(--text-secondary)]">
        {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
        <button className="text-[var(--primary)] font-medium hover:underline">
          {isLogin ? "Sign up" : "Sign in"}
        </button>
      </p>
    </motion.div>
  );
}
'''


def generate_empty_state_tsx() -> str:
    return '''import React from "react";
import { motion } from "framer-motion";

interface EmptyStateProps {
  icon?: React.ReactNode;
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export function EmptyState({
  icon,
  title = "Nothing here yet",
  description = "Get started by creating your first item.",
  actionLabel,
  onAction,
  className = "",
}: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`flex flex-col items-center justify-center py-16 px-6 text-center ${className}`}
    >
      <div className="text-6xl mb-6">
        {icon || "📭"}
      </div>
      <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
        {title}
      </h3>
      <p className="text-sm text-[var(--text-secondary)] max-w-sm mb-6">
        {description}
      </p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-6 py-2.5 rounded-xl bg-[var(--primary)] text-white text-sm font-medium hover:shadow-[var(--shadow-glow)] transition-shadow"
        >
          {actionLabel}
        </button>
      )}
    </motion.div>
  );
}
'''


def generate_error_boundary_tsx() -> str:
    return '''import React, { Component, ErrorInfo, ReactNode } from "react";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.props.onError?.(error, errorInfo);
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
          <div className="text-6xl mb-6">⚠️</div>
          <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
            Something went wrong
          </h3>
          <p className="text-sm text-[var(--text-secondary)] max-w-md mb-2">
            {this.state.error?.message || "An unexpected error occurred"}
          </p>
          <details className="text-xs text-[var(--text-tertiary)] mb-6 max-w-md text-left">
            <summary className="cursor-pointer hover:text-[var(--text-secondary)]">Technical details</summary>
            <pre className="mt-2 p-3 rounded-lg bg-[var(--background)] overflow-x-auto">
              {this.state.error?.stack?.slice(0, 500) || "No stack trace available"}
            </pre>
          </details>
          <button
            onClick={this.handleRetry}
            className="px-6 py-2.5 rounded-xl bg-[var(--primary)] text-white text-sm font-medium hover:shadow-[var(--shadow-glow)] transition-shadow"
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
'''


def generate_skeleton_loader_tsx() -> str:
    return '''import React from "react";

interface SkeletonLoaderProps {
  variant?: "text" | "card" | "table" | "chart" | "circle" | "custom";
  lines?: number;
  className?: string;
}

export function SkeletonLoader({
  variant = "text",
  lines = 3,
  className = "",
}: SkeletonLoaderProps) {
  const baseClass = "bg-[var(--surface-raised)] rounded animate-pulse";

  if (variant === "card") {
    return (
      <div className={`p-6 rounded-xl bg-[var(--surface)] border border-[var(--border)] ${className}`}>
        <div className={`h-5 w-1/3 ${baseClass} mb-4`} />
        <div className={`h-32 w-full ${baseClass} mb-3`} />
        <div className={`h-4 w-2/3 ${baseClass}`} />
      </div>
    );
  }

  if (variant === "table") {
    return (
      <div className={`rounded-xl bg-[var(--surface)] border border-[var(--border)] ${className}`}>
        <div className="p-4 border-b border-[var(--border)]">
          <div className={`h-5 w-1/4 ${baseClass}`} />
        </div>
        {[...Array(lines)].map((_, i) => (
          <div key={i} className="px-4 py-3 border-b border-[var(--divider)] flex gap-4">
            <div className={`h-4 w-1/5 ${baseClass}`} />
            <div className={`h-4 w-1/3 ${baseClass}`} />
            <div className={`h-4 w-1/4 ${baseClass}`} />
          </div>
        ))}
      </div>
    );
  }

  if (variant === "chart") {
    return (
      <div className={`p-6 rounded-xl bg-[var(--surface)] border border-[var(--border)] ${className}`}>
        <div className={`h-5 w-1/4 ${baseClass} mb-4`} />
        <div className={`h-48 w-full ${baseClass}`} />
      </div>
    );
  }

  if (variant === "circle") {
    return <div className={`rounded-full ${baseClass} ${className}`} />;
  }

  // Default: text lines
  return (
    <div className={`space-y-3 ${className}`}>
      {[...Array(lines)].map((_, i) => (
        <div
          key={i}
          className={`h-4 ${baseClass}`}
          style={{ width: `${30 + Math.random() * 50}%` }}
        />
      ))}
    </div>
  );
}
'''


def generate_toast_notification_tsx() -> str:
    return '''import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface ToastProps {
  id: string;
  type?: "success" | "error" | "warning" | "info";
  title: string;
  message?: string;
  duration?: number;
  onDismiss?: (id: string) => void;
}

export function Toast({
  id,
  type = "info",
  title,
  message,
  duration = 5000,
  onDismiss,
}: ToastProps) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => onDismiss?.(id), duration);
      return () => clearTimeout(timer);
    }
  }, [id, duration, onDismiss]);

  const colors = {
    success: { bg: "bg-[var(--success)]/10", border: "border-[var(--success)]/30", text: "text-[var(--success)]", icon: "✅" },
    error: { bg: "bg-[var(--error)]/10", border: "border-[var(--error)]/30", text: "text-[var(--error)]", icon: "❌" },
    warning: { bg: "bg-[var(--warning)]/10", border: "border-[var(--warning)]/30", text: "text-[var(--warning)]", icon: "⚠️" },
    info: { bg: "bg-[var(--info)]/10", border: "border-[var(--info)]/30", text: "text-[var(--info)]", icon: "ℹ️" },
  };

  const c = colors[type];

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 100, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, scale: 0.95 }}
      className={`flex items-start gap-3 p-4 rounded-xl border ${c.bg} ${c.border} shadow-lg min-w-[300px] max-w-[400px]`}
    >
      <span className="text-lg flex-shrink-0">{c.icon}</span>
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${c.text}`}>{title}</p>
        {message && <p className="text-xs text-[var(--text-secondary)] mt-0.5">{message}</p>}
      </div>
      <button
        onClick={() => onDismiss?.(id)}
        className="text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors flex-shrink-0"
      >
        ✕
      </button>
    </motion.div>
  );
}

// Toast Container (manages multiple toasts)
interface ToastContainerProps {
  toasts: ToastProps[];
  onDismiss: (id: string) => void;
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  return (
    <div className="fixed bottom-4 right-4 z-[var(--z-tooltip)] flex flex-col gap-2">
      <AnimatePresence>
        {toasts.map((toast) => (
          <Toast key={toast.id} {...toast} onDismiss={onDismiss} />
        ))}
      </AnimatePresence>
    </div>
  );
}
'''


# =====================================================================
# UPDATE FUNCTION FOR COMPONENT REGISTRY
# =====================================================================

def get_batch2_tsx_generators():
    """Return all TSX generators for batch 2 components"""
    return {
        "search_bar": generate_search_bar_tsx,
        "notification_bell": generate_notification_bell_tsx,
        "modal": generate_modal_tsx,
        "auth_form": generate_auth_form_tsx,
        "empty_state": generate_empty_state_tsx,
        "error_boundary": generate_error_boundary_tsx,
        "skeleton_loader": generate_skeleton_loader_tsx,
        "toast_notification": generate_toast_notification_tsx,
    }