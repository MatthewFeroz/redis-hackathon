<script lang="ts">
	import { getStore } from '$lib/stores.svelte';

	const store = getStore();

	const dailyData = $derived(() => {
		const raw = store.analytics?.daily_reviews ?? {};
		const entries = Object.entries(raw).sort(([a], [b]) => a.localeCompare(b));
		const maxVal = Math.max(...entries.map(([, v]) => v), 1);
		return entries.map(([date, count]) => ({
			date,
			count,
			label: new Date(date + 'T00:00:00').toLocaleDateString('en', { weekday: 'short' }),
			height: (count / maxVal) * 100
		}));
	});
</script>

<div class="card-glow p-4 sm:p-5">
	<div class="flex items-center gap-3 mb-5">
		<div class="bg-indigo-500/10 rounded-lg p-2">
			<svg class="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
				<path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
			</svg>
		</div>
		<h2 class="text-lg font-semibold tracking-tight">Reviews This Week</h2>
	</div>

	<div class="flex items-end gap-1.5 sm:gap-3" style="height: 140px;">
		{#each dailyData() as bar, i}
			<div class="flex-1 flex flex-col items-center gap-1 sm:gap-1.5 h-full justify-end min-w-0">
				<span class="text-[10px] sm:text-xs text-slate-400 font-medium">{bar.count}</span>
				<div
					class="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-t opacity-80 hover:opacity-100 transition-opacity"
					style="height: {Math.max(bar.height, 6)}%; min-height: 4px; animation: count-up 0.4s ease-out {i * 0.08}s both;"
				></div>
				<span class="text-[9px] sm:text-[11px] text-slate-500">{bar.label}</span>
			</div>
		{/each}
		{#if dailyData().length === 0}
			<div class="flex-1 flex items-center justify-center text-slate-600 text-sm h-full">No reviews yet</div>
		{/if}
	</div>
</div>
