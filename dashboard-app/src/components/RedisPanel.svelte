<script lang="ts">
	import { getStore } from '$lib/stores.svelte';

	const store = getStore();

	const typeIcons: Record<string, string> = {
		'JSON': '{ }',
		'List': '[ ]',
		'Stream': '≫',
		'Pub/Sub': '⚡',
		'Sorted Set': '⇅',
		'Vector Set': '◎',
		'Key Expiry': '⏱'
	};

	const typeColors: Record<string, { border: string; text: string; badge: string; glow: string }> = {
		'JSON': { border: 'border-sky-500/30', text: 'text-sky-400', badge: 'bg-sky-500/15 text-sky-400', glow: 'shadow-sky-500/10' },
		'List': { border: 'border-violet-500/30', text: 'text-violet-400', badge: 'bg-violet-500/15 text-violet-400', glow: 'shadow-violet-500/10' },
		'Stream': { border: 'border-orange-500/30', text: 'text-orange-400', badge: 'bg-orange-500/15 text-orange-400', glow: 'shadow-orange-500/10' },
		'Pub/Sub': { border: 'border-yellow-500/30', text: 'text-yellow-400', badge: 'bg-yellow-500/15 text-yellow-400', glow: 'shadow-yellow-500/10' },
		'Sorted Set': { border: 'border-pink-500/30', text: 'text-pink-400', badge: 'bg-pink-500/15 text-pink-400', glow: 'shadow-pink-500/10' },
		'Vector Set': { border: 'border-teal-500/30', text: 'text-teal-400', badge: 'bg-teal-500/15 text-teal-400', glow: 'shadow-teal-500/10' },
		'Key Expiry': { border: 'border-rose-500/30', text: 'text-rose-400', badge: 'bg-rose-500/15 text-rose-400', glow: 'shadow-rose-500/10' }
	};

	function getColors(type: string) {
		return typeColors[type] ?? { border: 'border-slate-500/30', text: 'text-slate-400', badge: 'bg-slate-500/15 text-slate-400', glow: '' };
	}
</script>

<div class="space-y-4">
	<!-- Header -->
	<div class="flex items-center gap-4">
		<div class="flex items-center gap-3">
			<!-- Redis logo mark -->
			<div class="relative">
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-red-600 to-red-800 flex items-center justify-center shadow-lg shadow-red-500/20">
					<svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
						<path d="M10.5 2.661l.54.997-1.797.644 2.409.218.748 1.246.467-1.397 2.326-.252-1.864-.586.543-1.07L12.066 3.7l-1.566-1.04zm-3.88 4.278L2 9.721l7.932 3.283 8.564-3.127-4.597-2.782-7.28-.156zM2 14.809l7.932 3.283 8.564-3.127L12 12.036l-10 2.773z"/>
					</svg>
				</div>
				<div class="absolute -top-0.5 -right-0.5 w-3 h-3 bg-emerald-400 rounded-full border-2 border-surface-900" style="animation: pulse-glow 2s infinite"></div>
			</div>
			<div>
				<h2 class="text-lg font-bold tracking-tight text-white">Redis Infrastructure</h2>
				<p class="text-xs text-slate-500 font-[family-name:var(--font-mono)]">7 data structures · live cluster view</p>
			</div>
		</div>
		<div class="ml-auto flex items-center gap-2 bg-emerald-500/10 rounded-full px-3 py-1">
			<span class="w-2 h-2 rounded-full bg-emerald-400" style="animation: pulse-glow 2s infinite"></span>
			<span class="text-xs font-medium text-emerald-400">Connected</span>
		</div>
	</div>

	<!-- Grid -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
		{#each store.redisStats as stat, i}
			{@const colors = getColors(stat.type)}
			<div
				class="card-redis group {colors.border} hover:shadow-lg {colors.glow} transition-all duration-300"
				style="animation: count-up 0.4s cubic-bezier(0.16, 1, 0.3, 1) {i * 0.06}s both"
			>
				<div class="p-4">
					<!-- Type icon + badge -->
					<div class="flex items-start justify-between mb-3">
						<span class="text-2xl {colors.text} font-[family-name:var(--font-mono)] opacity-60 group-hover:opacity-100 transition-opacity">
							{typeIcons[stat.type] ?? '?'}
						</span>
						<span class="{colors.badge} text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full font-[family-name:var(--font-mono)]">
							{stat.type}
						</span>
					</div>

					<!-- Name & Count -->
					<h3 class="text-sm font-semibold text-white mb-1">{stat.name}</h3>
					<p class="text-3xl font-bold {colors.text} font-[family-name:var(--font-mono)] tabular-nums">
						{stat.count}
					</p>

					<!-- Key pattern -->
					<code class="block mt-2 text-[10px] text-slate-500 font-[family-name:var(--font-mono)] bg-surface-900/50 rounded px-2 py-1 truncate">
						{stat.key_pattern}
					</code>

					<!-- Purpose -->
					<p class="mt-2 text-[11px] text-slate-500 leading-relaxed line-clamp-2">{stat.purpose}</p>
				</div>

				<!-- Bottom glow bar -->
				<div class="h-0.5 w-full bg-gradient-to-r from-transparent via-current to-transparent {colors.text} opacity-0 group-hover:opacity-30 transition-opacity"></div>
			</div>
		{/each}

		{#if store.redisStats.length === 0}
			{#each Array(7) as _, i}
				<div class="card-redis p-4 animate-pulse" style="animation-delay: {i * 0.1}s">
					<div class="h-6 w-8 bg-surface-700 rounded mb-3"></div>
					<div class="h-4 w-20 bg-surface-700 rounded mb-2"></div>
					<div class="h-8 w-12 bg-surface-700 rounded mb-2"></div>
					<div class="h-3 w-full bg-surface-700 rounded"></div>
				</div>
			{/each}
		{/if}
	</div>
</div>
