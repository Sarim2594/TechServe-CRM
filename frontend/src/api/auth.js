import client from "./client";

export const login = async (credentials) => (await client.post("/auth/login", credentials)).data;
export const getMe = async () => (await client.get("/auth/me")).data;
export const getUsers = async () => (await client.get("/auth/users")).data;
