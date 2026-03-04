import React, { useEffect, useState } from 'react';
import { useStore } from '../store';
import { agentsAPI, simulationAPI } from '../services/api';
import type { AgentCreateRequest, AgentType, LeadershipType } from '../types';

function AgentsManagement() {
  const {
    agents,
    setAgents,
    addAgent,
    removeAgent,
    setSelectedAgent,
    selectedAgent,
  } = useStore();
  const [showDialog, setShowDialog] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [formData, setFormData] = useState<AgentCreateRequest>({
    agent_id: '',
    name: '',
    name_zh: '',
    agent_type: AgentType.GREAT_POWER,
    leadership_type: LeadershipType.WANGDAO,
    is_active: true,
  });

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const data = await agentsAPI.list();
      setAgents(data);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    }
  };

  const handleLoadPreset = async () => {
    try {
      const data = await agentsAPI.loadPreset('basic');
      setAgents(data);
    } catch (error) {
      console.error('Failed to load preset:', error);
    }
  };

  const handleCreateAgent = async () => {
    try {
      const newAgent = await agentsAPI.create(formData);
      addAgent(newAgent);
      setShowDialog(false);
      resetForm();
    } catch (error) {
      console.error('Failed to create agent:', error);
      alert('Failed to create agent');
    }
  };

  const handleUpdateAgent = async () => {
    if (!selectedAgent) return;

    try {
      await agentsAPI.update(selectedAgent.agent_id, {
        name: formData.name,
        name_zh: formData.name_zh,
        leadership_type: formData.leadership_type,
        is_active: formData.is_active,
      });
      setShowDialog(false);
      resetForm();
      fetchAgents();
    } catch (error) {
      console.error('Failed to update agent:', error);
      alert('Failed to update agent');
    }
  };

  const handleDeleteAgent = async (agentId: string) => {
    if (!confirm('Are you sure you want to delete this agent?')) return;

    try {
      await agentsAPI.delete(agentId);
      removeAgent(agentId);
    } catch (error) {
      console.error('Failed to delete agent:', error);
      alert('Failed to delete agent');
    }
  };

  const openCreateDialog = () => {
    setEditingAgent(null);
    resetForm();
    setShowDialog(true);
  };

  const openEditDialog = (agent: Agent) => {
    setEditingAgent(agent);
    setFormData({
      agent_id: agent.agent_id,
      name: agent.name,
      name_zh: agent.name_zh,
      agent_type: agent.agent_type as AgentType,
      leadership_type: agent.leadership_type as LeadershipType,
      is_active: agent.is_active,
    });
    setShowDialog(true);
  };

  const resetForm = () => {
    setFormData({
      agent_id: '',
      name: '',
      name_zh: '',
      agent_type: AgentType.GREAT_POWER,
      leadership_type: LeadershipType.WANGDAO,
      is_active: true,
    });
  };

  const getLeadershipColor = (type: LeadershipType) => {
    switch (type) {
      case LeadershipType.WANGDAO:
        return 'text-wangdao';
      case LeadershipType.HEGEMON:
        return 'text-hegemon';
      case LeadershipType.QIANGQUAN:
        return 'text-qiangquan';
      case LeadershipType.HUNYONG:
        return 'text-hunyong';
      default:
        return 'text-text-secondary';
    }
  };

  const getLeadershipBadge = (type: LeadershipType) => {
    const labels = {
      [LeadershipType.WANGDAO]: '王道型',
      [LeadershipType.HEGEMON]: '霸权型',
      [LeadershipType.QIANGQUAN]: '强权型',
      [LeadershipType.HUNYONG]: '混合型',
    };
    return labels[type] || type;
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-text-primary">
          Agents Management
        </h1>
        <button
          onClick={openCreateDialog}
          className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
        >
          + Add Agent
        </button>
      </div>

      <div className="flex gap-2 mb-4">
        <button
          onClick={handleLoadPreset}
          className="px-4 py-2 bg-bg-tertiary text-text-primary rounded-lg hover:bg-bg-card transition"
        >
          Load Preset
        </</button>
      </div>

      {/* Agents List */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">All Agents ({agents.length})</h2>
        {agents.length === 0 ? (
          <p className="text-text-secondary">No agents configured. Add agents or load a preset.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent) => (
              <div
                key={agent.agent_id}
                className="bg-bg-secondary rounded-lg p-4"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium">{agent.name}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs ${getLeadershipColor(agent.leadership_type as LeadershipType)}`}>
                    {getLeadershipBadge(agent.leadership_type as LeadershipType)}
                  </span>
                </div>
                <p className="text-sm text-text-secondary mb-2">
                  {agent.name_zh}
                </p>
                {agent.capability_index !== undefined && (
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-sm text-text-muted">Capability:</span>
                    <div className="flex-1 bg-bg-tertiary rounded-full h-2">
                      <div
                        className="h-full bg-primary rounded-full"
                        style={{ width: `${agent.capability_index}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">
                      {agent.capability_index.toFixed(1)}
                    </span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => openEditDialog(agent)}
                    className="flex-1 px-3 py-1.5 bg-bg-tertiary text-text-primary rounded-lg hover:bg-bg-card transition text-sm"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteAgent(agent.agent_id)}
                    className="px-3 py-1.5 bg-error text-white rounded-lg hover:opacity-80 transition text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Agent Dialog */}
      {showDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {editingAgent ? 'Edit Agent' : 'Create Agent'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Agent ID
                </label>
                <input
                  type="text"
                  value={formData.agent_id}
                  onChange={(e) => setFormData({ ...formData, agent_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="agent_1"
                  disabled={!!editingAgent}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="Country Name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Name (Chinese)
                </label>
                <input
                  type="text"
                  value={formData.name_zh}
                  onChange={(e) => setFormData({ ...formData, name_zh: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="国家名称"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Agent Type
                </label>
                <select
                  value={formData.agent_type}
                  onChange={(e) => setFormData({ ...formData, agent_type: e.target.value as AgentType })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value={AgentType.GREAT_POWER}>Great Power</option>
                  <option value={AgentType.SMALL_STATE}>Small State</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Leadership Type
                </label>
                <select
                  value={formData.leadership_type}
                  onChange={(e) => setFormData({ ...formData, leadership_type: e.target.value as LeadershipType })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value={LeadershipType.WANGDAO}>王道型</option>
                  <option value={LeadershipType.HEGEMON}>霸权型</option>
                  <option value={LeadershipType.QIANGQUAN}>强权型</option>
                  <option value={LeadershipType.HUNYONG}>混合型</option>
                </select>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={editingAgent ? handleUpdateAgent : handleCreateAgent}
                className="flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
              >
                {editingAgent ? 'Update' : 'Create'}
              </button>
              <button
                onClick={() => setShowDialog(false)}
                className="flex-1 px-4 py-2 bg-bg-tertiary text-text-primary rounded-lg hover:bg-bg-card transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AgentsManagement;
