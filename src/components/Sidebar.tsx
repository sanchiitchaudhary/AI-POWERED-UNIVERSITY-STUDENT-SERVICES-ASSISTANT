import React from 'react';
import { 
  LayoutDashboard, 
  Bot, 
  BookOpenCheck, 
  FileCheck2, 
  Wallet, 
  TicketCheck, 
  Home, 
  CalendarDays, 
  ShieldAlert,
  Sparkles,
  Zap
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  openTicketCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  openTicketCount
}) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard Overview', icon: LayoutDashboard, badge: null },
    { id: 'copilot', label: 'AI Student Copilot', icon: Bot, badge: 'AI 24/7', highlight: true },
    { id: 'academic', label: 'Academic & Degree Audit', icon: BookOpenCheck, badge: null },
    { id: 'certificates', label: 'Transcripts & Seals', icon: FileCheck2, badge: 'Instant' },
    { id: 'verification', label: 'Public Verification', icon: ShieldAlert, badge: 'RSA-2048' },
    { id: 'financial', label: 'Financial Aid & Fees', icon: Wallet, badge: null },
    { id: 'tickets', label: 'Support Tickets', icon: TicketCheck, badge: openTicketCount > 0 ? `${openTicketCount} Active` : null },
    { id: 'housing', label: 'Housing & Dining', icon: Home, badge: null },
    { id: 'advisors', label: 'Advisor Booking', icon: CalendarDays, badge: null },
    { id: 'security', label: 'Emergency & Safety', icon: ShieldAlert, badge: 'SOS', alert: true },
  ];

  return (
    <aside className="w-full lg:w-64 shrink-0 glass-panel border-r border-slate-800/80 bg-slate-950/60 p-4 flex flex-col justify-between">
      <div>
        <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
          <span>Student Services Hub</span>
          <span className="flex items-center gap-1 text-emerald-400 text-[10px]">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            AI Online
          </span>
        </div>

        <nav className="mt-2 space-y-1">
          {menuItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                  isActive 
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/25 border border-indigo-400/40 scale-[1.02]' 
                    : item.highlight
                    ? 'bg-indigo-950/40 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-900/40 hover:text-white'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/80 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  <item.icon className={`w-4 h-4 ${isActive ? 'text-white' : item.highlight ? 'text-indigo-400' : item.alert ? 'text-rose-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>

                {item.badge && (
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                    isActive 
                      ? 'bg-white/20 text-white' 
                      : item.alert 
                      ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' 
                      : 'bg-slate-800 text-indigo-300 border border-slate-700'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* AI System Capability & HCL Banner */}
      <div className="mt-6 pt-4 border-t border-slate-800/80">
        <div className="p-3 rounded-2xl bg-gradient-to-b from-indigo-950/60 to-purple-950/60 border border-indigo-500/30 relative overflow-hidden">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400 animate-spin-slow" />
            <h4 className="text-xs font-bold text-white">HCL Hackathon Edition</h4>
          </div>
          <p className="text-[11px] text-slate-300 mt-1 leading-snug">
            Autonomous multi-modal RAG assistant trained on university regulations & registrar records.
          </p>
          <div className="mt-2.5 flex items-center justify-between text-[10px] text-slate-400">
            <span>Latency: <strong className="text-emerald-400 font-mono">14ms</strong></span>
            <span>Uptime: <strong className="text-indigo-300 font-mono">99.99%</strong></span>
          </div>
        </div>
      </div>
    </aside>
  );
};
