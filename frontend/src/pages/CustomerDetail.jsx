import { Edit3, Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import { getCustomer } from "../api/customers";
import Badge from "../components/Badge";

export default function CustomerDetail() {
  const { id } = useParams();
  const location = useLocation();
  const [customer, setCustomer] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getCustomer(id)
      .then(setCustomer)
      .catch(() => setError("Customer details could not be loaded."));
  }, [id]);

  if (error) return <p className="rounded-lg bg-rose-50 p-3 text-rose-700">{error}</p>;
  if (!customer) return <p className="text-slate-500">Loading customer...</p>;

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-blue-600">{customer.company || "No company listed"}</p>
          <h1 className="text-3xl font-bold text-slate-900">{customer.full_name}</h1>
          <p className="mt-1 text-sm text-slate-500">{customer.email} | {customer.phone || "No phone listed"}</p>
        </div>
        <Link className="btn-secondary" to={`/customers/${id}/edit`}><Edit3 size={16} /> Edit profile</Link>
      </div>
      {location.state?.message && <p className="mt-4 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-700">{location.state.message}</p>}
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="card">
          <h2 className="font-bold text-slate-900">Customer details</h2>
          <dl className="mt-4 space-y-3 text-sm">
            <Detail label="Email" value={customer.email} />
            <Detail label="Phone" value={customer.phone || "Not provided"} />
            <Detail label="Company" value={customer.company || "Not provided"} />
            <Detail label="Assigned agent" value={customer.assigned_agent?.name || "Unassigned"} />
            <Detail label="Date added" value={new Date(customer.created_at).toLocaleDateString()} />
          </dl>
          <h3 className="mt-6 text-sm font-bold text-slate-900">Notes</h3>
          <p className="mt-2 whitespace-pre-wrap text-sm text-slate-600">{customer.notes || "No notes recorded."}</p>
        </div>
        <div className="card lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-slate-900">Ticket history</h2>
            <Link className="btn-primary" to={`/tickets/new?customer_id=${id}`}><Plus size={16} /> New ticket</Link>
          </div>
          <div className="mt-4 space-y-3">
            {customer.ticket_history.map((ticket) => (
              <Link className="block rounded-lg border border-slate-200 p-3 transition hover:border-blue-300" key={ticket.id} to={`/tickets/${ticket.id}`}>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-semibold text-slate-800">#{ticket.id} {ticket.title}</span>
                  <span className="flex gap-2"><Badge>{ticket.status}</Badge><Badge>{ticket.priority}</Badge></span>
                </div>
                <p className="mt-2 text-xs text-slate-400">{new Date(ticket.created_at).toLocaleString()}</p>
              </Link>
            ))}
            {!customer.ticket_history.length && <p className="text-sm text-slate-500">No tickets yet.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

function Detail({ label, value }) {
  return <div><dt className="text-xs font-semibold uppercase text-slate-400">{label}</dt><dd className="mt-1 text-slate-700">{value}</dd></div>;
}
