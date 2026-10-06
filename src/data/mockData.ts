import { StudentProfile, Ticket, Course, Scholarship, AdvisorSlot, CampusEvent } from '../types';

export const initialStudentProfile: StudentProfile = {
  id: 'HCL2026-8891',
  name: 'Alex Mercer',
  email: 'alex.mercer@university.edu',
  avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80',
  major: 'B.Tech Computer Science & AI',
  department: 'School of Computing & Data Science',
  year: '3rd Year (Senior)',
  semester: 6,
  gpa: 3.86,
  creditsEarned: 94,
  totalRequiredCredits: 120,
  financialStatus: 'Clear',
  balanceDue: 0,
  advisorName: 'Dr. Sarah Jenkins',
  advisorEmail: 'sarah.jenkins@university.edu',
  hostelRoom: 'Block B - Room 402',
  mealBalance: 145.50,
};

export const initialCourses: Course[] = [
  // Semester 6 (Current)
  { code: 'CS601', title: 'Deep Learning & Neural Networks', credits: 4, semester: 'Spring 2026', type: 'Core', status: 'Enrolled', professor: 'Dr. Alan Turing' },
  { code: 'CS602', title: 'Cloud Computing & Microservices', credits: 3, semester: 'Spring 2026', type: 'Core', status: 'Enrolled', professor: 'Prof. Werner Vogels' },
  { code: 'CS603', title: 'Natural Language Processing', credits: 4, semester: 'Spring 2026', type: 'Elective', status: 'Enrolled', professor: 'Dr. Fei-Fei Li' },
  { code: 'CS604', title: 'Software Engineering Capstone I', credits: 3, semester: 'Spring 2026', type: 'Project', status: 'Enrolled', professor: 'Dr. Sarah Jenkins' },

  // Completed Courses
  { code: 'CS501', title: 'Artificial Intelligence Principles', credits: 4, grade: 'A', semester: 'Fall 2025', type: 'Core', status: 'Completed', professor: 'Dr. Peter Norvig' },
  { code: 'CS502', title: 'Database Systems & NoSQL', credits: 4, grade: 'A-', semester: 'Fall 2025', type: 'Core', status: 'Completed', professor: 'Prof. Michael Stonebraker' },
  { code: 'CS503', title: 'Computer Networks & Security', credits: 3, grade: 'A', semester: 'Fall 2025', type: 'Core', status: 'Completed', professor: 'Dr. Vint Cerf' },
  { code: 'CS401', title: 'Data Structures & Algorithms', credits: 4, grade: 'A', semester: 'Spring 2025', type: 'Core', status: 'Completed', professor: 'Dr. Donald Knuth' },
  { code: 'CS402', title: 'Operating Systems & Concurrency', credits: 4, grade: 'B+', semester: 'Spring 2025', type: 'Core', status: 'Completed', professor: 'Prof. Linus Torvalds' },

  // Recommended Next Semester (Sem 7)
  { code: 'CS701', title: 'Advanced Generative AI Systems', credits: 4, semester: 'Fall 2026', type: 'Elective', status: 'Recommended', professor: 'Dr. Yann LeCun' },
  { code: 'CS702', title: 'Quantum Computing Fundamentals', credits: 3, semester: 'Fall 2026', type: 'Elective', status: 'Recommended', professor: 'Dr. David Deutsch' },
  { code: 'CS703', title: 'Software Engineering Capstone II', credits: 4, semester: 'Fall 2026', type: 'Project', status: 'Prerequisite Required', professor: 'Dr. Sarah Jenkins' },
];

export const initialTickets: Ticket[] = [
  {
    id: 'TICK-9042',
    title: 'Request for Official Bonafide Certificate for Visa Renewal',
    category: 'Bonafide Certificate',
    department: 'Registrar',
    priority: 'High',
    status: 'In Review',
    dateCreated: '2026-10-04',
    lastUpdated: '2026-10-05',
    description: 'Require official seal bonafide student status letter for international passport & visa compliance.',
    aiSummary: 'Student has zero dues and active enrollment. Approved preliminary document verification.',
    updates: [
      {
        author: 'Alex Mercer',
        role: 'Student',
        timestamp: '2026-10-04 10:15 AM',
        message: 'Submitted request with passport draft copy attached.'
      },
      {
        author: 'UniAssist AI',
        role: 'AI Assistant',
        timestamp: '2026-10-04 10:16 AM',
        message: 'Automated verification check passed. Forwarded to Registrar Officer Mr. Robert Vance for final seal.'
      },
      {
        author: 'Mr. Robert Vance',
        role: 'Staff',
        timestamp: '2026-10-05 02:30 PM',
        message: 'Document generated and queued for digital signature. Available for preview in your Certificates portal.'
      }
    ]
  },
  {
    id: 'TICK-8821',
    title: 'Hostel AC Service & Filter Cleaning',
    category: 'Hostel Maintenance',
    department: 'Housing',
    priority: 'Medium',
    status: 'Resolved',
    dateCreated: '2026-09-28',
    lastUpdated: '2026-09-30',
    description: 'Air conditioner unit in Block B Room 402 requires filter replacement and cooling inspection.',
    aiSummary: 'Dispatched maintenance ticket to Facilities Maintenance Team 4.',
    updates: [
      {
        author: 'Alex Mercer',
        role: 'Student',
        timestamp: '2026-09-28 04:00 PM',
        message: 'Reported cooling malfunction.'
      },
      {
        author: 'Facilities Team',
        role: 'Staff',
        timestamp: '2026-09-30 11:00 AM',
        message: 'Maintenance completed. Replaced air filter and refilled coolant. Closed.'
      }
    ]
  }
];

export const initialScholarships: Scholarship[] = [
  {
    id: 'SCH-2026-01',
    name: 'HCL AI & Innovation Excellence Award',
    amount: 5000,
    status: 'Awarded',
    deadline: '2026-11-15',
    description: 'Merit-based scholarship awarded to top 5% computer science students specializing in AI & Machine Learning.',
    provider: 'HCL Tech Foundation'
  },
  {
    id: 'SCH-2026-02',
    name: "Dean's Honor List Merit Grant",
    amount: 2500,
    status: 'Awarded',
    deadline: '2026-12-01',
    description: 'Automatic grant awarded to students maintaining a CGPA of 3.80 or higher.',
    provider: 'University Academic Senate'
  },
  {
    id: 'SCH-2026-03',
    name: 'Global Student Research Fellowship',
    amount: 7500,
    status: 'Eligible',
    deadline: '2026-10-30',
    description: 'Grant supporting undergraduate students presenting AI research papers at international conferences.',
    provider: 'National Science & Tech Board'
  }
];

export const initialAdvisorSlots: AdvisorSlot[] = [
  {
    id: 'SLOT-101',
    advisorName: 'Dr. Sarah Jenkins',
    role: 'Primary Academic Advisor',
    department: 'Computer Science',
    date: '2026-10-08',
    time: '10:30 AM - 11:00 AM',
    isBooked: false
  },
  {
    id: 'SLOT-102',
    advisorName: 'Dr. Sarah Jenkins',
    role: 'Primary Academic Advisor',
    department: 'Computer Science',
    date: '2026-10-08',
    time: '02:00 PM - 02:30 PM',
    isBooked: false
  },
  {
    id: 'SLOT-103',
    advisorName: 'Prof. Marcus Brody',
    role: 'Career & Internship Counselor',
    department: 'Student Placement Cell',
    date: '2026-10-09',
    time: '11:00 AM - 11:30 AM',
    isBooked: false
  },
  {
    id: 'SLOT-104',
    advisorName: 'Ms. Elena Rostova',
    role: 'Financial Aid & Grant Officer',
    department: 'Bursar & Finance Office',
    date: '2026-10-10',
    time: '03:15 PM - 03:45 PM',
    isBooked: false
  }
];

export const initialCampusEvents: CampusEvent[] = [
  {
    id: 'EVT-01',
    title: 'HCL Hackathon 2026: AI for Smart Campuses',
    date: '2026-10-12 • 09:00 AM',
    location: 'Auditorium Hall A & Virtual',
    category: 'Hackathon',
    organizer: 'HCL Tech & University Innovation Club'
  },
  {
    id: 'EVT-02',
    title: 'LLM Fine-Tuning & Agentic Workflows Workshop',
    date: '2026-10-14 • 03:00 PM',
    location: 'Lab 4, Innovation Building',
    category: 'Workshop',
    organizer: 'Department of Computer Science'
  },
  {
    id: 'EVT-03',
    title: 'Fall Career Fair 2026: Tech & Engineering',
    date: '2026-10-20 • 10:00 AM',
    location: 'Student Union Plaza',
    category: 'Academic',
    organizer: 'Career Services Center'
  }
];

export const AI_KNOWLEDGE_BASE: Record<string, string> = {
  transcript: "You can view and instantly download your official transcript from the **Certificates & Transcripts** tab! Verified transcripts include a secure QR verification hash for employers and grad schools.",
  gpa: "Your current CGPA is **3.86 / 4.0**. To maintain your 3.80+ Dean's Honor status in Semester 6, aim for at least 3 'A' grades in your current 4 enrolled courses.",
  financial: "Your tuition fee status is **Clear (Balance: $0.00)**. You have received the **HCL AI & Innovation Excellence Award ($5,000)** and **Dean's Honor Grant ($2,500)**.",
  bonafide: "Bonafide letters are generated automatically by UniAssist AI. Click on **Certificates & Transcripts** to issue an official letter for visa renewal, passport validation, or bank loan processing.",
  housing: "You are currently assigned to **Hostel Block B, Room 402**. Maintenance requests are processed within 24 hours via the **Housing & Dining** portal.",
  advisor: "Your primary advisor is **Dr. Sarah Jenkins**. You can book a 1-on-1 consultation slot under the **Advisor Booking** tab.",
  capstone: "CS604 Software Engineering Capstone I requires completion of CS401 (Data Structures) and CS501 (AI Principles), both of which you completed with 'A' grades!"
};
