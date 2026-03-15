<script lang="ts">
	import { getStore } from '$lib/stores.svelte';

	const store = getStore();
</script>

{#if store.toasts.length > 0}
	<div class="fixed bottom-6 right-6 z-[60] space-y-2 max-w-sm">
		{#each store.toasts as toast (toast.id)}
			<div class="bg-surface-800 border border-emerald-500/30 rounded-xl shadow-2xl shadow-emerald-500/10 overflow-hidden animate-slide-in">
				<div class="flex items-center gap-3 px-4 py-3">
					<div class="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center shrink-0">
						<svg class="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
							<path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
						</svg>
					</div>
					<p class="text-sm text-slate-200 flex-1">{toast.message}</p>
				</div>
				<!-- Progress bar -->
				<div class="h-0.5 bg-emerald-500/20">
					<div class="h-full bg-emerald-500" style="animation: toast-progress 5s linear forwards"></div>
				</div>
			</div>
		{/each}
	</div>
{/if}
