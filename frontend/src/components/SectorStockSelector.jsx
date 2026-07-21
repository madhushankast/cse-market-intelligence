import { useState } from "react";
import "./SectorStockSelector.css";

const DEFAULT_SECTOR_MAP = {
  "Banks": [
    { symbol: "COMB", name: "Commercial Bank of Ceylon", score: 94.5 },
    { symbol: "HNB", name: "Hatton National Bank", score: 91.2 },
    { symbol: "SAMP", name: "Sampath Bank", score: 88.0 }
  ],
  "Diversified Financials": [
    { symbol: "LOLC", name: "LOLC Holdings", score: 93.0 }
  ],
  "Insurance": [
    { symbol: "AAIC", name: "Amana Takaful Life", score: 85.0 }
  ],
  "Capital Goods / Diversified Holdings": [
    { symbol: "JKH", name: "John Keells Holdings", score: 96.0 },
    { symbol: "HHL", name: "Hemas Holdings", score: 82.5 }
  ],
  "Telecommunication Services": [
    { symbol: "DIAL", name: "Dialog Axiata", score: 90.5 },
    { symbol: "SLTL", name: "Sri Lanka Telecom", score: 84.0 }
  ],
  "Food, Beverage & Tobacco": [
    { symbol: "DIST", name: "Distilleries Company of Sri Lanka", score: 89.0 }
  ],
  "Food & Staples Retailing": [
    { symbol: "CARG", name: "Cargills (Ceylon)", score: 87.5 }
  ],
  "Consumer Services (Hotels & Leisure)": [
    { symbol: "AHUN", name: "Aitken Spence Hotel Holdings", score: 83.0 }
  ],
  "Consumer Durables & Apparel": [
    { symbol: "HAYL", name: "Hayleys PLC", score: 92.0 }
  ],
  "Health Care Equipment & Services": [
    { symbol: "HEMA", name: "Hemas Holdings (Health)", score: 86.0 }
  ],
  "Materials": [
    { symbol: "ACL", name: "ACL Cables", score: 88.0 },
    { symbol: "TKYO", name: "Tokyo Cement Company", score: 85.5 }
  ],
  "Energy & Power": [
    { symbol: "LIOC", name: "Lanka IOC PLC", score: 91.0 }
  ],
  "Utilities": [
    { symbol: "LWL", name: "Lanka Tiles / Utilities", score: 81.0 }
  ],
  "Transportation": [
    { symbol: "EXPO", name: "Expolanka Holdings", score: 95.0 }
  ],
  "Automobiles & Components": [
    { symbol: "UML", name: "United Motors Lanka", score: 80.0 }
  ],
  "Retailing": [
    { symbol: "ODEL", name: "Odel PLC", score: 79.0 }
  ],
  "Household & Personal Products": [
    { symbol: "RICH", name: "Richard Pieris & Company", score: 87.0 }
  ],
  "Real Estate / Land & Property": [
    { symbol: "OSEA", name: "Overseas Realty (Ceylon)", score: 84.5 }
  ],
  "Plantations": [
    { symbol: "KGAL", name: "Kegalle Plantations", score: 78.5 },
    { symbol: "MADU", name: "Madulsima Plantations", score: 76.0 }
  ]
};

export default function SectorStockSelector({ sectorMap = DEFAULT_SECTOR_MAP, selectedSymbol, onSelect }) {
  // Filter out empty sectors
  const validSectors = Object.keys(sectorMap).filter(
    (sec) => Array.isArray(sectorMap[sec]) && sectorMap[sec].length > 0
  );

  const initialSector = validSectors.find((sec) =>
    sectorMap[sec].some((stk) => (typeof stk === "string" ? stk : stk.symbol) === selectedSymbol)
  ) || validSectors[0] || "Banks";

  const [currentSector, setCurrentSector] = useState(initialSector);

  // Get stock items for current sector sorted by rank score
  const getSectorStocks = (sec) => {
    const raw = sectorMap[sec] || [];
    return [...raw].sort((a, b) => (b.score ?? 0) - (a.score ?? 0));
  };

  const currentStocks = getSectorStocks(currentSector);
  const currentSymbol = selectedSymbol || (currentStocks[0]?.symbol ?? currentStocks[0] ?? "COMB");

  // Handle Sector Change -> pre-select top ranked stock in new sector
  const handleSectorChange = (e) => {
    const newSector = e.target.value;
    setCurrentSector(newSector);

    const newStocks = getSectorStocks(newSector);
    if (newStocks.length > 0) {
      const topStockSymbol = typeof newStocks[0] === "string" ? newStocks[0] : newStocks[0].symbol;
      onSelect(topStockSymbol);
    }
  };

  // Handle Stock Change
  const handleStockChange = (e) => {
    onSelect(e.target.value);
  };

  return (
    <div className="sector-stock-selector-container">
      <div className="selector-group">
        <label className="selector-label">GICS Sector</label>
        <select value={currentSector} onChange={handleSectorChange} className="custom-select">
          {validSectors.map((sec) => (
            <option key={sec} value={sec}>
              {sec} ({sectorMap[sec].length})
            </option>
          ))}
        </select>
      </div>

      <div className="selector-group">
        <label className="selector-label">Representative Stock</label>
        <select value={currentSymbol} onChange={handleStockChange} className="custom-select">
          {currentStocks.map((item) => {
            const sym = typeof item === "string" ? item : item.symbol;
            const name = typeof item === "object" && item.name ? ` — ${item.name}` : "";
            const isTop = typeof item === "object" && item.score >= 90 ? " ★" : "";
            return (
              <option key={sym} value={sym}>
                {sym}{name}{isTop}
              </option>
            );
          })}
        </select>
      </div>

      <div className="selected-stock-badge">
        <span>Active Security:</span>
        <strong>{currentSymbol}</strong>
      </div>
    </div>
  );
}
