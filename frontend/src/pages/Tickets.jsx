import { Eye, Pencil, Plus, Search, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getUsers } from "../api/auth";
import { deleteTicket, getTickets } from "../api/tickets";
import Badge from "../components/Badge";
import { useAuth } from "../context/AuthContext";

const initialFilters = { status: "", priority: "", agent_id: "", search: "" };

export default function Tickets() {
  const { isManager } = useAuth();
  const [tickets, setTickets] = useState([]);
  const [agents, setAgents] = useState([]);
  const [filters, setFilters] = useState(initialFilters);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadTickets = useCallback(async () => {
    setLoading(true);
    const params = Object.fromEntries(Object.entries(filters).filter(([, value]) => value));
    try {
      setTickets(await getTickets(params));
      setError("");
    } catch {
      setError("Tickets could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    const timer = setTimeout(loadTickets, 200);
    return () => clearTimeout(timer);
  }, [loadTickets]);

  useEffect(() => {
    if (!isManager) return;
    getUsers()
      .then((users) => setAgents(users.filter((user) => user.role === "agent")))
      .catch(() => setError("Agent filter options could not be loaded."));
  }, [isManager]);

  const remove = async (ticket) => {
    if (!window.confirm(`Delete ticket #${ticket.id}?`)) return;
    try {
      await deleteTicket(ticket.id);
      await loadTickets();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Ticket could not be deleted.");
    }
  };

  const setFilter = (name, value) => setFilters((current) => ({ ...current, [name]: value }));

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Tickets</h1>
          <p className="mt-1 text-sm text-slate-500">Track requests from intake through resolution.</p>
        </div>
        <Link className="btn-primary" to="/tickets/new"><Plus size={17} /> New ticket</Link>
      </div>
      <div className="card mt-6">
        <div className="flex flex-wrap gap-3">
          <label className="relative block min-w-64 flex-1" htmlFor="ticket-search">
            <span className="sr-only">Search tickets</span>
            <Search className="absolute left-3 top-2.5 text-slate-400" size={17} />
            <input id="ticket-search" className="input pl-9" placeholder="Search title, description, category, or customer" value={filters.search} onChange={(event) => setFilter("search", event.target.value)} />
          </label>
          <select aria-label="Filter by status" className="input max-w-48" value={filters.status} onChange={(event) => setFilter("status", event.target.value)}>
            <option value="">All statuses</option>
            {["Open", "In Progress", "Resolved", "Closed"].map((value) => <option key={value}>{value}</option>)}
          </select>
          <select aria-label="Filter by priority" className="input max-w-48" value={filters.priority} onChange={(event) => setFilter("priority", event.target.value)}>
            <option value="">All priorities</option>
            {["Low", "Medium", "High", "Critical"].map((value) => <option key={value}>{value}</option>)}
          </select>
          {isManager && (
            <select aria-label="Filter by assigned agent" className="input max-w-52" value={filters.agent_id} onChange={(event) => setFilter("agent_id", event.target.value)}>
              <option value="">All agents</option>
              {agents.map((agent) => <option key={agent.id} value={agent.id}>{agent.name}</option>)}
            </select>
          )}
        </div>
        {error && <p className="mt-4 text-sm text-rose-700">{error}</p>}
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left">
            <thead className="border-b border-slate-200 text-xs uppercase text-slate-400">
              <tr><th className="table-cell">Title</th><th className="table-cell">Customer</th><th className="table-cell">Status</th><th className="table-cell">Priority</th><th className="table-cell">Category</th><th className="table-cell">Assigned agent</th><th className="table-cell">Date created</th><th className="table-cell">Actions</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {tickets.map((ticket) => (
                <tr key={ticket.id}>
                  <td className="table-cell font-semibold text-slate-800">#{ticket.id} {ticket.title}</td>
                  <td className="table-cell">{ticket.customer.full_name}</td>
                  <td className="table-cell"><Badge>{ticket.status}</Badge></td>
                  <td className="table-cell"><Badge>{ticket.priority}</Badge></td>
                  <td className="table-cell">{ticket.category || ticket.ai_category || "General"}</td>
                  <td className="table-cell">{ticket.assigned_agent?.name || "Unassigned"}</td>
                  <td className="table-cell">{new Date(ticket.created_at).toLocaleDateString()}</td>
                  <td className="table-cell">
                    <div className="flex items-center gap-3">
                      <Link aria-label={`View ${ticket.title}`} className="text-blue-700 hover:text-blue-900" title="View ticket details" to={`/tickets/${ticket.id}`}><Eye size={16} /></Link>
                      <Link aria-label={`Edit ${ticket.title}`} className="text-blue-700 hover:text-blue-900" title="Edit ticket" to={`/tickets/${ticket.id}/edit`}><Pencil size={16} /></Link>
                      {isManager && <button aria-label={`Delete ${ticket.title}`} className="text-rose-600 hover:text-rose-800" title="Delete ticket" onClick={() => remove(ticket)}><Trash2 size={16} /></button>}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {loading && <p className="py-6 text-center text-sm text-slate-500">Loading tickets...</p>}
          {!loading && !tickets.length && <p className="py-6 text-center text-sm text-slate-500">No tickets match these filters.</p>}
        </div>
      </div>
    </div>
  );
}
