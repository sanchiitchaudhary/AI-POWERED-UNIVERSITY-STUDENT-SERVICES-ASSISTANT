export interface StudentProfile {
  id: string;
  name: string;
  email: string;
  avatar: string;
  major: string;
  department: string;
  year: string;
  semester: number;
  gpa: number;
  creditsEarned: number;
  totalRequiredCredits: number;
  financialStatus: 'Clear' | 'Pending' | 'Overdue';
  balanceDue: number;
  advisorName: string;
  advisorEmail: string;
  hostelRoom: string;
  mealBalance: number;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai' | 'system';
  text: string;
  timestamp: string;
  suggestedActions?: { label: string; action: string }[];
  category?: 'Academic' | 'Financial' | 'Administrative' | 'Housing' | 'General';
  relatedTicketId?: string;
}

export interface Ticket {
  id: string;
  title: string;
  category: 'Transcript' | 'Fee Dispute' | 'Hostel Maintenance' | 'Grade Appeal' | 'Course Drop/Add' | 'Bonafide Certificate' | 'Other';
  department: 'Registrar' | 'Finance' | 'Housing' | 'Academic Affairs' | 'IT Support';
  priority: 'Low' | 'Medium' | 'High' | 'Urgent';
  status: 'Open' | 'In Review' | 'Pending Info' | 'Resolved';
  dateCreated: string;
  lastUpdated: string;
  description: string;
  aiSummary?: string;
  updates: {
    author: string;
    role: 'Student' | 'Staff' | 'AI Assistant';
    timestamp: string;
    message: string;
  }[];
}

export interface Course {
  code: string;
  title: string;
  credits: number;
  grade?: string;
  semester: string;
  type: 'Core' | 'Elective' | 'Lab' | 'Project';
  status: 'Completed' | 'Enrolled' | 'Recommended' | 'Prerequisite Required';
  professor: string;
}

export interface Scholarship {
  id: string;
  name: string;
  amount: number;
  status: 'Awarded' | 'Under Review' | 'Eligible' | 'Not Eligible';
  deadline: string;
  description: string;
  provider: string;
}

export interface AdvisorSlot {
  id: string;
  advisorName: string;
  role: string;
  department: string;
  date: string;
  time: string;
  isBooked: boolean;
  meetingLink?: string;
}

export interface CampusEvent {
  id: string;
  title: string;
  date: string;
  location: string;
  category: 'Hackathon' | 'Workshop' | 'Academic' | 'Cultural' | 'Sports';
  organizer: string;
}
