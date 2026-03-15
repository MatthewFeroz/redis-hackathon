<script lang="ts">
	import { getStore } from '$lib/stores.svelte';

	const store = getStore();

	const stages = $derived(() => {
		const f = store.analytics?.funnel ?? {};
		const raw = [
			{ key: 'job_completed', label: 'Job Completed', icon: '🔧', color: 'from-blue-600 to-blue-500', border: 'border-blue-500/30', text: 'text-blue-400' },
			{ key: 'customer_contacted', label: 'Contacted', icon: '📱', color: 'from-indigo-600 to-indigo-500', border: 'border-indigo-500/30', text: 'text-indigo-400' },
			{ key: 'review_started', label: 'Review Started', icon: '✍️', color: 'from-amber-600 to-amber-500', border: 'border-amber-500/30', text: 'text-amber-400' },
			{ key: 'review_submitted', label: 'Submitted', icon: '⭐', color: 'from-emerald-600 to-emerald-500', border: 'border-emerald-500/30', text: 'text-emerald-400' }
		];
		return raw.map((stage, i) => {
			const count = f[stage.key] ?? 0;
			const prev = i > 0 ? (f[raw[i - 1].key] ?? 0) : 0;
			const dropoff = i > 0 && prev > 0 ? Math.round(((prev - count) / prev) * 100) : 0;
			return { ...stage, count, dropoff };
		});
	});
</script>

<div class="card-glow p-5">
	<div class="flex items-center gap-3 mb-5">
		<div class="bg-amber-500/10 rounded-lg p-2">
			<svg class="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
				<path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/>
			</svg>
		</div>
		<div>
			<h2 class="text-lg font-semibold tracking-tight">Event Pipeline</h2>
			<p class="text-xs text-slate-500 font-[family-name:var(--font-mono)]">Redis Streams · XADD/XRANGE</p>
		</div>
	</div>

	<div class="flex items-center gap-2 overflow-x-auto pb-2">
		{#each stages() as stage, i}
			<!-- Stage box -->
			<div
				class="flex-1 min-w-[120px] bg-surface-900 border {stage.border} rounded-xl p-4 text-center transition-all hover:scale-[1.02]"
				style="animation: count-up 0.4s ease-out {i * 0.12}s both"
			>
				<span class="text-2xl">{stage.icon}</span>
				<p class="text-2xl font-bold {stage.text} font-[family-name:var(--font-mono)] mt-1">{stage.count}</p>
				<p class="text-[10px] text-slate-500 uppercase tracking-wider mt-1 font-medium">{stage.label}</p>
			</div>

			{#if i < stages().length - 1}
				<!-- Arrow with drop-off -->
				<div class="flex flex-col items-center shrink-0 gap-0.5">
					<div class="flex items-center text-slate-600">
						<div class="w-6 h-px bg-gradient-to-r from-slate-600 to-slate-700"></div>
						<svg class="w-3 h-3 -ml-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
							<path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
						</svg>
					</div>
					{#if stages()[i + 1].dropoff > 0}
						<span class="text-[9px] text-red-400/60 font-[family-name:var(--font-mono)]">-{stages()[i + 1].dropoff}%</span>
					{/if}
				</div>
			{/if}
		{/each}
	</div>
</div>
