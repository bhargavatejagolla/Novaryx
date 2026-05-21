import { NextResponse } from 'next/server';

export async function GET() {
    try {
        // Try to import from Python backend
        // For now, return the known components
        const components = [
            { id: 'navbar', name: 'Navigation Bar', type: 'navigation', description: 'Responsive top navbar with logo, links, and mobile menu', complexity: 'medium', keywords: ['navbar', 'header', 'top bar', 'navigation'] },
            { id: 'sidebar', name: 'Sidebar Navigation', type: 'navigation', description: 'Collapsible sidebar with icon navigation and sections', complexity: 'medium', keywords: ['sidebar', 'navigation', 'menu', 'side nav'] },
            { id: 'stats_card', name: 'Statistics Card', type: 'data_display', description: 'KPI card showing metric value, label, and trend indicator', complexity: 'simple', keywords: ['stats', 'metrics', 'kpi', 'numbers'] },
            { id: 'chart_widget', name: 'Chart Widget', type: 'data_display', description: 'Interactive chart supporting line, bar, pie, and area types', complexity: 'complex', keywords: ['chart', 'graph', 'plot', 'analytics'] },
            { id: 'data_table', name: 'Data Table', type: 'data_display', description: 'Sortable, filterable, paginated data table with actions', complexity: 'complex', keywords: ['table', 'data', 'list', 'records'] },
            { id: 'activity_feed', name: 'Activity Feed', type: 'data_display', description: 'Timeline-style activity feed with icons and timestamps', complexity: 'medium', keywords: ['activity', 'feed', 'timeline', 'recent'] },
            { id: 'breadcrumbs', name: 'Breadcrumbs', type: 'navigation', description: 'Auto-generated breadcrumb trail showing page hierarchy', complexity: 'simple', keywords: ['breadcrumb', 'path', 'navigation'] },
            { id: 'theme_toggle', name: 'Theme Toggle', type: 'ui', description: 'Dark/light mode toggle button with animated transition', complexity: 'simple', keywords: ['theme', 'dark mode', 'light mode'] },
            { id: 'search_bar', name: 'Search Bar', type: 'input', description: 'Animated search input with suggestions dropdown', complexity: 'medium', keywords: ['search', 'find', 'lookup'] },
            { id: 'notification_bell', name: 'Notification Bell', type: 'ui', description: 'Notification bell with unread badge and dropdown', complexity: 'medium', keywords: ['notification', 'bell', 'alert'] },
            { id: 'modal', name: 'Modal Dialog', type: 'ui', description: 'Animated modal overlay with keyboard dismiss', complexity: 'medium', keywords: ['modal', 'dialog', 'popup'] },
            { id: 'auth_form', name: 'Authentication Form', type: 'form', description: 'Login/Register form with validation and social login', complexity: 'complex', keywords: ['login', 'register', 'auth'] },
            { id: 'empty_state', name: 'Empty State', type: 'ui', description: 'Illustrated empty state with action button', complexity: 'simple', keywords: ['empty', 'no data', 'placeholder'] },
            { id: 'error_boundary', name: 'Error Boundary', type: 'ui', description: 'React error boundary with fallback UI and retry', complexity: 'simple', keywords: ['error', 'crash', 'fallback'] },
            { id: 'skeleton_loader', name: 'Skeleton Loader', type: 'ui', description: 'Configurable skeleton loading placeholder', complexity: 'simple', keywords: ['skeleton', 'loading', 'placeholder'] },
            { id: 'toast_notification', name: 'Toast Notification', type: 'ui', description: 'Slide-in toast with auto-dismiss and stacking', complexity: 'medium', keywords: ['toast', 'notification', 'message'] },
        ];

        return NextResponse.json({ components, total: components.length });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}