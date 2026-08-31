import { Check, Sparkles, Zap, ShieldCheck, Crown } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useCreateOrder, useVerifyPayment } from "../../api/hooks/usePayments";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const PLANS = [
  {
    id: "free",
    name: "Free",
    price: "₹0",
    description: "For curious individuals exploring the AI simulator.",
    features: ["3 Resume Uploads", "5 Match Recommendations", "10 Tracked Applications", "Basic ATS Insights"],
    icon: Zap,
    color: "text-slate-400"
  },
  {
    id: "growth",
    name: "Growth",
    price: "₹299",
    period: "/mo",
    description: "The complete outcome-driven career toolkit.",
    features: ["Unlimited Uploads", "Unlimited Recommendations", "Unlimited CRM Tracker", "Interview Simulator Access", "Offer Comparison"],
    icon: Crown,
    color: "text-primary",
    popular: true
  },
  {
    id: "premium",
    name: "Premium",
    price: "₹499",
    period: "/mo",
    description: "Elite intelligence for high-stakes placements.",
    features: ["Everything in Growth", "AI Growth Coach", "Personalized Weekly Roadmap", "Advanced Funnel Analytics", "Priority Support"],
    icon: Crown,
    color: "text-amber-400"
  }
];

export const PricingPage = () => {
  const { mutate: createOrder, isPending: isOrdering } = useCreateOrder();
  const { mutate: verifyPayment, isPending: isVerifying } = useVerifyPayment();

  const handleUpgrade = (planId: string) => {
    if (planId === 'free') return;

    createOrder(planId, {
      onSuccess: (data) => {
        // In a real app, you would load Razorpay checkout here:
        // const rzp = new (window as any).Razorpay({ ...options }); rzp.open();
        
        toast.info("Mock: Initializing Razorpay Checkout...");
        
        // Simulating successful payment for demo
        setTimeout(() => {
          verifyPayment({
            order_id: data.order_id,
            payment_id: "pay_mock_123",
            signature: "sig_mock_456",
            plan_id: planId
          }, {
            onSuccess: () => toast.success(`Welcome to ${planId.toUpperCase()}!`),
            onError: () => toast.error("Verification failed")
          });
        }, 2000);
      }
    });
  };

  return (
    <div className="space-y-12 animate-fade-in py-10 pb-20">
      <header className="text-center space-y-4">
        <Badge variant="outline" className="bg-primary/10 border-primary/20 text-primary font-bold px-4 py-1">
          SIMPLE PRICING
        </Badge>
        <h1 className="text-4xl lg:text-5xl font-black tracking-tight text-white">Choose Your Growth Path</h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          From basic resume scoring to elite AI coaching. Unlock the full Outcomes Engine today.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
        {PLANS.map((plan) => (
          <Card 
            key={plan.id} 
            className={cn(
              "bg-card border-border flex flex-col relative overflow-hidden transition-all hover:scale-[1.02] duration-300",
              plan.popular && "border-primary shadow-[0_0_40px_rgba(37,99,235,0.15)] ring-1 ring-primary/20"
            )}
          >
            {plan.popular && (
              <div className="absolute top-0 right-0">
                <div className="bg-primary text-[10px] font-black uppercase text-white px-8 py-1 rotate-45 translate-x-6 translate-y-3">
                  Best Value
                </div>
              </div>
            )}
            
            <CardHeader className="p-8 space-y-4">
               <div className={cn("p-3 rounded-2xl bg-white/5 w-fit", plan.color)}>
                  <plan.icon className="w-8 h-8" />
               </div>
               <div>
                  <CardTitle className="text-2xl font-black text-slate-100">{plan.name}</CardTitle>
                  <p className="text-sm text-slate-500 mt-1">{plan.description}</p>
               </div>
               <div className="flex items-baseline gap-1 pt-2">
                  <span className="text-4xl font-black text-white">{plan.price}</span>
                  <span className="text-slate-500 text-sm font-bold uppercase tracking-widest">{plan.period}</span>
               </div>
            </CardHeader>

            <CardContent className="p-8 pt-0 flex-1 flex flex-col">
               <div className="space-y-4 mb-10 flex-1">
                  {plan.features.map((feature) => (
                    <div key={feature} className="flex items-start gap-3 text-sm text-slate-300 font-medium">
                       <Check className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                       {feature}
                    </div>
                  ))}
               </div>

               <Button 
                onClick={() => handleUpgrade(plan.id)}
                disabled={isOrdering || isVerifying || plan.id === 'free'}
                className={cn(
                  "w-full h-14 text-lg font-black rounded-2xl transition-all shadow-lg",
                  plan.popular ? "bg-primary shadow-primary/20" : "bg-white/5 border-white/10 hover:bg-white/10"
                )}
               >
                 {isOrdering || isVerifying ? "Processing..." : plan.id === 'free' ? "Current Plan" : `Upgrade to ${plan.name}`}
               </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <footer className="max-w-3xl mx-auto text-center space-y-6 pt-10">
         <div className="flex justify-center gap-10">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-widest">
               <ShieldCheck className="w-4 h-4 text-emerald-500" /> Secure Payments
            </div>
            <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-widest">
               <Sparkles className="w-4 h-4 text-primary" /> Cancel Anytime
            </div>
         </div>
         <p className="text-xs text-slate-600 leading-relaxed">
           Taxes included. By upgrading, you agree to our Terms of Service and Privacy Policy. 
           India-first support with UPI, Netbanking, and Card support via Razorpay.
         </p>
      </footer>
    </div>
  );
};
