import client from "./client";

export const getCustomers = async (search = "") => {
  const params = typeof search === "string" ? (search ? { search } : {}) : search;
  return (await client.get("/customers", { params })).data;
};
export const getCustomer = async (id) => (await client.get(`/customers/${id}`)).data;
export const createCustomer = async (payload) => (await client.post("/customers", payload)).data;
export const updateCustomer = async (id, payload) => (await client.put(`/customers/${id}`, payload)).data;
export const deleteCustomer = async (id) => client.delete(`/customers/${id}`);
