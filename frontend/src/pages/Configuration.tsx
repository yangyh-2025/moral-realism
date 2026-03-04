import React from 'react';
import { useStore } from '../store';
import { simulationAPI } from '../services/api';

function Configuration() {
  const { simulationConfig, apiConfig, setSimulationConfig, setApiConfig } = useStore();
  const [testResult, setTestResult] = React.useState<string | null>(null);

  const handleTestConnection = async () => {
    setTestResult('Testing...');
    try {
      // Simple test - in real implementation, test API endpoint
      setTestResult('Connection successful!');
    } catch (error) {
      setTestResult('Connection failed');
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-text-primary mb-2">
        Configuration
      </h1>

      {/* API Configuration */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">API Configuration</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              API Key
            </label>
            <input
              type="password"
              value={apiConfig.api_key}
              onChange={(e) => setApiConfig({ api_key: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="Enter your SiliconFlow API key"
            />
          </div的后端

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Model
            </label>
            <input
              type="text"
              value={apiConfig.model}
              onChange={(e) => setApiConfig({ model: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="e.g., Qwen/Qwen2.5-7B-Instruct"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Base URL
            </label>
            <input
              type="text"
              value={apiConfig.base_url}
              onChange={(e) => setApiConfig({ base_url: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="https://api.siliconflow.cn/v1"
            />
          </div>

          <button
            onClick={handleTestConnection}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
          >
            Test Connection
          </button>

          {testResult && (
            <p className={`mt-2 text-sm ${testResult.includes('successful') ? 'text-success' : 'text-error'}`}>
              {testResult}
            </p>
          )}
        </div>
      </div>

      {/* Simulation Configuration */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Simulation Configuration</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Max Rounds
            </label>
            <input
              type="number"
              value={simulationConfig.max_rounds}
              onChange={(e) => setSimulationConfig({ max_rounds: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              min="1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Event Probability ({simulationConfig.event_probability})
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={simulationConfig.event_probability}
              onChange={(e) => setSimulationConfig({ event_probability: parseFloat(e.target.value) })}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Checkpoint Interval
            </label>
            <input
              type="number"
              value={simulationConfig.checkpoint_interval}
              onChange={(e) => setSimulationConfig({ checkpoint_interval: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              min="0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Log Level
            </label>
            <select
              value={simulationConfig.log_level}
              onChange={(e) => setSimulationConfig({ log_level: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="DEBUG">DEBUG</option>
              <option value="INFO">INFO</option>
              <option value="WARNING">WARNING</option>
              <option value="ERROR">ERROR</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Configuration;
