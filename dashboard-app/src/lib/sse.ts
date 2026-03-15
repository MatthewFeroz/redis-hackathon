type SSECallback = (data: Record<string, string>) => void;

export function connectSSE(onNotification: SSECallback): () => void {
	let source: EventSource | null = null;
	let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

	function connect() {
		source = new EventSource('/api/notifications');

		source.addEventListener('notification', (e: MessageEvent) => {
			try {
				const data = JSON.parse(e.data);
				onNotification(data);
			} catch {
				// ignore malformed data
			}
		});

		source.onerror = () => {
			source?.close();
			reconnectTimer = setTimeout(connect, 5000);
		};
	}

	connect();

	return () => {
		source?.close();
		if (reconnectTimer) clearTimeout(reconnectTimer);
	};
}
