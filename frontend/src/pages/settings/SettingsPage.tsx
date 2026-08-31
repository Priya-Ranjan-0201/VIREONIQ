import { 
  User, 
  Bell, 
  Shield, 
  CreditCard, 
  RefreshCw
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { useCalendarStatus } from "../../api/hooks/useNotifications";
import { toast } from "sonner";

export const SettingsPage = () => {
  const { data: calendars } = useCalendarStatus();

  const handleConnect = (provider: string) => {
    toast.promise(
      new Promise((resolve) => setTimeout(resolve, 1500)),
      {
        loading: `Connecting to ${provider}...`,
        success: `${provider} Calendar linked successfully!`,
        error: 'Failed to link account'
      }
    );
  };

  return (
    <div className="max-w-4xl mx-auto space-y-10 animate-fade-in pb-20">
      <header>
        <h1 className="text-3xl font-black tracking-tight text-white">Settings</h1>
        <p className="text-slate-400 mt-2 text-lg">Manage your identity, alerts, and integrations.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        {/* Nav Sidebar */}
        <aside className="space-y-2">
           {[
             { id: 'account', label: 'Account', icon: User },
             { id: 'notifications', label: 'Notifications', icon: Bell },
             { id: 'integrations', label: 'Integrations', icon: RefreshCw },
             { id: 'billing', label: 'Billing', icon: CreditCard },
             { id: 'security', label: 'Security', icon: Shield },
           ].map((item) => (
             <button 
               key={item.id}
               className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 transition-all text-sm font-bold"
             >
               <item.icon className="w-4 h-4" /> {item.label}
             </button>
           ))}
        </aside>

        {/* Content */}
        <div className="lg:col-span-2 space-y-8">
           {/* Integrations */}
           <Card className="bg-card border-border overflow-hidden">
              <CardHeader className="bg-white/[0.02] border-b border-white/5">
                 <CardTitle className="text-sm font-bold flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 text-primary" /> Connected Integrations
                 </CardTitle>
              </CardHeader>
              <CardContent className="p-8 space-y-8">
                 <div className="flex items-center justify-between p-6 rounded-2xl bg-white/[0.02] border border-white/5">
                    <div className="flex items-center gap-4">
                       <div className="h-12 w-12 rounded-xl bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
                          <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Google_Calendar_icon_%282020%29.svg" className="w-6 h-6" alt="Google" />
                       </div>
                       <div>
                          <h4 className="font-bold text-slate-100">Google Calendar</h4>
                          <p className="text-xs text-slate-500">Auto-sync interviews and deadlines.</p>
                       </div>
                    </div>
                    {calendars?.some((c: any) => c.provider === 'google' && c.is_active) ? (
                      <Badge className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20">CONNECTED</Badge>
                    ) : (
                      <Button variant="outline" size="sm" onClick={() => handleConnect('Google')} className="rounded-xl font-bold">
                        Link Account
                      </Button>
                    )}
                 </div>

                 <div className="flex items-center justify-between p-6 rounded-2xl bg-white/[0.02] border border-white/5 opacity-50">
                    <div className="flex items-center gap-4">
                       <div className="h-12 w-12 rounded-xl bg-blue-600/10 flex items-center justify-center border border-blue-600/20">
                          <img src="https://upload.wikimedia.org/wikipedia/commons/d/df/Microsoft_Office_Outlook_%282018%E2%80%93present%29.svg" className="w-6 h-6" alt="Outlook" />
                       </div>
                       <div>
                          <h4 className="font-bold text-slate-100">Outlook Calendar</h4>
                          <p className="text-xs text-slate-500">Coming soon for Enterprise users.</p>
                       </div>
                    </div>
                    <Badge variant="outline" className="border-white/10 text-slate-500">LOCKED</Badge>
                 </div>
              </CardContent>
           </Card>

           {/* Notifications */}
           <Card className="bg-card border-border overflow-hidden">
              <CardHeader className="bg-white/[0.02] border-b border-white/5">
                 <CardTitle className="text-sm font-bold flex items-center gap-2">
                    <Bell className="w-4 h-4 text-primary" /> Alert Preferences
                 </CardTitle>
              </CardHeader>
              <CardContent className="p-8 space-y-6">
                 {[
                   { title: 'Interview Reminders', desc: 'Get alerted 24h and 2h before any scheduled session.' },
                   { title: 'Offer Deadline Alerts', desc: 'Final warning 48h before an offer expires.' },
                   { title: 'Market Pulse Nudges', desc: 'Alerts when a new role matches your ROI targets.' },
                   { title: 'Weekly Performance Report', desc: 'Summary of your conversion funnel and activity.' },
                 ].map((pref, i) => (
                   <div key={i} className="flex items-center justify-between py-4 border-b border-white/5 last:border-0">
                      <div className="space-y-1">
                         <h4 className="text-sm font-bold text-slate-100">{pref.title}</h4>
                         <p className="text-xs text-slate-500">{pref.desc}</p>
                      </div>
                      <Switch defaultChecked />
                   </div>
                 ))}
              </CardContent>
           </Card>

           <div className="pt-6 flex justify-end gap-4">
              <Button variant="ghost" className="rounded-xl font-bold">Discard Changes</Button>
              <Button className="rounded-xl font-bold px-8 shadow-lg shadow-primary/20">Save Preferences</Button>
           </div>
        </div>
      </div>
    </div>
  );
};
