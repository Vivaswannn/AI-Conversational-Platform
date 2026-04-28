const WS_BASE = import.meta.env.VITE_API_URL
  ? import.meta.env.VITE_API_URL.replace(/^http/, 'ws')
  : '';

export class SalvationSocket {
  private ws: WebSocket | null = null;

  onToken: (token: string) => void = () => {};
  onDone: () => void = () => {};
  onError: (msg: string) => void = () => {};

  constructor(
    private readonly conversationId: string,
    private readonly token: string,
  ) {}

  connect(): void {
    const url = `${WS_BASE}/ws/conversations/${this.conversationId}`;
    this.ws = new WebSocket(url, [`bearer.${this.token}`]);
    this.ws.onmessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data as string) as Record<string, unknown>;
      if (typeof data.token === 'string') this.onToken(data.token);
      else if (data.done === true) this.onDone();
      else if (typeof data.error === 'string') this.onError(data.error);
    };
    this.ws.onerror = () => this.onError('Connection lost. Please try again.');
  }

  send(content: string): void {
    this.ws?.send(JSON.stringify({ content }));
  }

  disconnect(): void {
    this.ws?.close();
    this.ws = null;
  }
}
