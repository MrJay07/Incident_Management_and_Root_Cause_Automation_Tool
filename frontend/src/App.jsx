import { useCallback, useEffect, useMemo, useState } from 'react'

const API_BASE = '/api'

const levelColor = {
  WARNING: 'bg-amber-500/20 text-amber-300',
  ERROR: 'bg-orange-500/20 text-orange-300',
  CRITICAL: 'bg-rose-500/20 text-rose-300',
}

function formatDate(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

function StatCard({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-100">{value}</p>
    </div>
  )
}

function App() {
  const [incidents, setIncidents] = useState([])
  const [alerts, setAlerts] = useState([])
  const [metrics, setMetrics] = useState(null)
  const [rcaReports, setRcaReports] = useState([])
  const [statusMessage, setStatusMessage] = useState('Loading...')

  const refresh = useCallback(async () => {
    try {
      const [incidentRes, alertRes, metricRes, rcaRes] = await Promise.all([
        fetch(`${API_BASE}/incidents`),
        fetch(`${API_BASE}/alerts/history`),
        fetch(`${API_BASE}/incidents/dashboard/metrics`),
        fetch(`${API_BASE}/rca`),
      ])

      const [incidentData, alertData, metricData, rcaData] = await Promise.all([
        incidentRes.json(),
        alertRes.json(),
        metricRes.json(),
        rcaRes.json(),
      ])

      setIncidents(Array.isArray(incidentData) ? incidentData : [])
      setAlerts(Array.isArray(alertData) ? alertData : [])
      setMetrics(metricData || null)
      setRcaReports(Array.isArray(rcaData) ? rcaData : [])
      setStatusMessage(`Updated ${new Date().toLocaleTimeString()}`)
    } catch {
      setStatusMessage('Backend unavailable. Start API and ingest sample logs.')
    }
  }, [])

  useEffect(() => {
    const bootstrap = setTimeout(() => refresh(), 0)
    const timer = setInterval(refresh, 10000)
    return () => {
      clearTimeout(bootstrap)
      clearInterval(timer)
    }
  }, [refresh])

  const openIncidents = useMemo(
    () => incidents.filter((incident) => incident.status !== 'Resolved').length,
    [incidents],
  )

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl space-y-6 px-4 py-8">
        <header className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold">Incident Management & RCA Dashboard</h1>
            <p className="text-sm text-slate-400">{statusMessage}</p>
          </div>
          <button
            className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-slate-950 hover:bg-sky-400"
            onClick={refresh}
          >
            Refresh
          </button>
        </header>

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total incidents" value={incidents.length} />
          <StatCard label="Open incidents" value={openIncidents} />
          <StatCard label="Alerts triggered" value={alerts.length} />
          <StatCard label="Avg recovery (min)" value={metrics?.average_recovery_minutes ?? 0} />
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
            <h2 className="mb-3 text-lg font-semibold">Incident Feed</h2>
            <div className="max-h-[350px] space-y-3 overflow-auto">
              {incidents.map((incident) => (
                <article key={incident.id} className="rounded-lg border border-slate-800 bg-slate-900 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="font-medium">{incident.title}</p>
                    <span className={`rounded px-2 py-0.5 text-xs ${levelColor[incident.severity] || 'bg-slate-700 text-slate-300'}`}>
                      {incident.severity}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-slate-300">{incident.description}</p>
                  <p className="mt-2 text-xs text-slate-400">
                    Service: {incident.service} • Status: {incident.status} • Last seen: {formatDate(incident.last_seen)}
                  </p>
                </article>
              ))}
              {incidents.length === 0 && <p className="text-sm text-slate-400">No incidents yet.</p>}
            </div>
          </div>

          <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
            <h2 className="mb-3 text-lg font-semibold">Real-time Activity Feed</h2>
            <div className="max-h-[350px] space-y-3 overflow-auto">
              {metrics?.recent_activity?.map((activity, idx) => (
                <article key={`${activity.incident_id}-${idx}`} className="rounded-lg border border-slate-800 bg-slate-900 p-3">
                  <p className="font-medium">RCA for incident #{activity.incident_id}</p>
                  <p className="mt-1 text-sm text-slate-300">{activity.summary}</p>
                  <p className="mt-2 text-xs text-slate-400">{formatDate(activity.created_at)}</p>
                </article>
              ))}
              {(!metrics?.recent_activity || metrics.recent_activity.length === 0) && (
                <p className="text-sm text-slate-400">Run RCA simulation to populate activity feed.</p>
              )}
            </div>
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
            <h2 className="mb-3 text-lg font-semibold">Alert History</h2>
            <div className="max-h-[260px] overflow-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-slate-400">
                  <tr>
                    <th className="pb-2">Incident</th>
                    <th className="pb-2">Recipient</th>
                    <th className="pb-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map((alert) => (
                    <tr key={alert.id} className="border-t border-slate-800">
                      <td className="py-2">#{alert.incident_id}</td>
                      <td className="py-2">{alert.recipient}</td>
                      <td className="py-2">{alert.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
            <h2 className="mb-3 text-lg font-semibold">RCA Reports</h2>
            <div className="max-h-[260px] space-y-3 overflow-auto">
              {rcaReports.map((report) => (
                <article key={report.id} className="rounded-lg border border-slate-800 bg-slate-900 p-3">
                  <p className="font-medium">Incident #{report.incident_id}</p>
                  <p className="mt-1 text-sm text-slate-300">Bottleneck: {report.bottleneck}</p>
                  <p className="mt-1 text-xs text-slate-400">{report.summary}</p>
                </article>
              ))}
              {rcaReports.length === 0 && <p className="text-sm text-slate-400">No RCA reports generated.</p>}
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}

export default App
