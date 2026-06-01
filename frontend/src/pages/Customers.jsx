import { Eye, Pencil, Plus, Search, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { deleteCustomer, getCustomers } from "../api/customers";
import { useAuth } from "../context/AuthContext";

export default function Customers() {
  const { user } = useAuth();
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadCustomers = useCallback(async () => {
    setLoading(true);
    try {
      setCustomers(await getCustomers(search));
      setError("");
    } catch {
      setError("Customers could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    const timer = setTimeout(loadCustomers, 200);
    return () => clearTimeout(timer);
  }, [loadCustomers]);

  const remove = async (customer) => {
    if (!window.confirm(`Delete ${customer.full_name}?`)) return;
    try {
      await deleteCustomer(customer.id);
      await loadCustomers();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Customer could not be deleted.");
    }
  };

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Customers</h1>
          <p className="mt-1 text-sm text-slate-500">Search profiles and review their service history.</p>
        </div>
        <Link className="btn-primary" to="/customers/new"><Plus size={17} /> Add customer</Link>
      </div>
      <div className="card mt-6">
        <label className="relative block max-w-md" htmlFor="customer-search">
          <span className="sr-only">Search customers</span>
          <Search className="absolute left-3 top-2.5 text-slate-400" size={17} />
          <input id="customer-search" className="input pl-9" placeholder="Search name, email, or company" value={search} onChange={(event) => setSearch(event.target.value)} />
        </label>
        {error && <p className="mt-4 text-sm text-rose-700">{error}</p>}
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left">
            <thead className="border-b border-slate-200 text-xs uppercase text-slate-400">
              <tr><th className="table-cell">Full name</th><th className="table-cell">Email</th><th className="table-cell">Phone</th><th className="table-cell">Company</th><th className="table-cell">Date added</th><th className="table-cell">Actions</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {customers.map((customer) => (
                <tr key={customer.id}>
                  <td className="table-cell font-semibold text-slate-800">{customer.full_name}</td>
                  <td className="table-cell">{customer.email}</td>
                  <td className="table-cell">{customer.phone || "Not provided"}</td>
                  <td className="table-cell">{customer.company || "Not provided"}</td>
                  <td className="table-cell">{new Date(customer.created_at).toLocaleDateString()}</td>
                  <td className="table-cell">
                    <div className="flex items-center gap-3">
                      <Link aria-label={`View ${customer.full_name}`} className="text-blue-700 hover:text-blue-900" title="View customer details" to={`/customers/${customer.id}`}><Eye size={16} /></Link>
                      <Link aria-label={`Edit ${customer.full_name}`} className="text-blue-700 hover:text-blue-900" title="Edit customer" to={`/customers/${customer.id}/edit`}><Pencil size={16} /></Link>
                      {user?.role === "manager" && <button aria-label={`Delete ${customer.full_name}`} className="text-rose-600 hover:text-rose-800" title="Delete customer" onClick={() => remove(customer)}><Trash2 size={16} /></button>}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {loading && <p className="py-6 text-center text-sm text-slate-500">Loading customers...</p>}
          {!loading && !customers.length && <p className="py-6 text-center text-sm text-slate-500">No customers found.</p>}
        </div>
      </div>
    </div>
  );
}
