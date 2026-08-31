import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { TrendingUp, DollarSign, Target, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatsProps {
  employabilityIndex: number;
  salaryBand: string;
  placementProb: number;
  weeklyProgress: number;
}

export const OpportunityStats = ({ employabilityIndex, salaryBand, placementProb, weeklyProgress }: StatsProps) => {
  const stats = [
    { 
      label: "Employability Index", 
      value: `${employabilityIndex}%`, 
      icon: Activity, 
      color: "text-primary",
      desc: "Market readiness score"
    },
    { 
      label: "Predicted Salary", 
      value: salaryBand, 
      icon: DollarSign, 
      color: "text-emerald-400",
      desc: "Based on current skills"
    },
    { 
      label: "Placement Prob.", 
      value: `${placementProb}%`, 
      icon: Target, 
      color: "text-amber-400",
      desc: "Offer likelihood"
    },
    { 
      label: "Weekly Progress", 
      value: `${weeklyProgress}%`, 
      icon: TrendingUp, 
      color: "text-purple-400",
      desc: "Target completion"
    },
  ];

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.label} className="bg-card border-border hover:border-primary/30 transition-all group">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-bold text-slate-500 uppercase tracking-widest">{stat.label}</CardTitle>
            <div className={cn("p-2 rounded-lg bg-white/5", stat.color)}>
              <stat.icon className="w-4 h-4" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-black text-slate-100">{stat.value}</div>
            <p className="text-[10px] text-slate-500 mt-1">{stat.desc}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
