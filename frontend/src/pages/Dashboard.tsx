import React, { useEffect } from 'react';
import { useStore } from '../store';
import { metricsAPI, agentsAPI, checkpointsAPI, systemicEventsAPI } from '../services/api';
import { simulationAPI, wsService, disconnectWebSocket } from '../services/websocket';
import OrderTypeBadge from '../components/OrderTypeBadge';

function Dashboard() {
  const {
    currentMetrics,
    metricsHistory,
    agents,
    simulationStatus,
    setCurrentView,
    setAgents,
    setCurrentMetrics,
  } = useStore();

  useEffect(() => {
    fetchData();
    connectWebSocket();

    return () => {
      disconnectWebSocket();
    };
  }, []);

  const fetchData = async () => {
    try {
      const [metrics, agentsData, checkpoints] = await Promise.all([
        metricsAPI.getCurrent(),
        agentsAPI.list(),
        checkpointsAPI.list(),
      ]);

      setCurrentMetrics(metrics);
      setAgents(agentsData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };

  const connectWebSocket = async () => {
    try {
      wsService.connect();
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  };

  if (!currentMetrics) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-text-secondary">Loading metrics...</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h1 className="text-2xl font-bold text-text-primary mb-2">
          Moral Realism ABM Dashboard
        </h1>
        <p className="text-text-secondary">
          Real-time monitoring and visualization of moral realism simulations
        </p>
      </div>

      {/* Simulation Status */}
      {simulationStatus && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">Simulation Status</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-text-muted">Status</p>
              <p className="font-medium">{simulationStatus.status}</p>
            </div>
            <div>
              <p className="text-sm text-text-muted">Current Round</p>
              <p className="font-medium">{simulationStatus.state?.current_round || 0}</p>
            </div>
            <div>
              <p className="text-sm text-text-muted">Remaining Rounds</p>
              <p className="font-medium">{simulationStatus.remaining_rounds || 0}</p>
            </div>
            <div>
              <p className="text-sm text-text-muted">Agent Count</p>
              <p className="font-medium">{simulationStatus.agent_count || 0}</p>
            </div>
          </div>
        </div>
      )}

      {/* System Metrics */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">System Metrics</h2>
        {currentMetrics.system_metrics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-text-muted">Pattern Type</p>
              <p className="font-medium">{currentMetrics.system_metrics.pattern_type}</p>
            </div>
            <div>
              <p className="text-sm text-text-muted">Power Concentration</p>
              <p className="font-medium">
                {(currentMetrics.system_metrics.power_concentration * 100).toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-sm text-text-muted">Order Stability</p>
              <p className="font-medium">
                {currentMetrics.system_metrics.order_stability.toFixed(1)}
              </p>
            </div>
            <div>
              <p className="text-sm text-text-muted">Norm Consensus</p>
              <p className="font-medium">
                {currentMetrics.system_metrics.norm_consensus.toFixed(1)}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Agents Overview */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Agents ({agents.length})</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {agents.slice(0, 6).map((agent) => (
            <div
              key={agent.agent_id}
              className="bg-bg-secondary rounded-lg p-4"
            >
              <h3 className="font-medium mb-2">{agent.name}</h3>
              <p className="text-sm text-text-muted">
                {agent.leadership_name || agent.leadership_type}
              </p>
              {agent.capability_index !== undefined && (
                <p className="text-sm font-medium mt-2">
                  Capability: {agent.capability_index.toFixed(1)}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex gap-4">
        <button
          onClick={() => setCurrentView('configuration')}
          className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
        >
          Configuration
        </button>
        <button
          onClick={() => setCurrentView('agents')}
          className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
        >
          Agents
        </button>
        <button
          onClick={() => setCurrentView('monitor')}
          className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
        >
          Monitor
        </button>
      </div>
    </div>
  );
}

export default Dashboard;
