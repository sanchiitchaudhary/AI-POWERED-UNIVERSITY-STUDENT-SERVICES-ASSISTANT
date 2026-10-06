import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { DashboardOverview } from './components/DashboardOverview';
import { AIChatCopilot } from './components/AIChatCopilot';
import { AcademicAudit } from './components/AcademicAudit';
import { TranscriptsCertificates } from './components/TranscriptsCertificates';
import { FinancialAid } from './components/FinancialAid';
import { TicketingSystem } from './components/TicketingSystem';
import { HousingDining } from './components/HousingDining';
import { AdvisorBooking } from './components/AdvisorBooking';
import { CampusSecurity } from './components/CampusSecurity';
import { DocumentVerification } from './components/DocumentVerification';
import { DocumentModal } from './components/DocumentModal';

import { 
  initialStudentProfile, 
  initialCourses, 
  initialTickets, 
  initialScholarships, 
  initialAdvisorSlots, 
  initialCampusEvents 
} from './data/mockData';
import { Ticket } from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [student, setStudent] = useState(initialStudentProfile);
  const [courses, setCourses] = useState(initialCourses);
  const [tickets, setTickets] = useState<Ticket[]>(initialTickets);
  const [scholarships, setScholarships] = useState(initialScholarships);
  const [slots, setSlots] = useState(initialAdvisorSlots);
  const [events, setEvents] = useState(initialCampusEvents);
  
  // Voice Assistant modal trigger state
  const [isVoiceActive, setIsVoiceActive] = useState(false);

  // Document modal ('transcript' | 'bonafide' | null)
  const [documentType, setDocumentType] = useState<'transcript' | 'bonafide' | null>(null);

  // Create new ticket handler
  const handleCreateTicket = (
    title: string,
    category: Ticket['category'],
    department: Ticket['department'],
    description: string
  ) => {
    const newTicket: Ticket = {
      id: `TICK-${Math.floor(1000 + Math.random() * 9000)}`,
      title,
      category,
      department,
      priority: 'High',
      status: 'In Review',
      dateCreated: new Date().toISOString().split('T')[0],
      lastUpdated: 'Just now',
      description,
      aiSummary: 'Autonomous ticket creation & Registrar verification pipeline initiated.',
      updates: [
        {
          author: student.name,
          role: 'Student',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          message: description
        },
        {
          author: 'UniAssist AI',
          role: 'AI Assistant',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          message: `Ticket dispatched to ${department} Department. Expected SLA: 4 hours.`
        }
      ]
    };

    setTickets(prev => [newTicket, ...prev]);
  };

  // Add message to ticket thread
  const handleAddMessageToTicket = (ticketId: string, message: string) => {
    setTickets(prev => prev.map(t => {
      if (t.id === ticketId) {
        return {
          ...t,
          lastUpdated: 'Just now',
          updates: [
            ...t.updates,
            {
              author: student.name,
              role: 'Student',
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              message
            }
          ]
        };
      }
      return t;
    }));
  };

  // Book Advisor Slot
  const handleBookSlot = (slotId: string) => {
    setSlots(prev => prev.map(s => s.id === slotId ? { ...s, isBooked: true } : s));
  };

  const openTicketCount = tickets.filter(t => t.status !== 'Resolved').length;

  return (
    <div className="min-h-screen bg-[#12141c] text-slate-900 flex flex-col font-sans selection:bg-slate-900 selection:text-white">
      
      {/* Top Navigation Bar */}
      <Navbar 
        student={student}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenDocumentModal={(type) => setDocumentType(type)}
        onVoiceTrigger={() => {
          setActiveTab('copilot');
          setIsVoiceActive(!isVoiceActive);
        }}
      />

      {/* Body Area */}
      <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 flex flex-col lg:flex-row gap-6">
        
        {/* Left Navigation Sidebar */}
        <Sidebar 
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          openTicketCount={openTicketCount}
        />

        {/* Main Content Pane */}
        <main className="flex-1 min-w-0">
          {activeTab === 'dashboard' && (
            <DashboardOverview 
              student={student}
              tickets={tickets}
              events={events}
              setActiveTab={setActiveTab}
              onOpenDocumentModal={(type) => setDocumentType(type)}
            />
          )}

          {activeTab === 'copilot' && (
            <AIChatCopilot 
              student={student}
              onOpenDocumentModal={(type) => setDocumentType(type)}
              onCreateTicket={handleCreateTicket}
              isVoiceActive={isVoiceActive}
              setIsVoiceActive={setIsVoiceActive}
            />
          )}

          {activeTab === 'academic' && (
            <AcademicAudit 
              student={student}
              courses={courses}
            />
          )}

          {activeTab === 'certificates' && (
            <TranscriptsCertificates 
              student={student}
              courses={courses}
              onOpenDocumentModal={(type) => setDocumentType(type)}
            />
          )}

          {activeTab === 'verification' && (
            <DocumentVerification />
          )}

          {activeTab === 'financial' && (
            <FinancialAid 
              student={student}
              scholarships={scholarships}
            />
          )}

          {activeTab === 'tickets' && (
            <TicketingSystem 
              student={student}
              tickets={tickets}
              onCreateTicket={handleCreateTicket}
              onAddMessageToTicket={handleAddMessageToTicket}
            />
          )}

          {activeTab === 'housing' && (
            <HousingDining 
              student={student}
              onCreateTicket={(title, category, dept, desc) => handleCreateTicket(title, category, dept, desc)}
            />
          )}

          {activeTab === 'advisors' && (
            <AdvisorBooking 
              student={student}
              slots={slots}
              onBookSlot={handleBookSlot}
            />
          )}

          {activeTab === 'security' && (
            <CampusSecurity />
          )}
        </main>

      </div>

      {/* Printable Document Modal for Transcript & Bonafide */}
      <DocumentModal 
        type={documentType}
        onClose={() => setDocumentType(null)}
        student={student}
        courses={courses}
      />

    </div>
  );
}

export default App;
