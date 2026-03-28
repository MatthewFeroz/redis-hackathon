import type {
	Session,
	DetailedAnalytics,
	ChatMessage,
	MeResponse,
	PipelineEvent,
	RedisStatCard
} from './types';
import { api } from './api';

let sessions = $state<Session[]>([]);
let sessionsLoading = $state(false);
let analytics = $state<DetailedAnalytics | null>(null);
let me = $state<MeResponse | null>(null);
let events = $state<PipelineEvent[]>([]);
let redisStats = $state<RedisStatCard[]>([]);
let selectedSessionId = $state<string | null>(null);
let chatHistory = $state<ChatMessage[]>([]);
let chatLoading = $state(false);
let toasts = $state<{ id: number; message: string }[]>([]);
let toastCounter = $state(0);
let activeFilter = $state('all');
let searchQuery = $state('');

export function getStore() {
	const filteredSessions = $derived(
		sessions.filter((s) => {
			const matchesFilter = activeFilter === 'all' || s.status === activeFilter;
			const matchesSearch =
				!searchQuery || s.customer_name.toLowerCase().includes(searchQuery.toLowerCase());
			return matchesFilter && matchesSearch;
		})
	);

	return {
		get sessions() { return sessions; },
		get filteredSessions() { return filteredSessions; },
		get sessionsLoading() { return sessionsLoading; },
		get analytics() { return analytics; },
		get me() { return me; },
		set me(value: MeResponse | null) { me = value; },
		get events() { return events; },
		get redisStats() { return redisStats; },
		get selectedSessionId() { return selectedSessionId; },
		set selectedSessionId(v: string | null) { selectedSessionId = v; },
		get chatHistory() { return chatHistory; },
		get chatLoading() { return chatLoading; },
		get toasts() { return toasts; },
		get activeFilter() { return activeFilter; },
		set activeFilter(v: string) { activeFilter = v; },
		get searchQuery() { return searchQuery; },
		set searchQuery(v: string) { searchQuery = v; },

		async loadSessions() {
			sessionsLoading = true;
			try {
				sessions = await api.getSessions();
			} finally {
				sessionsLoading = false;
			}
		},

		async loadAnalytics() {
			analytics = await api.getDetailedAnalytics();
		},

		async loadEvents() {
			events = await api.getEvents();
		},

		async loadRedisStats() {
			redisStats = await api.getRedisStats();
		},

		async openConversation(sessionId: string) {
			selectedSessionId = sessionId;
			chatLoading = true;
			try {
				chatHistory = await api.getSessionHistory(sessionId);
			} finally {
				chatLoading = false;
			}
		},

		closeConversation() {
			selectedSessionId = null;
			chatHistory = [];
		},

		addToast(message: string) {
			const id = ++toastCounter;
			toasts = [...toasts, { id, message }];
			setTimeout(() => {
				toasts = toasts.filter((t) => t.id !== id);
			}, 5000);
		},

		async refreshAll() {
			await Promise.all([
				this.loadSessions(),
				this.loadAnalytics(),
				this.loadEvents(),
				this.loadRedisStats()
			]);
		}
	};
}
