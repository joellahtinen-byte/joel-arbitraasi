'use client';

import { useState, useEffect } from 'react';
import ArbitrageCard from './components/ArbitrageCard';
import Header from './components/Header';

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
    const interval = setInterval(fetchOpportunities, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-400 via-pink-400 to-red-400">
      <Header
        status={status}
        onRefresh={triggerScan}
        loading={loading}
      />

      <main className="container mx-auto px-4 py-8">
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block animate-bounce text-6xl">🎰</div>
            <p className="text-white text-2xl font-bold mt-4 animate-pulse">
              Loading arbitrage opportunities...
            </p>
          </div>
        )}

        {error && (
          <div className="bg-red-500 text-white p-6 rounded-3xl shadow-2xl max-w-2xl mx-auto">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold mb-2">Oops! Connection Error</h2>
            <p className="mb-4">{error}</p>
            <p className="text-sm">Make sure the API server is running:</p>
            <code className="bg-red-700 px-3 py-1 rounded text-sm">
              python3 api_server.py
            </code>
          </div>
        )}

        {!loading && !error && opportunities.length === 0 && (
          <div className="text-center py-20">
            <div className="text-8xl mb-6 animate-bounce">🔍</div>
            <h2 className="text-white text-3xl font-bold mb-4">
              No Arbitrage Opportunities Found
            </h2>
            <p className="text-white text-xl mb-6">
              Keep scanning! They pop up all the time.
            </p>
            <button
              onClick={triggerScan}
              className="bg-yellow-400 hover:bg-yellow-500 text-purple-900 font-bold py-3 px-8 rounded-full text-xl shadow-lg transform hover:scale-105 transition"
            >
              🔄 Scan Again
            </button>
          </div>
        )}

        {!loading && !error && opportunities.length > 0 && (
          <div>
            <div className="text-center mb-8">
              <h2 className="text-white text-4xl font-black mb-2 drop-shadow-lg">
                💰 {opportunities.length} Hot Opportunities! 💰
              </h2>
              <p className="text-white text-xl">
                Sorted by profit (highest first) 🚀
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-2 max-w-7xl mx-auto">
              {opportunities.map((opp, index) => (
                <ArbitrageCard
                  key={index}
                  opportunity={opp}
                  rank={index + 1}
                />
              ))}
            </div>
          </div>
        )}
      </main>

      <footer className="text-center py-8 text-white">
        <p className="text-sm">
          🎯 ArbStream - Making money while you sleep 😴
        </p>
      </footer>
    </div>
  );
}
