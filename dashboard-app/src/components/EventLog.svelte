<script lang="ts">
	import { getStore } from '$lib/stores.svelte';

	const store = getStore();

	const eventColors: Record<string, { dot: string; text: string }> = {
		job_completed: { dot: 'bg-blue-400', text: 'text-blue-400' },
		customer_contacted: { dot: 'bg-indigo-400', text: 'text-indigo-400' },
		review_started: { dot: 'bg-amber-400', text: 'text-amber-400' },
		review_submitted: { dot: 'bg-emerald-400', text: 'text-emerald-400' }
	};

	function getColor(event: string) {
		return eventColors[event] ?? { dot: 'bg-slate-400', text: 'text-slate-400' };
	}

	function formatTime(ts: string) {
		return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
	}
</script>

<div class="card-glow p-5">
	<div class="flex items-center gap-3 mb-4">
		<div class="bg-orange-500/10 rounded-lg p-2">
			<svg class="w-5 h-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
				<path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
			</svg>
		</div>
		<div>
			<h2 class="text-lg font-semibold tracking-tight">Event Log</h2>
			<p class="text-xs text-slate-500 font-[family-name:var(--font-mono)]">Redis Streams · XREVRANGE</p>
		</div>
		<span class="ml-auto text-[10px] text-slate-600 font-[family-name:var(--font-mono)]">{store.events.length} events</span>
	</div>

	<div class="max-h-64 overflow-y-auto space-y-0.5 pr-1">
		{#each store.events as event, i (event.id)}
			{@const colors = getColor(event.event)}
			<div
				class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-surface-700/30 transition-colors group"
				style="animation: count-up 0.2s ease-out {Math.min(i * 0.03, 0.5)}s both"
			>
				<span class="w-2 h-2 rounded-full {colors.dot} shrink-0"></span>
				<span class="{colors.text} text-xs font-medium font-[family-name:var(--font-mono)] w-36 truncate">{event.event}</span>
				<span class="text-xs text-slate-600 font-[family-name:var(--font-mono)] truncate flex-1">{event.session_id}</span>
				<span class="text-[10px] text-slate-600 font-[family-name:var(--font-mono)] shrink-0 tabular-nums">{formatTime(event.timestamp)}</span>
			</div>
		{:else}
			<div class="text-center py-8 text-slate-600 text-sm">No events recorded yet</div>
		{/each}
	</div>
</div>
