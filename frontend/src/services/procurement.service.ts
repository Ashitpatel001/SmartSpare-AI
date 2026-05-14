import { apiClient } from "@/lib/axios";

export interface PurchaseOrder {
  id: string;
  part_name: string;
  sku: string;
  quantity: number;
  urgency: string;
  status: string;
  timestamp: string | null;
}

export const getPendingPOs = async (): Promise<PurchaseOrder[]> => {
  const response = await apiClient.get("/api/procurement/pending");
  return Array.isArray(response.data?.data) ? response.data.data : [];
};

export const approvePO = async (poId: string) => {
  const response = await apiClient.put(`/api/procurement/${poId}/approve`);
  return response.data;
};

export const rejectPO = async (poId: string) => {
  const response = await apiClient.put(`/api/procurement/${poId}/reject`);
  return response.data;
};
