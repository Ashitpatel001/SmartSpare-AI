import { apiClient } from "@/lib/axios";

// Chat function — factory_id is resolved server-side from PostgreSQL
export const sendChatMessage = async (message: string) => {
  const response = await apiClient.post("/api/intelligence/chat", {
    message: message
  });
  return response.data;
};

// The NEW Diagnosis function you must add
export const runAiDiagnosis = async (errorCode: string) => {
  const response = await apiClient.post("/api/intelligence/diagnose", {
    error_code: errorCode
  });
  return response.data;
};