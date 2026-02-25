// Rally Timing - API Client
// Centralized fetch wrapper for all backend calls

const API_BASE_URL = 'http://localhost:5050/api';

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    };

    try {
        const response = await fetch(url, config);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Error desconocido');
        }
        return data.data;
    } catch (err) {
        if (err.message === 'Failed to fetch') {
            throw new Error('No se pudo conectar al servidor. Verifica que el backend este corriendo.');
        }
        throw err;
    }
}

// --- Pilots ---
const PilotsAPI = {
    list: (search = '') => {
        const params = search ? `?search=${encodeURIComponent(search)}` : '';
        return apiRequest(`/pilots${params}`);
    },
    get: (id) => apiRequest(`/pilots/${id}`),
    create: (data) => apiRequest('/pilots', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiRequest(`/pilots/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiRequest(`/pilots/${id}`, { method: 'DELETE' }),
};

// --- Cars ---
const CarsAPI = {
    list: (filters = {}) => {
        const params = new URLSearchParams();
        if (filters.pilot_id) params.set('pilot_id', filters.pilot_id);
        if (filters.category) params.set('category', filters.category);
        const qs = params.toString();
        return apiRequest(`/cars${qs ? '?' + qs : ''}`);
    },
    get: (id) => apiRequest(`/cars/${id}`),
    create: (data) => apiRequest('/cars', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiRequest(`/cars/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiRequest(`/cars/${id}`, { method: 'DELETE' }),
};

// --- Runs ---
const RunsAPI = {
    list: (filters = {}) => {
        const params = new URLSearchParams();
        if (filters.pilot_id) params.set('pilot_id', filters.pilot_id);
        if (filters.date) params.set('date', filters.date);
        if (filters.condition) params.set('condition', filters.condition);
        if (filters.category) params.set('category', filters.category);
        const qs = params.toString();
        return apiRequest(`/runs${qs ? '?' + qs : ''}`);
    },
    get: (id) => apiRequest(`/runs/${id}`),
    create: (data) => apiRequest('/runs', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiRequest(`/runs/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiRequest(`/runs/${id}`, { method: 'DELETE' }),
    addPenalty: (runId, data) => apiRequest(`/runs/${runId}/penalties`, { method: 'POST', body: JSON.stringify(data) }),
    removePenalty: (runId, penaltyId) => apiRequest(`/runs/${runId}/penalties/${penaltyId}`, { method: 'DELETE' }),
};

// --- Categories ---
const CategoriesAPI = {
    list: (search = '') => {
        const params = search ? `?search=${encodeURIComponent(search)}` : '';
        return apiRequest(`/categories${params}`);
    },
    get: (id) => apiRequest(`/categories/${id}`),
    create: (data) => apiRequest('/categories', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiRequest(`/categories/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiRequest(`/categories/${id}`, { method: 'DELETE' }),
};

// --- Rankings ---
const RankingsAPI = {
    bestTimes: (filters = {}) => {
        const params = new URLSearchParams();
        if (filters.condition) params.set('condition', filters.condition);
        if (filters.category) params.set('category', filters.category);
        const qs = params.toString();
        return apiRequest(`/rankings/best-times${qs ? '?' + qs : ''}`);
    },
    history: (pilotId) => apiRequest(`/rankings/history/${pilotId}`),
    records: () => apiRequest('/rankings/records'),
    summary: () => apiRequest('/rankings/summary'),
};
