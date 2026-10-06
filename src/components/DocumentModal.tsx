import React from 'react';
import { X, Printer, Download, ShieldCheck, QrCode } from 'lucide-react';
import confetti from 'canvas-confetti';
import { StudentProfile, Course } from '../types';

interface DocumentModalProps {
  type: 'transcript' | 'bonafide' | null;
  onClose: () => void;
  student: StudentProfile;
  courses: Course[];
}

export const DocumentModal: React.FC<DocumentModalProps> = ({
  type,
  onClose,
  student,
  courses
}) => {
  if (!type) return null;

  const triggerConfetti = () => {
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 }
    });
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-3xl w-full p-6 sm:p-8 space-y-6 shadow-2xl relative my-8">
        
        {/* Top Control Bar */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 no-print">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="text-sm font-bold text-white">
              {type === 'transcript' ? 'Official Academic Transcript Preview' : 'Bonafide Student Certificate Preview'}
            </h3>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={triggerConfetti}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition-all"
            >
              <Printer className="w-4 h-4" />
              <span>Print / Download PDF</span>
            </button>

            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Printable Document Box */}
        <div id="printable-document" className="bg-white text-slate-900 p-8 sm:p-12 rounded-xl shadow-xl space-y-6 border border-slate-200 text-xs font-serif leading-relaxed">
          
          {/* Document Header */}
          <div className="text-center border-b-2 border-indigo-900 pb-6 space-y-1">
            <h1 className="text-xl sm:text-2xl font-extrabold font-sans uppercase tracking-wider text-indigo-950">
              NATIONAL INSTITUTE OF ADVANCED TECHNOLOGY
            </h1>
            <p className="text-[11px] font-sans text-slate-600 uppercase font-semibold">
              Office of Academic Affairs & Registrar • University Seal of Excellence
            </p>
            <p className="text-[10px] font-mono text-slate-500">
              Campus Central Drive, Academic Block A • Accreditation: Tier-1 NBA & NAAC A++
            </p>
          </div>

          {/* TRANSCRIPT SPECIFIC BODY */}
          {type === 'transcript' && (
            <div className="space-y-6">
              <div className="text-center my-4">
                <h2 className="text-lg font-bold font-sans uppercase tracking-widest text-slate-900 border-b border-slate-300 inline-block pb-1">
                  OFFICIAL ACADEMIC TRANSCRIPT
                </h2>
              </div>

              {/* Student Metadata Table */}
              <div className="grid grid-cols-2 gap-4 bg-slate-50 p-4 rounded border border-slate-200 font-sans text-xs">
                <div>
                  <p><strong>Student Name:</strong> {student.name}</p>
                  <p><strong>Student ID / Roll:</strong> {student.id}</p>
                  <p><strong>Major:</strong> {student.major}</p>
                </div>
                <div>
                  <p><strong>Cumulative GPA:</strong> {student.gpa} / 4.0</p>
                  <p><strong>Credits Completed:</strong> {student.creditsEarned} / {student.totalRequiredCredits}</p>
                  <p><strong>Academic Status:</strong> Good Standing (Dean's List)</p>
                </div>
              </div>

              {/* Course Grade Breakdown Table */}
              <div>
                <h4 className="font-sans font-bold text-xs uppercase mb-2 text-indigo-950">Course History & Grades</h4>
                <table className="w-full border-collapse border border-slate-300 text-left font-sans text-xs">
                  <thead>
                    <tr className="bg-slate-100 border-b border-slate-300">
                      <th className="p-2 border-r border-slate-300">Course Code</th>
                      <th className="p-2 border-r border-slate-300">Course Title</th>
                      <th className="p-2 border-r border-slate-300 text-center">Credits</th>
                      <th className="p-2 border-r border-slate-300 text-center">Semester</th>
                      <th className="p-2 text-center">Grade</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {courses.map((c) => (
                      <tr key={c.code}>
                        <td className="p-2 font-mono font-semibold border-r border-slate-200">{c.code}</td>
                        <td className="p-2 border-r border-slate-200">{c.title}</td>
                        <td className="p-2 text-center border-r border-slate-200">{c.credits}</td>
                        <td className="p-2 text-center border-r border-slate-200">{c.semester}</td>
                        <td className="p-2 text-center font-bold font-mono">{c.grade || 'Enrolled'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* BONAFIDE CERTIFICATE SPECIFIC BODY */}
          {type === 'bonafide' && (
            <div className="space-y-6 py-4">
              <div className="text-center my-4">
                <h2 className="text-lg font-bold font-sans uppercase tracking-widest text-slate-900 border-b border-slate-300 inline-block pb-1">
                  BONAFIDE STUDENT CERTIFICATE
                </h2>
              </div>

              <div className="space-y-4 text-justify font-sans text-xs sm:text-sm leading-relaxed">
                <p>
                  This is to certify that <strong>{student.name}</strong> (Student Roll No: <strong>{student.id}</strong>) is a full-time bonafide student of the National Institute of Advanced Technology, currently enrolled in <strong>Semester {student.semester}</strong> of the <strong>{student.major}</strong> program for the Academic Year 2026.
                </p>

                <p>
                  According to official university records, {student.name} maintains an outstanding academic standing with a Cumulative Grade Point Average (CGPA) of <strong>{student.gpa} / 4.0</strong>, and has completed all fee dues.
                </p>

                <p>
                  This bonafide certificate is issued upon the student's request for official purposes, including <strong>Passport / Student Visa Renewal, Educational Bank Loan Compliance, or Official Internships</strong>.
                </p>
              </div>
            </div>
          )}

          {/* Document Footer with Seal & QR Verification */}
          <div className="pt-8 border-t-2 border-slate-200 flex items-end justify-between font-sans">
            <div className="space-y-2">
              <div className="w-16 h-16 bg-slate-100 border border-slate-300 rounded flex items-center justify-center p-1">
                <QrCode className="w-12 h-12 text-slate-800" />
              </div>
              <p className="text-[9px] text-slate-500 font-mono">
                Scan QR or verify online at:<br />
                verify.university.edu/{student.id}
              </p>
            </div>

            <div className="text-center space-y-1">
              <div className="w-40 h-10 mx-auto border-b border-slate-400 flex items-center justify-center">
                <span className="font-serif italic text-indigo-900 font-bold text-sm">Dr. Arthur Pendelton</span>
              </div>
              <p className="text-[10px] font-bold uppercase text-slate-800">Registrar & Controller of Examinations</p>
              <p className="text-[9px] text-slate-500">Issued Date: {new Date().toLocaleDateString()}</p>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
