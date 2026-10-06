import React, { useState } from 'react';
import { 
  CalendarDays, 
  UserCheck, 
  CheckCircle2, 
  Clock, 
  Sparkles, 
  Video, 
  Mail, 
  Building
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { AdvisorSlot, StudentProfile } from '../types';

interface AdvisorBookingProps {
  student: StudentProfile;
  slots: AdvisorSlot[];
  onBookSlot: (slotId: string) => void;
}

export const AdvisorBooking: React.FC<AdvisorBookingProps> = ({ student, slots, onBookSlot }) => {
  const [bookedSuccessSlot, setBookedSuccessSlot] = useState<string | null>(null);

  const handleBooking = (slotId: string) => {
    confetti({ particleCount: 70, spread: 60, origin: { y: 0.6 } });
    onBookSlot(slotId);
    setBookedSuccessSlot(slotId);
  };

  return (
    <div className="space-y-6 pb-8">
      
      {/* Header */}
      <div className="rounded-2xl border border-white/30 bg-[#12141c] p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <CalendarDays className="w-5 h-5 text-slate-200" />
            <h2 className="text-lg font-bold text-white">1-on-1 Academic & Career Advisor Booking</h2>
          </div>
          <p className="text-xs text-slate-300 mt-1">
            Primary Academic Advisor: <strong className="text-white">{student.advisorName}</strong> ({student.advisorEmail})
          </p>
        </div>
      </div>

      {/* Slots List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {slots.map((slot) => (
          <div key={slot.id} className="rounded-2xl border border-white/30 bg-[#12141c] p-5 space-y-3 flex flex-col justify-between shadow-sm">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-200 px-2.5 py-0.5 rounded bg-white/5 border border-white/15">
                  {slot.department}
                </span>
                <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                  slot.isBooked 
                    ? 'bg-white/5 text-slate-300 border border-white/15' 
                    : 'bg-emerald-500/10 text-emerald-300 border border-emerald-400/20'
                }`}>
                  {slot.isBooked ? 'Booked' : 'Available'}
                </span>
              </div>

              <h4 className="text-sm font-bold text-white mt-3">{slot.advisorName}</h4>
              <p className="text-xs text-slate-300">{slot.role}</p>

              <div className="mt-3 p-3 rounded-xl bg-[#181a24] border border-white/15 text-xs space-y-1 text-slate-300">
                <div className="flex justify-between">
                  <span className="text-slate-400">Date:</span>
                  <span className="font-semibold text-white">{slot.date}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Time Slot:</span>
                  <span className="font-mono text-slate-200">{slot.time}</span>
                </div>
              </div>
            </div>

            <div className="pt-3">
              {slot.isBooked ? (
                <div className="w-full py-2.5 rounded-xl bg-white/5 border border-white/15 text-slate-300 text-xs font-bold text-center flex items-center justify-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-300" />
                  <span>Consultation Confirmed</span>
                </div>
              ) : (
                <button
                  onClick={() => handleBooking(slot.id)}
                  className="w-full py-2.5 rounded-xl bg-white/5 border border-white/20 hover:bg-white/[0.08] text-white font-bold text-xs flex items-center justify-center gap-2 transition-all"
                >
                  <Video className="w-4 h-4 text-slate-200" />
                  <span>Confirm Slot Appointment</span>
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

    </div>
  );
};
