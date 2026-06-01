import { useEffect, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";

import { getUsers } from "../api/auth";
import { getCustomers } from "../api/customers";
import { createTicket, getTicket, updateTicket } from "../api/tickets";
import { useAuth } from "../context/AuthContext";

const initialForm = { title: "", description: "", status: "Open", priority: "Medium", category: "", customer_id: "", assigned_agent_id: "" };

export default function TicketForm() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const { isManager } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ ...initialForm, customer_id: searchParams.get("customer_id") || "" });
  const [customers, setCustomers] = useState([]);
  const [agents, setAgents] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      try {
        const [ticket, customerOptions, users] = await Promise.all([
          id ? getTicket(id) : Promise.resolve(null),
          getCustomers(),
          isManager ? getUsers() : Promise.resolve([]),
        ]);
        if (!active) return;
        setCustomers(customerOptions);
        setAgents(users.filter((user) => user.role === "agent"));
        if (ticket) {
          setForm({
            title: ticket.title,
            description: ticket.description,
            status: ticket.status,
            priority: ticket.priority,
            category: ticket.category || "",
            customer_id: ticket.customer_id,
            assigned_agent_id: ticket.assigned_agent_id || "",
          });
        }
      } catch {
        if (active) setError("Ticket form data could not be loaded.");
      } finally {
        if (active) setLoading(false);
      }
    };
    load();
    return () => {
      active = false;
    };
  }, [id, isManager]);

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    if (!form.title.trim()) {
      setError("Title is required.");
      return;
    }
    if (!form.description.trim()) {
      setError("Description is required.");
      return;
    }
    if (!form.customer_id) {
      setError("Choose a customer.");
      return;
    }
    setSaving(true);
    const payload = {
      ...form,
      title: form.title.trim(),
      description: form.description.trim(),
      customer_id: Number(form.customer_id),
      assigned_agent_id: form.assigned_agent_id ? Number(form.assigned_agent_id) : null,
      category: form.category.trim() || null,
    };
    try {
      const ticket = id ? await updateTicket(id, payload) : await createTicket(payload);
      navigate(`/tickets/${ticket.id}`, {
        state: { message: `Ticket ${id ? "updated" : "created"} successfully.` },
      });
    } catch (requestError) {
      setError(formatApiError(requestError));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p className="text-slate-500">Loading ticket...</p>;

  return (
    <div className="max-w-3xl">
      <h1 className="text-3xl font-bold text-slate-900">{id ? "Edit ticket" : "Create ticket"}</h1>
      <p className="mt-1 text-sm text-slate-500">AI categorization and sentiment run whenever a ticket is created.</p>
      <form className="card mt-6 grid gap-4 sm:grid-cols-2" onSubmit={submit}>
        <div className="sm:col-span-2"><Field label="Title"><input className="input" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required /></Field></div>
        <div className="sm:col-span-2"><Field label="Description"><textarea className="input min-h-36" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} required /></Field></div>
        <Field label="Customer"><select aria-label="Customer" className="input" value={form.customer_id} onChange={(event) => setForm({ ...form, customer_id: event.target.value })} required><option value="">Choose customer</option>{customers.map((customer) => <option key={customer.id} value={customer.id}>{customer.full_name}</option>)}</select></Field>
        <Field label="Category"><input className="input" placeholder="Leave blank for AI category" value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })} /></Field>
        <Field label="Status"><select aria-label="Status" className="input" value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })}>{["Open", "In Progress", "Resolved", "Closed"].map((value) => <option key={value}>{value}</option>)}</select></Field>
        <Field label="Priority"><select aria-label="Priority" className="input" value={form.priority} onChange={(event) => setForm({ ...form, priority: event.target.value })}>{["Low", "Medium", "High", "Critical"].map((value) => <option key={value}>{value}</option>)}</select></Field>
        {isManager && <Field label="Assigned agent"><select aria-label="Assigned agent" className="input" value={form.assigned_agent_id} onChange={(event) => setForm({ ...form, assigned_agent_id: event.target.value })}><option value="">Unassigned</option>{agents.map((agent) => <option key={agent.id} value={agent.id}>{agent.name}</option>)}</select></Field>}
        {error && <p className="sm:col-span-2 text-sm text-rose-700">{error}</p>}
        <div className="flex gap-3 sm:col-span-2"><button className="btn-primary" disabled={saving}>{saving ? "Saving..." : "Save ticket"}</button><Link className="btn-secondary" to="/tickets">Cancel</Link></div>
      </form>
    </div>
  );
}

function formatApiError(requestError) {
  const detail = requestError.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(" ");
  return detail || "Ticket could not be saved.";
}

function Field({ label, children }) {
  return <label><span className="label">{label}</span>{children}</label>;
}
