import client from "./client";

export const getReportSummary = async () => (await client.get("/reports/summary")).data;
