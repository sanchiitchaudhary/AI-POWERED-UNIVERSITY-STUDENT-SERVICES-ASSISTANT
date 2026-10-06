import React, { useState } from 'react';
import { 
  GraduationCap, 
  Sparkles, 
  Bell, 
  Search, 
  ChevronDown, 
  ShieldCheck,
  CheckCircle2,
  Calendar
} from 'lucide-react';
import { StudentProfile } from '../types';

interface NavbarProps {
  student: StudentProfile;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenDocumentModal: (type: 'transcript' | 'bonafide') => void;
  onVoiceTrigger: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  student,
  setActiveTab,
  onOpenDocumentModal,
  onVoiceTrigger
}) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const notifications = [
    { id: 1, title: 'Bonafide Certificate Ready', desc: 'Registrar has approved TICK-9042', time: '10 min ago', icon: CheckCircle2, color: 'text-emerald-400' },
    { id: 2, title: 'Upcoming Deadline', desc: 'CS601 Assignment 3 due in 24h', time: '2 hours ago', icon: Calendar, color: 'text-amber-400' },
    { id: 3, title: 'Scholarship Disbursed', desc: 'HCL AI Excellence Award $5,000 credited', time: '1 day ago', icon: ShieldCheck, color: 'text-indigo-400' },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-white/10 bg-[#12141c]/90 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        
        {/* Brand */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-slate-100 text-slate-900 border border-slate-200">
            <GraduationCap className="w-4 h-4 text-slate-900" />
          </div>
          <div className="leading-none">
            <span className="font-semibold text-base tracking-tight text-slate-100">
              UniAssist
            </span>
          </div>
        </div>

        {/* Command Bar */}
        <div className="hidden md:flex flex-1 max-w-2xl items-center justify-center">
          <div className="relative w-full max-w-xl">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search services, records, or requests..."
              onClick={() => setActiveTab('copilot')}
              className="w-full pl-9 pr-12 py-2.5 text-xs bg-[#1a1d26] border border-white/10 rounded-xl text-white placeholder:text-slate-400 focus:outline-none focus:border-white/20 transition-colors cursor-pointer"
              readOnly
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1 text-[10px] text-slate-400">
              <span className="px-1.5 py-0.5 rounded border border-white/10 bg-[#21262f] text-slate-200">⌘K</span>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Notifications Dropdown */}
          <div className="relative">
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-xl bg-slate-100 text-slate-900 border border-slate-200 hover:bg-slate-200 transition-colors"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-slate-900"></span>
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 rounded-2xl glass-card bg-slate-900/95 border border-slate-800 p-4 shadow-2xl z-50 animate-in fade-in slide-in-from-top-2">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <h4 className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                    AI Campus Notifications
                  </h4>
                  <span className="text-[10px] bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-full">3 New</span>
                </div>
                <div className="divide-y divide-slate-800/60 my-2">
                  {notifications.map((item) => (
                    <div key={item.id} className="py-2.5 flex items-start gap-3 hover:bg-slate-800/40 rounded-lg p-2 transition-colors cursor-pointer">
                      <item.icon className={`w-4 h-4 mt-0.5 shrink-0 ${item.color}`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-slate-200">{item.title}</p>
                        <p className="text-[11px] text-slate-400 truncate">{item.desc}</p>
                        <span className="text-[10px] text-slate-500 mt-1 block">{item.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <button 
                  onClick={() => { setShowNotifications(false); setActiveTab('tickets'); }}
                  className="w-full text-center text-xs text-indigo-400 hover:text-indigo-300 pt-2 font-medium"
                >
                  View All Administrative Updates →
                </button>
              </div>
            )}
          </div>

          {/* Student Profile Quick Badge */}
          <div className="relative">
            <button 
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="flex items-center gap-2 pl-2 pr-1.5 py-1 rounded-xl bg-slate-100 border border-slate-200 text-slate-900 transition-colors hover:bg-slate-200"
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-900 text-[10px] font-semibold text-white ring-2 ring-slate-300">
                {student.name
                  .split(' ')
                  .map(part => part[0])
                  .slice(0, 2)
                  .join('')
                  .toUpperCase()}
              </div>
              <div className="text-left hidden xl:block">
                <p className="text-xs font-bold text-slate-200 leading-none">{student.name}</p>
                <p className="text-[10px] text-slate-400 leading-tight mt-0.5">Student</p>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {showProfileMenu && (
              <div className="absolute right-0 mt-2 w-64 rounded-2xl glass-card bg-slate-900/95 border border-slate-800 p-4 shadow-2xl z-50">
                <div className="flex items-center gap-3 pb-3 border-b border-slate-800">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500/80 to-slate-700 text-xs font-semibold text-white">
                    {student.name
                      .split(' ')
                      .map(part => part[0])
                      .slice(0, 2)
                      .join('')
                      .toUpperCase()}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-100">{student.name}</h4>
                    <p className="text-[11px] text-slate-400">{student.major}</p>
                    <span className="text-[10px] text-indigo-400 font-mono">{student.email}</span>
                  </div>
                </div>

                <div className="py-3 text-xs space-y-2">
                  <div className="flex justify-between text-slate-300">
                    <span className="text-slate-400">Semester:</span>
                    <span className="font-semibold">{student.semester}th Sem ({student.year})</span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span className="text-slate-400">Advisor:</span>
                    <span className="font-semibold text-indigo-300">{student.advisorName}</span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span className="text-slate-400">Fee Status:</span>
                    <span className="font-semibold text-emerald-400 flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> {student.financialStatus}
                    </span>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-800 flex gap-2">
                  <button 
                    onClick={() => { setShowProfileMenu(false); setActiveTab('copilot'); }}
                    className="w-full text-center py-1.5 text-xs rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition-colors"
                  >
                    Open AI Copilot
                  </button>
                </div>
              </div>
            )}
          </div>

        </div>

      </div>
    </header>
  );
};
