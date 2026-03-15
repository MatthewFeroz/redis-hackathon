<script lang="ts">
	import { getStore } from '$lib/stores.svelte';

	const store = getStore();

	const customerSession = $derived(
		store.selectedSessionId
			? store.sessions.find(s => s.session_id === store.selectedSessionId)
			: null
	);

	function formatTs(ts: number) {
		return new Date(ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	}

	function handleOverlayClick(e: MouseEvent) {
		if (e.target === e.currentTarget) store.closeConversation();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') store.closeConversation();
	}
</script>

{#if store.selectedSessionId}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-50 flex justify-end animate-fade-in"
		onclick={handleOverlayClick}
		onkeydown={handleKeydown}
	>
		<!-- Backdrop -->
		<div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>

		<!-- Panel -->
		<div class="relative w-full max-w-md bg-surface-800 border-l border-surface-600 shadow-2xl animate-slide-in flex flex-col">
			<!-- Header -->
			<div class="flex items-center justify-between px-5 py-4 border-b border-surface-700">
				<div>
					<h3 class="font-semibold text-white">{customerSession?.customer_name ?? 'Conversation'}</h3>
					<p class="text-xs text-slate-500 mt-0.5">
						{store.chatHistory.length} messages
					</p>
				</div>
				<button
					onclick={() => store.closeConversation()}
					aria-label="Close conversation"
					class="p-2 hover:bg-surface-700 rounded-lg transition-colors text-slate-400 hover:text-white cursor-pointer"
				>
					<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
					</svg>
				</button>
			</div>

			<!-- Messages -->
			<div class="flex-1 overflow-y-auto p-5 space-y-3">
				{#if store.chatLoading}
					<div class="flex items-center justify-center py-12">
						<svg class="animate-spin w-6 h-6 text-slate-500" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
						</svg>
					</div>
				{:else if store.chatHistory.length === 0}
					<div class="text-center py-12 text-slate-600 text-sm">No messages yet</div>
				{:else}
					{#each store.chatHistory as msg, i}
						<div
							class="flex {msg.role === 'user' ? 'justify-end' : 'justify-start'}"
							style="animation: count-up 0.2s ease-out {i * 0.05}s both"
						>
							<div class="max-w-[80%] {msg.role === 'user'
								? 'bg-emerald-600/20 border border-emerald-500/20 text-emerald-50'
								: 'bg-surface-700 border border-surface-600 text-slate-300'
							} rounded-2xl px-4 py-2.5 text-sm leading-relaxed {msg.role === 'user' ? 'rounded-br-md' : 'rounded-bl-md'}">
								<p class="whitespace-pre-wrap">{msg.content}</p>
								<p class="text-[10px] mt-1.5 {msg.role === 'user' ? 'text-emerald-400/50' : 'text-slate-600'}">
									{formatTs(msg.ts)}
								</p>
							</div>
						</div>
					{/each}
				{/if}
			</div>
		</div>
	</div>
{/if}
