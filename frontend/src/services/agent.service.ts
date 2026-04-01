import { apiClient } from "@/lib/axios";

// Your existing chat function might be here
export const sendChatMessage = async (message: string, factoryId: string) => {
  const response = await apiClient.post("/api/intelligence/chat", {
    message: message,
    factory_id: factoryId
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