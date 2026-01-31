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

interface ArbitrageCardProps {
  opportunity: Opportunity;
  rank: number;
}

export default function ArbitrageCard({ opportunity, rank }: ArbitrageCardProps) {
  const getProfitColor = (margin: number) => {
    if (margin >= 5) return 'text-green-600 bg-green-50 border-green-200';
    if (margin >= 2) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (margin >= 1) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-purple-600 bg-purple-50 border-purple-200';
  };

  const getProfitBadgeColor = (margin: number) => {
    if (margin >= 5) return 'bg-green-100 text-green-800';
    if (margin >= 2) return 'bg-blue-100 text-blue-800';
    if (margin >= 1) return 'bg-orange-100 text-orange-800';
    return 'bg-purple-100 text-purple-800';
  };

  const formatBookmakerName = (key: string) => {
    const names: { [key: string]: string } = {
      'unibet_nl': 'Unibet',
      'bet365': 'Bet365',
      'betfair_ex_eu': 'Betfair',
      'matchbook': 'Matchbook',
      'onexbet': '1xBet',
      'pinnacle': 'Pinnacle',
      'coolbet': 'Coolbet',
      'betsson': 'Betsson',
      'nordicbet': 'Nordicbet',
    };
    return names[key] || key;
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-slate-200 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="p-6 border-b border-slate-200">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-xs font-semibold text-slate-500">#{rank}</span>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getProfitBadgeColor(opportunity.profit_margin)}`}>
                {opportunity.profit_margin.toFixed(2)}% margin
              </span>
            </div>
            <h3 className="text-lg font-semibold text-slate-900">
              {opportunity.event_name}
            </h3>
          </div>
          <div className="text-right ml-4">
            <div className="text-2xl font-bold text-green-600">
              €{opportunity.guaranteed_profit.toFixed(2)}
            </div>
            <div className="text-xs text-slate-500">Guaranteed Profit</div>
          </div>
        </div>
      </div>

      {/* Bets */}
      <div className="p-6">
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-slate-500">Total Investment</span>
            <span className="font-semibold text-slate-900">€{opportunity.total_investment.toFixed(2)}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-500">ROI</span>
            <span className="font-semibold text-slate-900">{opportunity.roi.toFixed(2)}%</span>
          </div>
        </div>

        <div className="space-y-3 mt-4">
          {opportunity.bets.map((bet, index) => (
            <div
              key={index}
              className="border border-slate-200 rounded-lg p-4 hover:border-blue-300 transition"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="font-medium text-slate-900">{bet.market}</div>
                  <div className="text-sm text-slate-500">{formatBookmakerName(bet.bookmaker)}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-slate-500">Odds</div>
                  <div className="text-lg font-bold text-slate-900">{bet.odds.toFixed(2)}</div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-500">Stake</div>
                  <div className="text-xl font-bold text-blue-600">€{bet.stake.toFixed(0)}</div>
                </div>

                <a
                  href={bet.bet_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition"
                >
                  Place Bet
                  <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
