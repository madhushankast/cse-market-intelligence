import React, { useEffect, useRef, useState } from 'react';
import {
  createChart,
  LineSeries,
  LineStyle,
  ColorType,
  type IChartApi,
  type ISeriesApi,
  type Time,
} from 'lightweight-charts';
import type { PredictionPayload } from '../api';

interface ForecastChartProps {
  prediction: PredictionPayload;
}

export const ForecastChart: React.FC<ForecastChartProps> = ({ prediction }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  const [hoverInfo, setHoverInfo] = useState<{
    date?: string;
    close?: number;
    p50?: number;
    p90?: number;
    p10?: number;
  }>({});

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Initialize chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0d1117' },
        textColor: '#8b949e',
        fontSize: 12,
        fontFamily: 'JetBrains Mono, monospace',
      },
      grid: {
        vertLines: { color: '#21262d' },
        horzLines: { color: '#21262d' },
      },
      crosshair: {
        vertLine: {
          color: '#58a6ff',
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: '#21262d',
        },
        horzLine: {
          color: '#58a6ff',
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: '#21262d',
        },
      },
      rightPriceScale: {
        borderColor: '#30363d',
        scaleMargins: {
          top: 0.15,
          bottom: 0.15,
        },
      },
      timeScale: {
        borderColor: '#30363d',
        timeVisible: true,
        secondsVisible: false,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
    });

    chartRef.current = chart;

    // 1. Historical Series (Solid Brand Blue)
    const histSeries: ISeriesApi<'Line'> = chart.addSeries(LineSeries, {
      color: '#58a6ff',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      title: 'Historical',
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.01,
      },
    });

    // 2. P90 Upside Ceiling (Dashed Emerald Green)
    const p90Series: ISeriesApi<'Line'> = chart.addSeries(LineSeries, {
      color: '#3fb950',
      lineWidth: 2,
      lineStyle: LineStyle.Dashed,
      title: 'P90 Ceiling',
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.01,
      },
    });

    // 3. P50 Expected Median (Solid Sky Blue)
    const p50Series: ISeriesApi<'Line'> = chart.addSeries(LineSeries, {
      color: '#38bdf8',
      lineWidth: 3,
      lineStyle: LineStyle.Solid,
      title: 'P50 Expected',
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.01,
      },
    });

    // 4. P10 Downside Floor (Dashed Coral Red)
    const p10Series: ISeriesApi<'Line'> = chart.addSeries(LineSeries, {
      color: '#f85149',
      lineWidth: 2,
      lineStyle: LineStyle.Dashed,
      title: 'P10 Floor',
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.01,
      },
    });

    // Populate Historical Data
    if (prediction.historical_series && prediction.historical_series.length > 0) {
      const histData = prediction.historical_series.map((bar) => ({
        time: bar.date as Time,
        value: bar.close,
      }));
      histSeries.setData(histData);
    } else {
      histSeries.setData([
        { time: prediction.as_of_date as Time, value: prediction.current_price },
      ]);
    }

    // Anchor forecast cone at as_of_date with current_price
    const anchorPoint = {
      time: prediction.as_of_date as Time,
      value: prediction.current_price,
    };

    if (prediction.cone_trajectory && prediction.cone_trajectory.length > 0) {
      const p90Data = [
        anchorPoint,
        ...prediction.cone_trajectory.map((p) => ({
          time: p.date as Time,
          value: p.price_p90,
        })),
      ];

      const p50Data = [
        anchorPoint,
        ...prediction.cone_trajectory.map((p) => ({
          time: p.date as Time,
          value: p.price_p50,
        })),
      ];

      const p10Data = [
        anchorPoint,
        ...prediction.cone_trajectory.map((p) => ({
          time: p.date as Time,
          value: p.price_p10,
        })),
      ];

      p90Series.setData(p90Data);
      p50Series.setData(p50Data);
      p10Series.setData(p10Data);
    }

    // Crosshair move handler
    chart.subscribeCrosshairMove((param) => {
      if (!param.time || !param.point) {
        setHoverInfo({});
        return;
      }

      const dateStr = param.time.toString();
      const histVal = param.seriesData.get(histSeries) as { value?: number } | undefined;
      const p50Val = param.seriesData.get(p50Series) as { value?: number } | undefined;
      const p90Val = param.seriesData.get(p90Series) as { value?: number } | undefined;
      const p10Val = param.seriesData.get(p10Series) as { value?: number } | undefined;

      setHoverInfo({
        date: dateStr,
        close: histVal?.value,
        p50: p50Val?.value,
        p90: p90Val?.value,
        p10: p10Val?.value,
      });
    });

    chart.timeScale().fitContent();

    // Resize observer
    const resizeObserver = new ResizeObserver((entries) => {
      if (entries.length === 0 || !entries[0].contentRect) return;
      const { width, height } = entries[0].contentRect;
      chart.applyOptions({ width, height });
    });

    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, [prediction]);

  return (
    <div className="flex flex-col h-full w-full bg-surface border border-borderline rounded-xl overflow-hidden shadow-2xl">
      {/* Chart Top Bar & Legend */}
      <div className="flex flex-wrap items-center justify-between px-5 py-3 border-b border-borderline bg-surface/80 backdrop-blur gap-3">
        <div className="flex items-center space-x-3">
          <span className="text-xs font-mono uppercase tracking-wider text-muted font-semibold">
            Forecast Cone
          </span>
          <span className="text-xs px-2 py-0.5 rounded bg-brand/10 text-brand border border-brand/20 font-mono">
            30-Trading-Day Horizon
          </span>
        </div>

        {/* Dynamic Legend / Cursor Tooltip */}
        <div className="flex flex-wrap items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-0.5 bg-[#58a6ff] rounded-full inline-block" />
            <span className="text-muted">Hist Close:</span>
            <span className="text-gray-200 font-semibold">
              {hoverInfo.close !== undefined
                ? `LKR ${hoverInfo.close.toFixed(2)}`
                : `LKR ${prediction.current_price.toFixed(2)}`}
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-0.5 bg-[#3fb950] border-t border-dashed border-[#3fb950] inline-block" />
            <span className="text-muted">P90 Ceiling:</span>
            <span className="text-bullish font-semibold">
              {hoverInfo.p90 !== undefined
                ? `LKR ${hoverInfo.p90.toFixed(2)}`
                : `LKR ${prediction.target_prices.price_p90.toFixed(2)}`}
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-1 bg-[#38bdf8] rounded-full inline-block" />
            <span className="text-muted">P50 Median:</span>
            <span className="text-[#38bdf8] font-bold">
              {hoverInfo.p50 !== undefined
                ? `LKR ${hoverInfo.p50.toFixed(2)}`
                : `LKR ${prediction.target_prices.price_p50.toFixed(2)}`}
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-0.5 bg-[#f85149] border-t border-dashed border-[#f85149] inline-block" />
            <span className="text-muted">P10 Floor (VaR 90%):</span>
            <span className="text-bearish font-semibold">
              {hoverInfo.p10 !== undefined
                ? `LKR ${hoverInfo.p10.toFixed(2)}`
                : `LKR ${prediction.target_prices.price_p10.toFixed(2)}`}
            </span>
          </div>
        </div>
      </div>

      {/* Chart Canvas */}
      <div
        ref={chartContainerRef}
        className="w-full flex-1 min-h-[440px] relative"
      />
    </div>
  );
};
