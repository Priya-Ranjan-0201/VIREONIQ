import React, { useState, useEffect } from 'react';
import { ToggleLeft, ToggleRight, Settings, Sliders, CheckCircle2, ShieldCheck, ZapOff, Wifi } from 'lucide-react';
import { toast } from 'sonner';

export const LabMode = () => {
  const [labModeEnabled, setLabModeEnabled] = useState(
    () => localStorage.getItem('lab_mode_enabled') === 'true'
  );
  const [lowBandwidthImages, setLowBandwidthImages] = useState(
    () => localStorage.getItem('lab_mode_low_bandwidth_images') === 'true'
  );
  const [disabledAvatars, setDisabledAvatars] = useState(
    () => localStorage.getItem('lab_mode_disabled_avatars') === 'true'
  );
  const [useLocalCompilation, setUseLocalCompilation] = useState(
    () => localStorage.getItem('lab_mode_local_compile') === 'true'
  );

  const handleToggleLabMode = () => {
    const nextVal = !labModeEnabled;
    setLabModeEnabled(nextVal);
    localStorage.setItem('lab_mode_enabled', String(nextVal));
    
    // Automatically toggle dependencies if main mode is switched
    if (nextVal) {
      setLowBandwidthImages(true);
      setDisabledAvatars(true);
      localStorage.setItem('lab_mode_low_bandwidth_images', 'true');
      localStorage.setItem('lab_mode_disabled_avatars', 'true');
      toast.success('Lab Mode activated! High-fidelity video avatars and rich image rendering are now bypassed.');
    } else {
      toast.info('Lab Mode disabled. Standard settings restored.');
    }
  };

  const handleToggleOption = (key: string, val: boolean, setter: (v: boolean) => void) => {
    setter(val);
    localStorage.setItem(key, String(val));
    toast.success('Optimization settings updated.');
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header>
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">
          Lab Mode Configurations
        </h2>
        <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">
          Optimize asset weights, bypass resource-intensive scripts, and adapt the compiler for slow lab connections
        </p>
      </header>

      {/* Main Switch Panel */}
      <div className="glass-panel p-6 rounded-3xl flex justify-between items-center bg-slate-900/50 border border-slate-850">
        <div className="space-y-1 max-w-xl">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-amber-400 uppercase tracking-wider bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
              Low-Connectivity Accelerator
            </span>
          </div>
          <h3 className="text-lg font-bold text-white mt-2">Activate Lab Mode</h3>
          <p className="text-slate-400 text-xs leading-relaxed">
            Main toggle to bundle all bandwidth optimization guidelines. Suitable for shared campus lab computers running old browsers or congested proxy servers.
          </p>
        </div>
        <button onClick={handleToggleLabMode} className="text-slate-300 hover:text-white transition">
          {labModeEnabled ? (
            <ToggleRight className="w-14 h-10 text-primary" />
          ) : (
            <ToggleLeft className="w-14 h-10 text-slate-600" />
          )}
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Detailed Controls */}
        <div className="glass-panel p-6 rounded-3xl space-y-5">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Sliders className="w-4 h-4 text-primary" />
            Granular Optimization Gates
          </h3>

          <div className="divide-y divide-slate-850">
            {/* Control 1 */}
            <div className="flex justify-between items-center py-4 first:pt-0">
              <div className="space-y-0.5">
                <h4 className="text-xs font-bold text-white">Disable High-Fidelity 3D Avatars</h4>
                <p className="text-[10px] text-slate-500">Bypass loading voice response animations and interactive agents.</p>
              </div>
              <button
                onClick={() => handleToggleOption('lab_mode_disabled_avatars', !disabledAvatars, setDisabledAvatars)}
                className="text-slate-400 hover:text-white transition"
              >
                {disabledAvatars ? <ToggleRight className="w-10 h-7 text-primary" /> : <ToggleLeft className="w-10 h-7 text-slate-600" />}
              </button>
            </div>

            {/* Control 2 */}
            <div className="flex justify-between items-center py-4">
              <div className="space-y-0.5">
                <h4 className="text-xs font-bold text-white">Compress & Lazy-Load Images</h4>
                <p className="text-[10px] text-slate-500">Substitute SVGs and raster graphics with lightweight text placeholders.</p>
              </div>
              <button
                onClick={() => handleToggleOption('lab_mode_low_bandwidth_images', !lowBandwidthImages, setLowBandwidthImages)}
                className="text-slate-400 hover:text-white transition"
              >
                {lowBandwidthImages ? <ToggleRight className="w-10 h-7 text-primary" /> : <ToggleLeft className="w-10 h-7 text-slate-600" />}
              </button>
            </div>

            {/* Control 3 */}
            <div className="flex justify-between items-center py-4 last:pb-0">
              <div className="space-y-0.5">
                <h4 className="text-xs font-bold text-white">Optimistic Local Code Compilation</h4>
                <p className="text-[10px] text-slate-500">Run code logic client-side before forwarding compilation payloads to Judge0.</p>
              </div>
              <button
                onClick={() => handleToggleOption('lab_mode_local_compile', !useLocalCompilation, setUseLocalCompilation)}
                className="text-slate-400 hover:text-white transition"
              >
                {useLocalCompilation ? <ToggleRight className="w-10 h-7 text-primary" /> : <ToggleLeft className="w-10 h-7 text-slate-600" />}
              </button>
            </div>
          </div>
        </div>

        {/* Optimizations Impact Report */}
        <div className="glass-panel p-6 rounded-3xl space-y-6 flex flex-col justify-between">
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Wifi className="w-4 h-4 text-primary" />
              Bandwidth Performance Impact
            </h3>

            <div className="space-y-3">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-400">Average JS Bundle Size</span>
                <span className="text-emerald-400 font-bold font-mono">-64% Saved</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-400">Media Assets Network Weight</span>
                <span className="text-emerald-400 font-bold font-mono">-88% Saved</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-400">Initial Page Paint (FCP)</span>
                <span className="text-emerald-400 font-bold font-mono">0.6s (Fast)</span>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-850 flex items-center gap-2 text-[10px] text-slate-500 font-bold uppercase tracking-wider">
            <ShieldCheck className="text-primary w-4 h-4" />
            <span>Optimal performance on 3G and GPRS networks</span>
          </div>
        </div>
      </div>
    </div>
  );
};
export default LabMode;
