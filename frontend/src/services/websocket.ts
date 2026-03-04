// WebSocket service for real-time simulation updates
import { useStore } from '../store';

const WS_BASE_URL = 'ws://localhost:8000';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private heartbeatInterval: number | null = null;

  constructor(private simulationId: string = 'default') {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      try {
        this.ws = new WebSocket(`${WS_BASE_URL}/ws/simulation/${this.simulationId}`);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          useStore.getState().setIsConnected(true);
          this.startHeartbeat();
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event.data);
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          useStore.getState().setIsConnected(false);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          useStore.getState().setIsConnected(false);
          this.stopHeartbeat();
          this.tryReconnect();
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.stopHeartbeat();
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = window.setInterval(() => {
      this.send({ type: 'ping' });
    }, 30000); // Send ping every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private tryReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);

      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  send(message: object): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  private handleMessage(data: string): void {
    try {
      const message = JSON.parse(data);
      const store = useStore.getState();

      switch (message.type) {
        case 'connected':
          console.log('WebSocket connection confirmed');
          break;

        case 'round_start':
          console.log(`Round ${message.round} started`);
          break;

        case 'round_complete':
          console.log(`Round ${message.round} completed`);
          if (message.metrics) {
            store.setCurrentMetrics(message.metrics);
            store.addMetricsHistory(message.metrics);
          }
          break;

        case 'simulation_complete':
          console.log('Simulation completed', message.summary);
          store.setSimulationStatus({
            status: 'completed' as any,
            ...message.summary,
          });
          break;

        case 'error':
          console.error('Simulation error:', message.error);
          store.addLog({
            timestamp: new Date().toISOString(),
            level: 'ERROR',
            message: message.error || 'Unknown error',
          });
          break;

        case 'log':
          if (message.level && message.message) {
            store.addLog({
              timestamp: message.timestamp || new Date().toISOString(),
              level: message.level,
              message: message.message,
            });
          }
          break;

        case 'checkpoint_saved':
          console.log('Checkpoint saved:', message.checkpoint_id);
          break;

        case 'metrics_update':
          if (message.metrics) {
            store.setCurrentMetrics(message.metrics);
          }
          break;

        case 'status_update':
          if (message.status) {
            store.setSimulationStatus({
              status: message.status as any,
              ...message.state,
            });
          }
          break;

        default:
          console.log('Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Global WebSocket service instance
let wsService: WebSocketService | null = null;

export function getWebSocketService(): WebSocketService {
  if (!wsService) {
    wsService = new WebSocketService();
  }
  return wsService;
}

export function disconnectWebSocket(): void {
  if (wsService) {
    wsService.disconnect();
    wsService = null;
  }
}
