/**
 * WebSocket 客户端
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import { AppDispatch } from '../store';
import {
  updateStatus,
  updateProgress,
  addLLMLog,
  updateMetrics,
  addInteraction,
} from '../store/slices/simulationSlice';
import {
  updateAgentPower,
} from '../store/slices/agentsSlice';
import { addNotification } from '../store/slices/uiSlice';

// WebSocket 事件类型
export type WSMessageType = 'decision' | 'action' | 'metrics' | 'round_complete' | 'simulation_complete' | 'error' | 'order_update' | 'agent_state_update' | 'llm_log' | 'interactions_update';

export interface WSMessage {
  type: WSMessageType;
  data: any;
  timestamp: string;
}

export interface DecisionEvent {
  agent_id: string;
  agent_name: string;
  round: number;
  action_type: string;
  target_id?: string;
  reasoning: string;
}

export interface ActionEvent {
  agent_id: string;
  agent_name: string;
  action_type: string;
  target_id?: string;
  parameters: any;
  outcome: any;
  timestamp: string;
}

export interface MetricUpdate {
  round: number;
  metrics: {
    power_concentration: number;
    power_concentration_index: number;
    norm_validity: number;
    conflict_level: number;
    order_type: string;
    power_pattern: string;
    institutionalization: number;
  };
  agent_powers: Record<string, number>;
  agent_supports: Record<string, number>;
}

export interface InteractionsUpdate {
  round: number;
  interactions: {
    round: number;
    initiator_id: string;
    target_id: string | null;
    interaction_type: string;
    timestamp: string;
  }[];
}

export interface RoundComplete {
  round: number;
  decisions: DecisionEvent[];
  actions: ActionEvent[];
  metrics: any;
  duration: number;
}

export interface SimulationComplete {
  simulation_id: string;
  total_rounds: number;
  final_state: any;
  summary: string;
}

// 事件处理器类型
type EventHandler<T> = (data: T) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectDelay: number = 5000;
  private isConnected: boolean = false;
  private eventHandlers: Map<WSMessageType, Set<EventHandler<any>>> = new Map();
  private dispatch: AppDispatch | null = null;
  private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
  private lastMessageTime: number = Date.now();
  private heartbeatTimeout: number = 60000; // 60秒
  private connectionStable: boolean = false;
  private stabilizeTimeout: ReturnType<typeof setTimeout> | null = null;

  constructor(private url: string, dispatch?: AppDispatch) {
    this.dispatch = dispatch || null;
  }

  /**
   * 连接WebSocket服务器
   */
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          this.isConnected = true;
          this.connectionStable = false;
          this.reconnectAttempts = 0;
          this.lastMessageTime = Date.now();

          // 延迟启动心跳检测，等待连接稳定
          this.stopHeartbeat();
          this.stabilizeTimeout = setTimeout(() => {
            this.connectionStable = true;
            this.startHeartbeat();
          }, 3000); // 3秒后认为连接稳定

          if (this.dispatch) {
            this.dispatch(addNotification({
              type: 'success',
              title: '连接成功',
              message: 'WebSocket已连接',
              autoClose: true,
            }));
          }

          resolve();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnected = false;

          if (this.reconnectAttempts === 0) {
            if (this.dispatch) {
              this.dispatch(addNotification({
                type: 'error',
                title: '连接失败',
                message: 'WebSocket连接失败',
                autoClose: true,
              }));
            }
          }

          reject(error);
        };

        this.ws.onclose = () => {
          this.isConnected = false;
          this.connectionStable = false;
          this.stopHeartbeat();
          if (this.stabilizeTimeout) {
            clearTimeout(this.stabilizeTimeout);
            this.stabilizeTimeout = null;
          }

          // 尝试重连
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`WebSocket closed. Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

            setTimeout(() => {
              this.connect().catch(err => console.error('Reconnect failed:', err));
            }, this.reconnectDelay * this.reconnectAttempts);
          } else {
            if (this.dispatch) {
              this.dispatch(addNotification({
                type: 'error',
                title: '连接断开',
                message: 'WebSocket已断开，请刷新页面重试',
                autoClose: false,
              }));
            }
          }
        };

        this.ws.onmessage = (event) => {
          this.lastMessageTime = Date.now();

          try {
            const message: WSMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 断开WebSocket连接
   */
  disconnect(): void {
    this.stopHeartbeat();
    if (this.stabilizeTimeout) {
      clearTimeout(this.stabilizeTimeout);
      this.stabilizeTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.isConnected = false;
    this.connectionStable = false;
    this.eventHandlers.clear();
  }

  /**
   * * 发送消息到服务器
   */
  send(message: any): void {
    if (!this.isConnected || !this.ws) {
      console.warn('WebSocket is not connected');
      return;
    }

    try {
      this.ws.send(JSON.stringify(message));
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
    }
  }

  /**
   * 注册事件处理器
   */
  on(event: WSMessageType, callback: EventHandler<any>): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }

    this.eventHandlers.get(event)!.add(callback);
  }

  /**
   * 移除事件处理器
   */
  off(event: WSMessageType, callback: EventHandler<any>): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.delete(callback);
    }
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(message: WSMessage): void {
    const handlers = this.eventHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message.data);
        } catch (error) {
          console.error('Error in event handler:', error);
        }
      });
    }

    // 默认处理
    this.defaultHandler(message);
  }

  /**
   * 默认消息处理器
   */
  private defaultHandler(message: WSMessage): void {
    if (!this.dispatch) return;

    switch (message.type) {
      case 'decision':
        this.handleDecision(message.data as DecisionEvent);
        break;
      case 'action':
        this.handleAction(message.data as ActionEvent);
        break;
      case 'metrics':
        this.handleMetricUpdate(message.data as MetricUpdate);
        break;
      case 'order_update':
        // 处理秩序类型更新
        this.handleOrderUpdate(message.data);
        break;
      case 'agent_state_update':
        // 处理智能体状态更新
        break;
      case 'round_complete':
        this.handleRoundComplete(message.data as RoundComplete);
        break;
      case 'simulation_complete':
        this.handleSimulationComplete(message.data as SimulationComplete);
        break;
      case 'error':
        if (this.dispatch) {
          this.dispatch(addNotification({
            type: 'error',
            title: '仿真错误',
            message: message.data.message || '未知错误',
          }));
        }
        break;
      case 'llm_log':
        this.handleLLMLog(message.data);
        break;
      case 'interactions_update':
        this.handleInteractionsUpdate(message.data as InteractionsUpdate);
        break;
    }
  }

  /**
   * 处理LLM日志
   */
  private handleLLMLog(data: any): void {
    if (!this.dispatch) return;

    this.dispatch(addLLMLog({
      agent_id: data.agent_id,
      agent_name: data.agent_name,
      request_type: data.request_type,
      content: data.content,
      round: data.round,
      timestamp: data.timestamp,
    }));
  }

  /**
   * 处理决策事件
   */
  private handleDecision(data: DecisionEvent): void {
    // 可以更新相关的UI状态或触发通知
    console.log('Decision received:', data);
  }

  /**
   * 处理行动事件
   */
  private handleAction(data: ActionEvent): void {
    console.log('Action received:', data);

    // 存储互动记录
    if (this.dispatch) {
      this.dispatch(addInteraction({
        round: 0, // 需要从 data 中获取，目前设为0
        initiator_id: data.agent_id,
        target_id: data.target_id,
        interaction_type: data.action_type,
        timestamp: data.timestamp,
      }));
    }
  }

  /**
   * 处理指标更新
   */
  private handleMetricUpdate(data: MetricUpdate): void {
    if (!this.dispatch) return;

    // 添加调试日志
    console.log('Metrics update received:', {
      round: data.round,
      agent_powers: data.agent_powers,
      metrics: data.metrics
    });

    // 根据 power_concentration_index 计算实力模式
    const powerPattern = this.determinePowerPattern({
      power_concentration_index: data.metrics.power_concentration_index || data.metrics.power_concentration || 0
    });

    // 计算实力分布（基于综合实力值的分布）
    const powerDistribution = this.calculatePowerDistribution(data.agent_powers);

    // 更新仿真状态
    this.dispatch(updateStatus({
      current_round: data.round,
      order_type: data.metrics.order_type || '未判定',
      power_pattern: data.metrics.power_pattern || powerPattern,
    }));

    // 更新进度
    this.dispatch(updateProgress({
      current_round: data.round,
    }));

    // 更新智能体实力
    Object.entries(data.agent_powers).forEach(([agentId, power]) => {
      this.dispatch(updateAgentPower({
        agentId,
        power: {
          C: power * 0.2, // 估算基本实体
          E: power * 0.4, // 估算经济实力
          M: power * 0.4, // 估算军事实力
          S: 0.75, // 默认战略目标
          W: 0.75, // 默认国家意志
          comprehensive_power: power,
        },
      }));
    });

    // 更新仪表盘指标数据
    // 注意：后端现在发送正确的字段名
    this.dispatch(updateMetrics({
      round: data.round,
      power_concentration: data.metrics.power_concentration,
      power_concentration_index: data.metrics.power_concentration_index || data.metrics.power_concentration || 0,
      international_norm_effectiveness: data.metrics.international_norm_effectiveness || 0,  // 修复：使用正确的字段名
      conflict_level: data.metrics.conflict_level || 0,
      institutionalization_index: data.metrics.institutionalization_index || data.metrics.institutionalization || 0,  // 修复：使用正确的字段名
      order_type: data.metrics.order_type || '未判定',
      power_pattern: data.metrics.power_pattern || powerPattern,
      agent_powers: data.agent_powers,
      power_distribution: powerDistribution,
    }));
  }

  /**
   * 计算实力分布（基于综合实力值的)
   */
  private calculatePowerDistribution(agentPowers: Record<string, number>): {
    superpower: number;
    great_power: number;
    middle_power: number;
    small_power: number;
  } {
    const powers = Object.values(agentPowers);
    if (powers.length === 0) {
      return { superpower: 0, great_power: 0, middle_power: 0, small_power: 0 };
    }

    // 计算平均值和标准差
    const mean = powers.reduce((sum, p) => sum + p, 0) / powers.length;
    const variance = powers.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / powers.length;
    const stdDev = Math.sqrt(variance);

    // 基于 z-score 分类实力层级
    const distribution = { superpower: 0, great_power: 0, middle_power: 0, small_power: 0 };

    for (const power of powers) {
      const zScore = stdDev > 0 ? (power - mean) / stdDev : 0;

      if (zScore >= 1.5) {
        distribution.superpower++;
      } else if (zScore >= 0.5) {
        distribution.great_power++;
      } else if (zScore >= -0.5) {
        distribution.middle_power++;
      } else {
        distribution.small_power++;
      }
    }

    return distribution;
  }

  /**
   * 处理互动数据更新
   */
  private handleInteractionsUpdate(data: InteractionsUpdate): void {
    if (!this.dispatch) return;

    // 将互动数据添加到 Redux store
    data.interactions.forEach(interaction => {
      this.dispatch(addInteraction({
        round: interaction.round,
        initiator_id: interaction.initiator_id,
        target_id: interaction.target_id,
        interaction_type: interaction.interaction_type,
        action_content: (interaction as any).action_content || '',  // 确保 action_content 被传递
        timestamp: interaction.timestamp,
      }));
    });

    console.log(`Received ${data.interactions.length} interactions for round ${data.round}`);
  }

  /**
   * 处理秩序类型更新
   */
  private handleOrderUpdate(data: any): void {
    if (!this.dispatch) return;

    // 计算实力分布
    const powerPattern = this.determinePowerPattern(data.indicators);
    const powerDistribution = this.calculatePowerDistribution(data.indicators?.agent_powers || {});

    // 提取指标数据
    const indicators = data.indicators || {};

    // 更新仿真状态中的秩序类型
    this.dispatch(updateStatus({
      order_type: data.order_type || '未判定',
      power_pattern: powerPattern,
    }));

    // 更新仪表盘指标数据（使 indicators 与 metrics 数据同步）
    // 注意：后端发送的字段名可能与前端期望不完全一致，需要映射
    this.dispatch(updateMetrics({
      round: data.round || 0,
      power_concentration: indicators.power_concentration || indicators.power_concentration_index || 0,
      power_concentration_index: indicators.power_concentration_index || 0,
      international_norm_effectiveness: indicators.international_norm_effectiveness || 0,
      conflict_level: indicators.conflict_level || 0,
      institutionalization_index: indicators.institutionalization_index || indicators.institutionalization || 0,
      order_type: data.order_type || '未判定',
      power_pattern: powerPattern,
      agent_powers: indicators.agent_powers || {},
      power_distribution: powerDistribution,
    }));

    console.log('Order update received:', data);
  }

  /**
   * 根据指标确定实力模式
   */
  private determinePowerPattern(indicators: any): string {
    if (!indicators) return '未判定';

    const powerConcentration = indicators.power_concentration_index || 0;

    if (powerConcentration > 60) {
      return '单极主导';
    } else if (powerConcentration > 40) {
      return '多极均衡';
    } else if (powerConcentration > 20) {
      return '力量分散';
    } else {
      return '未判定';
    }
  }

  /**
   * 处理轮次完成
   */
  private handleRoundComplete(data: RoundComplete): void {
    if (!this.dispatch) { }

    this.dispatch(addNotification({
      type: 'info',
      title: '轮次完成',
      message: `第 ${data.round} 轮已完成`,
      autoClose: true,
    }));
  }

  /**
   * 处理仿真完成
   */
  private handleSimulationComplete(data: SimulationComplete): void {
    if (!this.dispatch) return;

    this.dispatch(updateStatus({
      is_running: false,
      is_paused: false,
    }));

    this.dispatch(addNotification({
      type: 'success',
      title: '仿真完成',
      message: '所有轮次已完成，您可以查看结果',
      autoClose: false,
    }));
  }

  /**
   * 启动心跳检测
   */
  private startHeartbeat(): void {
    // 每30秒发送一次ping
    this.heartbeatInterval = setInterval(() => {
      const now = Date.now();

      // 只有在连接稳定后才检测超时
      if (this.connectionStable && now - this.lastMessageTime > this.heartbeatTimeout) {
        console.warn('No heartbeat received, reconnecting...');
        this.disconnect();
        this.connect().catch(err => console.error('Reconnect failed:', err));
      } else if (this.isConnected && this.isReady()) {
        // 发送ping
        this.send({ type: 'ping', timestamp: now });
      }
    }, 30000); // 30秒心跳间隔
  }

  /**
   * 停止心跳检测
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * 检查连接状态
   */
  isReady(): boolean {
    return this.isConnected && this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * 决策事件处理器（便捷方法）
   */
  onDecision(callback: EventHandler<DecisionEvent>): void {
    this.on('decision', callback);
  }

  /**
   * 行动事件处理器（便捷方法）
   */
  onAction(callback: EventHandler<ActionEvent>): void {
    this.on('action', callback);
  }

  /**
   * 指标更新事件处理器（便捷方法）
   */
  onMetricUpdate(callback: EventHandler<MetricUpdate>): void {
    this.on('metrics', callback);
  }

  /**
    * 轮次完成事件处理器（便捷方法）
    */
  onRoundComplete(callback: EventHandler<RoundComplete>): void {
    this.on('round_complete', callback);
  }

  /**
   * 仿真完成事件处理器（便捷方法）
   */
  onSimulationComplete(callback: EventHandler<SimulationComplete>): void {
    this.on('simulation_complete', callback);
  }
}

// 创建全局WebSocket客户端实例管理器
let wsClients: Map<string, WebSocketClient> = new Map();
let globalCurrentSimulationId: string | null = null;

export const getWebSocketClient = (url?: string, dispatch?: AppDispatch): WebSocketClient => {
  if (!url) {
    const defaultClient = wsClients.get('default');
    return defaultClient || null;
  }

  // 如果URL已存在且与当前仿真ID相同，返回现有客户端
  if (wsClients.has(url) && globalCurrentSimulationId === url) {
    const existingClient = wsClients.get(url);
    return existingClient!;
  }

  // 断开旧连接
  wsClients.forEach((client) => {
    client.disconnect();
  });
  wsClients.clear();

  // 创建新客户端
  const wsClient = new WebSocketClient(url, dispatch);
  wsClients.set(url, wsClient);
  globalCurrentSimulationId = url;

  console.log(`Created WebSocket client for: ${url}`);

  return wsClient;
};

export const disconnectWebSocket = (url?: string): void => {
  if (url) {
    const client = wsClients.get(url);
    if (client) {
      client.disconnect();
      wsClients.delete(url);
    }
  } else {
    // 断开所有连接
    wsClients.forEach((client) => {
      client.disconnect();
    });
    wsClients.clear();
    globalCurrentSimulationId = null;
  }
};

export default WebSocketClient;
