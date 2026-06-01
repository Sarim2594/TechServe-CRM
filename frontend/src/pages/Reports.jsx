import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getReportSummary } from "../api/reports";
import Badge from "../components/Badge";
import StatCard from "../components/StatCard";

export default function Reports() {
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    getReportSummary()
      .then((data) => {
        if (active) {
          setReport(data);
          setError("");
        }
      })
      .catch(() => {
        if (active) setError("Report data could not be loaded.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold text-slate-900">Reports</h1>
      <p className="mt-1 text-sm text-slate-500">Manager insights for ownership, service demand, and resolution trends.</p>
      {error && <p className="mt-5 rounded-lg bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
      {loading && <p className="mt-6 text-sm text-slate-500">Loading report data...</p>}
      {!loading && report && (
        <>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <StatCard label="Total tickets" value={report.total_tickets} />
            <StatCard label="Total customers" value={report.total_customers} />
            <StatCard label="Resolved tickets" value={report.resolved_tickets} tone="emerald" />
            <StatCard label="Critical tickets" value={report.critical_tickets} tone="rose" />
            <StatCard label="Average resolution" value={report.average_resolution_time_hours == null ? "No data" : `${report.average_resolution_time_hours} hrs`} tone="amber" />
          </div>
          <div className="mt-6 grid gap-6 lg:grid-cols-2 xl:grid-cols-4">
            <ReportCard title="Tickets by category" values={report.ticket_count_by_category} />
            <ReportCard title="Tickets by status" values={report.ticket_count_by_status} />
            <ReportCard title="Tickets by priority" values={report.ticket_count_by_priority} />
            <ReportCard title="Tickets by agent" values={report.ticket_count_by_agent} />
          </div>
          <RecentResolvedTickets tickets={report.recent_resolved_tickets} />
        </>
      )}
    </div>
  );
}

function ReportCard({ title, values }) {
  const entries = Object.entries(values || {});

  return (
    <section className="card">
      <h2 className="font-bold text-slate-900">{title}</h2>
      <div className="mt-4 space-y-3">
        {entries.length ? entries.map(([label, count]) => (
          <div className="flex justify-between gap-3 text-sm" key={label}>
            <span className="text-slate-600">{label}</span>
            <strong className="text-slate-800">{count}</strong>
          </div>
        )) : <p className="text-sm text-slate-500">No data yet.</p>}
      </div>
    </section>
  );
}

function RecentResolvedTickets({ tickets }) {
  return (
    <section className="card mt-6">
      <h2 className="font-bold text-slate-900">Recent resolved tickets</h2>
      <div className="mt-4 overflow-x-auto">
        {tickets.length ? (
          <table className="w-full text-left">
            <thead className="border-b border-slate-200 text-xs uppercase text-slate-400">
              <tr><th className="table-cell">Ticket</th><th className="table-cell">Customer</th><th className="table-cell">Priority</th><th className="table-cell">Category</th><th className="table-cell">Assigned agent</th><th className="table-cell">Resolved</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {tickets.map((ticket) => (
                <tr key={ticket.id}>
                  <td className="table-cell"><Link className="font-semibold text-blue-700 hover:text-blue-900" to={`/tickets/${ticket.id}`}>#{ticket.id} {ticket.title}</Link></td>
                  <td className="table-cell">{ticket.customer_name}</td>
                  <td className="table-cell"><Badge>{ticket.priority}</Badge></td>
                  <td className="table-cell">{ticket.category}</td>
                  <td className="table-cell">{ticket.assigned_agent_name || "Unassigned"}</td>
                  <td className="table-cell">{new Date(ticket.resolved_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <p className="text-sm text-slate-500">No resolved tickets yet.</p>}
      </div>
    </section>
  );
}
