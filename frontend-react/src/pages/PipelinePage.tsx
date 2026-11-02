import React, { useEffect, useState } from 'react';
import {
  fetchPipelineStatus,
  triggerPipeline,
  type PipelineStatusData,
  type EquityDataStatus,
} from '../api';
import {
  Database,
  RefreshCw,
  Play,
  Calendar,
  CheckCircle2,
  AlertCircle,
  Clock,
  Search,
  ArrowUpDown,
  Layers,
  Activity,
} from 'lucide-react';

export const PipelinePage: React.FC = () => {
  const [statusData, setStatusData] = useState<PipelineStatusData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [triggering, setTriggering] = useState<boolean>(false);
  const [syncingSymbol, setSyncingSymbol] = useState<string | null>(null);
  const [selectedScope, setSelectedScope] = useState<string>('ALL');
  const [retrainModels, setRetrainModels] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sortField, setSortField] = useState<keyof EquityDataStatus>('latest_date');
  const [sortAsc, setSortAsc] = useState<boolean>(false);
  const [bannerMessage, setBannerMessage] = useState<{
    type: 'success' | 'error';
    text: string;
  } | null>(null);

  const loadStatus = () => {
    setLoading(true);
    fetchPipelineStatus()
      .then((data) => {
        setStatusData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch pipeline status:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleRunPipeline = async (overrideSymbol?: string) => {
    const targetSyms = overrideSymbol
      ? [overrideSymbol]
      : selectedScope === 'ALL'
      ? null
      : [selectedScope];

    if (overrideSymbol) {
      setSyncingSymbol(overrideSymbol);
    } else {
      setTriggering(true);
    }
    setBannerMessage(null);

    try {
      const res = await triggerPipeline({
        symbols: targetSyms,
        sync_live: true,
        retrain: retrainModels,
      });

      const refreshed = await fetchPipelineStatus();
      setStatusData(refreshed);

      const latestDate =
        refreshed.summary.latest_market_date ||
        refreshed.summary.latest_equity_date ||
        'latest session';
      const scopeLabel = targetSyms ? targetSyms.join(', ') : 'All 26 CSE Equities + ASPI';

      setBannerMessage({
        type: 'success',
        text: `Pipeline finished in ${res.result.duration_seconds}s for ${scopeLabel} (${res.result.predictions_stored} forecasts refreshed${
          res.result.models_retrained > 0 ? `, ${res.result.models_retrained} models retrained` : ''
        }). Data updated through ${latestDate}.`,
      });
    } catch (err: any) {
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        'Unable to trigger live CSE sync. Ensure the backend service is awake.';
      setBannerMessage({
        type: 'error',
        text: `Pipeline execution error: ${detail}`,
      });
    } finally {
      setTriggering(false);
      setSyncingSymbol(null);
    }
  };

  const handleSort = (field: keyof EquityDataStatus) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const equities = statusData?.equities || [];
  const filteredEquities = equities.filter(
    (e) =>
      e.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.sector.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedEquities = [...filteredEquities].sort((a, b) => {
    const valA = a[sortField];
    const valB = b[sortField];
    if (typeof valA === 'number' && typeof valB === 'number') {
      return sortAsc ? valA - valB : valB - valA;
    }
    const strA = String(valA ?? '');
    const strB = String(valB ?? '');
    return sortAsc ? strA.localeCompare(strB) : strB.localeCompare(strA);
  });

  return (
    <div className="flex-1 max-w-[1600px] w-full mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6 flex flex-col gap-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 text-xs font-mono text-brand mb-1">
            <Database className="w-4 h-4 shrink-0" />
            <span>DATA FRESHNESS & MANUAL PIPELINE CONSOLE</span>
          </div>
          <h1 className="text-xl sm:text-3xl font-bold text-gray-100 font-sans tracking-tight">
            CSE Market Data Sync & MLOps Pipeline
          </h1>
          <p className="text-xs sm:text-sm text-gray-400 mt-1 font-sans">
            Inspect the exact date each equity and benchmark dataset was last updated, or manually trigger live CSE ingestion and LightGBM forecast regeneration.
          </p>
        </div>

        <button
          onClick={loadStatus}
          disabled={loading || triggering}
          className="self-start sm:self-center flex items-center gap-2 px-3.5 py-2 rounded-lg bg-subsurface hover:bg-borderline border border-borderline text-xs font-mono text-muted hover:text-gray-100 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-brand' : ''}`} />
          <span>Refresh Status</span>
        </button>
      </div>

      {/* Status Notification Banner */}
      {bannerMessage && (
        <div
          className={`p-4 rounded-xl border flex items-start gap-3 text-xs font-mono ${
            bannerMessage.type === 'success'
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
              : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
          }`}
        >
          {bannerMessage.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          )}
          <div className="flex-1 leading-relaxed">{bannerMessage.text}</div>
        </div>
      )}

      {/* 1. Data Freshness KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="p-4 bg-surface border border-borderline rounded-xl flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-mono text-muted uppercase">
            <span>Latest Equity Date</span>
            <Calendar className="w-4 h-4 text-brand" />
          </div>
          <div className="mt-2">
            <div className="text-xl sm:text-2xl font-bold font-mono text-gray-100">
              {statusData?.summary.latest_equity_date || '—'}
            </div>
            <div className="text-[11px] font-mono text-muted mt-1">
              Oldest active ticker: {statusData?.summary.oldest_equity_date || '—'}
            </div>
          </div>
        </div>

        <div className="p-4 bg-surface border border-borderline rounded-xl flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-mono text-muted uppercase">
            <span>ASPI Benchmark Date</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2">
            <div className="text-xl sm:text-2xl font-bold font-mono text-emerald-400">
              {statusData?.aspi.latest_date || '—'}
            </div>
            <div className="text-[11px] font-mono text-muted mt-1">
              {statusData?.aspi.latest_close
                ? `Index: ${statusData.aspi.latest_close.toLocaleString()} (${statusData.aspi.total_rows.toLocaleString()} days)`
                : 'Official CSE Benchmark'}
            </div>
          </div>
        </div>

        <div className="p-4 bg-surface border border-borderline rounded-xl flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-mono text-muted uppercase">
            <span>Database Storage</span>
            <Database className="w-4 h-4 text-brand" />
          </div>
          <div className="mt-2">
            <div className="text-xl sm:text-2xl font-bold font-mono text-gray-100">
              {statusData ? statusData.summary.total_bars.toLocaleString() : '—'}
            </div>
            <div className="text-[11px] font-mono text-muted mt-1">
              {statusData?.summary.database_engine || 'Database'} •{' '}
              {statusData?.summary.db_predictions_count ?? 26} Forecasts Stored
            </div>
          </div>
        </div>

        <div className="p-4 bg-surface border border-borderline rounded-xl flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-mono text-muted uppercase">
            <span>Trained Ensembles</span>
            <Layers className="w-4 h-4 text-brand" />
          </div>
          <div className="mt-2">
            <div className="text-xl sm:text-2xl font-bold font-mono text-brand">
              {statusData
                ? `${statusData.summary.trained_models_count} / ${statusData.summary.total_equities}`
                : '26 / 26'}
            </div>
            <div className="text-[11px] font-mono text-muted mt-1">
              P10, P50, P90 LightGBM models ready
            </div>
          </div>
        </div>
      </div>

      {/* 2. Manual Pipeline Execution Console */}
      <div className="p-4 sm:p-6 bg-surface border border-borderline rounded-xl flex flex-col lg:flex-row lg:items-end justify-between gap-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-end gap-3 sm:gap-4 flex-1">
          {/* Target Scope Selector */}
          <div className="flex flex-col flex-1 max-w-md">
            <label className="text-[10px] font-mono uppercase tracking-wider text-muted mb-1.5">
              1. Select Target Equity Scope
            </label>
            <select
              value={selectedScope}
              onChange={(e) => setSelectedScope(e.target.value)}
              disabled={triggering}
              className="bg-subsurface border border-borderline text-gray-100 text-xs sm:text-sm font-mono rounded-lg px-3 py-2.5 focus:outline-none focus:border-brand transition-colors"
            >
              <option value="ALL">All 26 CSE Equities + ASPI Benchmark</option>
              {equities.map((eq) => (
                <option key={eq.symbol} value={eq.symbol}>
                  {eq.code} • {eq.name} (Last: {eq.latest_date})
                </option>
              ))}
            </select>
          </div>

          {/* Retrain Checkbox Toggle */}
          <label className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-lg bg-subsurface border border-borderline cursor-pointer select-none text-xs font-mono text-gray-200">
            <input
              type="checkbox"
              checked={retrainModels}
              onChange={(e) => setRetrainModels(e.target.checked)}
              disabled={triggering}
              className="rounded border-borderline text-brand focus:ring-0 accent-[#58a6ff] w-4 h-4"
            />
            <span>Retrain LightGBM Models on Expanded History</span>
          </label>
        </div>

        {/* Trigger Action Button */}
        <button
          onClick={() => handleRunPipeline()}
          disabled={triggering || syncingSymbol !== null}
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-brand hover:bg-sky-400 disabled:opacity-60 text-gray-950 font-mono font-bold text-xs sm:text-sm transition-colors cursor-pointer shrink-0"
        >
          {triggering ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Syncing CSE API & Running Pipeline...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Fetch Live Data & Run Pipeline</span>
            </>
          )}
        </button>
      </div>

      {/* 3. Equity Data Freshness & Last Updated Date Table */}
      <div className="bg-surface border border-borderline rounded-xl p-4 sm:p-5 flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-bold text-gray-100">
              Dataset Coverage & Last Updated Dates (26 CSE Equities)
            </h2>
            <p className="text-xs text-muted font-sans">
              Exact historical date boundaries and latest closing session synced for each equity. Click "Sync" on any row to fetch that stock immediately.
            </p>
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter ticker or sector..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-subsurface border border-borderline rounded-lg pl-9 pr-3 py-1.5 text-xs font-mono text-gray-100 placeholder-muted focus:outline-none focus:border-brand transition-colors"
            />
          </div>
        </div>

        <div className="overflow-x-auto rounded-xl border border-borderline">
          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="bg-subsurface/80 text-muted uppercase text-[10px] tracking-wider border-b border-borderline select-none">
                <th
                  onClick={() => handleSort('symbol')}
                  className="py-3 px-4 cursor-pointer hover:text-gray-200"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Equity</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('sector')}
                  className="py-3 px-4 cursor-pointer hover:text-gray-200"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Sector</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('min_date')}
                  className="py-3 px-4 cursor-pointer hover:text-gray-200"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Start Date</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('latest_date')}
                  className="py-3 px-4 cursor-pointer hover:text-gray-200"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Last Updated Date</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('total_rows')}
                  className="py-3 px-4 cursor-pointer hover:text-gray-200"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Sessions</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('latest_close')}
                  className="py-3 px-4 cursor-pointer hover:text-gray-200"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Latest Close</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-4">Model Status</th>
                <th className="py-3 px-4 text-right">Manual Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-borderline">
              {sortedEquities.map((item) => {
                const isRowSyncing = syncingSymbol === item.symbol;
                return (
                  <tr key={item.symbol} className="hover:bg-subsurface/40 transition-colors">
                    <td className="py-2.5 px-4 font-bold text-gray-100">
                      {item.code}
                      <span className="text-[10px] text-muted block font-normal truncate max-w-[180px]">
                        {item.name}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-muted">{item.sector}</td>
                    <td className="py-2.5 px-4 text-gray-400">{item.min_date}</td>
                    <td className="py-2.5 px-4">
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-brand/10 border border-brand/25 text-brand font-bold">
                        <Calendar className="w-3 h-3" />
                        {item.latest_date}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-gray-300">
                      {item.total_rows.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-4 font-semibold text-gray-100">
                      LKR {item.latest_close.toFixed(2)}
                    </td>
                    <td className="py-2.5 px-4">
                      {item.model_trained ? (
                        <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Ready
                        </span>
                      ) : (
                        <span className="text-amber-400">On-the-fly</span>
                      )}
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <button
                        onClick={() => handleRunPipeline(item.symbol)}
                        disabled={triggering || syncingSymbol !== null}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-subsurface hover:bg-borderline border border-borderline text-gray-200 hover:text-brand disabled:opacity-50 transition-colors text-[11px]"
                      >
                        <RefreshCw
                          className={`w-3 h-3 ${isRowSyncing ? 'animate-spin text-brand' : ''}`}
                        />
                        <span>{isRowSyncing ? 'Syncing...' : 'Sync Now'}</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Pipeline Execution History Log */}
      {statusData?.recent_runs && statusData.recent_runs.length > 0 && (
        <div className="bg-surface border border-borderline rounded-xl p-4 sm:p-5 flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-brand" />
            <h3 className="text-sm font-bold text-gray-100 font-mono uppercase tracking-wider">
              Recent Pipeline Execution Audit Log
            </h3>
          </div>

          <div className="overflow-x-auto rounded-xl border border-borderline">
            <table className="w-full text-left text-xs font-mono border-collapse">
              <thead>
                <tr className="bg-subsurface/80 text-muted uppercase text-[10px] tracking-wider border-b border-borderline">
                  <th className="py-2.5 px-4">Run Date</th>
                  <th className="py-2.5 px-4">Job Name</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4">Bars Synced</th>
                  <th className="py-2.5 px-4">Models Retrained</th>
                  <th className="py-2.5 px-4">Duration</th>
                  <th className="py-2.5 px-4">Summary</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-borderline">
                {statusData.recent_runs.map((run) => (
                  <tr key={run.id} className="hover:bg-subsurface/40">
                    <td className="py-2.5 px-4 text-gray-300">{run.run_date}</td>
                    <td className="py-2.5 px-4 font-semibold text-gray-200">{run.job_name}</td>
                    <td className="py-2.5 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          run.status === 'SUCCESS'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                        }`}
                      >
                        {run.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-gray-300">
                      {run.records_ingested.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-4 text-gray-300">{run.models_retrained}</td>
                    <td className="py-2.5 px-4 text-muted">{run.duration_seconds.toFixed(1)}s</td>
                    <td className="py-2.5 px-4 text-gray-400 max-w-md truncate">{run.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

