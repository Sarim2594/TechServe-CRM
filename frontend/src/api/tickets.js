import client from "./client";

export const getTickets = async (params = {}) => (await client.get("/tickets", { params })).data;
export const getTicket = async (id) => (await client.get(`/tickets/${id}`)).data;
export const createTicket = async (payload) => (await client.post("/tickets", payload)).data;
export const updateTicket = async (id, payload) => (await client.put(`/tickets/${id}`, payload)).data;
export const deleteTicket = async (id) => client.delete(`/tickets/${id}`);
export const getTicketComments = async (id) => (await client.get(`/tickets/${id}/comments`)).data;
export const addTicketComment = async (id, payload) => (await client.post(`/tickets/${id}/comments`, payload)).data;
export const getTicketActivity = async (id) => (await client.get(`/tickets/${id}/activity`)).data;
export const analyzeTicketAI = async (id) => (await client.post(`/tickets/${id}/ai/analyze`)).data;
export const getAISuggestion = async (id) => (await client.post(`/tickets/${id}/ai/suggest-response`)).data;
export const summarizeTicketAI = async (id) => (await client.post(`/tickets/${id}/ai/summarize`)).data;
export const getTicketNotifications = async (id) => (await client.get(`/tickets/${id}/notifications`)).data;
export const sendTestTicketNotification = async (id) => (await client.post(`/tickets/${id}/notifications/test`)).data;
export const getSuggestedResponse = async (id) => {
  const response = await getAISuggestion(id);
  return { suggested_response: response.suggestion };
};

export const getComments = getTicketComments;
export const addComment = addTicketComment;
export const getActivity = getTicketActivity;
