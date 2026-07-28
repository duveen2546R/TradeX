import axios from "axios";

const localApiBase = typeof window === "undefined"
  ? "http://127.0.0.1:5000"
  : `${window.location.protocol}//${window.location.hostname}:5000`;

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || localApiBase,
  withCredentials: true,
});

export default api;
