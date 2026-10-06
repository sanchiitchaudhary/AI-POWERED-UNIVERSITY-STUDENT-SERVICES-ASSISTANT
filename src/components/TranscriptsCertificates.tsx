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
      <div className="rounded-2xl border border-white/30 bg-[#12141c] p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm transition-colors hover:border-white/40">
        <div>
          <div className="flex items-center gap-2">
            <FileCheck2 className="w-5 h-5 text-slate-200" />
            <h2 className="text-lg font-bold text-white">Official Documents & Verified Seals</h2>
          </div>
          <p className="text-xs text-slate-300 mt-1">
            Instantly issue digitally signed transcripts, bonafide letters, and enrollment verifications.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onOpenDocumentModal('transcript')}
            className="px-4 py-2.5 rounded-xl bg-white/5 border border-white/20 hover:border-white/40 text-white font-bold text-xs flex items-center gap-2 transition-all"
          >
            <FileText className="w-4 h-4 text-slate-200" />
            <span>Generate Official Transcript</span>
          </button>
          <button
            onClick={() => onOpenDocumentModal('bonafide')}
            className="px-4 py-2.5 rounded-xl bg-[#181a24] border border-white/20 hover:border-white/40 text-white font-bold text-xs flex items-center gap-2 transition-all"
          >
            <ShieldCheck className="w-4 h-4 text-slate-200" />
            <span>Issue Bonafide Letter</span>
          </button>
        </div>
      </div>

      {/* Verification Checksum & Cryptographic Hash */}
      <div className="rounded-2xl border border-white/30 bg-[#12141c] p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/[0.04] text-slate-200 border border-white/15 flex items-center justify-center shrink-0">
            <QrCode className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] text-slate-300 font-mono uppercase tracking-wider block">Registrar Cryptographic Hash</span>
            <span className="text-xs font-mono font-bold text-white">{digitalVerificationHash}</span>
          </div>
        </div>

        <button
          onClick={handleCopyHash}
          className="px-3 py-1.5 rounded-lg border border-white/20 bg-[#181a24] hover:bg-white/[0.04] text-xs font-semibold text-slate-200 transition-colors shrink-0"
        >
          {copiedHash ? '✓ Hash Copied!' : 'Copy Hash Verification'}
        </button>
      </div>

      {/* Available Document Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Card 1: Official Transcript */}
        <div className="rounded-2xl border border-white/30 bg-[#12141c] p-6 hover:border-white/45 transition-all flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center justify-between">
              <div className="w-10 h-10 rounded-xl bg-white/[0.04] text-slate-100 border border-white/15 flex items-center justify-center">
                <FileText className="w-5 h-5" />
              </div>
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-400/20">
                Official Digital Seal
              </span>
            </div>

            <h3 className="text-base font-bold text-white mt-4">Official Academic Transcript</h3>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              Complete academic history including semester GPA breakdown, enrolled credits, major declaration, and degree progress. Suitable for WES, grad schools, and employer background checks.
            </p>

            <div className="mt-4 p-3 rounded-xl bg-[#181a24] border border-white/15 text-xs space-y-1.5 text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-400">Student ID:</span>
                <span className="font-mono font-semibold text-white">{student.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Cumulative GPA:</span>
                <span className="font-mono font-semibold text-white">{student.gpa} / 4.0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Completed Credits:</span>
                <span className="font-mono font-semibold text-white">{student.creditsEarned} Credits</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-white/10 flex items-center gap-2">
            <button
              onClick={() => onOpenDocumentModal('transcript')}
              className="flex-1 py-2.5 rounded-xl bg-white/5 hover:bg-white/[0.08] border border-white/20 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all"
            >
              <FileText className="w-4 h-4 text-slate-200" />
              <span>Preview & Print PDF</span>
            </button>
          </div>
        </div>

        {/* Card 2: Bonafide Certificate */}
        <div className="rounded-2xl border border-white/30 bg-[#12141c] p-6 hover:border-white/45 transition-all flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center justify-between">
              <div className="w-10 h-10 rounded-xl bg-white/[0.04] text-slate-100 border border-white/15 flex items-center justify-center">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-200 border border-indigo-400/20">
                Verified Student Letter
              </span>
            </div>

            <h3 className="text-base font-bold text-white mt-4">Bonafide Student Certificate</h3>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              Official university letterhead document certifying full-time enrollment status for passport renewal, student visa applications, housing verification, or educational loan processing.
            </p>

            <div className="mt-4 p-3 rounded-xl bg-[#181a24] border border-white/15 text-xs space-y-1.5 text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-400">Issuer:</span>
                <span className="font-semibold text-white">Office of Registrar & Academic Records</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Validity:</span>
                <span className="font-semibold text-emerald-300">Academic Year 2026</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Verification QR:</span>
                <span className="font-mono font-semibold text-slate-200">Enabled</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-white/10 flex items-center gap-2">
            <button
              onClick={() => onOpenDocumentModal('bonafide')}
              className="flex-1 py-2.5 rounded-xl bg-white/5 hover:bg-white/[0.08] border border-white/20 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all"
            >
              <ShieldCheck className="w-4 h-4 text-slate-200" />
              <span>Preview & Print Bonafide</span>
            </button>
          </div>
        </div>

      </div>

    </div>
  );
};
