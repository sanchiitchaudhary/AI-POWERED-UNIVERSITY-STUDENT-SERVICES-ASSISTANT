import React, { useState } from 'react';
import { 
  GraduationCap, 
  Sparkles, 
  Bell, 
  Mic, 
  FileText, 
  Search, 
  ChevronDown, 
  ShieldCheck,
  Zap,
  CheckCircle2,
  Calendar,
  AlertTriangle
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
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        
        {/* Brand & Logo */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-cyan-400 p-0.5 shadow-lg shadow-indigo-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <GraduationCap className="w-5 h-5 text-indigo-400" />
            </div>
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent">
                UniAssist <span className="text-indigo-400">AI</span>
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                HCL Hackathon
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">University Student Services Assistant</p>
          </div>
        </div>

        {/* Global Search Bar & Shortcuts */}
        <div className="hidden md:flex flex-1 max-w-md items-center">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Ask UniAssist AI (e.g. transcript, GPA calculation, fee clearance)..."
              onClick={() => setActiveTab('copilot')}
              className="w-full pl-9 pr-24 py-1.5 text-xs bg-slate-900/90 border border-slate-800 rounded-full text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/60 transition-all cursor-pointer"
              readOnly
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
              <span className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-400 border border-slate-700">⌘K</span>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 sm:gap-3">
          
          {/* Quick Certificate Actions */}
          <div className="hidden lg:flex items-center gap-2">
            <button 
              onClick={() => onOpenDocumentModal('transcript')}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-indigo-950/60 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-900/60 hover:border-indigo-400 transition-all"
            >
              <FileText className="w-3.5 h-3.5 text-indigo-400" />
              <span>Transcript PDF</span>
            </button>
            <button 
              onClick={() => onOpenDocumentModal('bonafide')}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-purple-950/60 text-purple-300 border border-purple-500/30 hover:bg-purple-900/60 hover:border-purple-400 transition-all"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
              <span>Bonafide Seal</span>
            </button>
          </div>

          {/* Voice AI Assistant Mic Button */}
          <button 
            onClick={onVoiceTrigger}
            title="Speak with AI Voice Assistant"
            className="relative flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r from-cyan-600/30 to-indigo-600/30 border border-cyan-500/40 text-cyan-300 hover:from-cyan-600/50 hover:to-indigo-600/50 transition-all text-xs font-semibold group shadow-lg shadow-cyan-950"
          >
            <Mic className="w-3.5 h-3.5 text-cyan-400 group-hover:scale-110 transition-transform animate-pulse" />
            <span className="hidden sm:inline">Voice Assistant</span>
          </button>

          {/* Notifications Dropdown */}
          <div className="relative">
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-xl bg-slate-900/90 text-slate-300 border border-slate-800 hover:border-slate-700 hover:text-white transition-all"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-indigo-500"></span>
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
              className="flex items-center gap-2 pl-2 pr-1.5 py-1 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all"
            >
              <img 
                src={student.avatar} 
                alt={student.name} 
                className="w-7 h-7 rounded-lg object-cover ring-2 ring-indigo-500/40"
              />
              <div className="text-left hidden xl:block">
                <p className="text-xs font-bold text-slate-200 leading-none">{student.name}</p>
                <p className="text-[10px] text-indigo-400 font-mono leading-tight mt-0.5">GPA {student.gpa} • {student.id}</p>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {showProfileMenu && (
              <div className="absolute right-0 mt-2 w-64 rounded-2xl glass-card bg-slate-900/95 border border-slate-800 p-4 shadow-2xl z-50">
                <div className="flex items-center gap-3 pb-3 border-b border-slate-800">
                  <img src={student.avatar} alt={student.name} className="w-10 h-10 rounded-xl object-cover" />
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
