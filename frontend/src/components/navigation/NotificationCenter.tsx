import { useState } from "react";
import { Bell, Clock, MessageSquare, Gift, Info } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useNotifications, useMarkRead } from "../../api/hooks/useNotifications";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export const NotificationCenter = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { data: notifications, isLoading } = useNotifications();
  const { mutate: markRead } = useMarkRead();

  const unreadCount = notifications?.filter((n: any) => !n.is_read).length || 0;

  const getIcon = (type: string) => {
    switch (type) {
      case 'INTERVIEW': return <MessageSquare className="w-4 h-4 text-amber-500" />;
      case 'OFFER': return <Gift className="w-4 h-4 text-emerald-500" />;
      case 'NUDGE': return <Clock className="w-4 h-4 text-primary" />;
      default: return <Info className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="relative">
      <Button 
        variant="ghost" 
        size="icon" 
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "rounded-xl relative hover:bg-white/5 transition-colors",
          isOpen && "bg-white/5"
        )}
      >
        <Bell className="w-5 h-5 text-slate-400" />
        {unreadCount > 0 && (
          <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-primary border-2 border-slate-950 animate-pulse" />
        )}
      </Button>

      <AnimatePresence>
        {isOpen && (
          <>
            <div 
              className="fixed inset-0 z-40" 
              onClick={() => setIsOpen(false)} 
            />
            <motion.div
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.95 }}
              className="absolute right-0 mt-4 w-80 md:w-96 bg-slate-900 border border-white/10 rounded-2xl shadow-2xl z-50 overflow-hidden"
            >
              <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                 <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest">Inbox</h3>
                 {unreadCount > 0 && (
                   <Badge className="bg-primary/10 text-primary border-none text-[10px]">{unreadCount} NEW</Badge>
                 )}
              </div>

              <div className="max-h-[400px] overflow-y-auto custom-scrollbar">
                {isLoading ? (
                  <div className="p-10 text-center text-xs text-slate-500 animate-pulse font-bold uppercase tracking-widest">
                    Syncing...
                  </div>
                ) : notifications?.length === 0 ? (
                  <div className="p-10 text-center space-y-3">
                     <Bell className="w-8 h-8 text-slate-800 mx-auto" />
                     <p className="text-xs text-slate-600 font-bold uppercase tracking-tighter">Nothing to see here yet</p>
                  </div>
                ) : (
                  <div className="divide-y divide-white/5">
                    {notifications?.map((n: any) => (
                      <div 
                        key={n.id} 
                        className={cn(
                          "p-4 hover:bg-white/[0.02] transition-colors cursor-pointer group flex gap-4",
                          !n.is_read && "bg-primary/[0.02]"
                        )}
                        onClick={() => markRead(n.id)}
                      >
                         <div className="h-8 w-8 rounded-lg bg-white/5 flex items-center justify-center shrink-0 border border-white/5">
                            {getIcon(n.type)}
                         </div>
                         <div className="flex-1 space-y-1">
                            <div className="flex justify-between items-start">
                               <h4 className="text-sm font-bold text-slate-100">{n.title}</h4>
                               {!n.is_read && <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1" />}
                            </div>
                            <p className="text-xs text-slate-400 leading-relaxed">{n.message}</p>
                            <p className="text-[10px] text-slate-600 font-bold uppercase mt-2">
                               {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </p>
                         </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="p-3 border-t border-white/5 bg-white/[0.01] text-center">
                 <button className="text-[10px] font-black text-slate-500 hover:text-primary transition-colors uppercase tracking-widest">
                   View All Notifications
                 </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
