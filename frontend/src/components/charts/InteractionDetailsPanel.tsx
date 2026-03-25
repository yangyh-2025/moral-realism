/**
 * 互动详情面板
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

interface Interaction {
  source_agent: string;
  target_agent: string;
  interaction_type: string;
  action_content: string;
  count: number;
}

interface Agent {
  id: string;
  name: string;
}

interface InteractionDetailsPanelProps {
  interaction: Interaction;
  agents: Agent[];
  onClose: () => void;
}

const InteractionDetailsPanel: React.FC<InteractionDetailsPanelProps> = ({
  interaction,
  agents,
  onClose,
}) => {
  const initiatorAgent = agents.find(a => a.id === interaction.source_agent);
  const targetAgent = agents.find(a => a.id === interaction.target_agent);

  return React.createElement('div', { className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50' },
    React.createElement('div', { className: 'bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-80vh overflow-y-auto' },
      // 标题栏
      React.createElement('div', { className: 'flex justify-between items-center p-6 border-b border-gray-200' },
        React.createElement('h3', { className: 'text-xl font-semibold text-gray-900' }, '互动详情'),
        React.createElement('button', {
          onClick: onClose,
          className: 'text-gray-500 hover:text-gray-700 text-2xl font-light transition-colors'
        }, '×')
      ),

      // 内容
      React.createElement('div', { className: 'p-6 space-y-4' },
        // 发起国家
        React.createElement('div', { className: 'bg-gray-50 rounded-lg p-4' },
          React.createElement('div', { className: 'text-sm font-medium text-gray-600 mb-1' }, '发起国家'),
          React.createElement('div', { className: 'text-lg font-semibold text-gray-900' }, initiatorAgent?.name || interaction.source_agent)
        ),

        // 目标国家
        React.createElement('div', { className: 'bg-gray-50 rounded-lg p-4' },
          React.createElement('div', { className: 'text-sm font-medium text-gray-600 mb-1' }, '目标国家'),
          React.createElement('div', { className: 'text-lg font-semibold text-gray-900' }, targetAgent?.name || interaction.target_agent)
        ),

        // 行动类型
        React.createElement('div', { className: 'bg-blue-50 rounded-lg p-4 border border-blue-200' },
          React.createElement('div', { className: 'text-sm font-medium text-blue-700 mb-1' }, '行动类型'),
          React.createElement('div', { className: 'text-lg font-semibold text-blue-900' }, interaction.interaction_type)
        ),

        // 行动内容
        interaction.action_content && React.createElement('div', { className: 'bg-gray-50 rounded-lg p-4' },
          React.createElement('div', { className: 'text-sm font-medium text-gray-600 mb-2' }, '行动内容'),
          React.createElement('p', { className: 'text-gray-700 leading-relaxed bg-white p-4 rounded border border-gray-200' }, interaction.action_content)
        ),

        // 互动次数
        React.createElement('div', { className: 'bg-gray-50 rounded-lg p-4' },
          React.createElement('div', { className: 'text-sm font-medium text-gray-600 mb-1' }, '互动次数'),
          React.createElement('div', { className: 'text-lg font-semibold text-gray-900' }, String(interaction.count))
        )
      ),

      // 底部按钮
      React.createElement('div', { className: 'flex justify-end p-6 border-t border-gray-200' },
        React.createElement('button', {
          onClick: onClose,
          className: 'px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium'
        }, '关闭')
      )
    )
  );
};

export default InteractionDetailsPanel;
