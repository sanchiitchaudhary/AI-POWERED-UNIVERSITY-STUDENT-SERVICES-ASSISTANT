import React from 'react';
import { 
  GraduationCap, 
  Sparkles, 
  Award, 
  FileText, 
  Wallet, 
  TicketCheck, 
  Calendar, 
  ArrowUpRight, 
  CheckCircle2, 
  Clock, 
  ChevronRight,
  TrendingUp,
  ShieldCheck,
  Building,
  UserCheck
} from 'lucide-react';
import { StudentProfile, Ticket, CampusEvent } from '../types';

interface DashboardOverviewProps {
  student: StudentProfile;
  tickets: Ticket[];
  events: CampusEvent[];
  setActiveTab: (tab: string) => void;
  onOpenDocumentModal: (type: 'transcript' | 'bonafide') => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  student,
  tickets,
  events,
  setActiveTab,
  onOpenDocumentModal
}) => {
  const activeTickets = tickets.filter(t => t.status !== 'Resolved');

  return (
    <div className="space-y-6 pb-8">
      
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl glass-card border border-indigo-500/30 p-6 sm:p-8 bg-gradient-to-r from-slate-950 via-indigo-950/60 to-purple-950/40">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
        
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-spin-slow" />
              <span>AI Student Assistant Active • Fall Semester 2026</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Welcome back, <span className="bg-gradient-to-r from-indigo-300 via-purple-300 to-cyan-300 bg-clip-text text-transparent">{student.name}</span> 👋
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              You are on track for graduation in <strong className="text-white">Senior Year (Sem 6)</strong>. Your bonafide certificate request was approved today. All financial aid awards are credited.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={() => setActiveTab('copilot')}
              className="px-5 py-3 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-bold text-xs flex items-center gap-2 shadow-xl shadow-indigo-600/30 transition-all scale-100 hover:scale-105"
            >
              <Sparkles className="w-4 h-4 text-cyan-200" />
              <span>Launch AI Copilot</span>
            </button>
          </div>
        </div>
      </div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Metric 1: CGPA */}
        <div className="glass-card p-5 rounded-2xl border border-slate-800 hover:border-indigo-500/40 transition-all group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">Cumulative GPA</span>
            <div className="w-8 h-8 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <GraduationCap className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-black text-white">{student.gpa}</span>
            <span className="text-[11px] text-emerald-400 font-semibold flex items-center gap-0.5">
              <TrendingUp className="w-3 h-3" /> Top 5% Dean's List
            </span>
          </div>
          <div className="mt-3 w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full" style={{ width: `${(student.gpa / 4.0) * 100}%` }}></div>
          </div>
        </div>

        {/* Metric 2: Financial Dues */}
        <div className="glass-card p-5 rounded-2xl border border-slate-800 hover:border-emerald-500/40 transition-all group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">Tuition & Fee Dues</span>
            <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-black text-white">$0.00</span>
            <span className="text-[11px] text-emerald-400 font-semibold flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> Clear (Zero Dues)
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-3">Scholarships Credited: <strong className="text-indigo-300">$7,500</strong></p>
        </div>

        {/* Metric 3: Credits Earned */}
        <div className="glass-card p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/40 transition-all group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">Earned Credits</span>
            <div className="w-8 h-8 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-black text-white">{student.creditsEarned} <span className="text-xs font-normal text-slate-400">/ {student.totalRequiredCredits}</span></span>
            <span className="text-[11px] text-cyan-400 font-semibold">78% Progress</span>
          </div>
          <div className="mt-3 w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-gradient-to-r from-cyan-500 to-indigo-500 h-full rounded-full" style={{ width: `${(student.creditsEarned / student.totalRequiredCredits) * 100}%` }}></div>
          </div>
        </div>

        {/* Metric 4: Active Tickets */}
        <div className="glass-card p-5 rounded-2xl border border-slate-800 hover:border-purple-500/40 transition-all group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">Active Support Tickets</span>
            <div className="w-8 h-8 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center">
              <TicketCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-black text-white">{activeTickets.length}</span>
            <span className="text-[11px] text-indigo-300 font-semibold">In Review</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-3">Latest: <strong className="text-slate-200">TICK-9042 (Registrar)</strong></p>
        </div>

      </div>

      {/* Quick Action Launcher Grid */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          AI Smart Actions Launcher
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          
          <button 
            onClick={() => onOpenDocumentModal('transcript')}
            className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-indigo-500/50 hover:bg-indigo-950/40 text-left transition-all group"
          >
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
              <FileText className="w-4 h-4" />
            </div>
            <p className="text-xs font-bold text-white">Official Transcript</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Instant Verified PDF</p>
          </button>

          <button 
            onClick={() => onOpenDocumentModal('bonafide')}
            className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-purple-500/50 hover:bg-purple-950/40 text-left transition-all group"
          >
            <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <p className="text-xs font-bold text-white">Bonafide Letter</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Visa & Bank Seal</p>
          </button>

          <button 
            onClick={() => setActiveTab('financial')}
            className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-emerald-500/50 hover:bg-emerald-950/40 text-left transition-all group"
          >
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
              <Wallet className="w-4 h-4" />
            </div>
            <p className="text-xs font-bold text-white">Fee Receipts</p>
            <p className="text-[10px] text-slate-400 mt-0.5">View Payment Gateway</p>
          </button>

          <button 
            onClick={() => setActiveTab('advisors')}
            className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/50 hover:bg-cyan-950/40 text-left transition-all group"
          >
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
              <UserCheck className="w-4 h-4" />
            </div>
            <p className="text-xs font-bold text-white">Book Advisor</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Dr. Sarah Jenkins</p>
          </button>

          <button 
            onClick={() => setActiveTab('housing')}
            className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-amber-500/50 hover:bg-amber-950/40 text-left transition-all group"
          >
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
              <Building className="w-4 h-4" />
            </div>
            <p className="text-xs font-bold text-white">Hostel & Dining</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Room 402 Services</p>
          </button>

        </div>
      </div>

      {/* Two Column Section: Live Tickets Pipeline & Upcoming Events */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Support Tickets Overview */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <TicketCheck className="w-4 h-4 text-purple-400" />
                Administrative Request Tickets
              </h3>
              <button 
                onClick={() => setActiveTab('tickets')}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1"
              >
                <span>View All Desk</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="space-y-3">
              {tickets.slice(0, 2).map((ticket) => (
                <div key={ticket.id} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">{ticket.id}</span>
                    <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                      ticket.status === 'Resolved' 
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' 
                        : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                    }`}>
                      {ticket.status}
                    </span>
                  </div>
                  <h4 className="text-xs font-bold text-white mt-2">{ticket.title}</h4>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">{ticket.description}</p>
                  
                  {ticket.aiSummary && (
                    <div className="mt-2.5 p-2 rounded-lg bg-indigo-950/40 border border-indigo-500/20 text-[10px] text-indigo-200 flex items-center gap-2">
                      <Sparkles className="w-3 h-3 text-cyan-400 shrink-0" />
                      <span>{ticket.aiSummary}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Campus Events & Hackathons */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Calendar className="w-4 h-4 text-cyan-400" />
                Upcoming Campus Events & Hackathons
              </h3>
              <span className="text-[10px] bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded-full">HCL Featured</span>
            </div>

            <div className="space-y-3">
              {events.map((evt) => (
                <div key={evt.id} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        {evt.category}
                      </span>
                      <span className="text-[10px] text-slate-400">{evt.organizer}</span>
                    </div>
                    <h4 className="text-xs font-bold text-white mt-1.5">{evt.title}</h4>
                    <p className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-3">
                      <span>🗓️ {evt.date}</span>
                      <span>📍 {evt.location}</span>
                    </p>
                  </div>
                  <button 
                    onClick={() => alert(`Registered for ${evt.title}!`)}
                    className="shrink-0 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-bold transition-all"
                  >
                    RSVP Now
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
