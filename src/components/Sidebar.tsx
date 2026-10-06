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
  Sparkles
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
    { id: 'copilot', label: 'Regulations Search', icon: Bot, badge: null, highlight: true },
    { id: 'academic', label: 'Academic & Degree Audit', icon: BookOpenCheck, badge: null },
    { id: 'certificates', label: 'Transcripts & Seals', icon: FileCheck2, badge: 'Instant' },
    { id: 'verification', label: 'Public Verification', icon: ShieldAlert, badge: 'RSA-2048' },
    { id: 'financial', label: 'Financial Aid & Fees', icon: Wallet, badge: null },
    { id: 'tickets', label: 'Support Tickets', icon: TicketCheck, badge: openTicketCount > 0 ? `${openTicketCount} Active` : null },
    { id: 'housing', label: 'Housing & Dining', icon: Home, badge: null },
    { id: 'advisors', label: 'Advisor Booking', icon: CalendarDays, badge: null },
    { id: 'security', label: 'Emergency & Safety', icon: ShieldAlert, badge: null, alert: true },
  ];

  return (
    <aside className="w-full lg:w-64 shrink-0 border-r border-white/10 bg-[#0a0b10] p-4 flex flex-col justify-between">
      <div>
        <div className="px-3 py-2 text-[11px] font-medium uppercase tracking-[0.12em] text-slate-500 flex items-center justify-between">
          <span>Student Services</span>
          <span className="flex items-center gap-1.5 text-emerald-400 text-[10px]">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            Active
          </span>
        </div>

        <nav className="mt-2 space-y-1">
          {menuItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-colors duration-150 ${
                  isActive 
                    ? 'bg-slate-100 text-slate-900 font-semibold border border-slate-100' 
                    : item.highlight
                    ? 'bg-white/5 text-slate-300 border border-white/5 hover:bg-white/10 hover:text-white'
                    : 'text-slate-300 hover:text-white hover:bg-white/10 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  <item.icon className={`w-4 h-4 ${isActive ? 'text-slate-900' : item.highlight ? 'text-slate-200' : item.alert ? 'text-rose-300' : 'text-slate-300'}`} />
                  <span>{item.label}</span>
                </div>

                {item.badge && (
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                    isActive 
                      ? 'bg-slate-900 text-white' 
                      : item.alert 
                      ? 'bg-rose-500/15 text-rose-200 border border-rose-500/20' 
                      : 'bg-slate-800 text-slate-200 border border-slate-700'
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
      <div className="mt-6 pt-4 border-t border-white/10">
        <div className="p-3 rounded-xl border border-white/10 bg-[#12151d]">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-slate-200" />
            <h4 className="text-xs font-medium text-slate-100">System status</h4>
          </div>
          <p className="text-[11px] text-slate-400 mt-1 leading-snug">
            Service coverage for records, fees, transcripts, and support requests.
          </p>
          <div className="mt-2.5 flex items-center justify-between text-[10px] text-slate-400">
            <span>Latency: <strong className="text-emerald-400 font-mono">14ms</strong></span>
            <span>Uptime: <strong className="text-slate-200 font-mono">99.99%</strong></span>
          </div>
        </div>
      </div>
    </aside>
  );
};
