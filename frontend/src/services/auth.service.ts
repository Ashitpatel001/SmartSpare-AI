import { apiClient } from "@/lib/axios";

export const loginUser = async (email: string, password: string) => {
  // Revert back to JSON if fastapi is using UserLogin schema
  const response = await apiClient.post("/api/identity/login", { email, password });

  return response.data; // This will contain { access_token: "eyJhb...", token_type: "bearer" }
};

// Add this to your auth.service.ts file
export const registerUser = async (name: string, contact_number: string, email: string, password: string) => {
  try {
    const response = await apiClient.post("/api/identity/register", { 
      name, 
      contact_number, 
      email, 
      password 
    });
    return response.data;
  } catch (error: any) {
    let errorMessage = "Failed to register user";
    
    const errorData = error.response?.data;
    if (errorData && Array.isArray(errorData.detail)) {
      errorMessage = errorData.detail[0].msg || errorMessage;
    } else if (errorData && typeof errorData.detail === "string") {
      errorMessage = errorData.detail;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    throw new Error(errorMessage);
  }
};

