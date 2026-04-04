import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getInteractions = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.intent) params.append('intent', filters.intent);
  if (filters.urgency_min) params.append('urgency_min', filters.urgency_min);
  if (filters.urgency_max) params.append('urgency_max', filters.urgency_max);
  if (filters.spam_confidence) params.append('spam_confidence', filters.spam_confidence);

  const response = await api.get(`/interactions?${params.toString()}`);
  return response.data;
};

export const getInteractionById = async (id) => {
  const response = await api.get(`/interactions/${id}`);
  return response.data;
};

export const createInteraction = async (data) => {
  const response = await api.post('/interactions', data);
  return response.data;
};

export default api;
