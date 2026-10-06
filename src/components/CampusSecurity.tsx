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
      <div className="glass-card rounded-2xl p-6 border border-rose-500/30 bg-gradient-to-r from-slate-950 via-rose-950/30 to-slate-950 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            <h2 className="text-lg font-bold text-white">Emergency Safety & Student Welfare Hub</h2>
          </div>
          <p className="text-xs text-slate-300 mt-1">
            24/7 Campus Security Control Room Direct Hotline & Health Services
          </p>
        </div>

        {/* SOS Emergency Button */}
        <button
          onClick={handleSos}
          className={`px-6 py-3 rounded-2xl font-black text-xs uppercase tracking-wider flex items-center gap-2 transition-all shadow-xl ${
            sosActivated 
              ? 'bg-rose-600 text-white animate-pulse shadow-rose-600/50' 
              : 'bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white shadow-rose-600/30'
          }`}
        >
          <AlertTriangle className="w-4 h-4 text-amber-200" />
          <span>{sosActivated ? '🚨 SOS Alert Sent!' : 'Press 1-Tap SOS Alert'}</span>
        </button>
      </div>

      {/* Emergency Phone Contacts */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400">Campus Police</span>
            <PhoneCall className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-lg font-black text-white font-mono">+1 (800) 555-SAFE</p>
          <p className="text-[10px] text-slate-400">Control Room • Response time &lt; 3 mins</p>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400">Medical Health Center</span>
            <HeartPulse className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-lg font-black text-white font-mono">+1 (800) 555-CARE</p>
          <p className="text-[10px] text-slate-400">Block C Ambulance & Urgent Care</p>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400">Mental Health Counselor</span>
            <HeartPulse className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-lg font-black text-white font-mono">+1 (800) 555-HEAL</p>
          <p className="text-[10px] text-slate-400">Confidential 24/7 Helpline</p>
        </div>
      </div>

    </div>
  );
};
