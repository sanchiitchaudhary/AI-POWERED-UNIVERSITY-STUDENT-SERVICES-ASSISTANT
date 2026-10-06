import React, { useState } from 'react';
import { 
  FileCheck2, 
  Download, 
  Printer, 
  QrCode, 
  ShieldCheck, 
  FileText, 
  Sparkles, 
  CheckCircle2, 
  ExternalLink,
  Award
} from 'lucide-react';
import { StudentProfile, Course } from '../types';

interface TranscriptsCertificatesProps {
  student: StudentProfile;
  courses: Course[];
  onOpenDocumentModal: (type: 'transcript' | 'bonafide') => void;
}

export const TranscriptsCertificates: React.FC<TranscriptsCertificatesProps> = ({
  student,
  courses,
  onOpenDocumentModal
}) => {
  const [copiedHash, setCopiedHash] = useState(false);
  const digitalVerificationHash = "VERIFIED-HASH-HCL2026-8891-99421A";

  const handleCopyHash = () => {
    navigator.clipboard.writeText(digitalVerificationHash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  return (
    <div className="space-y-6 pb-8">
      
      {/* Header */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <FileCheck2 className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-bold text-white">Official Documents & Verified Seals</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Instantly issue digitally signed transcripts, bonafide letters, and enrollment verifications.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onOpenDocumentModal('transcript')}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition-all"
          >
            <FileText className="w-4 h-4" />
            <span>Generate Official Transcript</span>
          </button>
          <button
            onClick={() => onOpenDocumentModal('bonafide')}
            className="px-4 py-2.5 rounded-xl bg-purple-950/80 border border-purple-500/40 hover:bg-purple-900/80 text-purple-200 font-bold text-xs flex items-center gap-2 transition-all"
          >
            <ShieldCheck className="w-4 h-4 text-purple-400" />
            <span>Issue Bonafide Letter</span>
          </button>
        </div>
      </div>

      {/* Verification Checksum & Cryptographic Hash */}
      <div className="glass-card rounded-2xl p-5 border border-indigo-500/30 bg-slate-950/80 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0">
            <QrCode className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">Registrar Cryptographic Hash</span>
            <span className="text-xs font-mono font-bold text-indigo-300">{digitalVerificationHash}</span>
          </div>
        </div>

        <button
          onClick={handleCopyHash}
          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors shrink-0"
        >
          {copiedHash ? '✓ Hash Copied!' : 'Copy Hash Verification'}
        </button>
      </div>

      {/* Available Document Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Card 1: Official Transcript */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 hover:border-indigo-500/40 transition-all flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                <FileText className="w-5 h-5" />
              </div>
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Official Digital Seal
              </span>
            </div>

            <h3 className="text-base font-bold text-white mt-4">Official Academic Transcript</h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Complete academic history including semester GPA breakdown, enrolled credits, major declaration, and degree progress. Suitable for WES, grad schools, and employer background checks.
            </p>

            <div className="mt-4 p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1.5 text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-400">Student ID:</span>
                <span className="font-mono font-semibold">{student.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Cumulative GPA:</span>
                <span className="font-mono font-semibold text-indigo-300">{student.gpa} / 4.0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Completed Credits:</span>
                <span className="font-mono font-semibold">{student.creditsEarned} Credits</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 flex items-center gap-2">
            <button
              onClick={() => onOpenDocumentModal('transcript')}
              className="flex-1 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-md shadow-indigo-600/30"
            >
              <FileText className="w-4 h-4" />
              <span>Preview & Print PDF</span>
            </button>
          </div>
        </div>

        {/* Card 2: Bonafide Certificate */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 hover:border-purple-500/40 transition-all flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <div className="w-10 h-10 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                Verified Student Letter
              </span>
            </div>

            <h3 className="text-base font-bold text-white mt-4">Bonafide Student Certificate</h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Official university letterhead document certifying full-time enrollment status for passport renewal, student visa applications, housing verification, or educational loan processing.
            </p>

            <div className="mt-4 p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1.5 text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-400">Issuer:</span>
                <span className="font-semibold">Office of Registrar & Academic Records</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Validity:</span>
                <span className="font-semibold text-emerald-400">Academic Year 2026</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Verification QR:</span>
                <span className="font-mono font-semibold text-purple-300">Enabled</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 flex items-center gap-2">
            <button
              onClick={() => onOpenDocumentModal('bonafide')}
              className="flex-1 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-md shadow-purple-600/30"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Preview & Print Bonafide</span>
            </button>
          </div>
        </div>

      </div>

    </div>
  );
};
