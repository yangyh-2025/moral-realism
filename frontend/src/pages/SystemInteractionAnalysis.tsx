import React, { useEffect, useState } from 'react';
import { useStore } from '../store';
import { systemicEventsAPI } from '../services/api';
import OrderTypeBadge from '../components/OrderTypeBadge';
import NormEvolutionChart from '../components/NormEvolutionChart';
import SystemicEventsTable from '../components/SystemicEventsTable';
import type { SystemicEvent, Norm } from '../types';

function SystemInteractionAnalysis() {
  const {
    systemicEvents,
    currentNorms,
    normsHistory,
    setSystemicEvents,
    setCurrentNorms,
    setCurrentView,
  } = useStore();

  const [selectedEvent, setSelectedEvent] = useState<SystemicEvent | null>(null);
  const [selectedNormId, setSelectedNormId] = useState<string> | undefined>();
  const [orderEvolution, setOrderEvolution] = useState<Array<{ round: number; order_type: string }>>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch all systemic events
      const events = await systemicEventsAPI.getEvents();
      setSystemicEvents(events);

      // Fetch current norms
      const norms = await systemicEventsAPI.getNorms();
      setCurrentNorms(norms);

      // Fetch order evolution
      const evolution = await systemicEventsAPI.getOrderEvolution(0);
      setOrderEvolution(evolution);
    } catch (error) {
      console.error('Failed to fetch systemic interaction data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportEvents = async () => {
    try {
      const blob = await systemicEventsAPI.exportEventsCSV();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `systemic_events_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to export events:', error);
      alert('Failed to export events');
    }
  };

  const getOrderTypeCounts = () => {
    const counts: Record<string, number> = {};
    orderEvolution.forEach((entry) => {
      counts[entry.order_type] = (counts[entry.order_type] || 0) + 1;
    });
    return counts;
  };

  const getNormsByCategory = () => {
    const byCategory: Record<string, Norm[]> = {};
    currentNorms.forEach((norm) => {
      if (!byCategory[norm.category]) {
        byCategory[norm.category] = [];
      }
      byCategory[norm.category].push(norm);
    });
    return byCategory;
  };

  const orderTypeCounts = getOrderTypeCounts();
  const normsByCategory = getNormsByCategory();
  const activeNorms = currentNorms.filter((n) => n.strength >= 0.5);
  const avgNormStrength = currentNorms.length > 0
    ? currentNorms.reduce((sum, n) => sum + n.strength, 0) / currentNorms.length
    : 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading system interaction data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary mb-2">
              System Interaction Analysis
            </h1>
            <p className="text-text-secondary">
              Analysis of international order evolution, norm development, and values competition
            </p>
          </div>
          <button
            onClick={() => setCurrentView('dashboard')}
            className="px-4 py-2 bg-bg-tertiary text-text-primary rounded-lg hover:bg-bg-card transition"
          >
            Back to Dashboard
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm p-4">
          <p className="text-sm text-text-muted mb-1">Total Events</p>
          <p className="text-2xl font-bold text-text-primary">{systemicEvents.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4">
          <p className="text-sm text-text-muted mb-1">Active Norms</p>
          <p className="text-2xl font-bold text-text-primary">{activeNorms.length} / {currentNorms.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4">
          <p className="text-sm text-text-muted mb-1">Avg Norm Strength</p>
          <p className="text-2xl font-bold text-text-primary">{(avgNormStrength * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4">
          <p className="text-sm text-text-muted mb-1">Rounds Tracked</p>
          <p className="text-2xl font-bold text-text-primary">{orderEvolution.length}</p>
        </div>
      </div>

      {/* Order Evolution Timeline */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">International Order Evolution</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          {Object.entries(orderTypeCounts).map(([orderType, count]) => (
            <div key={orderType} className="bg-bg-secondary rounded-lg p-3">
              <OrderTypeBadge orderType={orderType} />
              <p className="text-sm text-text-secondary mt-2">
                {count} rounds ({((count / orderEvolution.length) * 100).toFixed(1)}%)
              </p>
            </div>
          ))}
        </div>
        <div className="overflow-x-auto">
          <div className="flex gap-2 min-w-max">
            {orderEvolution.map((entry, idx) => (
              <div
                key={idx}
                className="flex flex-col items-center bg-bg-secondary rounded-lg p-3 min-w-[120px]"
              >
                <span className="text-xs text-text-muted mb-1">Round {entry.round}</span>
                <OrderTypeBadge orderType={entry.order_type} showChinese={false} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* {orderEvolution.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">International Order Evolution</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            {Object.entries(orderTypeCounts).map(([orderType, count]) => (
              <div key={orderType} className="bg-bg-secondary rounded-lg p-3">
                <OrderTypeBadge orderType={orderType} />
                <p className="text-sm text-text-secondary mt-2">
                  {count} rounds ({((count / orderEvolution.length) * 100).toFixed(1)}%)
                </p>
              </div>
            ))}
          </div>
          <div className="overflow-x-auto">
            <div className="flex gap-2 min-w-max">
              {orderEvolution.map((entry, idx) => (
                <div
                  key={idx}
                  className="flex flex-col items-center bg-bg-secondary rounded-lg p-3 min-w-[120px]"
                >
                  <span className="text-xs text-text-muted mb-1">Round {entry.round}</span>
                  <OrderTypeBadge orderType={entry.order_type} showChinese={false} />
                </div>
              ))}
            </div>
          </div>
        </div>
      )} */}

      {/* Norm Evolution Chart */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Norm Evolution</h2>
          {selectedNormId && (
            <button
              onClick={() => setSelectedNormId(undefined)}
              className="px-3 py-1.5 text-sm bg-bg-tertiary text-text-primary rounded hover:bg-bg-card transition"
            >
              Show All Norms
            </button>
          )}
        </div>
        {normsHistory.size > 0 ? (
          <NormEvolutionChart
            normsHistory={normsHistory}
            selectedNormId={selectedNormId}
            onNormClick={(norm) => setSelectedNormId(norm?.norm_id)}
          />
        ) : (
          <p className="text-text-secondary text-center py-8">
            No norm evolution data available yet. Run the simulation to see norm changes over time.
          </p>
        )}
      </div>

      {/* Norms by Category */}
      {currentNorms.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">Current Norms by Category</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(normsByCategory).map(([category, norms]) => (
              <div key={category} className="bg-bg-secondary rounded-lg p-4">
                <h3 className="font-medium text-text-primary mb-3">{category}</h3>
                <div className="space-y-2">
                  {norms.map((norm) => (
                    <div
                      key={norm.norm_id}
                      onClick={() => setSelectedNormId(norm.norm_id)}
                      className="flex items-center justify-between p-2 bg-white rounded hover:bg-bg-tertiary cursor-pointer transition
                      >
                        <div className="flex-1">
                          <p className="text-sm font-medium">{norm.name}</p>
                          <p className="text-xs text-text-muted">{norm.name_zh}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-bold text-primary">
                            {(norm.strength * 100).toFixed(0)}%
                          </p>
                          <p className="text-xs text-text-muted">
                            {norm.adoption_level.toFixed(2)} adoption
                          </p>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Events Table */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">System Events History</h2>
          <button
            onClick={handleExportEvents}
            disabled={systemicEvents.length === 0}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Export CSV
          </button>
        </div>
        <SystemicEventsTable
          events={systemicEvents}
          onEventClick={setSelectedEvent}
        />
      </div>

      {/* Event Details Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Event Details</h3>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-text-secondary hover:text-text-primary transition"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-3">
              <div>
                <span className="text-sm text-text-muted">Event ID:</span>
                <p className="text-sm font-mono">{selectedEvent.event_id}</p>
              </div>
              <div>
                <span className="text-sm text-text-muted">Type:</span>
                <p className="text-sm">{selectedEvent.event_type}</p>
              </div>
              <div>
                <span className="text-sm text-text-muted">Round:</span>
                <p className="text-sm">{selectedEvent.round}</p>
              </div>
              <div>
                <span className="text-sm text-text-muted">Description:</span>
                <p className="text-sm">{selectedEvent.description}</p>
                <p className="text-sm text-text-muted">{selectedEvent.description_zh}</p>
              </div>
              <div>
                <span className="text-sm text-text-muted">Participants:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {selectedEvent.participants.map((participant, idx) => (
                    <span key={idx} className="px-2 py-1 bg-bg-secondary rounded text-sm">
                      {participant}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <span className="text-sm text-text-muted">Impact Level:</span>
                <div className="mt-1">
                  <div className="w-full bg-bg-secondary rounded-full h-2">
                    <div
                      className="h-full bg-primary rounded-full"
                      style={{ width: `${selectedEvent.impact_level * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-text-secondary mt-1">
                    {(selectedEvent.impact_level * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
              <div>
                <span className="text-sm text-text-muted">Timestamp:</span>
                <p className="text-sm">{new Date(selectedEvent.timestamp).toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SystemInteractionAnalysis;
