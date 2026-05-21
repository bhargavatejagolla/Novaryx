const API_BASE = '';

export async function generateProject(prompt: string, theme?: any) {
    const res = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, theme }),
    });
    if (!res.ok) throw new Error('Generation failed');
    return res.json();
}

export async function getComponents() {
    const res = await fetch(`${API_BASE}/api/components`);
    if (!res.ok) throw new Error('Failed to fetch components');
    return res.json();
}

export async function getTheme() {
    const res = await fetch(`${API_BASE}/api/theme`);
    if (!res.ok) throw new Error('Failed to fetch theme');
    return res.json();
}

export async function updateTheme(theme: any) {
    const res = await fetch(`${API_BASE}/api/theme`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(theme),
    });
    if (!res.ok) throw new Error('Failed to update theme');
    return res.json();
}

export async function getProjects() {
    const res = await fetch(`${API_BASE}/api/projects`);
    if (!res.ok) throw new Error('Failed to fetch projects');
    return res.json();
}

export async function exportProject(projectId: string) {
    const res = await fetch(`${API_BASE}/api/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ projectId }),
    });
    if (!res.ok) throw new Error('Export failed');
    return res.json();
}