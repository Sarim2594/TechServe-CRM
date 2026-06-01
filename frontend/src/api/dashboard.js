import client from "./client";

export const getDashboardStats = async () => (await client.get("/dashboard/stats")).data;
