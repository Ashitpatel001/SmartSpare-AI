import { apiClient } from "@/lib/axios";

export interface SparePart {
  id: string;
  sku: string | null;
  name: string;
  current_stock: number;
  minimum_threshold: number;
  location_bin: string | null;
  category: string | null;
}

export const getInventory = async () => {
  const response = await apiClient.get("/api/warehouse/parts");
  const partsData = Array.isArray(response.data?.data) ? response.data.data : Array.isArray(response.data) ? response.data : [];
  return partsData as SparePart[];
};

// --- NEW CRUD OPERATIONS ---

export const createPart = async (partData: Partial<SparePart>) => {
  const response = await apiClient.post("/api/warehouse/parts", partData);
  return response.data;
};

export const updatePart = async ({ id, data }: { id: string; data: Partial<SparePart> }) => {
  const response = await apiClient.put(`/api/warehouse/parts/${id}`, data);
  return response.data;
};

export const deletePart = async (id: string) => {
  const response = await apiClient.delete(`/api/warehouse/parts/${id}`);
  return response.data;
};


export const uploadInventoryPdf = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file); // "file" must exactly match the parameter name in FastAPI
  
  const response = await apiClient.post("/api/warehouse/parts/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};