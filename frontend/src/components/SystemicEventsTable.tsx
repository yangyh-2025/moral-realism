import React, { useState } from 'react';
import type { SystemicEvent } from '../types';

interface SystemicEventsTableProps {
  events: SystemicEvent[];
  onEventClick?: (event: SystemicEvent) => void;
}

const SystemicEventsTable: React.FC<SystemicEventsTableProps> = ({ events, onEventClick }) => {
  const [filter, setFilter] = useState<string>('');
  const [roundFilter, setRoundFilter] = useState<number> | null>(null);
  const [participantFilter, setParticipantFilter] = useState<string>('');

  const filteredEvents = events.filter((event) => {
    if (filter && event.event_type !== filter) return false;
    if (roundFilter !== null && event.round !== roundFilter) return false;
    if (participantFilter && !event.participants.includes(participantFilter)) return false;
    return true;
  });

  const eventTypeColors: Record<string, string> = {
    order_shaping: 'bg-purple-100 text-purple-700',
    norm_evolution: 'bg-blue-100 text-blue-700',
    values_competition: 'bg-amber-100 text-amber-700',
    conflict_emergence: 'bg-red-100 text-red-700',
    cooperation_strengthening: 'bg-green-100 text-green-700',
  };

  const eventTypeLabels: Record<string, string> = {
    order_shaping: 'Order Shaping',
    norm_evolution: 'Norm Evolution',
    values_competition: 'Values Competition',
    conflict_emergence: 'Conflict',
    cooperation_strengthening: 'Cooperation',
  };

  const uniqueEventTypes = Array.from(new Set(events.map((e) => e.event_type)));
  const uniqueRounds = Array.from(new Set(events.map((e) => e.round))).sort((a, b) => b - a);
  const uniqueParticipants = Array.from(new Set(events.flatMap((e) => e.participants))).sort();

  const getImpactBadge = (impact: number) => {
    if (impact >= 0.8) return { text: 'Critical', color: 'bg-red-500 text-white' };
    if (impact >= 0.6) return { text: 'High', color: 'bg-orange-500 text-white' };
    if (impact >= 0.4) return { text: 'Medium', color: 'bg-yellow-500 text-black' };
    return { text: 'Low', color: 'bg-green-500 text-white' };
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="bg-bg-secondary rounded-lg p-4 space-y-3">
        <h3 className="text-sm font-semibold text-text-primary">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Event Type Filter */}
          <div>
            <label className="block text-xs text-text-secondary mb-1">Event Type</label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-light"
            >
              <option value="">All Types</option>
              {uniqueEventTypes.map((type) => (
                <option key={type} value={type}>
                  {eventTypeLabels[type] || type}
                </option>
              ))}
            </select>
          </div>

          {/* Round Filter */}
          <div>
            <label className="block text-xs text-text-secondary mb-1">Round</label>
            <select
              value={roundFilter?.toString() || ''}
              onChange={(e) => setRoundFilter(e.target.value ? parseInt(e.target.value) : null)}
              className="w-full px-3 py-2 bg-white border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-light"
            >
              <option value="">All Rounds</option>
              {uniqueRounds.map((round) => (
                <option key={round} value={round.toString()}>
                  Round {round}
                </option>
              ))}
            </select>
          </div>

          {/* Participant Filter */}
          <div>
            <label className="block text-xs text-text-secondary mb-1">Participant</label>
            <select
              value={participantFilter}
              onChange={(e) => setParticipantFilter(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-light"
            >
              <option value="">All Participants</option>
              {uniqueParticipants.map((participant) => (
                <option key={participant} value={participant}>
                  {participant}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Clear Filters Button */}
        {(filter || roundFilter !== null || participantFilter) && (
          <button
            onClick={() => {
              setFilter('');
              setRoundFilter(null);
              setParticipantFilter('');
            }}
            className="text-sm text-primary hover:text-primary-dark transition"
          >
            Clear all filters
          </button>
        )}
      </div>

      {/* Events Table */}
      <div className="bg-white border border-border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-bg-secondary">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Round
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Type
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Description
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Participants
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Impact
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {filteredEvents.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-text-muted">
                  No events found matching the current filters
                </td>
              </tr>
            ) : (
              filteredEvents.map((event) => {
                const impactBadge = getImpactBadge(event.impact_level);
                const eventTypeColor = eventTypeColors[event.event_type] || 'bg-gray-100 text-gray-700';
                const eventTypeLabel = eventTypeLabels[event.event_type] || event.event_type;

                return (
                  <tr
                    key={event.event_id}
                    onClick={() => onEventClick?.(event)}
                    className="hover:bg-bg-secondary cursor-pointer transition"
                  >
                    <td className="px-4 py-3 text-sm text-text-primary font-medium">
                      {event.round}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${eventTypeColor}`}>
                        {eventTypeLabel}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-text-primary max-w-xs truncate">
                      {event.description_zh || event.description}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {event.participants.map((participant, idx) => (
                          <span
                            key={idx}
                            className="inline-block px-2 py-0.5 bg-bg-tertiary rounded text-xs text-text-secondary"
                          >
                            {participant}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${impactBadge.color}`}>
                        {impactBadge.text}
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      <div className="text-sm text-text-secondary">
        Showing {filteredEvents.length} of {events.length} events
      </div>
    </div>
  );
};

export default SystemicEventsTable;
