import { apiClient } from "@/lib/axios";

export const loginUser = async (email: string, password: string) => {
  // FastAPI explicitly expects 'username' and 'password' as form data
  const formData = new URLSearchParams();
  formData.append("username", email); 
  formData.append("password", password);

  const response = await apiClient.post("/api/identity/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  
  return response.data; // This will contain { access_token: "eyJhb...", token_type: "bearer" }
};