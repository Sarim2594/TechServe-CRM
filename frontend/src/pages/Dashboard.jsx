import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getDashboardStats } from "../api/dashboard";
import Badge from "../components/Badge";
import StatCard from "../components/StatCard";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user, isManager } = useAuth();
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    getDashboardStats()
      .then((data) => {
        if (active) {
          setStats(data);
          setError("");
        }
      })
      .catch(() => {
        if (active) setError("Dashboard metrics could not be loaded.");
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
      <div>
        <p className="text-sm font-semibold text-blue-600">Overview</p>
        <h1 className="text-3xl font-bold text-slate-900">Welcome back, {user?.name}</h1>
        <p className="mt-1 text-sm text-slate-500">
          {isManager ? "A full view of your service operation." : "A focused view of your assigned service workload."}
        </p>
      </div>
      {error && <p className="mt-5 rounded-lg bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
      {loading && <p className="mt-6 text-sm text-slate-500">Loading dashboard metrics...</p>}
      {!loading && stats && (
        <>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <StatCard label="Total tickets" value={stats.total_tickets} />
            <StatCard label="Open tickets" value={stats.open_tickets} tone="amber" />
            <StatCard label="Resolved today" value={stats.resolved_today} tone="emerald" />
            <StatCard label="Critical tickets" value={stats.critical_tickets} tone="rose" />
            <StatCard label="Total customers" value={stats.total_customers} />
          </div>
          <div className="mt-6 grid gap-6 lg:grid-cols-3">
            <MetricList title="Tickets by status" values={stats.tickets_by_status} />
            <MetricList title="Tickets by priority" values={stats.tickets_by_priority} />
            <MetricList title="Tickets by category" values={stats.tickets_by_category} />
          </div>
          <WorkloadTable workloads={stats.agent_workloads} />
          <RecentTickets tickets={stats.recent_tickets} />
        </>
      )}
    </div>
  );
}

function MetricList({ title, values }) {
  const entries = Object.entries(values || {});
  const maxValue = Math.max(...entries.map(([, value]) => value), 1);

  return (
    <section className="card">
      <h2 className="font-bold text-slate-900">{title}</h2>
      <div className="mt-4 space-y-4">
        {entries.length ? entries.map(([label, value]) => (
          <div key={label}>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-600">{label}</span>
              <strong className="text-slate-800">{value}</strong>
            </div>
            <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-100">
              <div className="h-full rounded-full bg-blue-500" style={{ width: `${(value / maxValue) * 100}%` }} />
            </div>
          </div>
        )) : <p className="text-sm text-slate-500">No ticket data yet.</p>}
      </div>
    </section>
  );
}

function WorkloadTable({ workloads }) {
  return (
    <section className="card mt-6">
      <h2 className="font-bold text-slate-900">Agent workloads</h2>
      <div className="mt-4 overflow-x-auto">
        {workloads.length ? (
          <table className="w-full text-left">
            <thead className="border-b border-slate-200 text-xs uppercase text-slate-400">
              <tr><th className="table-cell">Agent</th><th className="table-cell">Assigned</th><th className="table-cell">Open</th><th className="table-cell">In progress</th><th className="table-cell">Resolved</th><th className="table-cell">Critical</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {workloads.map((agent) => (
                <tr key={agent.agent_id}>
                  <td className="table-cell font-semibold text-slate-800">{agent.agent_name}</td>
                  <td className="table-cell">{agent.total_assigned_tickets}</td>
                  <td className="table-cell">{agent.open_assigned_tickets}</td>
                  <td className="table-cell">{agent.in_progress_assigned_tickets}</td>
                  <td className="table-cell">{agent.resolved_assigned_tickets}</td>
                  <td className="table-cell">{agent.critical_assigned_tickets}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <p className="text-sm text-slate-500">No agent workload data yet.</p>}
      </div>
    </section>
  );
}

function RecentTickets({ tickets }) {
  return (
    <section className="card mt-6">
      <h2 className="font-bold text-slate-900">Recent tickets</h2>
      <div className="mt-4 overflow-x-auto">
        {tickets.length ? (
          <table className="w-full text-left">
            <thead className="border-b border-slate-200 text-xs uppercase text-slate-400">
              <tr><th className="table-cell">Ticket</th><th className="table-cell">Customer</th><th className="table-cell">Status</th><th className="table-cell">Priority</th><th className="table-cell">Category</th><th className="table-cell">Assigned agent</th><th className="table-cell">Created</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {tickets.map((ticket) => (
                <tr key={ticket.id}>
                  <td className="table-cell"><Link className="font-semibold text-blue-700 hover:text-blue-900" to={`/tickets/${ticket.id}`}>#{ticket.id} {ticket.title}</Link></td>
                  <td className="table-cell">{ticket.customer_name}</td>
                  <td className="table-cell"><Badge>{ticket.status}</Badge></td>
                  <td className="table-cell"><Badge>{ticket.priority}</Badge></td>
                  <td className="table-cell">{ticket.category}</td>
                  <td className="table-cell">{ticket.assigned_agent_name || "Unassigned"}</td>
                  <td className="table-cell">{new Date(ticket.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <p className="text-sm text-slate-500">No recent tickets yet.</p>}
      </div>
    </section>
  );
}
