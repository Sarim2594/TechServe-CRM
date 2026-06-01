import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getUsers } from "../api/auth";
import { createCustomer, getCustomer, updateCustomer } from "../api/customers";
import { useAuth } from "../context/AuthContext";

const initialForm = { full_name: "", email: "", phone: "", company: "", notes: "", assigned_agent_id: "" };

export default function CustomerForm() {
  const { id } = useParams();
  const { isManager } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [agents, setAgents] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(Boolean(id));
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(Boolean(id));
      try {
        const [customer, users] = await Promise.all([
          id ? getCustomer(id) : Promise.resolve(null),
          isManager ? getUsers() : Promise.resolve([]),
        ]);
        if (!active) return;
        if (customer) {
          setForm({
            ...customer,
            phone: customer.phone || "",
            company: customer.company || "",
            notes: customer.notes || "",
            assigned_agent_id: customer.assigned_agent_id || "",
          });
        }
        setAgents(users.filter((item) => item.role === "agent"));
      } catch {
        if (active) setError("Customer could not be loaded.");
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
    if (!form.full_name.trim()) {
      setError("Full name is required.");
      return;
    }
    if (!form.email.trim()) {
      setError("A valid email is required.");
      return;
    }
    setSaving(true);
    const payload = {
      ...form,
      full_name: form.full_name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim() || null,
      company: form.company.trim() || null,
      notes: form.notes.trim() || null,
      assigned_agent_id: form.assigned_agent_id ? Number(form.assigned_agent_id) : null,
    };
    try {
      const customer = id ? await updateCustomer(id, payload) : await createCustomer(payload);
      navigate(`/customers/${customer.id}`, {
        state: { message: `Customer ${id ? "updated" : "created"} successfully.` },
      });
    } catch (requestError) {
      setError(formatApiError(requestError));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p className="text-slate-500">Loading customer...</p>;

  return (
    <div className="max-w-3xl">
      <h1 className="text-3xl font-bold text-slate-900">{id ? "Edit customer" : "Add customer"}</h1>
      <p className="mt-1 text-sm text-slate-500">Keep contact details and ownership clear for the support team.</p>
      <form className="card mt-6 grid gap-4 sm:grid-cols-2" onSubmit={submit}>
        <Field label="Full name"><input className="input" value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} required /></Field>
        <Field label="Email"><input className="input" type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required /></Field>
        <Field label="Phone"><input className="input" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} /></Field>
        <Field label="Company"><input className="input" value={form.company} onChange={(event) => setForm({ ...form, company: event.target.value })} /></Field>
        {isManager && <Field label="Assigned agent"><select className="input" value={form.assigned_agent_id} onChange={(event) => setForm({ ...form, assigned_agent_id: event.target.value })}><option value="">Unassigned</option>{agents.map((agent) => <option key={agent.id} value={agent.id}>{agent.name}</option>)}</select></Field>}
        <div className="sm:col-span-2"><Field label="Notes"><textarea className="input min-h-28" value={form.notes || ""} onChange={(event) => setForm({ ...form, notes: event.target.value })} /></Field></div>
        {error && <p className="sm:col-span-2 text-sm text-rose-700">{error}</p>}
        <div className="flex gap-3 sm:col-span-2"><button className="btn-primary" disabled={saving}>{saving ? "Saving..." : "Save customer"}</button><Link className="btn-secondary" to="/customers">Cancel</Link></div>
      </form>
    </div>
  );
}

function formatApiError(requestError) {
  const detail = requestError.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(" ");
  return detail || "Customer could not be saved.";
}

function Field({ label, children }) {
  return <label><span className="label">{label}</span>{children}</label>;
}
