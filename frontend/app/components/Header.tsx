interface HeaderProps {
  status: {
    last_scan: string | null;
    opportunities_count: number;
    scan_in_progress: boolean;
  } | null;
  onRefresh: () => void;
  loading: boolean;
}

export default function Header({ status, onRefresh, loading }: HeaderProps) {
  const formatTime = (isoString: string | null) => {
    if (!isoString) return 'Never';
    const date = new Date(isoString);
    return date.toLocaleTimeString();
  };

  return (
    <header className="bg-gradient-to-r from-indigo-600 to-purple-600 shadow-2xl">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="text-6xl animate-bounce">🎰</div>
            <div>
              <h1 className="text-4xl font-black text-white drop-shadow-lg">
                ArbStream
              </h1>
              <p className="text-purple-200 text-sm">
                Arbitrage Betting Dashboard
              </p>
            </div>
          </div>

          <div className="text-right">
            <button
              onClick={onRefresh}
              disabled={loading || status?.scan_in_progress}
              className="bg-yellow-400 hover:bg-yellow-500 text-purple-900 font-bold py-2 px-6 rounded-full shadow-lg transform hover:scale-105 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {status?.scan_in_progress ? '⏳ Scanning...' : '🔄 Refresh'}
            </button>
            <div className="mt-2 text-white text-sm">
              Last scan: {formatTime(status?.last_scan || null)}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
