function getWsBase(): string {
  const configured = import.meta.env.VITE_API_URL?.trim();
  if (configured) return configured.replace(/^http/i, 'ws').replace(/\/+$/, '');

  // In local dev, VITE_API_URL is intentionally unset and Vite proxy handles /ws.
  // Build an absolute ws(s) URL from current browser origin.
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  return `${protocol}://${window.location.host}`;
}

export class SalvationSocket {
  private ws: WebSocket | null = null;
  private pending: string[] = [];

  onToken: (token: string) => void = () => {};
  onDone: () => void = () => {};
  onError: (msg: string) => void = () => {};

  constructor(
    private readonly conversationId: string,
    private readonly token: string,
  ) {}

  connect(): void {
    const url = `${getWsBase()}/ws/conversations/${this.conversationId}`;
    this.ws = new WebSocket(url, [`bearer.${this.token}`]);
    this.ws.onopen = () => {
      if (this.pending.length === 0) return;
      for (const payload of this.pending) this.ws?.send(payload);
      this.pending = [];
    };
    this.ws.onmessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data as string) as Record<string, unknown>;
      if (typeof data.token === 'string') this.onToken(data.token);
      else if (data.done === true) this.onDone();
      else if (typeof data.error === 'string') this.onError(data.error);
    };
    this.ws.onerror = () => this.onError('Connection lost. Please try again.');
  }

  send(content: string): void {
    const payload = JSON.stringify({ content });
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(payload);
      return;
    }
    // If user sends quickly after mounting, hold message until socket opens.
    this.pending.push(payload);
  }

  disconnect(): void {
    this.ws?.close();
    this.ws = null;
    this.pending = [];
  }
}
