import { apiClient } from "@/lib/axios";

export const loginUser = async (email: string, password: string) => {
  // Revert back to JSON if fastapi is using UserLogin schema
  const response = await apiClient.post("/api/identity/login", { email, password });

  return response.data; // This will contain { access_token: "eyJhb...", token_type: "bearer" }
};

// Add this to your auth.service.ts file
export const registerUser = async (name: string, contact_number: string, email: string, password: string) => {
  const response = await fetch("http://localhost:8000/api/identity/register", { // or use apiClient.post("/api/identity/register", { name, contact_number, email, password })
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, contact_number, email, password }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to register user");
  }

  return response.json();
};

