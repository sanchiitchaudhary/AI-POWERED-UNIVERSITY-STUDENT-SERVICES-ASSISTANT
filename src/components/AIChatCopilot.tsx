import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  Send, 
  User, 
  Sparkles, 
  Mic, 
  MicOff, 
  Paperclip, 
  FileText, 
  Zap, 
  RefreshCw, 
  CheckCircle2, 
  ArrowRight,
  ShieldAlert,
  HelpCircle,
  BookOpen,
  DollarSign,
  Building,
  Award
} from 'lucide-react';
import { ChatMessage, StudentProfile, Ticket } from '../types';
import { AI_KNOWLEDGE_BASE } from '../data/mockData';

interface AIChatCopilotProps {
  student: StudentProfile;
  onOpenDocumentModal: (type: 'transcript' | 'bonafide') => void;
  onCreateTicket: (title: string, category: Ticket['category'], department: Ticket['department'], description: string) => void;
  isVoiceActive: boolean;
  setIsVoiceActive: (active: boolean) => void;
}

export const AIChatCopilot: React.FC<AIChatCopilotProps> = ({
  student,
  onOpenDocumentModal,
  onCreateTicket,
  isVoiceActive,
  setIsVoiceActive
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'msg-1',
      sender: 'ai',
      text: `Hello **${student.name}**! 👋 I am **UniAssist AI**, your 24/7 autonomous student services assistant. 

How can I help you today? You can ask me to:
- 📜 **Generate Official Transcripts or Bonafide Certificates**
- 📊 **Calculate Target GPA & Prerequisites**
- 💳 **Verify Tuition Fees & Scholarship Status**
- 🎟️ **Submit Administrative Support Tickets**
- 🏠 **Manage Hostel & Dining Services**`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      category: 'General',
      suggestedActions: [
        { label: '📜 Download Official Transcript', action: 'transcript' },
        { label: '🎓 Check Bonafide Certificate', action: 'bonafide' },
        { label: '📈 Calculate Target GPA', action: 'gpa' },
        { label: '💰 Scholarship & Fee Status', action: 'financial' },
      ]
    }
  ]);

  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<'All' | 'Academic' | 'Financial' | 'Administrative' | 'Housing'>('All');
  const [escalateTicketTitle, setEscalateTicketTitle] = useState('');
  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickPrompts = [
    { text: "Can I get an official transcript for grad school applications?", icon: FileText, category: 'Academic' },
    { text: "What is my current fee balance and scholarship status?", icon: DollarSign, category: 'Financial' },
    { text: "How do I request a bonafide letter for my visa renewal?", icon: Award, category: 'Administrative' },
    { text: "My hostel room AC needs filter cleaning", icon: Building, category: 'Housing' },
    { text: "Who is my academic advisor and how do I book a meeting?", icon: BookOpen, category: 'Academic' },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Voice Web Speech API setup
  const toggleVoice = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert("Speech recognition is simulated in this browser session!");
      setIsVoiceActive(!isVoiceActive);
      return;
    }

    setIsVoiceActive(!isVoiceActive);
    if (!isVoiceActive) {
      handleSendText("What is my current GPA and fee status?");
    }
  };

  const handleSendText = (textToSend?: string) => {
    const messageText = textToSend || input;
    if (!messageText.trim()) return;

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text: messageText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setIsTyping(true);

    // Simulate AI Intelligence RAG search & response synthesis
    setTimeout(() => {
      const lower = messageText.toLowerCase();
      let responseText = "";
      let suggestedActions: { label: string; action: string }[] | undefined;

      if (lower.includes('transcript') || lower.includes('grade sheet') || lower.includes('marksheet')) {
        responseText = `Here is your official transcript update for **${student.name}** (ID: **${student.id}**):\n\n` +
          `- **Cumulative GPA:** 3.86 / 4.0\n` +
          `- **Total Completed Credits:** 94 / 120\n` +
          `- **Enrolled Courses (Sem 6):** CS601, CS602, CS603, CS604\n\n` +
          `You can view and print your digitally signed transcript right now!`;
        suggestedActions = [
          { label: '📄 Open Transcript Viewer', action: 'transcript' },
          { label: '📜 Download Bonafide Seal', action: 'bonafide' }
        ];
      } else if (lower.includes('bonafide') || lower.includes('visa') || lower.includes('certificate')) {
        responseText = `I have verified your active enrollment in **${student.major}**. Your bonafide student status letter has been pre-verified with digital QR checksum.\n\n` +
          `Status: **APPROVED & SEALED** by Registrar Office. Click below to view and download.`;
        suggestedActions = [
          { label: '📜 Open Bonafide Letter', action: 'bonafide' }
        ];
      } else if (lower.includes('gpa') || lower.includes('grade') || lower.includes('target')) {
        responseText = `Your current CGPA is **3.86 / 4.0**. You need **26 more credits** to graduate.\n\n` +
          `💡 **AI Target Recommendation:** Achieving 'A' grades in CS601 (Deep Learning) & CS603 (NLP) will elevate your graduation CGPA to **3.89**!`;
        suggestedActions = [
          { label: '📊 Open Academic Audit', action: 'tab_academic' }
        ];
      } else if (lower.includes('fee') || lower.includes('financial') || lower.includes('scholarship') || lower.includes('dues')) {
        responseText = `Financial Summary for **${student.name}**:\n\n` +
          `- **Current Dues:** $0.00 (Clear)\n` +
          `- **Active Scholarships:** HCL AI & Innovation Award ($5,000) + Dean's Honor Grant ($2,500)\n` +
          `- **Next Semester Estimate:** Fully covered by research assistantship grant.`;
        suggestedActions = [
          { label: '💳 View Fee Receipt & Portal', action: 'tab_financial' }
        ];
      } else if (lower.includes('hostel') || lower.includes('ac') || lower.includes('room') || lower.includes('maintenance')) {
        responseText = `You are registered in **${student.hostelRoom}**. If you need room repairs or AC filter cleaning, I can open an automatic ticket for the Facilities team!`;
        suggestedActions = [
          { label: '🔧 Open Hostel Service Request', action: 'create_hostel_ticket' }
        ];
      } else if (lower.includes('advisor') || lower.includes('meeting') || lower.includes('sarah')) {
        responseText = `Your assigned academic advisor is **${student.advisorName}** (${student.advisorEmail}). Dr. Jenkins has available appointment slots on **October 8th**.`;
        suggestedActions = [
          { label: '📅 Book 1-on-1 Consultation', action: 'tab_advisors' }
        ];
      } else {
        responseText = `I processed your inquiry regarding **"${messageText}"** against the University Academic & Registrar knowledge base.\n\n` +
          `If you require human administrative staff escalation, I can immediately format and file an official ticket for you with full AI context attached!`;
        suggestedActions = [
          { label: '🎟️ Submit Support Ticket', action: 'escalate_ticket' },
          { label: '📜 View Official Transcripts', action: 'transcript' }
        ];
      }

      const aiMsg: ChatMessage = {
        id: `msg-${Date.now()}`,
        sender: 'ai',
        text: responseText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        suggestedActions
      };

      setMessages(prev => [...prev, aiMsg]);
      setIsTyping(false);
    }, 800);
  };

  const handleActionClick = (action: string, text?: string) => {
    if (action === 'transcript') {
      onOpenDocumentModal('transcript');
    } else if (action === 'bonafide') {
      onOpenDocumentModal('bonafide');
    } else if (action === 'escalate_ticket' || action === 'create_hostel_ticket') {
      setEscalateTicketTitle(text || 'Administrative Support Inquiry');
      setShowEscalateModal(true);
    } else if (action === 'tab_academic') {
      // handled externally
    }
  };

  const submitEscalatedTicket = (e: React.FormEvent) => {
    e.preventDefault();
    onCreateTicket(
      escalateTicketTitle,
      'Other',
      'Registrar',
      `Auto-escalated from AI Chat Copilot conversation. Student ID: ${student.id}`
    );
    setShowEscalateModal(false);
    
    setMessages(prev => [
      ...prev,
      {
        id: `msg-${Date.now()}`,
        sender: 'ai',
        text: `✅ **Ticket Created Successfully!** Ticket title: "${escalateTicketTitle}". Dispatched to Registrar & Student Services team. You can track real-time progress in the **Support Tickets** tab.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col glass-panel rounded-2xl border border-slate-800 overflow-hidden relative">
      
      {/* Copilot Header */}
      <div className="px-6 py-4 border-b border-slate-800/80 bg-slate-950/80 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-400 p-0.5 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Bot className="w-5 h-5 text-cyan-400 animate-pulse" />
            </div>
          </div>
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              UniAssist AI Copilot
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                v3.8 RAG Engine
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">Contextual RAG model connected to University Registrar & Bursar database</p>
          </div>
        </div>

        {/* Voice Visualizer Indicator */}
        <div className="flex items-center gap-2">
          {isVoiceActive && (
            <div className="flex items-center gap-1 bg-cyan-950/60 border border-cyan-500/40 px-3 py-1 rounded-full">
              <span className="text-cyan-300 text-xs font-semibold animate-pulse">Listening...</span>
              <div className="flex items-end gap-0.5 h-4 px-1">
                <span className="w-1 bg-cyan-400 rounded-full wave-bar"></span>
                <span className="w-1 bg-indigo-400 rounded-full wave-bar"></span>
                <span className="w-1 bg-purple-400 rounded-full wave-bar"></span>
                <span className="w-1 bg-cyan-400 rounded-full wave-bar"></span>
              </div>
            </div>
          )}

          <button
            onClick={toggleVoice}
            className={`p-2 rounded-xl border transition-all ${
              isVoiceActive 
                ? 'bg-cyan-500/30 border-cyan-400 text-cyan-200 shadow-lg shadow-cyan-500/30' 
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
            }`}
            title="Toggle Voice Input"
          >
            {isVoiceActive ? <Mic className="w-4 h-4 text-cyan-300" /> : <MicOff className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-950/40 radiant-bg">
        {messages.map((msg) => (
          <div 
            key={msg.id}
            className={`flex gap-3 max-w-3xl ${msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
          >
            {/* Avatar */}
            <div className={`w-8 h-8 rounded-xl shrink-0 flex items-center justify-center shadow-md ${
              msg.sender === 'user' 
                ? 'bg-gradient-to-tr from-purple-600 to-indigo-600 text-white' 
                : 'bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white'
            }`}>
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            {/* Content Bubble */}
            <div className={`space-y-2 text-xs leading-relaxed ${
              msg.sender === 'user'
                ? 'bg-indigo-600 text-white p-4 rounded-2xl rounded-tr-none shadow-lg shadow-indigo-600/20 border border-indigo-400/30'
                : 'glass-card bg-slate-900/90 text-slate-200 p-4 rounded-2xl rounded-tl-none border border-slate-800'
            }`}>
              {/* Message text with basic Markdown styling support */}
              <div className="whitespace-pre-wrap font-sans">
                {msg.text.split('\n').map((line, idx) => {
                  // bold replacement
                  const parts = line.split(/(\*\*.*?\*\*)/g);
                  return (
                    <p key={idx} className={idx > 0 ? 'mt-1.5' : ''}>
                      {parts.map((part, pIdx) => {
                        if (part.startsWith('**') && part.endsWith('**')) {
                          return <strong key={pIdx} className="font-bold text-white">{part.slice(2, -2)}</strong>;
                        }
                        return part;
                      })}
                    </p>
                  );
                })}
              </div>

              {/* Action Buttons attached to message */}
              {msg.suggestedActions && msg.suggestedActions.length > 0 && (
                <div className="pt-3 flex flex-wrap gap-2 border-t border-slate-800/80 mt-3">
                  {msg.suggestedActions.map((act, i) => (
                    <button
                      key={i}
                      onClick={() => handleActionClick(act.action, msg.text)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/30 hover:border-indigo-400 hover:text-white transition-all font-semibold"
                    >
                      <span>{act.label}</span>
                      <ArrowRight className="w-3 h-3 text-indigo-400" />
                    </button>
                  ))}
                </div>
              )}

              <span className={`text-[10px] block mt-1 ${msg.sender === 'user' ? 'text-indigo-200 text-right' : 'text-slate-500'}`}>
                {msg.timestamp}
              </span>
            </div>
          </div>
        ))}

        {/* AI Typing Indicator */}
        {isTyping && (
          <div className="flex gap-3 max-w-xl">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center text-white shrink-0">
              <Bot className="w-4 h-4 animate-spin-slow" />
            </div>
            <div className="glass-card bg-slate-900/90 text-slate-300 px-4 py-3 rounded-2xl rounded-tl-none border border-slate-800 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400 animate-spin" />
              <span className="text-xs text-slate-400 font-medium">UniAssist AI is querying university registrar database...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts Bar */}
      <div className="px-6 py-2.5 bg-slate-950/90 border-t border-slate-800/80 overflow-x-auto flex items-center gap-2 no-scrollbar">
        <span className="text-[10px] uppercase font-bold text-slate-500 shrink-0 flex items-center gap-1">
          <Zap className="w-3 h-3 text-amber-400" /> Quick Ask:
        </span>
        {quickPrompts.map((qp, idx) => (
          <button
            key={idx}
            onClick={() => handleSendText(qp.text)}
            className="shrink-0 text-[11px] px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800 text-slate-300 hover:bg-indigo-950/60 hover:border-indigo-500/40 hover:text-indigo-200 transition-all flex items-center gap-1.5"
          >
            <qp.icon className="w-3 h-3 text-indigo-400" />
            <span>{qp.text}</span>
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <div className="p-4 bg-slate-950 border-t border-slate-800">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSendText(); }}
          className="flex items-center gap-2"
        >
          <div className="relative flex-1 flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask UniAssist AI anything about courses, transcripts, fees, or hostel..."
              className="w-full pl-4 pr-10 py-3 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
            />
            <button
              type="button"
              onClick={() => onOpenDocumentModal('transcript')}
              title="Attach Document Context"
              className="absolute right-3 text-slate-500 hover:text-indigo-400 transition-colors"
            >
              <Paperclip className="w-4 h-4" />
            </button>
          </div>

          <button
            type="submit"
            disabled={!input.trim()}
            className="px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition-all shrink-0"
          >
            <span>Send</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>

      {/* Escalate Support Ticket Modal */}
      {showEscalateModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-400" />
                Escalate Inquiry to Administrative Staff
              </h3>
              <button onClick={() => setShowEscalateModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>
            <p className="text-xs text-slate-400">
              UniAssist AI will automatically bundle your current session context, student ID (**{student.id}**), and submit an official support ticket.
            </p>
            <form onSubmit={submitEscalatedTicket} className="space-y-3">
              <div>
                <label className="text-[11px] text-slate-300 font-semibold block mb-1">Ticket Subject</label>
                <input
                  type="text"
                  value={escalateTicketTitle}
                  onChange={(e) => setEscalateTicketTitle(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:border-indigo-500 outline-none"
                  required
                />
              </div>
              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowEscalateModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-bold hover:bg-indigo-500 shadow-md shadow-indigo-600/30"
                >
                  Confirm & Submit Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
