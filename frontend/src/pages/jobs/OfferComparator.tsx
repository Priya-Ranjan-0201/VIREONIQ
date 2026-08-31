import { useState, useMemo } from "react";
import { 
  Gift, 
  TrendingUp, 
  MapPin, 
  Calendar,
  ArrowLeft,
  Plus,
  DollarSign,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  Building2,
  X,
  Scale,
  Award,
  ChevronRight
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useApplications } from "../../api/hooks/useCRM";
import { Spinner } from "@/components/shared/Spinner";
import { Link } from "react-router-dom";
import { toast } from "sonner";

interface OfferItem {
  id: string;
  company_name: string;
  title: string;
  base_salary: number; // In INR per annum
  bonus: number;
  equity_per_year: number;
  location: string;
  deadline: string;
  work_mode: "Remote" | "Hybrid" | "On-Site";
  benefits: string[];
}

const SAMPLE_OFFERS: OfferItem[] = [
  {
    id: "sample_offer_1",
    company_name: "Google",
    title: "Software Engineer (L3)",
    base_salary: 2400000,
    bonus: 400000,
    equity_per_year: 1400000,
    location: "Bengaluru",
    deadline: new Date(Date.now() + 14 * 86400000).toISOString(),
    work_mode: "Hybrid",
    benefits: ["Free Gourmet Meals", "₹10L Health Cover", "Generous Paternity/Maternity", "Annual Learning Budget"]
  },
  {
    id: "sample_offer_2",
    company_name: "Stripe",
    title: "Backend Infrastructure Engineer",
    base_salary: 2800000,
    bonus: 500000,
    equity_per_year: 1500000,
    location: "Remote (India)",
    deadline: new Date(Date.now() + 10 * 86400000).toISOString(),
    work_mode: "Remote",
    benefits: ["₹1.5L Home Office Setup", "Flexible Hours", "Global Offsites", "Wellness Allowance"]
  },
  {
    id: "sample_offer_3",
    company_name: "Swiggy",
    title: "Full-Stack Engineer (Platform)",
    base_salary: 1800000,
    bonus: 200000,
    equity_per_year: 400000,
    location: "Bengaluru",
    deadline: new Date(Date.now() + 21 * 86400000).toISOString(),
    work_mode: "Hybrid",
    benefits: ["Swiggy One VIP Access", "Medical Insurance", "Gym Membership", "Relocation Support"]
  }
];

export const OfferComparator = () => {
  const { data: applications, isLoading } = useApplications();

  // Extract offers from applications or fallback to sample offers
  const initialOffers = useMemo(() => {
    const realOffers: OfferItem[] = [];
    if (applications) {
      applications.forEach((app: any) => {
        if (app.offer) {
          realOffers.push({
            id: app.id,
            company_name: app.job?.company_name || "MNC Partner",
            title: app.job?.title || "Software Engineer",
            base_salary: app.offer.base_salary || 2000000,
            bonus: app.offer.bonus || 200000,
            equity_per_year: app.offer.equity_value || 500000,
            location: app.offer.location || app.job?.location || "Bengaluru",
            deadline: app.offer.deadline || new Date(Date.now() + 14 * 86400000).toISOString(),
            work_mode: "Hybrid",
            benefits: ["Comprehensive Medical", "Performance Bonus", "Tech Stipend"]
          });
        }
      });
    }
    return realOffers.length >= 2 ? realOffers : SAMPLE_OFFERS;
  }, [applications]);

  const [activeOffers, setActiveOffers] = useState<OfferItem[]>(initialOffers);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form state
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [base, setBase] = useState("2000000");
  const [bonus, setBonus] = useState("250000");
  const [equity, setEquity] = useState("500000");
  const [location, setLocation] = useState("Bengaluru");
  const [workMode, setWorkMode] = useState<"Remote" | "Hybrid" | "On-Site">("Hybrid");

  // Calculate estimated monthly in-hand after standard Indian tax regime
  const calculateInHand = (annualBase: number) => {
    // Approximate monthly take-home after standard deduction and slab rates
    const standardDeduction = 75000;
    const taxable = Math.max(0, annualBase - standardDeduction);
    let tax = 0;
    if (taxable > 1500000) {
      tax = 150000 + (taxable - 1500000) * 0.3;
    } else if (taxable > 1200000) {
      tax = 90000 + (taxable - 1200000) * 0.2;
    } else if (taxable > 1000000) {
      tax = 60000 + (taxable - 1000000) * 0.15;
    } else if (taxable > 700000) {
      tax = 20000 + (taxable - 700000) * 0.1;
    }
    const annualNet = annualBase - tax;
    return Math.round(annualNet / 12);
  };

  const handleAddOffer = (e: React.FormEvent) => {
    e.preventDefault();
    if (!company.trim() || !role.trim()) {
      toast.error("Please enter company and role");
      return;
    }

    const newOffer: OfferItem = {
      id: "offer_" + Date.now(),
      company_name: company,
      title: role,
      base_salary: Number(base) || 1800000,
      bonus: Number(bonus) || 200000,
      equity_per_year: Number(equity) || 400000,
      location: location,
      deadline: new Date(Date.now() + 14 * 86400000).toISOString(),
      work_mode: workMode,
      benefits: ["Health Insurance", "Annual Bonus", "Learning Stipend"]
    };

    setActiveOffers([newOffer, ...activeOffers]);
    setShowAddModal(false);
    setCompany("");
    setRole("");
    toast.success(`Offer from ${company} added for side-by-side comparison!`);
  };

  const handleLoadPresets = () => {
    setActiveOffers(SAMPLE_OFFERS);
    toast.success("Loaded Google, Stripe & Swiggy sample offers!");
  };

  if (isLoading) return <div className="h-[60vh] flex items-center justify-center"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-8 animate-fade-in pb-20">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="flex items-start gap-4">
          <Link to="/app/applications">
            <Button variant="ghost" size="icon" className="rounded-xl bg-slate-900 border border-white/10 hover:bg-white/10 mt-1">
              <ArrowLeft className="w-5 h-5 text-slate-300" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 tracking-wide uppercase mb-1">
              <Scale className="w-3.5 h-3.5" /> Total Compensation & Decision Science
            </div>
            <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white flex items-center gap-3">
              Offer Comparator
            </h1>
            <p className="text-slate-400 mt-1 text-sm max-w-xl">
              Side-by-side financial, equity vesting, cost-of-living, and career velocity analysis for candidate negotiations.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button
            onClick={handleLoadPresets}
            variant="outline"
            className="rounded-xl border-white/10 text-slate-300 hover:text-white text-xs font-bold py-5"
          >
            <Sparkles className="w-4 h-4 mr-2 text-amber-400" /> Reset Sample Top Offers
          </Button>

          <Button
            onClick={() => setShowAddModal(true)}
            className="rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold py-5 shadow-lg shadow-emerald-600/20"
          >
            <Plus className="w-4 h-4 mr-2" /> Add Custom Offer
          </Button>
        </div>
      </header>

      {/* Offer Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {activeOffers.map((offer, idx) => {
          const totalAnnual = offer.base_salary + offer.bonus + offer.equity_per_year;
          const monthlyInHand = calculateInHand(offer.base_salary);
          const isHighestCTC = activeOffers.every(
            (o) => o.base_salary + o.bonus + o.equity_per_year <= totalAnnual
          );

          return (
            <Card
              key={offer.id}
              className="bg-slate-950 border border-white/10 relative overflow-hidden rounded-3xl group hover:border-emerald-500/50 transition-all shadow-xl"
            >
              {isHighestCTC && (
                <div className="absolute top-0 right-0 bg-gradient-to-l from-emerald-500 to-teal-500 text-slate-950 font-black text-[9px] uppercase px-3 py-1 rounded-bl-xl tracking-wider shadow-md">
                  Highest Overall TC
                </div>
              )}
              <div className="h-1.5 w-full bg-gradient-to-r from-emerald-500 via-cyan-500 to-indigo-500" />

              <CardHeader className="p-6 pb-4">
                <div className="flex justify-between items-start mb-2">
                  <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-white/10 flex items-center justify-center font-black text-white text-base shadow-md">
                    {offer.company_name[0]}
                  </div>
                  <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-xs font-bold">
                    {offer.work_mode}
                  </Badge>
                </div>
                <CardTitle className="text-xl font-black text-white">{offer.title}</CardTitle>
                <p className="text-xs text-slate-400 font-bold mt-0.5">{offer.company_name}</p>
              </CardHeader>

              <CardContent className="p-6 pt-0 space-y-5">
                {/* Highlight CTC & Monthly In Hand */}
                <div className="p-4 rounded-2xl bg-slate-900/80 border border-white/5 space-y-3">
                  <div className="flex justify-between items-end">
                    <div>
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Total CTC (Year 1)</p>
                      <p className="text-2xl sm:text-3xl font-black text-white">
                        ₹{(totalAnnual / 100000).toFixed(1)}L
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Est. Monthly Take-Home</p>
                      <p className="text-base font-black text-emerald-400">
                        ₹{monthlyInHand.toLocaleString()} / mo
                      </p>
                    </div>
                  </div>

                  <div className="h-px bg-white/5" />

                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div>
                      <span className="text-[10px] text-slate-500 block font-bold">Fixed Base</span>
                      <span className="font-black text-slate-200">₹{(offer.base_salary / 100000).toFixed(1)}L</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 block font-bold">Sign-on Bonus</span>
                      <span className="font-black text-emerald-400">₹{(offer.bonus / 100000).toFixed(1)}L</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 block font-bold">Equity / Yr</span>
                      <span className="font-black text-cyan-400">₹{(offer.equity_per_year / 100000).toFixed(1)}L</span>
                    </div>
                  </div>
                </div>

                {/* Location and Deadline */}
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3 bg-slate-900/40 rounded-xl border border-white/5">
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-slate-400" /> Location
                    </p>
                    <p className="font-bold text-slate-200 mt-1">{offer.location}</p>
                  </div>
                  <div className="p-3 bg-slate-900/40 rounded-xl border border-white/5">
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                      <Calendar className="w-3 h-3 text-slate-400" /> Decision By
                    </p>
                    <p className="font-bold text-rose-400 mt-1">
                      {new Date(offer.deadline).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </p>
                  </div>
                </div>

                {/* Benefits */}
                <div className="space-y-2">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Key Perks & Benefits</p>
                  <div className="flex flex-wrap gap-1.5">
                    {offer.benefits.map((b, bIdx) => (
                      <span
                        key={bIdx}
                        className="text-[10px] bg-slate-900 text-slate-300 px-2.5 py-1 rounded-lg border border-white/5 font-semibold"
                      >
                        {b}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Direct link to Negotiator */}
                <Link to="/app/offer-negotiator" className="block pt-1">
                  <Button className="w-full py-5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-white/10 text-white text-xs font-bold flex items-center justify-center gap-2 group-hover:border-emerald-500/50">
                    Negotiate Counter-Offer <ChevronRight className="w-4 h-4 text-emerald-400" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Decision Matrix Table */}
      <Card className="bg-slate-950 border border-white/10 rounded-3xl p-6 sm:p-8 shadow-2xl overflow-x-auto">
        <h3 className="text-base font-black text-white flex items-center gap-2 mb-4">
          <Award className="w-4 h-4 text-amber-400" /> 4-Year Long-Term Equity & Financial Projection
        </h3>
        <table className="w-full text-xs text-left">
          <thead>
            <tr className="border-b border-white/10 text-slate-500 uppercase tracking-wider">
              <th className="pb-3 font-bold">Company & Role</th>
              <th className="pb-3 font-bold">Base (Yr 1)</th>
              <th className="pb-3 font-bold">Total Year 1 CTC</th>
              <th className="pb-3 font-bold">4-Year Projected TC</th>
              <th className="pb-3 font-bold">Work Mode</th>
              <th className="pb-3 font-bold">Tax Efficiency</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {activeOffers.map((offer) => {
              const yr1 = offer.base_salary + offer.bonus + offer.equity_per_year;
              const yr4 = (offer.base_salary * 1.15) * 4 + offer.bonus + (offer.equity_per_year * 4);
              return (
                <tr key={offer.id} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-4 font-bold text-white">
                    {offer.company_name} <span className="text-slate-400 font-normal block">{offer.title}</span>
                  </td>
                  <td className="py-4 text-slate-300 font-mono">₹{(offer.base_salary / 100000).toFixed(1)}L</td>
                  <td className="py-4 font-bold text-emerald-400 font-mono">₹{(yr1 / 100000).toFixed(1)}L</td>
                  <td className="py-4 font-black text-cyan-400 font-mono">₹{(yr4 / 100000).toFixed(1)}L</td>
                  <td className="py-4 text-slate-300">{offer.work_mode}</td>
                  <td className="py-4 text-slate-400">
                    {offer.work_mode === "Remote" ? "High (Zero Commute/Living Cost)" : "Moderate (Tier-1 City)"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>

      {/* Add Custom Offer Modal */}
      {showAddModal && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
          onClick={() => setShowAddModal(false)}
        >
          <div
            className="bg-slate-950 border border-slate-800 rounded-3xl w-full max-w-lg p-6 sm:p-8 space-y-5 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between pb-3 border-b border-slate-800">
              <div>
                <h3 className="text-lg font-black text-white">Add Offer for Comparison</h3>
                <p className="text-xs text-slate-400">Enter compensation details from your offer letter</p>
              </div>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddOffer} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-bold mb-1">Company Name</label>
                  <input
                    type="text"
                    placeholder="e.g. Microsoft, Atlassian"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-bold mb-1">Job Title</label>
                  <input
                    type="text"
                    placeholder="e.g. SDE-1"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white outline-none focus:border-emerald-500"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-300 font-bold mb-1">Base (₹/year)</label>
                  <input
                    type="number"
                    value={base}
                    onChange={(e) => setBase(e.target.value)}
                    className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-bold mb-1">Joining Bonus</label>
                  <input
                    type="number"
                    value={bonus}
                    onChange={(e) => setBonus(e.target.value)}
                    className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-bold mb-1">Equity / Year</label>
                  <input
                    type="number"
                    value={equity}
                    onChange={(e) => setEquity(e.target.value)}
                    className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-bold mb-1">Location</label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-bold mb-1">Work Mode</label>
                  <select
                    value={workMode}
                    onChange={(e: any) => setWorkMode(e.target.value)}
                    className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white outline-none focus:border-emerald-500"
                  >
                    <option value="Hybrid">Hybrid</option>
                    <option value="Remote">Remote</option>
                    <option value="On-Site">On-Site</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <Button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  variant="outline"
                  className="flex-1 py-5 rounded-xl border-slate-700 text-slate-300 text-xs font-bold"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="flex-1 py-5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-emerald-600/30"
                >
                  Add to Comparator ⚖️
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
