import axios from "axios";

export const apiClient = axios.create({
  // Ensure this points to your FastAPI backend URL
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000", 
});


apiClient.interceptors.request.use(
  (config) => {
    
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);


apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // If the backend rejects the token, instantly log the user out
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        window.location.href = "/"; // Kick back to login
      }
    }
    console.error("API Connection Error caught in Axios Interceptor:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);