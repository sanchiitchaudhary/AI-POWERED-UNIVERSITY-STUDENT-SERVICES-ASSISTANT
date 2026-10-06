import React, { useState } from 'react';
import { 
  ShieldAlert, 
  PhoneCall, 
  HeartPulse, 
  AlertTriangle, 
  MapPin, 
  CheckCircle2, 
  Clock 
} from 'lucide-react';

export const CampusSecurity: React.FC = () => {
  const [sosActivated, setSosActivated] = useState(false);

  const handleSos = () => {
    setSosActivated(true);
    setTimeout(() => {
      alert("🚨 CAMPUS EMERGENCY SOS SIGNAL DISPATCHED!\nCampus Security Officers & Medical Response team notified for Block B Room 402.");
    }, 500);
  };

  return (
    <div className="space-y-6 pb-8">
      
      {/* Header */}
      <div className="rounded-2xl border border-white/30 bg-[#12141c] p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-slate-200" />
            <h2 className="text-lg font-bold text-white">Emergency Safety & Student Welfare Hub</h2>
          </div>
          <p className="text-xs text-slate-300 mt-1">
            24/7 Campus Security Control Room Direct Hotline & Health Services
          </p>
        </div>

        {/* SOS Emergency Button */}
        <button
          onClick={handleSos}
          className={`px-6 py-3 rounded-2xl font-black text-xs uppercase tracking-wider flex items-center gap-2 transition-all ${
            sosActivated 
              ? 'bg-rose-500/20 text-rose-200 border border-rose-400/25 animate-pulse' 
              : 'bg-white/5 border border-white/20 hover:border-white/40 text-white'
          }`}
        >
          <AlertTriangle className="w-4 h-4 text-slate-200" />
          <span>{sosActivated ? '🚨 SOS Alert Sent!' : 'Press 1-Tap SOS Alert'}</span>
        </button>
      </div>

      {/* Emergency Phone Contacts */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-white/30 bg-[#12141c] p-5 space-y-2 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-300">Campus Police</span>
            <PhoneCall className="w-4 h-4 text-slate-200" />
          </div>
          <p className="text-lg font-black text-white font-mono">+1 (800) 555-SAFE</p>
          <p className="text-[10px] text-slate-400">Control Room • Response time &lt; 3 mins</p>
        </div>

        <div className="rounded-2xl border border-white/30 bg-[#12141c] p-5 space-y-2 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-300">Medical Health Center</span>
            <HeartPulse className="w-4 h-4 text-slate-200" />
          </div>
          <p className="text-lg font-black text-white font-mono">+1 (800) 555-CARE</p>
          <p className="text-[10px] text-slate-400">Block C Ambulance & Urgent Care</p>
        </div>

        <div className="rounded-2xl border border-white/30 bg-[#12141c] p-5 space-y-2 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-300">Mental Health Counselor</span>
            <HeartPulse className="w-4 h-4 text-slate-200" />
          </div>
          <p className="text-lg font-black text-white font-mono">+1 (800) 555-HEAL</p>
          <p className="text-[10px] text-slate-400">Confidential 24/7 Helpline</p>
        </div>
      </div>

    </div>
  );
};
