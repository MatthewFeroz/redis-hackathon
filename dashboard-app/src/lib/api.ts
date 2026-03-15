import type {
	Session,
	ChatMessage,
	Analytics,
	DetailedAnalytics,
	RedisStatCard,
	PipelineEvent,
	JobCreatePayload,
	JobResponse
} from './types';

const BASE = '';

async function get<T>(url: string): Promise<T> {
	const res = await fetch(`${BASE}${url}`);
	if (!res.ok) throw new Error(`GET ${url} failed: ${res.status}`);
	return res.json();
}

async function post<T>(url: string, body: unknown): Promise<T> {
	const res = await fetch(`${BASE}${url}`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	});
	if (!res.ok) throw new Error(`POST ${url} failed: ${res.status}`);
	return res.json();
}

export const api = {
	getSessions: () => get<Session[]>('/api/sessions'),
	getAnalytics: () => get<Analytics>('/api/analytics'),
	getDetailedAnalytics: () => get<DetailedAnalytics>('/api/analytics/detailed'),
	getEvents: (count = 50) => get<PipelineEvent[]>(`/api/events?count=${count}`),
	getRedisStats: () => get<RedisStatCard[]>('/api/redis-stats'),
	getSessionHistory: (id: string) => get<ChatMessage[]>(`/api/sessions/${id}/history`),
	createJob: (payload: JobCreatePayload) => post<JobResponse>('/api/jobs', payload)
};
