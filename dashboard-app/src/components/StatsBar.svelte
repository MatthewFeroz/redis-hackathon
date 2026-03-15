<script lang="ts">
	import { getStore } from '$lib/stores.svelte';

	const store = getStore();

	const cards = $derived([
		{
			label: 'Reviews Today',
			value: store.analytics?.reviews_today ?? 0,
			color: 'emerald',
			icon: `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>`,
			gradient: 'from-emerald-500/20 to-emerald-500/5'
		},
		{
			label: 'Total Customers',
			value: store.analytics?.total_sessions ?? 0,
			color: 'blue',
			icon: `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>`,
			gradient: 'from-blue-500/20 to-blue-500/5'
		},
		{
			label: 'Completion Rate',
			value: store.analytics?.completion_rate ?? 0,
			suffix: '%',
			color: 'amber',
			icon: `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>`,
			gradient: 'from-amber-500/20 to-amber-500/5'
		}
	]);

	const colorMap: Record<string, { ring: string; text: string; bg: string }> = {
		emerald: { ring: 'ring-emerald-500/30', text: 'text-emerald-400', bg: 'bg-emerald-500/10' },
		blue: { ring: 'ring-blue-500/30', text: 'text-blue-400', bg: 'bg-blue-500/10' },
		amber: { ring: 'ring-amber-500/30', text: 'text-amber-400', bg: 'bg-amber-500/10' }
	};
</script>

<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
	{#each cards as card, i}
		{@const colors = colorMap[card.color]}
		<div
			class="card-glow p-5 ring-1 {colors.ring} group hover:ring-2 transition-all duration-300"
			style="animation: count-up 0.4s cubic-bezier(0.16, 1, 0.3, 1) {i * 0.1}s both"
		>
			<div class="flex items-start justify-between">
				<div>
					<p class="text-xs font-medium uppercase tracking-widest text-slate-400 mb-2">{card.label}</p>
					<p class="text-4xl font-bold {colors.text} tracking-tight">
						{card.value}{card.suffix ?? ''}
					</p>
				</div>
				<div class="{colors.bg} rounded-lg p-2.5 {colors.text}">
					{@html card.icon}
				</div>
			</div>
		</div>
	{/each}
</div>
