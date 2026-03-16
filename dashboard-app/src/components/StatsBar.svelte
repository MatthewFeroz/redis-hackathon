<script lang="ts">
	import { getStore } from '$lib/stores.svelte';

	const store = getStore();
</script>

<div class="card-glow p-4 sm:p-5">
	<div class="flex items-center divide-x divide-surface-600">
		<!-- Reviews Today -->
		<div class="flex-1 flex items-center gap-3 pr-4 sm:pr-6">
			<div class="bg-emerald-500/10 rounded-lg p-2 shrink-0">
				<svg class="w-4 h-4 sm:w-5 sm:h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
				</svg>
			</div>
			<div>
				<p class="text-2xl sm:text-3xl font-bold text-emerald-400 tracking-tight leading-none">{store.analytics?.reviews_today ?? 0}</p>
				<p class="text-[10px] sm:text-xs text-slate-500 uppercase tracking-wider mt-0.5">Reviews Today</p>
			</div>
		</div>

		<!-- Total Customers -->
		<div class="flex-1 flex items-center gap-3 px-4 sm:px-6">
			<div class="bg-blue-500/10 rounded-lg p-2 shrink-0">
				<svg class="w-4 h-4 sm:w-5 sm:h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
				</svg>
			</div>
			<div>
				<p class="text-2xl sm:text-3xl font-bold text-blue-400 tracking-tight leading-none">{store.analytics?.total_sessions ?? 0}</p>
				<p class="text-[10px] sm:text-xs text-slate-500 uppercase tracking-wider mt-0.5">Total Customers</p>
			</div>
		</div>

		<!-- Completion Rate -->
		<div class="flex-1 flex items-center gap-3 pl-4 sm:pl-6">
			<div class="bg-amber-500/10 rounded-lg p-2 shrink-0">
				<svg class="w-4 h-4 sm:w-5 sm:h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
				</svg>
			</div>
			<div>
				<p class="text-2xl sm:text-3xl font-bold text-amber-400 tracking-tight leading-none">{store.analytics?.completion_rate ?? 0}%</p>
				<p class="text-[10px] sm:text-xs text-slate-500 uppercase tracking-wider mt-0.5">Completion Rate</p>
			</div>
		</div>
	</div>
</div>
