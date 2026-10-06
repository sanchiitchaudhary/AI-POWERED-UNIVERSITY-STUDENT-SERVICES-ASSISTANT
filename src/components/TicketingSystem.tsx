import React, { useState } from 'react';
import { 
  TicketCheck, 
  Plus, 
  Clock, 
  CheckCircle2, 
  Sparkles, 
  Send, 
  User, 
  Bot, 
  ShieldCheck, 
  Filter,
  MessageSquare
} from 'lucide-react';
import { Ticket, StudentProfile } from '../types';

interface TicketingSystemProps {
  student: StudentProfile;
  tickets: Ticket[];
  onCreateTicket: (title: string, category: Ticket['category'], department: Ticket['department'], description: string) => void;
  onAddMessageToTicket: (ticketId: string, message: string) => void;
}

export const TicketingSystem: React.FC<TicketingSystemProps> = ({
  student,
  tickets,
  onCreateTicket,
  onAddMessageToTicket
}) => {
  const [selectedTicketId, setSelectedTicketId] = useState<string>(tickets[0]?.id || '');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [replyText, setReplyText] = useState('');

  // Create Form state
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState<Ticket['category']>('Bonafide Certificate');
  const [newDept, setNewDept] = useState<Ticket['department']>('Registrar');
  const [newDesc, setNewDesc] = useState('');

  const selectedTicket = tickets.find(t => t.id === selectedTicketId) || tickets[0];

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newDesc.trim()) return;
    onCreateTicket(newTitle, newCategory, newDept, newDesc);
    setShowCreateModal(false);
    setNewTitle('');
    setNewDesc('');
  };

  const handleReplySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!replyText.trim() || !selectedTicket) return;
    onAddMessageToTicket(selectedTicket.id, replyText);
    setReplyText('');
  };

  return (
    <div className="space-y-6 pb-8">
      
      {/* Header */}
      <div className="rounded-2xl border border-white/30 bg-[#12141c] p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <TicketCheck className="w-5 h-5 text-slate-200" />
            <h2 className="text-lg font-bold text-white">Administrative Support Tickets</h2>
          </div>
          <p className="text-xs text-slate-300 mt-1">
            Autonomous ticketing pipeline with AI auto-verification & department escalation.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2.5 rounded-xl bg-white/5 border border-white/20 hover:border-white/40 text-white font-bold text-xs flex items-center gap-2 transition-all shrink-0"
        >
          <Plus className="w-4 h-4 text-slate-200" />
          <span>New Administrative Ticket</span>
        </button>
      </div>

      {/* Main Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Tickets List */}
        <div className="rounded-2xl border border-white/30 bg-[#12141c] p-4 space-y-3 shadow-sm">
          <div className="px-2 py-1 flex items-center justify-between text-xs font-bold text-slate-300">
            <span>Ticket Queue ({tickets.length})</span>
            <Filter className="w-3.5 h-3.5 text-slate-400" />
          </div>

          <div className="space-y-2">
            {tickets.map((t) => {
              const isSelected = t.id === selectedTicketId;
              return (
                <div
                  key={t.id}
                  onClick={() => setSelectedTicketId(t.id)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                    isSelected 
                      ? 'bg-white/[0.04] border-white/30 shadow-sm' 
                      : 'bg-[#181a24] border-white/15 hover:border-white/30'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold text-slate-200">{t.id}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      t.status === 'Resolved' 
                        ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-400/20' 
                        : 'bg-white/5 text-slate-200 border border-white/15'
                    }`}>
                      {t.status}
                    </span>
                  </div>

                  <h4 className="text-xs font-bold text-white mt-1.5 line-clamp-1">{t.title}</h4>
                  
                  <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
                    <span>{t.department}</span>
                    <span>Updated {t.lastUpdated}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Ticket Thread Detail */}
        {selectedTicket ? (
          <div className="lg:col-span-2 rounded-2xl border border-white/30 bg-[#12141c] p-6 flex flex-col justify-between space-y-6 shadow-sm">
            <div>
              {/* Detail Header */}
              <div className="pb-4 border-b border-white/10 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-slate-200 bg-[#181a24] px-2 py-1 rounded border border-white/15">
                      {selectedTicket.id}
                    </span>
                    <span className="text-xs text-slate-300">Dept: <strong className="text-white">{selectedTicket.department}</strong></span>
                  </div>
                  <span className={`text-xs font-bold px-3 py-1 rounded-full ${
                    selectedTicket.status === 'Resolved' ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-400/20' : 'bg-white/5 text-slate-200 border border-white/15'
                  }`}>
                    {selectedTicket.status}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white">{selectedTicket.title}</h3>
                <p className="text-xs text-slate-300 leading-relaxed bg-[#181a24] p-3 rounded-xl border border-white/15">
                  {selectedTicket.description}
                </p>

                {selectedTicket.aiSummary && (
                  <div className="p-3 rounded-xl bg-white/[0.03] border border-white/15 text-xs text-slate-200 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-slate-200 shrink-0" />
                    <span><strong className="text-white">AI Auto-Verification:</strong> {selectedTicket.aiSummary}</span>
                  </div>
                )}
              </div>

              {/* Updates Thread */}
              <div className="my-6 space-y-4 max-h-80 overflow-y-auto pr-2">
                <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                  <MessageSquare className="w-3.5 h-3.5 text-slate-200" />
                  Activity History & Updates ({selectedTicket.updates.length})
                </h4>

                {selectedTicket.updates.map((upd, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-[#181a24] border border-white/15 space-y-1.5 text-xs">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-bold text-white flex items-center gap-1.5">
                        {upd.role === 'Student' ? <User className="w-3.5 h-3.5 text-slate-200" /> : <Bot className="w-3.5 h-3.5 text-slate-200" />}
                        {upd.author} <span className="text-[10px] text-slate-400 font-normal">({upd.role})</span>
                      </span>
                      <span className="text-[10px] text-slate-400">{upd.timestamp}</span>
                    </div>
                    <p className="text-slate-300 leading-relaxed">{upd.message}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Reply Form */}
            <form onSubmit={handleReplySubmit} className="flex gap-2 pt-4 border-t border-white/10">
              <input
                type="text"
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                placeholder="Post a message or attachment update to this ticket thread..."
                className="flex-1 px-4 py-2.5 bg-[#181a24] border border-white/20 rounded-xl text-xs text-white placeholder:text-slate-400 focus:outline-none focus:border-white/50"
              />
              <button
                type="submit"
                className="px-4 py-2.5 rounded-xl bg-white/5 border border-white/20 hover:bg-white/[0.08] text-white font-bold text-xs flex items-center gap-1.5 transition-all"
              >
                <span>Post Reply</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        ) : (
          <div className="lg:col-span-2 rounded-2xl border border-white/30 bg-[#12141c] p-12 text-center text-slate-300 shadow-sm">
            Select a ticket to view conversation details.
          </div>
        )}

      </div>

      {/* Create Ticket Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#12141c] border border-white/20 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-white/10">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <TicketCheck className="w-4 h-4 text-slate-200" />
                Submit New Support Ticket
              </h3>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-300 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Ticket Title</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Transcript Name Correction, Hostel Room AC Repair"
                  className="w-full px-3 py-2 bg-[#181a24] border border-white/20 rounded-lg text-xs text-white focus:border-white/45 outline-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Category</label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value as any)}
                    className="w-full px-3 py-2 bg-[#181a24] border border-white/20 rounded-lg text-xs text-white focus:border-white/45 outline-none"
                  >
                    <option value="Bonafide Certificate">Bonafide Certificate</option>
                    <option value="Transcript">Transcript</option>
                    <option value="Fee Dispute">Fee Dispute</option>
                    <option value="Hostel Maintenance">Hostel Maintenance</option>
                    <option value="Grade Appeal">Grade Appeal</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Department</label>
                  <select
                    value={newDept}
                    onChange={(e) => setNewDept(e.target.value as any)}
                    className="w-full px-3 py-2 bg-[#181a24] border border-white/20 rounded-lg text-xs text-white focus:border-white/45 outline-none"
                  >
                    <option value="Registrar">Registrar</option>
                    <option value="Finance">Finance</option>
                    <option value="Housing">Housing</option>
                    <option value="Academic Affairs">Academic Affairs</option>
                    <option value="IT Support">IT Support</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Detailed Description</label>
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  rows={3}
                  placeholder="Provide complete details..."
                  className="w-full px-3 py-2 bg-[#181a24] border border-white/20 rounded-lg text-xs text-white focus:border-white/45 outline-none"
                  required
                />
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg bg-white/5 border border-white/15 text-slate-200 text-xs hover:bg-white/[0.08]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-white/5 border border-white/20 text-white text-xs font-bold hover:bg-white/[0.08]"
                >
                  Create & Auto-Verify
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
