import React, { useState } from 'react';
import { 
  GraduationCap, 
  Sparkles, 
  Award, 
  FileText, 
  Wallet, 
  TicketCheck, 
  ArrowUpRight, 
  CheckCircle2, 
  TrendingUp,
  ShieldCheck,
  Building,
  UserCheck,
  SendHorizonal,
  MessageSquareText
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
  const [assistantQuery, setAssistantQuery] = useState('');
  const querySuggestions = [
    'Check scholarship eligibility',
    'View attendance policy',
    'Request bonafide certificate'
  ];

  return (
    <div className="grid grid-cols-12 gap-6 items-stretch pb-8">
      <div className="col-span-12 lg:col-span-8 space-y-4">
        <div className="rounded-xl border border-white/30 bg-[#12141c] py-3 px-5 shadow-sm transition-colors hover:border-white/40">
          <div className="flex flex-col gap-1">
            <div className="inline-flex items-center gap-2 text-[10px] font-medium text-slate-300">
              <span className="inline-flex h-2 w-2 rounded-full bg-emerald-500" />
              <span>Fall Semester 2026</span>
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white leading-tight">
              Welcome back, {student.name}
            </h1>
            <p className="text-[11px] text-slate-300">
              <span className="text-white">Senior Year</span> • <span>Semester 6</span>
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="flex h-[135px] flex-col justify-between rounded-xl border border-white/30 bg-[#12141c] p-4 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-white/45 hover:shadow-md">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs text-slate-300 font-medium">Cumulative GPA</span>
              <GraduationCap className="w-4 h-4 text-slate-300" />
            </div>
            <div className="flex items-end justify-between gap-2">
              <span className="text-3xl font-bold text-white tracking-tight">{student.gpa}</span>
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400">
                <TrendingUp className="w-3 h-3" /> Top 5%
              </span>
            </div>
          </div>

          <div className="flex h-[135px] flex-col justify-between rounded-xl border border-white/30 bg-[#12141c] p-4 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-white/45 hover:shadow-md">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs text-slate-300 font-medium">Tuition & Fee Dues</span>
              <Wallet className="w-4 h-4 text-slate-300" />
            </div>
            <div className="flex items-end justify-between gap-2">
              <span className="text-3xl font-bold text-white tracking-tight">$0.00</span>
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400">
                <CheckCircle2 className="w-3 h-3" /> Clear
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Scholarships credited: <span className="text-white font-medium">$7,500</span></p>
          </div>

          <div className="flex h-[135px] flex-col justify-between rounded-xl border border-white/30 bg-[#12141c] p-4 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-white/45 hover:shadow-md">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs text-slate-300 font-medium">Earned Credits</span>
              <Award className="w-4 h-4 text-slate-300" />
            </div>
            <div className="flex items-end justify-between gap-2">
              <span className="text-3xl font-bold text-white tracking-tight">{student.creditsEarned}</span>
              <span className="text-[11px] font-semibold text-slate-300">78% progress</span>
            </div>
            <p className="text-[11px] text-slate-400">of {student.totalRequiredCredits} required</p>
          </div>

          <div className="flex h-[135px] flex-col justify-between rounded-xl border border-white/30 bg-[#12141c] p-4 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-white/45 hover:shadow-md">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs text-slate-300 font-medium">Active Tickets</span>
              <TicketCheck className="w-4 h-4 text-slate-300" />
            </div>
            <div className="flex items-end justify-between gap-2">
              <span className="text-3xl font-bold text-white tracking-tight">{activeTickets.length}</span>
              <span className="inline-flex items-center rounded-full border border-white/15 bg-white/5 px-2 py-0.5 text-[10px] font-semibold text-slate-200">In review</span>
            </div>
            <p className="text-[11px] text-slate-400">Latest: <span className="text-white font-medium">TICK-9042</span></p>
          </div>
        </div>

        <div className="rounded-xl border border-white/30 bg-[#12141c] p-4 shadow-sm transition-colors hover:border-white/40">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-medium text-white">
            <Sparkles className="w-4 h-4 text-slate-300" />
            Quick Actions
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            <button
              onClick={() => onOpenDocumentModal('transcript')}
              className="group relative rounded-xl border border-white/30 bg-[#181a24] p-3 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-white/45 hover:shadow-lg hover:shadow-black/20 cursor-pointer"
            >
              <ArrowUpRight className="absolute right-3 top-3 h-3.5 w-3.5 text-slate-300" />
              <div className="mb-2 text-slate-100">
                <FileText className="w-4 h-4" />
              </div>
              <p className="text-xs font-medium text-white">Official Transcript</p>
              <p className="mt-0.5 text-[10px] text-slate-400">Verified PDF</p>
            </button>

            <button
              onClick={() => onOpenDocumentModal('bonafide')}
              className="group relative rounded-xl border border-white/30 bg-[#181a24] p-3 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-white/45 hover:shadow-lg hover:shadow-black/20 cursor-pointer"
            >
              <ArrowUpRight className="absolute right-3 top-3 h-3.5 w-3.5 text-slate-300" />
              <div className="mb-2 text-slate-100">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <p className="text-xs font-medium text-white">Bonafide Letter</p>
              <p className="mt-0.5 text-[10px] text-slate-400">Visa & Bank Seal</p>
            </button>

            <button
              onClick={() => setActiveTab('financial')}
              className="group relative rounded-xl border border-white/30 bg-[#181a24] p-3 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-white/45 hover:shadow-lg hover:shadow-black/20 cursor-pointer"
            >
              <ArrowUpRight className="absolute right-3 top-3 h-3.5 w-3.5 text-slate-300" />
              <div className="mb-2 text-slate-100">
                <Wallet className="w-4 h-4" />
              </div>
              <p className="text-xs font-medium text-white">Fee Receipts</p>
              <p className="mt-0.5 text-[10px] text-slate-400">Payment Status</p>
            </button>

            <button
              onClick={() => setActiveTab('advisors')}
              className="group relative rounded-xl border border-white/30 bg-[#181a24] p-3 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-white/45 hover:shadow-lg hover:shadow-black/20 cursor-pointer"
            >
              <ArrowUpRight className="absolute right-3 top-3 h-3.5 w-3.5 text-slate-300" />
              <div className="mb-2 text-slate-100">
                <UserCheck className="w-4 h-4" />
              </div>
              <p className="text-xs font-medium text-white">Book Advisor</p>
              <p className="mt-0.5 text-[10px] text-slate-400">Dr. Sarah Jenkins</p>
            </button>

            <button
              onClick={() => setActiveTab('housing')}
              className="group relative rounded-xl border border-white/30 bg-[#181a24] p-3 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-white/45 hover:shadow-lg hover:shadow-black/20 cursor-pointer"
            >
              <ArrowUpRight className="absolute right-3 top-3 h-3.5 w-3.5 text-slate-300" />
              <div className="mb-2 text-slate-100">
                <Building className="w-4 h-4" />
              </div>
              <p className="text-xs font-medium text-white">Hostel & Dining</p>
              <p className="mt-0.5 text-[10px] text-slate-400">Room 402</p>
            </button>
          </div>
        </div>
      </div>

      <aside className="col-span-12 h-full lg:col-span-4">
        <div className="flex h-full flex-col justify-between rounded-2xl border border-white/30 bg-[#12141c] p-4 shadow-sm transition-all hover:border-white/40">
          <div className="flex items-center justify-between gap-3 pb-3">
            <h2 className="text-base font-semibold text-white">AI Assistant</h2>
            <span className="inline-flex items-center rounded-full border border-white/15 bg-white/5 px-2 py-0.5 text-[10px] font-semibold text-slate-200">● Active</span>
          </div>

          <div className="flex flex-1 flex-col justify-center">
            <div className="mb-6 flex items-center justify-center gap-2 text-slate-300">
              <Sparkles className="h-3.5 w-3.5 opacity-70" />
              <span className="text-center text-[11px] leading-relaxed text-slate-300">
                How can I assist with your university records or regulations today?
              </span>
            </div>
          </div>

          <div className="mt-auto">
            <div className="mb-3 flex flex-col gap-2">
              {['Scholarship eligibility', 'Attendance policy', 'Bonafide certificate'].map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => setAssistantQuery(suggestion)}
                  className="inline-flex w-full items-center justify-start rounded-full border border-white/30 bg-[#181a24] px-3 py-2 text-left text-[11px] font-medium text-white transition-colors hover:bg-white/[0.04] hover:border-white/45"
                >
                  <span className="mr-2 text-slate-300">✦</span>
                  {suggestion}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2 rounded-xl border border-white/30 bg-[#181a24] px-3 py-2.5 transition-all focus-within:border-white/60">
              <input
                value={assistantQuery}
                onChange={(e) => setAssistantQuery(e.target.value)}
                placeholder="Ask about records, eligibility, or policies"
                className="w-full bg-transparent text-xs text-white placeholder:text-slate-400 focus:outline-none"
              />
              <button
                onClick={() => setActiveTab('copilot')}
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/5 text-white transition-colors hover:bg-white/10 border border-white/10"
                aria-label="Send message"
              >
                <SendHorizonal className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
};
