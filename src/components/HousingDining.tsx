import React, { useState } from 'react';
import { 
  Home, 
  Utensils, 
  Wrench, 
  Plus, 
  CheckCircle2, 
  Sparkles, 
  Coffee,
  DollarSign
} from 'lucide-react';
import { StudentProfile } from '../types';

interface HousingDiningProps {
  student: StudentProfile;
  onCreateTicket: (title: string, category: 'Hostel Maintenance', department: 'Housing', description: string) => void;
}

export const HousingDining: React.FC<HousingDiningProps> = ({ student, onCreateTicket }) => {
  const [mealBalance, setMealBalance] = useState(student.mealBalance);
  const [showTopUpSuccess, setShowTopUpSuccess] = useState(false);

  const handleTopUpMealCard = (amount: number) => {
    setMealBalance(prev => prev + amount);
    setShowTopUpSuccess(true);
    setTimeout(() => setShowTopUpSuccess(false), 3000);
  };

  const cafeteriaMenu = [
    { day: 'Today (Lunch)', item: 'Grilled Herb Chicken / Tofu Paneer Bowl', calories: '580 kcal', status: 'Serving Now' },
    { day: 'Today (Dinner)', item: 'Artisanal Pasta & Garlic Focaccia', calories: '640 kcal', status: 'Starts 6:30 PM' },
    { day: 'Tomorrow (Breakfast)', item: 'Organic Avocado Toast & Cold Brew Coffee', calories: '420 kcal', status: 'Starts 7:30 AM' },
  ];

  return (
    <div className="space-y-6 pb-8">
      
      {/* Header */}
      <div className="rounded-2xl border border-white/30 bg-[#12141c] p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <Home className="w-5 h-5 text-slate-200" />
            <h2 className="text-lg font-bold text-white">Campus Housing & Dining Hub</h2>
          </div>
          <p className="text-xs text-slate-300 mt-1">
            Hostel Assignment: <strong className="text-white font-mono">{student.hostelRoom}</strong>
          </p>
        </div>

        <button
          onClick={() => onCreateTicket('Hostel Room Maintenance Request', 'Hostel Maintenance', 'Housing', `Issue reported in ${student.hostelRoom}`)}
          className="px-4 py-2.5 rounded-xl bg-white/5 border border-white/20 hover:border-white/40 text-white font-bold text-xs flex items-center gap-2 transition-all"
        >
          <Wrench className="w-4 h-4 text-slate-200" />
          <span>Report Room Issue</span>
        </button>
      </div>

      {/* Two Grid Column: Hostel Card & Dining Meal Card */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Hostel Details */}
        <div className="rounded-2xl border border-white/30 bg-[#12141c] p-6 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Home className="w-4 h-4 text-slate-200" />
              Room & Facility Status
            </h3>
            <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full border border-white/15 bg-white/5 text-slate-200">
              Occupied
            </span>
          </div>

          <div className="p-4 rounded-xl bg-[#181a24] border border-white/15 text-xs space-y-2 text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-400">Assigned Hostel:</span>
              <span className="font-semibold text-white">Block B (Tech Residence)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Room Number:</span>
              <span className="font-mono font-bold text-white">Room 402</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Roommate:</span>
              <span className="font-semibold text-slate-200">Jordan Lee (Senior CS)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Wi-Fi Network:</span>
              <span className="font-mono text-slate-200">Campus-Hostel-5G (Active)</span>
            </div>
          </div>
        </div>

        {/* Meal Card & Dining */}
        <div className="rounded-2xl border border-white/30 bg-[#12141c] p-6 space-y-4 flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Utensils className="w-4 h-4 text-slate-200" />
                Campus Dining Meal Pass Balance
              </h3>
              {showTopUpSuccess && (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-400/20 animate-bounce">
                  +$25 Added!
                </span>
              )}
            </div>

            <div className="mt-3 p-4 rounded-xl bg-[#181a24] border border-white/15 flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-bold block">Digital Meal Balance</span>
                <span className="text-2xl font-black text-white font-mono">${mealBalance.toFixed(2)}</span>
              </div>
              <button
                onClick={() => handleTopUpMealCard(25)}
                className="px-3.5 py-2 rounded-xl bg-white/5 border border-white/20 hover:bg-white/[0.08] text-white text-xs font-bold transition-all"
              >
                + Top Up $25
              </button>
            </div>
          </div>

          <div className="space-y-2 pt-2 border-t border-white/10">
            <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
              <Coffee className="w-3.5 h-3.5 text-slate-200" />
              Cafeteria Daily Menu
            </h4>
            <div className="space-y-2">
              {cafeteriaMenu.map((m, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-[#181a24] border border-white/15 text-xs flex justify-between items-center">
                  <div>
                    <span className="text-[10px] font-semibold text-slate-400 block">{m.day}</span>
                    <span className="font-bold text-slate-200">{m.item}</span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-200">{m.status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
