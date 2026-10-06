import React, { useState } from 'react';
import { 
  Wallet, 
  Award, 
  CheckCircle2, 
  Sparkles, 
  CreditCard, 
  FileText, 
  ShieldCheck, 
  Download,
  AlertCircle
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { StudentProfile, Scholarship } from '../types';

interface FinancialAidProps {
  student: StudentProfile;
  scholarships: Scholarship[];
}

export const FinancialAid: React.FC<FinancialAidProps> = ({ student, scholarships }) => {
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  const feeBreakdown = [
    { title: 'Tuition Fee (Sem 6)', amount: 4500, status: 'Paid by Scholarship' },
    { title: 'Laboratory & AI Compute Fee', amount: 800, status: 'Paid by Scholarship' },
    { title: 'Hostel Block B Rent & Utilities', amount: 1200, status: 'Paid by Student' },
    { title: 'Student Health & Activity Fee', amount: 300, status: 'Paid by Student' },
  ];

  const handleSimulatePayment = () => {
    confetti({ particleCount: 100, spread: 80, origin: { y: 0.6 } });
    setPaymentSuccess(true);
  };

  return (
    <div className="space-y-6 pb-8">
      
      {/* Header */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Wallet className="w-5 h-5 text-emerald-400" />
            <h2 className="text-lg font-bold text-white">Financial Aid, Fees & Scholarships</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Bursar ledger for Student ID: <strong className="text-indigo-300 font-mono">{student.id}</strong>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-xl bg-emerald-950/60 border border-emerald-500/30 text-right">
            <span className="text-[10px] text-slate-400 block uppercase font-bold">Outstanding Dues</span>
            <span className="text-lg font-black text-emerald-400 font-mono">$0.00 (Clear)</span>
          </div>
        </div>
      </div>

      {/* Active Scholarships Banner */}
      <div className="glass-card rounded-2xl p-6 border border-indigo-500/30 bg-gradient-to-r from-slate-950 via-indigo-950/50 to-purple-950/40">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Award className="w-4 h-4 text-cyan-400" />
            Active Scholarship & Merit Grants
          </h3>
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
            Total Awarded: $7,500
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {scholarships.map((sch) => (
            <div key={sch.id} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">{sch.id}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  sch.status === 'Awarded' 
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' 
                    : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                }`}>
                  {sch.status}
                </span>
              </div>
              <h4 className="text-xs font-bold text-white">{sch.name}</h4>
              <p className="text-[11px] font-mono font-bold text-emerald-400">${sch.amount.toLocaleString()} / Academic Year</p>
              <p className="text-[10px] text-slate-400 leading-snug">{sch.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Fee Breakdown & Payment Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Tuition Ledger */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <FileText className="w-4 h-4 text-purple-400" />
            Semester Fee Ledger (Spring 2026)
          </h3>

          <div className="divide-y divide-slate-800">
            {feeBreakdown.map((item, idx) => (
              <div key={idx} className="py-3 flex items-center justify-between text-xs">
                <div>
                  <p className="font-semibold text-slate-200">{item.title}</p>
                  <span className="text-[10px] text-slate-400">{item.status}</span>
                </div>
                <span className="font-mono font-bold text-slate-100">${item.amount.toLocaleString()}</span>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between font-bold text-sm">
            <span className="text-slate-300">Total Net Amount:</span>
            <span className="text-emerald-400 font-mono">$0.00</span>
          </div>
        </div>

        {/* Instant Fee Receipt Simulator */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-indigo-400" />
              Instant Official Fee Receipt
            </h3>

            <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Receipt Ref:</span>
                <span className="font-mono font-bold text-indigo-300">RCPT-2026-90412</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Payment Method:</span>
                <span className="font-semibold">HCL Merit Direct Disbursal</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Verification Status:</span>
                <span className="text-emerald-400 font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Fully Cleared
                </span>
              </div>
            </div>
          </div>

          <div className="mt-6">
            <button
              onClick={handleSimulatePayment}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20 transition-all"
            >
              <Download className="w-4 h-4" />
              <span>{paymentSuccess ? '✓ Receipt Downloaded' : 'Download Verified Fee Receipt'}</span>
            </button>
          </div>
        </div>

      </div>

    </div>
  );
};
