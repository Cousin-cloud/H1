import axios from 'axios';
export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL });
export const withAuth = (token: string) => ({ headers: { Authorization: `Bearer ${token}` } });
