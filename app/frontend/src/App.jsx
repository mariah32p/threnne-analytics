import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ShieldCheck, TrendingUp, MicVocal, History, Radar, Layers } from 'lucide-react';

export default function App() {
  const [activeView, setActiveView] = useState('forecast'); // 'forecast' or 'backtest'
  const [accelerating, setAccelerating] = useState([]);
  const [emerging, setEmerging] = useState([]);
  const [stacks, setStacks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);

    Promise.all([
      fetch(`http://127.0.0.1:8000/api/v1/${activeView}/tropes`).then((res) => res.json()),
      fetch(`http://127.0.0.1:8000/api/v1/${activeView}/stacks`).then((res) => res.json()),
    ])
      .then(([tropesJson, stacksJson]) => {
        const itemViewCount = (item) =>
          activeView === 'forecast' ? item.epoch3_count : item.epoch2_count;

        const formatTropes = (dataArray) =>
          dataArray.map((item) => ({
            name: item.trope.replace(/_/g, ' '),
            lift: parseFloat(item.trend_lift),
            books: itemViewCount(item),
            baseline: item.baseline_count,
          }));

        const formatStacks = (dataArray) =>
          dataArray.slice(0, 10).map((item, index) => ({
            rank: index + 1,
            name: item.stack.replace(/_/g, ' ').replace(/\+/g, ' + '),
            lift: parseFloat(item.trend_lift),
          }));

        setAccelerating(formatTropes(tropesJson.accelerating));
        setEmerging(formatTropes(tropesJson.emerging));
        setStacks(formatStacks(stacksJson.data));
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching data:', err);
        setLoading(false);
      });
  }, [activeView]);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-[#161616] border border-[#333] p-3 rounded shadow-lg">
          <p className="text-white font-bebas text-lg tracking-wide mb-1">{data.name}</p>
          <p className="text-[#FF3366] text-sm font-bold">{data.lift}x Trend Lift</p>
          <div className="mt-2 pt-2 border-t border-[#333] text-xs text-gray-400">
            <p>
              {activeView === 'forecast' ? 'Forecast' : 'Backtest'} Books:{' '}
              <span className="text-white">{data.books}</span>
            </p>
            <p>
              Baseline Books: <span className="text-white">{data.baseline}</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-threnne-bg text-threnne-accent p-8 font-sans">
      <header className="mb-8 border-b border-gray-800 pb-6 flex justify-between items-end flex-wrap gap-4">
        <div>
          <h1 className="text-6xl font-bebas tracking-wide">
            THRENNE <span className="text-gray-500">INTELLIGENCE</span>
          </h1>
          <p className="text-gray-400 mt-2 text-sm uppercase tracking-widest">
            Romance Market Predictive Analytics
          </p>
        </div>

        <div className="flex bg-[#161616] border border-gray-800 rounded-full p-1">
          <button
            type="button"
            onClick={() => setActiveView('backtest')}
            className={`flex items-center space-x-2 px-6 py-2 rounded-full text-sm font-semibold transition-all ${
              activeView === 'backtest'
                ? 'bg-[#333] text-white'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            <History className="w-4 h-4" />
            <span>2018-2023 BACKTEST</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveView('forecast')}
            className={`flex items-center space-x-2 px-6 py-2 rounded-full text-sm font-semibold transition-all ${
              activeView === 'forecast'
                ? 'bg-[#FF3366] text-white'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            <Radar className="w-4 h-4" />
            <span>LIVE FORECAST</span>
          </button>
        </div>
      </header>

      {/* CONFIDENCE & METHODOLOGY BANNER */}
      <div className="bg-threnne-card border border-gray-800 rounded-lg p-5 mb-8 flex items-start space-x-4">
        <ShieldCheck className="text-green-500 w-6 h-6 mt-1 flex-shrink-0" />
        <div>
          <h3 className="font-bebas text-xl tracking-wide text-white">
            THE CONFIDENCE RULE & DATA METHODOLOGY
          </h3>
          <p className="text-gray-400 text-sm mt-2 leading-relaxed">
            All trend multipliers are calculated against a static{' '}
            <strong>2010–2017 Baseline of 2.36 million books</strong>. Data is then split into two distinct signals:{' '}
            <br />
            <br />
            <strong>1. Accelerating Trends:</strong> Established tropes (Baseline &gt; 50 books) gaining verifiable
            market share.
            <br />
            <strong>2. Emerging Terminology:</strong> Terms with near-zero baselines, representing sudden shifts in
            reader marketing vocabulary. <br />
            <br />
            <span className="text-gray-300 italic">
              {activeView === 'forecast'
                ? 'Note: Live Forecast data is drawn from a highly curated daily sample of anticipated 2024-2026 releases and is subject to higher volatility.'
                : 'Note: The 2018-2023 Backtest utilizes thousands of published books to prove the mathematical model successfully predicted past market booms.'}
            </span>
          </p>
        </div>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-gray-500 animate-pulse font-bebas text-2xl tracking-widest">
          Querying Data Engine...
        </div>
      ) : (
        <div className="space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-threnne-card border border-gray-800 rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-2">
                <TrendingUp className="text-[#FF3366] w-6 h-6" />
                <h2 className="text-3xl font-bebas tracking-wide text-white">ACCELERATING TRENDS</h2>
              </div>
              <p className="text-xs text-gray-500 mb-6 uppercase tracking-wider">
                Historical Baseline &gt; 50 Books
              </p>

              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={accelerating}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" horizontal={true} vertical={false} />
                    <XAxis type="number" stroke="#666" tickFormatter={(value) => `${value}x`} />
                    <YAxis
                      dataKey="name"
                      type="category"
                      stroke="#E5E5E5"
                      width={140}
                      tick={{ fontSize: 11, fontFamily: 'Inter', fill: '#9ca3af' }}
                    />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: '#222' }} />
                    <Bar dataKey="lift" fill="#FF3366" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-threnne-card border border-gray-800 rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-2">
                <MicVocal className="text-[#33B5FF] w-6 h-6" />
                <h2 className="text-3xl font-bebas tracking-wide text-white">EMERGING TERMINOLOGY</h2>
              </div>
              <p className="text-xs text-gray-500 mb-6 uppercase tracking-wider">
                Taxonomy Shift (Baseline &lt; 50 Books)
              </p>

              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={emerging}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" horizontal={true} vertical={false} />
                    <XAxis type="number" stroke="#666" tickFormatter={(value) => `${value}x`} />
                    <YAxis
                      dataKey="name"
                      type="category"
                      stroke="#E5E5E5"
                      width={140}
                      tick={{ fontSize: 11, fontFamily: 'Inter', fill: '#9ca3af' }}
                    />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: '#222' }} />
                    <Bar dataKey="lift" fill="#33B5FF" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="bg-threnne-card border border-gray-800 rounded-lg p-6">
            <div className="flex items-center space-x-3 mb-2">
              <Layers className="text-[#A78BFA] w-6 h-6" />
              <h2 className="text-3xl font-bebas tracking-wide text-white">BREAKOUT TROPE COMBINATIONS</h2>
            </div>
            <p className="text-xs text-gray-500 mb-6 uppercase tracking-wider">
              High-Velocity Market Sub-Niches ({activeView === 'forecast' ? 'Live Forecast' : '2018-2023 Backtest'})
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-[#333] text-gray-400 text-xs uppercase tracking-widest">
                    <th className="pb-3 pl-2 font-medium w-16">Rank</th>
                    <th className="pb-3 font-medium">Combination Matrix</th>
                    <th className="pb-3 font-medium text-right pr-4">Trend Lift</th>
                  </tr>
                </thead>
                <tbody>
                  {stacks.map((stack) => (
                    <tr
                      key={stack.rank}
                      className="border-b border-[#222] hover:bg-[#1a1a1a] transition-colors"
                    >
                      <td className="py-4 pl-2 font-bebas text-xl text-gray-500">#{stack.rank}</td>
                      <td className="py-4 font-semibold text-white tracking-wide text-sm">{stack.name}</td>
                      <td className="py-4 text-right pr-4">
                        <span className="bg-[#FF3366]/10 text-[#FF3366] py-1 px-2 rounded font-bold text-sm">
                          {stack.lift}x
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
