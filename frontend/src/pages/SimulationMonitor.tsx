import React, { useEffect, useRef } from 'react';
import { useStore } from '../store';
import { simulationAPI, agentsAPI, checkpointsAPI, getWebSocketService, disconnectWebSocket } from '../services/api';
import { wsService } from '../services/websocket';

function SimulationMonitor() {
  const {
    simulationStatus,
    logs,
    logFilter,
    setLogs,
    setLogFilter,
    clearLogs,
    resetSimulation,
  } = useStore();
  const [autoScroll, setAutoScroll] = React.useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchStatus();
    connectWebSocket();

    return () => {
      disconnectWebSocket();
    };
  }, []);

  const fetchStatus = async () => {
    try {
      const status = await simulationAPI.getStatus();
      // Update store with status
    } catch (error) {
      console.error('Failed to fetch status:', error);
    }
  };

  const connectWebSocket = async () => {
    try {
      wsService.connect();
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  };

  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollTop = logsEndRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const handleStart = async () => {
    try {
      await simulationAPI.start();
    } catch (error) {
      console.error('Failed to start simulation:', error);
      alert('Failed to start simulation');
    }
  };

  const handlePause = async () => {
    try {
      await simulationAPI.pause();
    } catch (error) {
      console.error('Failed to pause simulation:', error);
      alert('Failed to pause simulation');
    }
  };

  const handleResume = async () => {
    try {
      await simulationAPI.resume();
    } catch (error) {
      console.error('Failed to resume simulation:', error);
      alert('Failed to resume simulation');
    }
  };

  const handleStop = async () => {
    if (!confirm('Are you sure you want to stop the simulation?')) return;

    try {
      await simulationAPI.stop();
    } catch (error) {
      console.error('Failed to stop simulation:', error);
      alert('Failed to stop simulation');
    }
  };

  const handleReset = async () => {
    if (!confirm('Are you sure you want to reset the simulation? All data will be lost.')) return;

    try {
      await simulationAPI.reset();
      resetSimulation();
      clearLogs();
    } catch (error) {
      console.error('Failed to reset simulation:', error);
      alert('Failed to reset simulation');
    }
  };

  const handleSaveCheckpoint = async () => {
    try {
      await checkpointsAPI.save();
      alert('Checkpoint saved successfully!');
    } catch (error) {
      console.error('Failed to save checkpoint:', error);
      alert('Failed to save checkpoint');
    }
  };

  const getStatusBadge = () => {
    if (!simulationStatus) {
      return { text: 'Unknown', color: 'bg-gray-200 text-gray-700' };
    }

    switch (simulationStatus.status) {
      case 'running':
        return { text: 'Running', color: 'bg-success text-white' };
      case 'paused':
        return { text: 'Paused', color: 'bg-warning text-white' };
      case 'completed':
        return { text: 'Completed', color: 'bg-info text-white' };
      case 'stopped':
        return { text: 'Stopped', color: 'bg-error text-white' };
      case 'error':
        return { text: 'Error', color: 'bg-error text-white' };
      default:
        return { text: 'Ready', color: 'bg-gray-200 text-gray-700' };
    }
  };

  const statusBadge = getStatusBadge();
  const isRunning = simulationStatus?.status === 'running';
  const isPaused = simulationStatus?.status === 'paused';

  const filteredLogs = logFilter
    ? logs.filter((log) => log.level === logFilter.toUpperCase())
    : logs;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-text-primary mb-2">
        Simulation Monitor
      </h1>

      {/* Simulation Control */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Control Panel</h2>

        <div className="flex items-center gap-4 mb-4">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusBadge.color}`}>
            {statusBadge.text}
          </span>
          {simulationStatus?.state && (
            <span className="text-text-secondary">
              Round {simulationStatus.state.current_round} / {simulationStatus.config?.max_rounds || 100}
            </span>
          )}
        </div>

        {/* Progress Bar */}
        {simulationStatus?.config && (
          <div className="mb-6">
            <div className="flex justify-between text-sm text-text-muted mb-2">
              <span>Progress</span>
              <span>
                {simulationStatus.state?.current_round || 0} / {simulationStatus.config.max_rounds}
              </span>
            </div>
            <div className="w-full bg-bg-tertiary rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-primary rounded-full transition-all duration-300"
                style={{
                  width: `${((simulationStatus.state?.current_round || 0) / simulationStatus.config.max_rounds) * 100}%`,
                }}
              />
            </div>
          </div>
        )}

        {/* Control Buttons */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <button
            onClick={handleStart}
            disabled={isRunning}
            className="px-4 py-2 bg-success text-white rounded-lg hover:opacity-80 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Start
          </button>
          <button
            onClick={handlePause}
            disabled={!isRunning || isPaused}
            className="px-4 py-2 bg-warning text-white rounded-lg hover:opacity-80 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Pause
          </button>
          <button
            onClick={handleResume}
            disabled={!isPaused}
            className="px-4 py-2 bg-info text-white rounded-lg hover:opacity-80 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Resume
          </button>
          <button
            onClick={handleStop}
            disabled={!isRunning && !isPaused}
            className="px-4 py-2 bg-error text-white rounded-lg hover:opacity-80 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Stop
          </button>
          <button
            onClick={handleReset}
            disabled={isRunning}
            className="px-4 py-2 bg-bg-tertiary text-text-primary rounded-lg hover:bg-bg-card transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Checkpoint Management */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Checkpoints</h2>
        <button
          onClick={handleSaveCheckpoint}
          className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
        >
        Save Checkpoint
        </button>
      </div>

      {/* Log Viewer */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Simulation Logs</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setLogFilter(null)}
              className={`px-3 py-1 rounded text-sm ${!logFilter ? 'bg-primary text-white' : 'bg-bg-tertiary text-text-primary hover:bg-bg-card transition'}`}
            >
              All
            </button>
            <button
              onClick={() => setLogFilter('error')}
              className={`px-3 py-1 rounded text-sm ${logFilter === 'error' ? 'bg-error text-white' : 'bg-bg-tertiary text-text-primary hover:bg-bg-card transition'}`}
            >
              Errors
            </button>
            <button
              onClick={() => setLogFilter('warning')}
              className={`px-3 py-1 rounded text-sm ${logFilter === 'warning' ? 'bg-warning text-white' : 'bg-bg-tertiary text-text-primary hover:bg-bg-card transition'}`}
            >
              Warnings
            </button>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={autoScroll}
                onChange={(e) => setAutoScroll(e.target.checked)}
                className="w-4 h-4"
              />
              <span className="text-sm">Auto-scroll</span>
            </label>
            <button
              onClick={clearLogs}
              className="px-3 py-1 bg-bg-tertiary text-text-primary rounded hover:bg-bg-card transition text-sm"
            >
              Clear
            </button>
          </div>
        </div>

        <div
          ref={logsEndRef}
          className="bg-gray-900 text-green-400 rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm"
          style={{ fontFamily: 'monospace' }}
        >
          {filteredLogs.length === 0 ? (
            <p className="text-gray-400">No logs available...</p>
          ) : (
            filteredLogs.map((log, index) => (
              <div key={`${log.timestamp}-${index}`} className="mb-1">
                <span className="text-gray-500">
                  [{new Date(log.timestamp).toLocaleTimeString()}]
                </span>
                <span className={`${log.level === 'ERROR' ? 'text-red-400' : log.level === 'WARNING' ? 'text-yellow-400' : ''}`}>
                  [{log.level}]
                </span>
                {log.message}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default SimulationMonitor;
