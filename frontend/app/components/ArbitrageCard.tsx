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
  const getRankEmoji = (rank: number) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  };

  const getProfitColor = (margin: number) => {
    if (margin >= 5) return 'from-green-400 to-emerald-500';
    if (margin >= 2) return 'from-blue-400 to-cyan-500';
    if (margin >= 1) return 'from-yellow-400 to-orange-500';
    return 'from-purple-400 to-pink-500';
  };

  const getMarketEmoji = (market: string) => {
    if (market === 'Home Win') return '🏠';
    if (market === 'Away Win') return '✈️';
    if (market === 'Draw') return '🤝';
    return '⚽';
  };

  return (
    <div className="bg-white rounded-3xl shadow-2xl overflow-hidden transform hover:scale-105 transition-all duration-300 border-4 border-purple-300">
      {/* Header */}
      <div className={`bg-gradient-to-r ${getProfitColor(opportunity.profit_margin)} p-6`}>
        <div className="flex items-center justify-between">
          <div className="text-4xl font-black text-white">
            {getRankEmoji(rank)}
          </div>
          <div className="text-right">
            <div className="text-3xl font-black text-white drop-shadow-lg">
              €{opportunity.guaranteed_profit.toFixed(2)}
            </div>
            <div className="text-white text-sm font-bold">
              {opportunity.profit_margin.toFixed(2)}% profit
            </div>
          </div>
        </div>

        <div className="mt-4">
          <h3 className="text-xl font-bold text-white drop-shadow">
            {opportunity.event_name}
          </h3>
        </div>
      </div>

      {/* Bets */}
      <div className="p-6 space-y-4">
        <div className="text-center mb-4">
          <div className="text-gray-600 text-sm font-semibold">
            Total Investment
          </div>
          <div className="text-2xl font-black text-purple-600">
            €{opportunity.total_investment.toFixed(2)}
          </div>
        </div>

        <div className="space-y-3">
          {opportunity.bets.map((bet, index) => (
            <div
              key={index}
              className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-2xl border-2 border-purple-200 hover:border-purple-400 transition"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{getMarketEmoji(bet.market)}</span>
                  <div>
                    <div className="font-bold text-purple-900">
                      {bet.market}
                    </div>
                    <div className="text-sm text-gray-600">
                      {bet.bookmaker}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-600">Odds</div>
                  <div className="font-black text-purple-600 text-lg">
                    {bet.odds.toFixed(2)}
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-600">Bet Amount</div>
                  <div className="text-2xl font-black text-green-600">
                    €{bet.stake.toFixed(0)}
                  </div>
                </div>

                <a
                  href={bet.bet_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-gradient-to-r from-green-400 to-emerald-500 hover:from-green-500 hover:to-emerald-600 text-white font-bold py-2 px-6 rounded-full shadow-lg transform hover:scale-105 transition"
                >
                  Place Bet 🎯
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="mt-6 pt-4 border-t-2 border-purple-200">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="bg-purple-100 p-3 rounded-xl">
              <div className="text-sm text-gray-600">ROI</div>
              <div className="text-xl font-black text-purple-600">
                {opportunity.roi.toFixed(2)}%
              </div>
            </div>
            <div className="bg-green-100 p-3 rounded-xl">
              <div className="text-sm text-gray-600">Profit</div>
              <div className="text-xl font-black text-green-600">
                €{opportunity.guaranteed_profit.toFixed(2)}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
