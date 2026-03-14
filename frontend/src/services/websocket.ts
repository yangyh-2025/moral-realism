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
} from '../store/slices/simulationSlice';
import {
  updateAgentPower,
  updateAgentSupport,
} from '../store/slices/agentsSlice';
import { addEvent } from '../store/slices/eventsSlice';
import { addNotification } from '../store/slices/uiSlice';

// WebSocket 事件类型
export type WSMessageType = 'decision' | 'action' | 'metric_update' | 'round_complete' | 'simulation_complete' | 'error';

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
    norm_validity: number;
    conflict_level: number;
    order_type: string;
  };
  agent_powers: Record<string, number>;
  agent_supports: Record<string, number>;
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
  private reconnectDelay: number = 3000;
  private isConnected: boolean = false;
  private eventHandlers: Map<WSMessageType, Set<EventHandler<any>>> = new Map();
  private dispatch: AppDispatch | null = null;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private lastMessageTime: number = Date.now();
  private heartbeatTimeout: number = 30000; // 30秒

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
          this.reconnectAttempts = 0;
          this.startHeartbeat();

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
          this.stopHeartbeat();

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

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.isConnected = false;
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
      case 'metric_update':
        this.handleMetricUpdate(message.data as MetricUpdate);
        break;
      case 'round_complete':
        this.handleRoundComplete(message.data as RoundComplete);
        break;
      case 'simulation_complete':
        this.handleSimulationComplete(message.data as SimulationComplete);
        break;
      case 'error':
        this.dispatch(addNotification({
          type: 'error',
          title: '仿真错误',
          message: message.data.message || '未知错误',
        }));
        break;
    }
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
  }

  /**
   * 处理指标更新
   */
  private handleMetricUpdate(data: MetricUpdate): void {
    if (!this.dispatch) return;

    // 更新仿真状态
    this.dispatch(updateStatus({
      current_round: data.round,
      order_type: data.metrics.order_type,
      ...data.metrics,
    }));

    // 更新进度
    this.dispatch(updateProgress({
      current_round: data.round,
    }));

    // 更新智能体实力
    Object.entries(data.agent_powers).forEach(([agentId, power]) => {
      this.dispatch(updateAgentPower({
        agentId,
        power_metrics: { comprehensive_power: power },
      }));
    });
  }

  /**
   * 处理轮次完成
   */
  private handleRoundComplete(data: RoundComplete): void {
    if (!this.dispatch) return;

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
    this.heartbeatInterval = setInterval(() => {
      const now = Date.now();
      if (now - this.lastMessageTime > this.heartbeatTimeout) {
        console.warn('No heartbeat received, reconnecting...');
        this.disconnect();
        this.connect().catch(err => console.error('Reconnect failed:', err));
      } else {
        // 发送ping
        this.send({ type: 'ping', timestamp: now });
      }
    }, this.heartbeatTimeout / 2);
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
    this.on('metric_update', callback);
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

// 创建全局WebSocket客户端实例
let wsClient: WebSocketClient | null = null;

export const getWebSocketClient = (url?: string, dispatch?: AppDispatch): WebSocketClient => {
  if (!wsClient) {
    const wsUrl = url || import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/simulation/default';
    wsClient = new WebSocketClient(wsUrl, dispatch);
  }
  return wsClient;
};


export const disconnectWebSocket = (): void => {
  if (wsClient) {
    wsClient.disconnect();
    wsClient = null;
  }
};

export default WebSocketClient;
