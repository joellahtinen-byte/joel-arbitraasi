'use client';

import { useState, useEffect } from 'react';
import ArbitrageCard from './components/ArbitrageCard';
import Header from './components/Header';
import StatsBar from './components/StatsBar';

interface Bet {
  bookmaker: string;
  market: string;
  odds: number;
  stake: number;
  bet_url: string;
}

interface Opportunity {
  event_name: string;
  profit_margin: number;
  guaranteed_profit: number;
  roi: number;
  total_investment: number;
  bets: Bet[];
  timestamp: string;
}

interface ScanStatus {
  last_scan: string | null;
  opportunities_count: number;
  scan_in_progress: boolean;
}

export default function Home() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [status, setStatus] = useState<ScanStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchOpportunities = async () => {
    try {
      const [oppsRes, statusRes] = await Promise.all([
        fetch(`${API_URL}/api/opportunities`),
        fetch(`${API_URL}/api/status`)
      ]);

      if (oppsRes.ok && statusRes.ok) {
        const oppsData = await oppsRes.json();
        const statusData = await statusRes.json();
        setOpportunities(oppsData);
        setStatus(statusData);
        setError(null);
      } else {
        setError('Failed to fetch data');
      }
    } catch (err) {
      setError('Could not connect to API');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const triggerScan = async () => {
    try {
      await fetch(`${API_URL}/api/scan`, { method: 'POST' });
      setTimeout(fetchOpportunities, 2000);
    } catch (err) {
      console.error('Failed to trigger scan:', err);
    }
  };

  useEffect(() => {
    fetchOpportunities();
    const interval = setInterval(fetchOpportunities, 10000);
    return () => clearInterval(interval);
  }, []);

  // Calculate total potential profit
  const totalProfit = opportunities.reduce((sum, opp) => sum + opp.guaranteed_profit, 0);
  const avgROI = opportunities.length > 0
    ? opportunities.reduce((sum, opp) => sum + opp.roi, 0) / opportunities.length
    : 0;

  return (
    <div className="min-h-screen bg-slate-50">
      <Header
        status={status}
        onRefresh={triggerScan}
        loading={loading}
      />

      <main className="container mx-auto px-4 py-8">
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
              <p className="mt-4 text-slate-600 text-lg font-medium">
                Loading opportunities...
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-white border-l-4 border-red-500 p-6 rounded-lg shadow-md max-w-2xl mx-auto">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-semibold text-slate-900">Connection Error</h3>
                <p className="mt-1 text-slate-600">{error}</p>
                <p className="mt-2 text-sm text-slate-500">
                  Ensure the API server is running: <code className="bg-slate-100 px-2 py-1 rounded">python3 api_server.py</code>
                </p>
              </div>
            </div>
          </div>
        )}

        {!loading && !error && opportunities.length === 0 && (
          <div className="text-center py-20">
            <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-8">
              <svg className="mx-auto h-16 w-16 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <h2 className="mt-4 text-xl font-semibold text-slate-900">
                No Opportunities Found
              </h2>
              <p className="mt-2 text-slate-600">
                The scanner is continuously looking for arbitrage opportunities.
              </p>
              <button
                onClick={triggerScan}
                className="mt-6 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition"
              >
                <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Scan Again
              </button>
            </div>
          </div>
        )}

        {!loading && !error && opportunities.length > 0 && (
          <div>
            <StatsBar
              opportunitiesCount={opportunities.length}
              totalProfit={totalProfit}
              avgROI={avgROI}
            />

            <div className="mt-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-slate-900">
                  Active Opportunities
                </h2>
                <span className="text-sm text-slate-500">
                  Sorted by profitability
                </span>
              </div>

              <div className="grid gap-6 lg:grid-cols-2">
                {opportunities.map((opp, index) => (
                  <ArbitrageCard
                    key={index}
                    opportunity={opp}
                    rank={index + 1}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="mt-16 border-t border-slate-200 bg-white py-8">
        <div className="container mx-auto px-4 text-center text-sm text-slate-600">
          <p>ArbStream - Professional Arbitrage Detection Platform</p>
          <p className="mt-1 text-slate-400">Data refreshes automatically every 10 seconds</p>
        </div>
      </footer>
    </div>
  );
}
