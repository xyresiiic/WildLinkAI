/**
 * WildLink AI — API Service
 */
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000,
});

// ────────────── Species ──────────────
export const getSpecies = () => api.get('/species');
export const getSpeciesById = (id) => api.get(`/species/${id}`);

// ────────────── Projects ──────────────
export const getProjects = () => api.get('/projects');
export const getProject = (id) => api.get(`/projects/${id}`);
export const createProject = (data) => api.post('/projects', data);
export const deleteProject = (id) => api.delete(`/projects/${id}`);
export const getDashboard = (projectId) => api.get(`/projects/${projectId}/dashboard`);

// ────────────── Analysis ──────────────
export const runAnalysis = (data) => api.post('/analysis/run', data);
export const getJobStatus = (jobId) => api.get(`/analysis/jobs/${jobId}`);
export const getHabitatZones = (projectId) => api.get(`/analysis/habitat/${projectId}`);
export const getCorridors = (projectId) => api.get(`/analysis/corridors/${projectId}`);
export const getPriorityZones = (projectId) => api.get(`/analysis/priority/${projectId}`);
export const getObservations = (projectId) => api.get(`/analysis/observations/${projectId}`);

// ────────────── Simulations ──────────────
export const createSimulation = (data) => api.post('/simulations', data);
export const getSimulation = (id) => api.get(`/simulations/${id}`);
export const getProjectSimulations = (projectId) => api.get(`/simulations/project/${projectId}`);

export default api;
