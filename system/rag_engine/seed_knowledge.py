"""
NOVARYX - RAG Knowledge Seeder
Seeds ChromaDB with high-quality TSX component examples for RAG retrieval.

Usage:
    python -m system.rag_engine.seed_knowledge
"""
import sys
import logging
import io
from pathlib import Path

# Force UTF-8 for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
logger = logging.getLogger("novaryx.seed")

COMPONENT_EXAMPLES = [
    {
        "id": "hero_saas_dark",
        "content": """import { motion } from 'framer-motion';
import Link from 'next/link';

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gray-950 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-950/50 via-gray-950 to-purple-950/50" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-900/20 via-transparent to-transparent" />
      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-sm font-medium mb-8">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" /> Now in beta
          </span>
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Build faster with <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">AI power</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
            The intelligent platform that turns your ideas into production-ready applications in minutes.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup" className="px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all duration-200 hover:scale-105 hover:shadow-lg hover:shadow-indigo-500/25">
              Get started free
            </Link>
            <Link href="/demo" className="px-8 py-4 border border-white/10 hover:border-white/30 text-white font-semibold rounded-xl transition-all duration-200 hover:bg-white/5">
              Watch demo
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}""",
        "metadata": {"component_type": "hero", "style": "dark", "has_animation": True, "framework": "nextjs"}
    },
    {
        "id": "dashboard_layout",
        "content": """'use client';
import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { label: 'Dashboard', href: '/dashboard', icon: '◈' },
  { label: 'Analytics', href: '/analytics', icon: '◉' },
  { label: 'Users', href: '/users', icon: '◎' },
  { label: 'Settings', href: '/settings', icon: '◌' },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <div className="flex h-screen bg-gray-950 text-white">
      <aside className={`${collapsed ? 'w-16' : 'w-64'} transition-all duration-300 bg-gray-900 border-r border-white/5 flex flex-col`}>
        <div className="p-4 flex items-center justify-between border-b border-white/5">
          {!collapsed && <span className="text-lg font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">NOVARYX</span>}
          <button onClick={() => setCollapsed(!collapsed)} className="p-2 rounded-lg hover:bg-white/5 text-gray-400">☰</button>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(item => (
            <Link key={item.href} href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200
                ${pathname === item.href ? 'bg-indigo-500/20 text-indigo-300' : 'text-gray-400 hover:bg-white/5 hover:text-white'}`}>
              <span className="text-lg">{item.icon}</span>
              {!collapsed && item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}""",
        "metadata": {"component_type": "layout", "style": "dashboard", "has_animation": False, "framework": "nextjs"}
    },
    {
        "id": "stats_cards",
        "content": """'use client';
import { motion } from 'framer-motion';

interface StatCard { label: string; value: string; change: string; positive: boolean; }

const stats: StatCard[] = [
  { label: 'Total Revenue', value: '$48,295', change: '+12.5%', positive: true },
  { label: 'Active Users', value: '3,842', change: '+8.2%', positive: true },
  { label: 'Conversion', value: '4.7%', change: '-0.3%', positive: false },
  { label: 'Avg Session', value: '6m 42s', change: '+1m 10s', positive: true },
];

export default function StatsCards() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, i) => (
        <motion.div key={stat.label}
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className="bg-gray-900 border border-white/5 rounded-2xl p-6 hover:border-indigo-500/30 transition-all duration-300">
          <p className="text-sm text-gray-400 mb-2">{stat.label}</p>
          <p className="text-3xl font-bold text-white mb-3">{stat.value}</p>
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${stat.positive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
            {stat.change}
          </span>
        </motion.div>
      ))}
    </div>
  );
}""",
        "metadata": {"component_type": "stats", "style": "dark", "has_animation": True, "framework": "nextjs"}
    },
    {
        "id": "auth_login_form",
        "content": """'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) throw new Error((await res.json()).message || 'Login failed');
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <div className="w-full max-w-md p-8 bg-gray-900 rounded-2xl border border-white/5">
        <h1 className="text-2xl font-bold text-white mb-2">Welcome back</h1>
        <p className="text-gray-400 mb-8">Sign in to your account</p>
        {error && <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm text-gray-300 mb-2">Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required
              className="w-full px-4 py-3 bg-gray-800 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition-colors"
              placeholder="you@company.com" />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-2">Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required
              className="w-full px-4 py-3 bg-gray-800 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition-colors"
              placeholder="••••••••" />
          </div>
          <button type="submit" disabled={loading}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold rounded-xl transition-all duration-200">
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}""",
        "metadata": {"component_type": "auth", "style": "dark", "has_auth": True, "framework": "nextjs"}
    },
    {
        "id": "pricing_table",
        "content": """'use client';
import { useState } from 'react';

const plans = [
  { name: 'Starter', price: { monthly: 0, yearly: 0 }, features: ['5 projects', '10GB storage', 'Basic analytics', 'Email support'], cta: 'Get started', highlighted: false },
  { name: 'Pro', price: { monthly: 29, yearly: 24 }, features: ['Unlimited projects', '100GB storage', 'Advanced analytics', 'Priority support', 'Custom domains', 'API access'], cta: 'Start free trial', highlighted: true },
  { name: 'Enterprise', price: { monthly: 99, yearly: 82 }, features: ['Everything in Pro', '1TB storage', 'SSO/SAML', 'SLA guarantee', 'Dedicated support', 'Custom integrations'], cta: 'Contact sales', highlighted: false },
];

export default function PricingTable() {
  const [yearly, setYearly] = useState(false);
  return (
    <section className="py-24 bg-gray-950">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">Simple, transparent pricing</h2>
          <div className="flex items-center justify-center gap-4 mt-8">
            <span className={`text-sm ${!yearly ? 'text-white' : 'text-gray-500'}`}>Monthly</span>
            <button onClick={() => setYearly(!yearly)} className={`relative w-12 h-6 rounded-full transition-colors ${yearly ? 'bg-indigo-600' : 'bg-gray-700'}`}>
              <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${yearly ? 'left-7' : 'left-1'}`} />
            </button>
            <span className={`text-sm ${yearly ? 'text-white' : 'text-gray-500'}`}>Yearly <span className="text-emerald-400 text-xs">-20%</span></span>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map(plan => (
            <div key={plan.name} className={`rounded-2xl p-8 border ${plan.highlighted ? 'bg-indigo-600 border-indigo-500' : 'bg-gray-900 border-white/5'}`}>
              <h3 className="text-lg font-semibold text-white mb-2">{plan.name}</h3>
              <div className="mb-8">
                <span className="text-5xl font-bold text-white">${yearly ? plan.price.yearly : plan.price.monthly}</span>
                <span className="text-gray-300 ml-2">/mo</span>
              </div>
              <ul className="space-y-3 mb-8">
                {plan.features.map(f => <li key={f} className="flex items-center gap-2 text-sm text-gray-200"><span className="text-emerald-400">✓</span>{f}</li>)}
              </ul>
              <button className={`w-full py-3 rounded-xl font-semibold transition-all ${plan.highlighted ? 'bg-white text-indigo-600 hover:bg-gray-100' : 'bg-indigo-600 hover:bg-indigo-500 text-white'}`}>{plan.cta}</button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}""",
        "metadata": {"component_type": "pricing", "style": "dark", "has_animation": False, "framework": "nextjs"}
    },
    {
        "id": "data_table",
        "content": """'use client';
import { useState } from 'react';

interface Column<T> { key: keyof T; label: string; render?: (val: any, row: T) => React.ReactNode; }
interface DataTableProps<T> { data: T[]; columns: Column<T>[]; title?: string; }

export function DataTable<T extends { id: string | number }>({ data, columns, title }: DataTableProps<T>) {
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState<keyof T | null>(null);

  const filtered = data.filter(row =>
    Object.values(row as object).some(v => String(v).toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="bg-gray-900 rounded-2xl border border-white/5 overflow-hidden">
      <div className="p-6 flex items-center justify-between border-b border-white/5">
        {title && <h3 className="text-lg font-semibold text-white">{title}</h3>}
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search..."
          className="px-4 py-2 bg-gray-800 border border-white/10 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-indigo-500" />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead><tr className="border-b border-white/5">
            {columns.map(col => (
              <th key={String(col.key)} onClick={() => setSortKey(col.key)}
                className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider cursor-pointer hover:text-white transition-colors">
                {col.label}
              </th>
            ))}
          </tr></thead>
          <tbody className="divide-y divide-white/5">
            {filtered.map(row => (
              <tr key={row.id} className="hover:bg-white/2 transition-colors">
                {columns.map(col => (
                  <td key={String(col.key)} className="px-6 py-4 text-sm text-gray-300">
                    {col.render ? col.render((row as any)[col.key], row) : String((row as any)[col.key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}""",
        "metadata": {"component_type": "table", "style": "dark", "has_animation": False, "framework": "nextjs"}
    },
    {
        "id": "settings_page",
        "content": """'use client';
import { useState } from 'react';

export default function SettingsPage() {
  const [saved, setSaved] = useState(false);
  const [form, setForm] = useState({ name: 'John Doe', email: 'john@example.com', notifications: true, darkMode: true });

  function save(e: React.FormEvent) {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-white mb-8">Settings</h1>
      <div className="space-y-6">
        <section className="bg-gray-900 rounded-2xl border border-white/5 p-6">
          <h2 className="text-lg font-semibold text-white mb-6">Profile</h2>
          <form onSubmit={save} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Name</label>
              <input value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                className="w-full px-4 py-2.5 bg-gray-800 border border-white/10 rounded-lg text-white focus:outline-none focus:border-indigo-500" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Email</label>
              <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                className="w-full px-4 py-2.5 bg-gray-800 border border-white/10 rounded-lg text-white focus:outline-none focus:border-indigo-500" />
            </div>
            <button type="submit" className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg transition-colors">
              {saved ? '✓ Saved!' : 'Save changes'}
            </button>
          </form>
        </section>
        <section className="bg-gray-900 rounded-2xl border border-white/5 p-6">
          <h2 className="text-lg font-semibold text-white mb-6">Preferences</h2>
          <div className="space-y-4">
            {[{key:'notifications',label:'Email notifications'},{key:'darkMode',label:'Dark mode'}].map(({key, label}) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-gray-300">{label}</span>
                <button onClick={() => setForm({...form, [key]: !(form as any)[key]})}
                  className={`w-12 h-6 rounded-full transition-colors ${(form as any)[key] ? 'bg-indigo-600':'bg-gray-700'} relative`}>
                  <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${(form as any)[key] ? 'left-7':'left-1'}`} />
                </button>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}""",
        "metadata": {"component_type": "settings", "style": "dark", "has_auth": True, "framework": "nextjs"}
    },
    {
        "id": "features_grid",
        "content": """import { motion } from 'framer-motion';

const features = [
  { icon: '⚡', title: 'Lightning Fast', desc: 'Built on edge infrastructure for sub-100ms response times worldwide.' },
  { icon: '🔒', title: 'Enterprise Security', desc: 'SOC2 compliant with end-to-end encryption and audit logs.' },
  { icon: '🤖', title: 'AI-Powered', desc: 'Intelligent automation that learns from your workflow.' },
  { icon: '📊', title: 'Real-time Analytics', desc: 'Instant insights with live dashboards and custom reports.' },
  { icon: '🔄', title: 'Seamless Integration', desc: '200+ native integrations with your existing tools.' },
  { icon: '🌍', title: 'Global Scale', desc: 'Deployed across 30+ regions with 99.99% uptime SLA.' },
];

export default function FeaturesGrid() {
  return (
    <section className="py-24 bg-gray-950">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">Everything you need to succeed</h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">A complete platform for modern teams who want to move fast without breaking things.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((f, i) => (
            <motion.div key={f.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ delay: i * 0.1 }}
              className="p-6 bg-gray-900 rounded-2xl border border-white/5 hover:border-indigo-500/30 transition-all duration-300 group">
              <div className="text-3xl mb-4">{f.icon}</div>
              <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-indigo-300 transition-colors">{f.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}""",
        "metadata": {"component_type": "features", "style": "dark", "has_animation": True, "framework": "nextjs"}
    },
]


def seed_chromadb():
    """Seed ChromaDB with component examples"""
    try:
        import chromadb
        from chromadb.config import Settings
        import os

        persist_dir = os.environ.get(
            "CHROMA_PERSIST_DIR",
            str(Path(__file__).parent / "chromadb")
        )
        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        client = chromadb.PersistentClient(path=persist_dir)

        # Get or create collection
        collection = client.get_or_create_collection(
            name="novaryx_components",
            metadata={"hnsw:space": "cosine"}
        )

        existing = collection.get()
        existing_ids = set(existing["ids"]) if existing["ids"] else set()

        to_add = [ex for ex in COMPONENT_EXAMPLES if ex["id"] not in existing_ids]

        if not to_add:
            print(f"   ✅ ChromaDB already seeded ({len(existing_ids)} examples)")
            return True

        # Try to get embeddings from Ollama
        try:
            import requests
            embeddings = []
            for ex in to_add:
                resp = requests.post(
                    "http://localhost:11434/api/embeddings",
                    json={"model": "nomic-embed-text:latest", "prompt": ex["content"][:500]},
                    timeout=30
                )
                if resp.status_code == 200:
                    embeddings.append(resp.json().get("embedding", []))
                else:
                    embeddings = None
                    break
        except Exception:
            embeddings = None

        if embeddings and len(embeddings) == len(to_add):
            collection.add(
                ids=[ex["id"] for ex in to_add],
                documents=[ex["content"] for ex in to_add],
                metadatas=[ex["metadata"] for ex in to_add],
                embeddings=embeddings
            )
        else:
            collection.add(
                ids=[ex["id"] for ex in to_add],
                documents=[ex["content"] for ex in to_add],
                metadatas=[ex["metadata"] for ex in to_add],
            )

        print(f"   ✅ Seeded {len(to_add)} component examples into ChromaDB")
        return True

    except ImportError:
        print("   ⚠️  chromadb not installed: pip install chromadb")
        return False
    except Exception as e:
        print(f"   ⚠️  ChromaDB seed failed: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  NOVARYX — Seeding RAG Knowledge Base")
    print("=" * 50)
    seed_chromadb()
    print("Done.\n")
