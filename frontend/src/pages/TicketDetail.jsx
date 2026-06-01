import { ClipboardCopy, Edit3, RefreshCw, Sparkles, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";

import {
  addTicketComment,
  analyzeTicketAI,
  deleteTicket,
  getAISuggestion,
  getTicket,
  getTicketNotifications,
  sendTestTicketNotification,
  summarizeTicketAI,
  updateTicket,
} from "../api/tickets";
import Badge from "../components/Badge";
import { useAuth } from "../context/AuthContext";

export default function TicketDetail() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { isManager } = useAuth();
  const [ticket, setTicket] = useState(null);
  const [comment, setComment] = useState({ message: "", is_internal: true });
  const [quickUpdate, setQuickUpdate] = useState({ status: "", priority: "" });
  const [suggestion, setSuggestion] = useState("");
  const [aiAction, setAIAction] = useState("");
  const [escalationRecommended, setEscalationRecommended] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [notificationError, setNotificationError] = useState("");
  const [notificationsLoading, setNotificationsLoading] = useState(true);
  const [notificationAction, setNotificationAction] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState(location.state?.message || "");
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    try {
      const ticketData = await getTicket(id);
      setTicket(ticketData);
      setQuickUpdate({ status: ticketData.status, priority: ticketData.priority });
      setError("");
    } catch {
      setError("Ticket details could not be loaded.");
    }
  }, [id]);

  const loadNotifications = useCallback(async () => {
    setNotificationsLoading(true);
    try {
      setNotifications(await getTicketNotifications(id));
      setNotificationError("");
    } catch {
      setNotificationError("Notification history could not be loaded.");
    } finally {
      setNotificationsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
    loadNotifications();
  }, [load, loadNotifications]);

  const submitComment = async (event) => {
    event.preventDefault();
    if (!comment.message.trim()) return;
    setSaving(true);
    try {
      await addTicketComment(id, { ...comment, message: comment.message.trim() });
      setComment({ ...comment, message: "" });
      setNotice("Comment added successfully.");
      await Promise.all([load(), loadNotifications()]);
    } catch {
      setError("Comment could not be added.");
    } finally {
      setSaving(false);
    }
  };

  const saveQuickUpdate = async () => {
    setSaving(true);
    try {
      await updateTicket(id, quickUpdate);
      setNotice("Ticket status and priority updated.");
      await Promise.all([load(), loadNotifications()]);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Ticket could not be updated.");
    } finally {
      setSaving(false);
    }
  };

  const remove = async () => {
    if (!window.confirm(`Delete ticket #${id}?`)) return;
    try {
      await deleteTicket(id);
      navigate("/tickets", { replace: true });
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Ticket could not be deleted.");
    }
  };

  const analyze = async () => {
    setAIAction("analyze");
    setError("");
    try {
      const response = await analyzeTicketAI(id);
      setEscalationRecommended(response.escalation_recommended);
      setNotice("AI category and sentiment refreshed.");
      await load();
    } catch {
      setError("Ticket analysis could not be refreshed.");
    } finally {
      setAIAction("");
    }
  };

  const suggest = async () => {
    setAIAction("suggest");
    setError("");
    try {
      const response = await getAISuggestion(id);
      setSuggestion(response.suggestion);
      setNotice("AI reply suggestion generated.");
    } catch {
      setError("AI reply suggestion could not be generated.");
    } finally {
      setAIAction("");
    }
  };

  const summarize = async () => {
    setAIAction("summarize");
    setError("");
    try {
      await summarizeTicketAI(id);
      setNotice("AI summary refreshed.");
      await load();
    } catch {
      setError("AI summary could not be generated.");
    } finally {
      setAIAction("");
    }
  };

  const copySuggestionToComment = () => {
    setComment({ ...comment, message: suggestion });
    setNotice("AI reply suggestion copied to the comment box.");
  };

  const sendTestNotification = async () => {
    setNotificationAction(true);
    setNotificationError("");
    try {
      const result = await sendTestTicketNotification(id);
      setNotice(`Test email notification ${result.status}.`);
      await loadNotifications();
    } catch {
      setNotificationError("Test email notification could not be logged.");
    } finally {
      setNotificationAction(false);
    }
  };

  if (error && !ticket) return <p className="rounded-lg bg-rose-50 p-3 text-rose-700">{error}</p>;
  if (!ticket) return <p className="text-slate-500">Loading ticket...</p>;

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-blue-600">Ticket #{ticket.id}</p>
          <h1 className="text-3xl font-bold text-slate-900">{ticket.title}</h1>
          <div className="mt-3 flex flex-wrap gap-2"><Badge>{ticket.status}</Badge><Badge>{ticket.priority}</Badge><Badge>{ticket.ai_sentiment}</Badge></div>
        </div>
        <div className="flex gap-3">
          <Link className="btn-secondary" to={`/tickets/${id}/edit`}><Edit3 size={16} /> Edit ticket</Link>
          {isManager && <button className="btn-secondary text-rose-700" onClick={remove}><Trash2 size={16} /> Delete ticket</button>}
        </div>
      </div>
      {notice && <p className="mt-4 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-700">{notice}</p>}
      {error && <p className="mt-4 rounded-lg bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <section className="card">
            <h2 className="font-bold text-slate-900">Request</h2>
            <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-600">{ticket.description}</p>
          </section>
          <section className="card">
            <div className="flex items-center justify-between"><h2 className="font-bold text-slate-900">Comments</h2><span className="text-xs text-slate-400">{ticket.comments.length} updates</span></div>
            <div className="mt-4 space-y-3">
              {ticket.comments.map((item) => <div className="rounded-lg bg-slate-50 p-3" key={item.id}><div className="flex justify-between gap-3"><p className="text-sm font-semibold">{item.agent.name}</p><p className="text-xs text-slate-400">{new Date(item.created_at).toLocaleString()}</p></div><p className="mt-2 whitespace-pre-wrap text-sm text-slate-600">{item.message}</p>{item.is_internal && <p className="mt-2 text-xs font-semibold text-amber-600">Internal note</p>}</div>)}
              {!ticket.comments.length && <p className="text-sm text-slate-500">No comments yet.</p>}
            </div>
            <form className="mt-4 border-t border-slate-100 pt-4" onSubmit={submitComment}>
              <label className="label" htmlFor="ticket-comment">Add update</label>
              <textarea id="ticket-comment" className="input min-h-24" placeholder="Add an update or internal note" value={comment.message} onChange={(event) => setComment({ ...comment, message: event.target.value })} />
              <label className="mt-3 flex items-center gap-2 text-sm text-slate-600"><input type="checkbox" checked={comment.is_internal} onChange={(event) => setComment({ ...comment, is_internal: event.target.checked })} /> Internal note</label>
              <button className="btn-primary mt-3" disabled={saving}>Add comment</button>
            </form>
          </section>
        </div>
        <div className="space-y-6">
          <section className="card">
            <h2 className="font-bold text-slate-900">Ticket details</h2>
            <dl className="mt-4 space-y-3 text-sm">
              <Detail label="Customer" value={ticket.customer.full_name} />
              <Detail label="Customer email" value={ticket.customer.email} />
              <Detail label="Agent" value={ticket.assigned_agent?.name || "Unassigned"} />
              <Detail label="Category" value={ticket.category || "General"} />
              <Detail label="Created" value={new Date(ticket.created_at).toLocaleString()} />
              {ticket.resolved_at && <Detail label="Resolved" value={new Date(ticket.resolved_at).toLocaleString()} />}
            </dl>
          </section>
          <section className="card">
            <h2 className="font-bold text-slate-900">Update status</h2>
            <label className="label mt-4" htmlFor="quick-status">Status</label>
            <select id="quick-status" className="input" value={quickUpdate.status} disabled={saving} onChange={(event) => setQuickUpdate({ ...quickUpdate, status: event.target.value })}>{["Open", "In Progress", "Resolved", "Closed"].map((value) => <option key={value}>{value}</option>)}</select>
            <label className="label mt-3" htmlFor="quick-priority">Priority</label>
            <select id="quick-priority" className="input" value={quickUpdate.priority} disabled={saving} onChange={(event) => setQuickUpdate({ ...quickUpdate, priority: event.target.value })}>{["Low", "Medium", "High", "Critical"].map((value) => <option key={value}>{value}</option>)}</select>
            <button className="btn-primary mt-4" disabled={saving} onClick={saveQuickUpdate}>Save changes</button>
          </section>
          <section className="card">
            <h2 className="font-bold text-slate-900">AI insights</h2>
            <p className="mt-2 text-sm text-slate-500">Local rules work by default. Configured AI providers safely fall back if unavailable.</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Badge>{ticket.ai_category || "General"}</Badge>
              <Badge>{ticket.ai_sentiment || "Neutral"}</Badge>
            </div>
            {escalationRecommended && <p className="mt-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">This frustrated request may need a priority escalation.</p>}
            <div className="mt-4 flex flex-wrap gap-2">
              <button className="btn-secondary" disabled={Boolean(aiAction)} onClick={analyze}><RefreshCw size={16} /> {aiAction === "analyze" ? "Re-analyzing..." : "Re-analyze ticket"}</button>
              <button className="btn-primary" disabled={Boolean(aiAction)} onClick={suggest}><Sparkles size={16} /> {aiAction === "suggest" ? "Generating..." : "Generate AI reply suggestion"}</button>
              <button className="btn-secondary" disabled={Boolean(aiAction)} onClick={summarize}><RefreshCw size={16} /> {aiAction === "summarize" ? "Summarizing..." : "Generate/Refresh summary"}</button>
            </div>
            {suggestion && (
              <div className="mt-4 rounded-lg bg-blue-50 p-3">
                <p className="text-xs font-bold uppercase tracking-wide text-blue-700">Suggested reply</p>
                <textarea aria-label="AI reply suggestion" className="input mt-3 min-h-40" readOnly value={suggestion} />
                <button className="btn-secondary mt-3" onClick={copySuggestionToComment}><ClipboardCopy size={16} /> Copy to comment box</button>
              </div>
            )}
            {ticket.ai_summary && <div className="mt-4 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800"><strong>AI summary:</strong> {ticket.ai_summary}</div>}
          </section>
          <section className="card">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="font-bold text-slate-900">Notification history</h2>
              {isManager && <button className="btn-secondary" disabled={notificationAction} onClick={sendTestNotification}>{notificationAction ? "Sending..." : "Send test email notification"}</button>}
            </div>
            {notificationError && <p className="mt-4 rounded-lg bg-rose-50 p-3 text-sm text-rose-700">{notificationError}</p>}
            {notificationsLoading && <p className="mt-4 text-sm text-slate-500">Loading notifications...</p>}
            {!notificationsLoading && !notifications.length && <p className="mt-4 text-sm text-slate-500">No notifications yet.</p>}
            {!notificationsLoading && notifications.length > 0 && (
              <div className="mt-4 space-y-3">
                {notifications.map((notification) => (
                  <div className="rounded-lg bg-slate-50 p-3" key={notification.id}>
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-xs font-bold uppercase tracking-wide text-slate-500">{notification.platform}</span>
                      <Badge>{notification.status}</Badge>
                    </div>
                    <p className="mt-2 line-clamp-3 whitespace-pre-wrap text-sm text-slate-600">{notification.message}</p>
                    <p className="mt-2 text-xs text-slate-400">{new Date(notification.sent_at).toLocaleString()}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
          <section className="card">
            <h2 className="font-bold text-slate-900">Activity log</h2>
            <div className="mt-4 space-y-3">
              {ticket.activity_log.map((item) => <div className="border-l-2 border-blue-200 pl-3" key={item.id}><p className="text-sm font-medium">{item.action}</p><p className="text-xs text-slate-400">{item.actor.name} | {new Date(item.created_at).toLocaleString()}</p>{item.old_value != null && <p className="mt-1 text-xs text-slate-500">{item.old_value} to {item.new_value}</p>}</div>)}
              {!ticket.activity_log.length && <p className="text-sm text-slate-500">No activity recorded yet.</p>}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function Detail({ label, value }) {
  return <div className="flex justify-between gap-3"><dt className="text-slate-400">{label}</dt><dd className="text-right font-medium text-slate-700">{value}</dd></div>;
}
