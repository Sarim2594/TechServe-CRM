import { BarChart3, ContactRound, LayoutDashboard, LogOut, TicketCheck } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/customers", label: "Customers", icon: ContactRound },
  { to: "/tickets", label: "Tickets", icon: TicketCheck },
];

export default function Sidebar() {
  const { user, isManager, logout } = useAuth();
  const navigate = useNavigate();
  const items = isManager ? [...navItems, { to: "/reports", label: "Reports", icon: BarChart3 }] : navItems;
  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <aside className="border-b border-slate-800 bg-navy-900 text-white md:fixed md:inset-y-0 md:w-64 md:border-b-0 md:border-r">
      <div className="flex min-h-full flex-col">
        <div className="px-5 py-5">
          <p className="text-lg font-bold">TechServe CRM</p>
          <p className="text-xs text-blue-200">AI-enhanced support desk</p>
        </div>
        <nav className="flex gap-1 overflow-auto px-3 pb-3 md:flex-col md:pb-0">
          {items.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive ? "bg-blue-600 text-white" : "text-blue-100 hover:bg-slate-800"
                }`
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="ml-auto px-4 py-3 md:mt-auto md:ml-0 md:border-t md:border-slate-800 md:py-4">
          <p className="hidden text-sm font-medium md:block">{user?.name}</p>
          <p className="hidden text-xs capitalize text-blue-200 md:block">{user?.role}</p>
          <button className="mt-1 flex items-center gap-2 text-xs text-blue-100 hover:text-white md:mt-3" onClick={handleLogout}>
            <LogOut size={15} />
            Sign out
          </button>
        </div>
      </div>
    </aside>
  );
}
