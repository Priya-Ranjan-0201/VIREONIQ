import { 
  X, 
  Calendar, 
  Plus, 
  FileText, 
  Trash2,
  ExternalLink,
  MapPin,
  CalendarDays
} from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAddAppEvent } from "../../api/hooks/useCRM";
import { useSyncEvent } from "../../api/hooks/useNotifications";
import { useState } from "react";
import { toast } from "sonner";

interface Props {
  application: any;
  onClose: () => void;
}

export const ApplicationDetail = ({ application, onClose }: Props) => {
  const { mutate: addEvent } = useAddAppEvent();
  const { mutate: syncToCal } = useSyncEvent();
  const [showEventForm, setShowEventForm] = useState(false);
  const [eventType, setEventType] = useState("Interview");
  const [eventDate, setEventDate] = useState("");

  const handleAddEvent = () => {
    if (!eventDate) return toast.error("Please select a date");
    
    addEvent({ 
      appId: application.id, 
      event: { 
        event_type: eventType, 
        event_date: eventDate,
        notes: "" 
      } 
    }, {
      onSuccess: () => {
        toast.success("Event logged!");
        setShowEventForm(false);
      }
    });
  };

  const handleSync = (e: React.MouseEvent, eventId: string) => {
    e.stopPropagation();
    syncToCal(eventId, {
      onSuccess: () => toast.success("Synced to Google Calendar"),
      onError: () => toast.error("Connect Google Calendar in Settings first")
    });
  };

  return (
    <motion.div
      initial={{ x: "100%" }}
      animate={{ x: 0 }}
      exit={{ x: "100%" }}
      className="fixed inset-y-0 right-0 w-full md:w-[500px] bg-slate-950 border-l border-border z-50 shadow-2xl flex flex-col"
    >
      <div className="p-6 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-4">
           <div className="h-10 w-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center font-black text-primary">
             {application.job.company_name[0]}
           </div>
           <div>
             <h2 className="font-bold text-slate-100">{application.job.title}</h2>
             <p className="text-xs text-slate-500">{application.job.company_name}</p>
           </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="rounded-xl">
           <X className="w-5 h-5" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-8 space-y-10">
        {/* Meta Info */}
        <section className="grid grid-cols-2 gap-4">
           <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5">
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Status</p>
              <Badge className="bg-primary/10 text-primary border-primary/20">{application.status.toUpperCase()}</Badge>
           </div>
           <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5">
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Location</p>
              <p className="text-sm font-medium text-slate-200 flex items-center gap-1.5">
                <MapPin className="w-3 h-3" /> {application.job.location}
              </p>
           </div>
        </section>

        {/* Timeline */}
        <section className="space-y-6">
           <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-100 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-primary" /> Application Timeline
              </h3>
              <Button size="sm" variant="ghost" onClick={() => setShowEventForm(true)} className="text-xs h-8">
                <Plus className="w-3 h-3 mr-1" /> Add Event
              </Button>
           </div>

           {showEventForm && (
             <div className="p-4 rounded-2xl bg-white/5 border border-primary/20 space-y-4">
                <div className="grid grid-cols-2 gap-3">
                   <select 
                     className="bg-slate-900 border-border rounded-lg text-xs p-2 text-slate-100"
                     value={eventType}
                     onChange={(e) => setEventType(e.target.value)}
                   >
                     <option>Interview</option>
                     <option>OA Received</option>
                     <option>Follow-up</option>
                     <option>Offer</option>
                   </select>
                   <input 
                     type="datetime-local" 
                     className="bg-slate-900 border-border rounded-lg text-xs p-2 text-slate-100"
                     value={eventDate}
                     onChange={(e) => setEventDate(e.target.value)}
                   />
                </div>
                <div className="flex gap-2">
                   <Button size="sm" className="flex-1 h-8 text-[10px]" onClick={handleAddEvent}>Log Event</Button>
                   <Button size="sm" variant="ghost" className="h-8 text-[10px]" onClick={() => setShowEventForm(false)}>Cancel</Button>
                </div>
             </div>
           )}

           <div className="space-y-6 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-px before:bg-white/5">
              {application.events?.map((event: any, i: number) => (
                <div key={i} className="pl-8 relative group/event">
                   <div className="absolute left-0 top-1.5 h-4 w-4 rounded-full bg-slate-900 border-2 border-primary z-10" />
                   <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm font-bold text-slate-100">{event.event_type}</p>
                        <p className="text-xs text-slate-500">{new Date(event.event_date).toLocaleString()}</p>
                      </div>
                      <Button 
                        size="sm" 
                        variant="ghost" 
                        className="h-8 w-8 rounded-lg opacity-0 group-hover/event:opacity-100 transition-opacity"
                        onClick={(e) => handleSync(e, event.id)}
                      >
                        <CalendarDays className="w-3 h-3 text-primary" />
                      </Button>
                   </div>
                   {event.notes && <p className="text-xs text-slate-400 mt-2 bg-white/5 p-2 rounded-lg">{event.notes}</p>}
                </div>
              ))}
              <div className="pl-8 relative">
                 <div className="absolute left-0 top-1.5 h-4 w-4 rounded-full bg-slate-900 border-2 border-slate-700 z-10" />
                 <p className="text-sm font-bold text-slate-500">Applied</p>
                 <p className="text-xs text-slate-600">{new Date(application.applied_at).toLocaleString()}</p>
              </div>
           </div>
        </section>

        {/* Notes */}
        <section className="space-y-4">
           <h3 className="font-bold text-slate-100 flex items-center gap-2">
             <FileText className="w-4 h-4 text-primary" /> Private Notes
           </h3>
           <textarea 
             className="w-full h-32 bg-white/[0.02] border border-white/5 rounded-2xl p-4 text-sm text-slate-300 focus:border-primary/50 transition-colors"
             placeholder="Add interview feedback, recruiter contact info, or follow-up strategies..."
             defaultValue={application.notes}
           />
        </section>

        {/* Actions */}
        <div className="pt-6 grid grid-cols-2 gap-4">
           <Button variant="outline" className="rounded-xl h-12">
             <ExternalLink className="w-4 h-4 mr-2" /> View Job Post
           </Button>
           <Button variant="destructive" className="rounded-xl h-12 bg-rose-500/10 text-rose-500 hover:bg-rose-500 hover:text-white border-rose-500/20">
             <Trash2 className="w-4 h-4 mr-2" /> Remove Track
           </Button>
        </div>
      </div>
    </motion.div>
  );
};
