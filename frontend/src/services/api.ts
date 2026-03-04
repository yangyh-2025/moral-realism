// API service for communicating with FastAPI backend
const API_BASE_URL = 'http://localhost:8000';

async function fetchAPI(
  endpoint: string,
  options: RequestInit = {},
): Promise<Response> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response;
}

export const simulationAPI = {
  async getStatus() {
    const response = await fetchAPI('/api/v1/simulation/status');
    return response.json();
  },

  async start() {
    const response = await fetchAPI('/api/v1/simulation/start', {
      method: 'POST',
    });
    return response.json();
  },

  async pause() {
    const response = await fetchAPI('/api/v1/simulation/pause', {
      method: 'POST',
    });
    return response.json();
  },

  async resume() {
    const response = await fetchAPI('/api/v1/simulation/resume', {
      method: 'POST',
    });
    return response.json();
  },

  async stop() {
    const response = await fetchAPI('/api/v1/simulation/stop', {
      method: 'POST',
    });
    return response.json();
  },

  async reset() {
    const response = await fetchAPI('/api/v1/simulation/reset', {
      method: 'POST',
    });
    return response.json();
  },

  async. configure(config: unknown) {
    const response = await fetchAPI('/api/v1/simulation/configure', {
      method: 'POST',
      body: JSON.stringify(config),
    });
    return response.json();
  },
};

export const agentsAPI = {
  async list() {
    const response = await fetchAPI('/api/v1/agents/');
    return response.json();
  },

  async get(agentId: string) {
    const response = await fetchAPI(`/api/v1/agents/${agentId}`);
    return response.json();
  },

  async create(agent: unknown) {
    const response = await fetchAPI('/api/v1/agents/', {
      method: 'POST',
      body: JSON.stringify(agent),
    });
    return response.json();
  },

  async update(agentId: string, updates: unknown) {
    const response = await fetchAPI(`/api/v1/agents/${agentId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
    return response.json();
  },

  async delete(agentId: string) {
    const response = await fetchAPI(`/api/v1/agents/${agentId}`, {
      method: 'DELETE',
    });
    return response.json();
  },

  async loadPreset(presetName: string) {
    const response = await fetchAPI(`/api/v1/agents/presets/${presetName}`, {
      method: 'POST',
    });
    return response.json();
  },
};

export const metricsAPI = {
  async getCurrent() {
    const response = await fetchAPI('/api/v1/metrics/current');
    return response.json();
  },

  async getTrends(startRound: number = 0, endRound?: number) {
    const params = new URLSearchParams({
      start_round: String(startRound),
    });
    if (endRound !== undefined) {
      params.append('end_round', String(endRound));
    }
    const response = await fetchAPI(`/api/v1/metrics/trends?${params}`);
    return response.json();
  },

  async getAgent(agentId: string, metricType?: string) {
    const params = new URLSearchParams();
    if (metricType !== undefined) {
      params.append('metric_type', metricType);
    }
    const response = await fetchAPI(
      `/api/v1/metrics/agents/${agentId}${params.toString() ? '?' + params.toString() : ''}`,
    );
    return response.json();
  },

  async getRound(roundId: number) {
    const response = await fetchAPI(`/api/v1/metrics/round/${roundId}`);
    return response.json();
  },

  async.exportCSV(
    dataType: string,
    startRound: number = 0,
    endRound?: number,
  ): Promise<Blob> {
    const params = new URLSearchParams({
      data_type: dataType,
      start_round: String(startRound),
    });
    if (endRound !== undefined) {
      params.append('end_round', String(endRound));
    }
    const response = await fetchAPI(`/api/v1/metrics/export/csv?${params}`);
    return response.blob();
  },

  async.exportJSON(
    startRound: number = 0,
    endRound?: number,
  ) {
    const params = new URLSearchParams({
      start_round: String(startRound),
    });
    if (endRound !== undefined) {
      params.append('end_round', String(endRound));
    }
    const response = await fetchAPI(`/api/v1/metrics/export/json?${params}`);
    return response.json();
  },
};

export const checkpointsAPI = {
  async list() {
    const response = await fetchAPI('/api/v1/checkpoints/');
    return response.json();
  },

  async get(checkpointId: string) {
    const response = await fetchAPI(`/api/v1/checkpoints/${checkpointId}`);
    return response.json();
  },

  async save(checkpointId?: string) {
    const body = checkpointId ? { checkpoint_id: checkpointId } : {};
    const response = await fetchAPI('/api/v1/checkpoints/save', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    return response.json();
  },

  async load(checkpointId: string) {
    const response = await fetchAPI(`/api/v1/checkpoints/load/${checkpointId}`, {
      method: 'POST',
    });
    return response.json();
  },

  async delete(checkpointId: string) {
    const response = await fetchAPI(`/api/v1/checkpoints/${checkpointId}`, {
      method: 'DELETE',
    });
    return response.json();
  },
};
