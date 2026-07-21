import "./MarketMomentumCard.css";

export default function MarketMomentumCard({
  aspiValue,
  aspiChange,
  stocks = [],
  fullMarketBreadth,
  marketTurnover,
  concentration,
  snpValue,
  snpChange
}) {
  // 1. Calculate Breadth Metrics
  let gainers = 0;
  let losers = 0;
  let flat = 0;
  let totalSecurities = 0;
  let isFullMarket = false;

  if (fullMarketBreadth && fullMarketBreadth.total > 0) {
    gainers = fullMarketBreadth.gainers ?? 0;
    losers = fullMarketBreadth.losers ?? 0;
    flat = fullMarketBreadth.flat ?? 0;
    totalSecurities = fullMarketBreadth.total;
    isFullMarket = true;
  } else if (stocks && stocks.length > 0) {
    totalSecurities = stocks.length;
    stocks.forEach((s) => {
      const chg = s.change_pct ?? s.change ?? 0;
      if (chg > 0) gainers++;
      else if (chg < 0) losers++;
      else flat++;
    });
  }

  const breadth = totalSecurities > 0 ? gainers / totalSecurities : 0;
  const changeNum = typeof aspiChange === "number" ? aspiChange : parseFloat(aspiChange) || 0;
  const convictionRatio = marketTurnover?.conviction_ratio ?? 1.0;
  const top3Pct = concentration?.top3_volume_pct ?? 38.5;

  // Composite Scoring
  let score = 0;
  if (changeNum > 0.5) score += 2;
  else if (changeNum > 0) score += 1;
  else if (changeNum < -0.5) score -= 2;
  else if (changeNum < 0) score -= 1;

  if (breadth > 0.6) score += 2;
  else if (breadth >= 0.5) score += 1;
  else if (breadth < 0.4) score -= 2;
  else if (breadth < 0.5) score -= 1;

  if (convictionRatio > 1.2) score += 1;
  else if (convictionRatio < 0.8) score -= 1;

  if (top3Pct > 60 && score > 0) score -= 1;

  let momentumState = "Flat / Mixed";
  let statusColor = "gray";

  if (score >= 3) {
    momentumState = "Strong Bullish";
    statusColor = "green";
  } else if (score >= 1) {
    momentumState = "Mild Bullish";
    statusColor = "green";
  } else if (score <= -3) {
    momentumState = "Strong Bearish";
    statusColor = "red";
  } else if (score <= -1) {
    momentumState = "Mild Bearish";
    statusColor = "red";
  } else {
    momentumState = "Flat / Mixed";
    statusColor = "gray";
  }

  const isPositive = changeNum > 0;
  const isNegative = changeNum < 0;
  const snpNum = typeof snpChange === "number" ? snpChange : parseFloat(snpChange) || 0;
  const isSnpPos = snpNum > 0;

  // Overview Plain Summary Generator
  const generateOverviewSummary = () => {
    let dirWord = changeNum > 0.5 ? "rising strongly" : changeNum > 0 ? "edging up" : changeNum < -0.5 ? "falling sharply" : changeNum < 0 ? "edging down" : "holding steady";
    let breadthWord = breadth > 0.6 ? "gains spread broadly across most stocks" : breadth >= 0.5 ? "gains spread fairly across many stocks" : "losses affecting a majority of stocks";
    let volumeWord = convictionRatio >= 1.2 ? "stronger-than-usual trading activity" : convictionRatio <= 0.8 ? "light trading activity" : "steady trading activity";

    return `The market is ${dirWord} today, with ${breadthWord} and ${volumeWord}.`;
  };

  // Factor 1: Direction
  const dirColor = changeNum > 0 ? "green" : changeNum < 0 ? "red" : "gray";
  const dirIcon = changeNum > 0 ? "▲" : changeNum < 0 ? "▼" : "▬";
  const dirLabel = changeNum > 0 ? "Upward" : changeNum < 0 ? "Downward" : "Flat";
  const dirValue = `ASPI ${changeNum > 0 ? "+" : ""}${changeNum.toFixed(2)}%`;
  const dirExplanation = changeNum > 0
    ? "The overall market index is rising compared to yesterday."
    : changeNum < 0
    ? "The overall market index is declining compared to yesterday."
    : "The overall market index is unchanged from yesterday's close.";

  // Factor 2: Breadth
  const breadthPctStr = `${(breadth * 100).toFixed(0)}% Gainers`;
  const breadthColor = breadth >= 0.5 ? "green" : breadth < 0.4 ? "red" : "gray";
  const breadthExplanation = breadth >= 0.6
    ? "Most traded stocks advanced today, signaling broad market buying."
    : breadth >= 0.5
    ? "Half of all traded stocks went up today — a fairly even mix, not one-sided."
    : "Decliners outnumbered gainers today, reflecting broader selling pressure.";

  // Factor 3: Conviction
  const convictionLabel = convictionRatio >= 1.2 ? `High Volume (${convictionRatio.toFixed(2)}x)` : convictionRatio <= 0.8 ? `Low Volume (${convictionRatio.toFixed(2)}x)` : `Normal Volume (${convictionRatio.toFixed(2)}x)`;
  const convictionColor = convictionRatio >= 1.2 ? "green" : convictionRatio <= 0.8 ? "red" : "gray";
  const convictionExplanation = convictionRatio >= 1.2
    ? "More shares changed hands than usual, suggesting today's move is backed by real buying interest, not just noise."
    : convictionRatio <= 0.8
    ? "Light trading activity today suggests price movements may be low-conviction noise."
    : "Trading volume is aligned with recent daily averages, reflecting steady market participation.";

  // Factor 4: Concentration
  const concLabel = top3Pct <= 60 ? `Broad (${top3Pct.toFixed(1)}%)` : `Concentrated (${top3Pct.toFixed(1)}%)`;
  const concColor = top3Pct <= 60 ? "green" : "red";
  const concExplanation = top3Pct <= 60
    ? "Trading activity is spread across many companies rather than just a few — a broader, healthier signal."
    : "Trading volume is heavily concentrated in a few top stocks — a more fragile market rally.";

  return (
    <div className="momentum-section-wrapper">
      {/* 1. Top Overview Card */}
      <div className={`momentum-overview-card ${statusColor}`}>
        <div className="momentum-header">
          <span className="momentum-title">Market Behavior Sentiment Overview</span>
          <div className={`momentum-badge ${statusColor}`}>
            <span className={`status-dot ${statusColor}`} />
            {momentumState}
          </div>
        </div>

        <div className="aspi-metric-section">
          <div className="indices-group">
            <div className="aspi-primary-val">
              {typeof aspiValue === "number"
                ? aspiValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                : aspiValue ?? "N/A"}
            </div>
            <div className={`aspi-change-pill ${isPositive ? "positive" : isNegative ? "negative" : "neutral"}`}>
              {isPositive ? "▲ +" : isNegative ? "▼ " : ""}
              {Math.abs(changeNum).toFixed(2)}%
            </div>
          </div>

          {snpValue && (
            <div className="secondary-index-block">
              <span className="secondary-index-name">S&amp;P SL20:</span>
              <span className="secondary-index-val">{snpValue.toLocaleString()}</span>
              <span className={`aspi-change-pill ${isSnpPos ? "positive" : "negative"}`} style={{ fontSize: "0.85rem", padding: "0.15rem 0.45rem" }}>
                {isSnpPos ? "+" : ""}{snpNum.toFixed(2)}%
              </span>
            </div>
          )}
        </div>

        <div className="overview-auto-summary">
          &ldquo;{generateOverviewSummary()}&rdquo;
        </div>
      </div>

      {/* 2. 2x2 Factor Cards Grid */}
      <div className="factor-cards-grid">
        {/* Card 1: Direction */}
        <div className="factor-card">
          <div className="factor-card-header">
            <div className={`factor-card-icon ${dirColor}`}>{dirIcon}</div>
            <div className="factor-card-meta">
              <span className="factor-card-title">Market Direction</span>
              <span className="factor-card-label">{dirLabel}</span>
            </div>
          </div>
          <span className="factor-card-value">{dirValue}</span>
          <p className="factor-plain-explanation">{dirExplanation}</p>
        </div>

        {/* Card 2: Breadth */}
        <div className="factor-card">
          <div className="factor-card-header">
            <div className={`factor-card-icon ${breadthColor}`}>📊</div>
            <div className="factor-card-meta">
              <span className="factor-card-title">Market Breadth</span>
              <span className="factor-card-label">{breadthPctStr}</span>
            </div>
          </div>
          <span className="factor-card-value">{gainers} up · {flat} flat · {losers} down</span>
          <p className="factor-plain-explanation">{breadthExplanation}</p>
        </div>

        {/* Card 3: Conviction */}
        <div className="factor-card">
          <div className="factor-card-header">
            <div className={`factor-card-icon ${convictionColor}`}>📈</div>
            <div className="factor-card-meta">
              <span className="factor-card-title">Trading Conviction</span>
              <span className="factor-card-label">{convictionLabel}</span>
            </div>
          </div>
          <span className="factor-card-value">{marketTurnover ? `LKR ${(marketTurnover.value_lkr / 1e6).toFixed(0)}M turnover` : "Normal volume"}</span>
          <p className="factor-plain-explanation">{convictionExplanation}</p>
        </div>

        {/* Card 4: Concentration */}
        <div className="factor-card">
          <div className="factor-card-header">
            <div className={`factor-card-icon ${concColor}`}>🎯</div>
            <div className="factor-card-meta">
              <span className="factor-card-title">Market Structure</span>
              <span className="factor-card-label">{concLabel}</span>
            </div>
          </div>
          <span className="factor-card-value">Top 3 stocks = {top3Pct.toFixed(1)}% volume</span>
          <p className="factor-plain-explanation">{concExplanation}</p>
        </div>
      </div>
    </div>
  );
}
