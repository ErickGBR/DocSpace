const API_BASE = 'http://localhost:8000/api';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  setTokens(access, refresh) {
    this.token = access;
    this.refreshToken = refresh;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }

  clearTokens() {
    this.token = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  getAuthHeader() {
    return this.token ? { Authorization: `Bearer ${this.token}` } : {};
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
        ...options.headers,
      },
      ...options,
    };

    if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
      config.body = JSON.stringify(config.body);
    }

    let response = await fetch(url, config);

    if (response.status === 401 && this.refreshToken && !endpoint.includes('/auth/')) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        config.headers.Authorization = `Bearer ${this.token}`;
        response = await fetch(url, config);
      } else {
        this.clearTokens();
        window.location.href = '/login';
        return;
      }
    }

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw { status: response.status, data };
    }
    return data;
  }

  async refreshAccessToken() {
    try {
      const response = await fetch(`${API_BASE}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: this.refreshToken }),
      });
      if (response.ok) {
        const data = await response.json();
        this.setTokens(data.access, data.refresh);
        return true;
      }
    } catch (e) {
      console.error('Refresh failed', e);
    }
    return false;
  }

  // Auth
  login(email, password) {
    return this.request('/auth/login/', {
      method: 'POST',
      body: { email, password },
    });
  }

  register(userData) {
    return this.request('/auth/register/', {
      method: 'POST',
      body: userData,
    });
  }

  logout() {
    return this.request('/auth/logout/', { method: 'POST' }).finally(() => this.clearTokens());
  }

  // Documentos
  uploadDocumento(formData) {
    return this.request('/documentos/upload/', {
      method: 'POST',
      headers: {
        ...this.getAuthHeader(),
      },
      body: formData,
    });
  }

  saveDocumento(id, content) {
    return this.request(`/documentos/${id}/save/`, {
      method: 'POST',
      body: { content },
    });
  }

  getDocumentos(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/documentos/?${query}`);
  }

  getDocumentoVersions(id) {
    return this.request(`/documentos/${id}/versions/`);
  }

  getDocumentoContent(id, version) {
    const query = version ? `?version=${version}` : '';
    return this.request(`/documentos/${id}/content/${query}`);
  }

  deleteDocumento(id) {
    return this.request(`/documentos/${id}/`, { method: 'DELETE' });
  }

  // Historial
  getHistorial(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/auditoria/historial/?${query}`);
  }
}


export const api = new ApiService();
