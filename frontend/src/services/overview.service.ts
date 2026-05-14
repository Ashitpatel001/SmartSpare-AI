import { apiClient } from "@/lib/axios";

export const getOverviewStats = async () => {
  const response = await apiClient.get("/api/warehouse/overview");
  return response.data?.data || null;
};
