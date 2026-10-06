import React, { useState } from 'react';
import { 
  BookOpenCheck, 
  Sparkles, 
  CheckCircle2, 
  GraduationCap, 
  Calculator, 
  Layers, 
  Award, 
  ArrowRight,
  Info
} from 'lucide-react';
import { Course, StudentProfile } from '../types';

interface AcademicAuditProps {
  student: StudentProfile;
  courses: Course[];
}

export const AcademicAudit: React.FC<AcademicAuditProps> = ({ student, courses }) => {
  const [targetGPA, setTargetGPA] = useState<number>(3.90);
  const [targetSemesterCredits, setTargetSemesterCredits] = useState<number>(14);

  const completedCourses = courses.filter(c => c.status === 'Completed');
  const enrolledCourses = courses.filter(c => c.status === 'Enrolled');
  const recommendedCourses = courses.filter(c => c.status === 'Recommended' || c.status === 'Prerequisite Required');

  // GPA Calculator Math
  const totalEarnedQualityPoints = completedCourses.reduce((acc, c) => {
    let pts = 4.0;
    if (c.grade === 'A') pts = 4.0;
    else if (c.grade === 'A-') pts = 3.7;
    else if (c.grade === 'B+') pts = 3.3;
    else if (c.grade === 'B') pts = 3.0;
    return acc + (pts * c.credits);
  }, 0);

  const completedCreditsTotal = completedCourses.reduce((acc, c) => acc + c.credits, 0);

  // Calculate required GPA for remaining target credits
  const calculateRequiredSemesterGPA = () => {
    const totalTargetCredits = completedCreditsTotal + targetSemesterCredits;
    const requiredTotalQualityPoints = targetGPA * totalTargetCredits;
    const neededPoints = requiredTotalQualityPoints - totalEarnedQualityPoints;
    const reqGPA = neededPoints / targetSemesterCredits;
    return Math.min(Math.max(reqGPA, 0), 4.0).toFixed(2);
  };

  return (
    <div className="space-y-6 pb-8">
      
      {/* Header */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BookOpenCheck className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-white">Degree Progress & Academic Audit</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Major: <strong className="text-slate-200">{student.major}</strong> • Catalog Year: 2023-2026
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-xl bg-indigo-950/60 border border-indigo-500/30 text-right">
            <span className="text-[10px] text-slate-400 block uppercase font-bold">Current CGPA</span>
            <span className="text-lg font-black text-indigo-300 font-mono">{student.gpa} / 4.0</span>
          </div>
          <div className="px-4 py-2 rounded-xl bg-purple-950/60 border border-purple-500/30 text-right">
            <span className="text-[10px] text-slate-400 block uppercase font-bold">Credits Completed</span>
            <span className="text-lg font-black text-purple-300 font-mono">{student.creditsEarned} / {student.totalRequiredCredits}</span>
          </div>
        </div>
      </div>

      {/* Interactive GPA Calculator Widget */}
      <div className="glass-card rounded-2xl p-6 border border-indigo-500/30 bg-gradient-to-r from-slate-950 via-indigo-950/40 to-slate-950">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Calculator className="w-4 h-4 text-cyan-400" />
            AI Target GPA Projection Simulator
          </h3>
          <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-mono">
            Interactive Calculator
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
          <div className="space-y-3">
            <label className="text-xs text-slate-300 font-semibold block">
              Desired Graduation CGPA: <strong className="text-cyan-400 font-mono text-sm">{targetGPA.toFixed(2)}</strong>
            </label>
            <input 
              type="range" 
              min="3.0" 
              max="4.0" 
              step="0.01" 
              value={targetGPA} 
              onChange={(e) => setTargetGPA(parseFloat(e.target.value))}
              className="w-full accent-cyan-400 cursor-pointer"
            />
            <p className="text-[10px] text-slate-400">Drag slider to test target GPA scenarios for graduation honors.</p>
          </div>

          <div className="space-y-3">
            <label className="text-xs text-slate-300 font-semibold block">
              Enrolled Semester Credits: <strong className="text-purple-400 font-mono text-sm">{targetSemesterCredits} Credits</strong>
            </label>
            <input 
              type="range" 
              min="12" 
              max="20" 
              step="1" 
              value={targetSemesterCredits} 
              onChange={(e) => setTargetSemesterCredits(parseInt(e.target.value))}
              className="w-full accent-purple-400 cursor-pointer"
            />
            <p className="text-[10px] text-slate-400">Total credits in current Spring 2026 semester.</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-center space-y-1">
            <span className="text-[10px] text-slate-400 uppercase font-bold">Required Term GPA</span>
            <div className="text-2xl font-black text-emerald-400 font-mono">
              {calculateRequiredSemesterGPA()} / 4.0
            </div>
            <p className="text-[11px] text-slate-300">
              {parseFloat(calculateRequiredSemesterGPA()) <= 4.0 ? '✅ Target is mathematically achievable!' : '⚠️ Target exceeds maximum 4.0 scale.'}
            </p>
          </div>
        </div>
      </div>

      {/* Course Enrollment Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Enrolled Courses (Spring 2026) */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-4 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              Currently Enrolled Courses (Spring 2026)
            </span>
            <span className="text-xs text-indigo-400 font-mono">14 Credits</span>
          </h3>

          <div className="space-y-3">
            {enrolledCourses.map((c) => (
              <div key={c.code} className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-indigo-300">{c.code}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">{c.type}</span>
                  </div>
                  <h4 className="text-xs font-bold text-white mt-1">{c.title}</h4>
                  <p className="text-[10px] text-slate-400">Prof. {c.professor} • {c.credits} Credits</p>
                </div>
                <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  Enrolled
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recommended Fall 2026 Registration */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-4 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-400" />
              AI Recommended Courses (Fall 2026)
            </span>
            <span className="text-xs text-slate-400 font-mono">Sem 7 Planner</span>
          </h3>

          <div className="space-y-3">
            {recommendedCourses.map((c) => (
              <div key={c.code} className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-purple-300">{c.code}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">{c.type}</span>
                  </div>
                  <h4 className="text-xs font-bold text-white mt-1">{c.title}</h4>
                  <p className="text-[10px] text-slate-400">Prof. {c.professor} • {c.credits} Credits</p>
                </div>
                <button 
                  onClick={() => alert(`Saved ${c.code} to your course cart!`)}
                  className="text-[11px] font-bold px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-all"
                >
                  Add to Cart
                </button>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};
