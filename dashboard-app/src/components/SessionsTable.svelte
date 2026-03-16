<script lang="ts">
	import { getStore } from '$lib/stores.svelte';

	const store = getStore();

	const tabs = [
		{ id: 'all', label: 'All' },
		{ id: 'created', label: 'Sent' },
		{ id: 'in_progress', label: 'In Progress' },
		{ id: 'submitted', label: 'Reviewed' },
		{ id: 'declined', label: 'Declined' }
	];

	const statusColors: Record<string, { bg: string; text: string; dot: string; label: string }> = {
		created: { bg: 'bg-blue-500/10', text: 'text-blue-400', dot: 'bg-blue-400', label: 'Sent' },
		in_progress: { bg: 'bg-amber-500/10', text: 'text-amber-400', dot: 'bg-amber-400', label: 'In Progress' },
		submitted: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', dot: 'bg-emerald-400', label: 'Reviewed' },
		declined: { bg: 'bg-red-500/10', text: 'text-red-400', dot: 'bg-red-400', label: 'Declined' }
	};

	function getStatusStyle(status: string) {
		return statusColors[status] ?? { bg: 'bg-slate-500/10', text: 'text-slate-400', dot: 'bg-slate-400', label: status };
	}

	function formatTime(iso: string) {
		const d = new Date(iso);
		const now = new Date();
		const diffMs = now.getTime() - d.getTime();
		const diffMins = Math.floor(diffMs / 60000);
		if (diffMins < 1) return 'just now';
		if (diffMins < 60) return `${diffMins}m ago`;
		const diffHours = Math.floor(diffMins / 60);
		if (diffHours < 24) return `${diffHours}h ago`;
		return d.toLocaleDateString();
	}

	function tabCount(id: string) {
		if (id === 'all') return store.sessions.length;
		return store.sessions.filter(s => s.status === id).length;
	}

	let searchInput = $state('');

	function handleSearch() {
		store.searchQuery = searchInput;
	}
</script>

<div class="card-glow overflow-hidden">
	<div class="p-4 sm:p-5 pb-0">
		<!-- Header: stacks on mobile -->
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
			<div class="flex items-center gap-3">
				<div class="bg-blue-500/10 rounded-lg p-2">
					<svg class="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
					</svg>
				</div>
				<h2 class="text-lg font-semibold tracking-tight">Customers</h2>
			</div>
			<div class="relative w-full sm:w-48">
				<svg class="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
				</svg>
				<input
					type="text"
					placeholder="Search customers..."
					bind:value={searchInput}
					oninput={handleSearch}
					class="w-full bg-surface-900 border border-surface-600 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-blue-500/40 transition-colors"
				/>
			</div>
		</div>

		<!-- Tabs: scrollable on mobile -->
		<div class="flex gap-1 border-b border-surface-600 overflow-x-auto">
			{#each tabs as tab}
				{@const count = tabCount(tab.id)}
				<button
					onclick={() => { store.activeFilter = tab.id; }}
					class="px-3 py-2 text-xs font-medium transition-colors relative cursor-pointer whitespace-nowrap shrink-0 {store.activeFilter === tab.id ? 'text-white' : 'text-slate-500 hover:text-slate-300'}"
				>
					{tab.label}
					{#if count > 0}
						<span class="ml-1 text-[10px] {store.activeFilter === tab.id ? 'text-emerald-400' : 'text-slate-600'}">{count}</span>
					{/if}
					{#if store.activeFilter === tab.id}
						<div class="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-500 rounded-full"></div>
					{/if}
				</button>
			{/each}
		</div>
	</div>

	<!-- Mobile: card layout. Desktop: table -->
	<div class="hidden sm:block overflow-x-auto">
		<table class="w-full text-sm">
			<thead>
				<tr class="text-[10px] font-medium uppercase tracking-wider text-slate-500">
					<th class="text-left px-5 py-3">Customer</th>
					<th class="text-left px-3 py-3">Job</th>
					<th class="text-left px-3 py-3">Plumber</th>
					<th class="text-left px-3 py-3">Status</th>
					<th class="text-center px-3 py-3">Messages</th>
					<th class="text-left px-3 py-3">Sent</th>
					<th class="text-right px-5 py-3"></th>
				</tr>
			</thead>
			<tbody>
				{#each store.filteredSessions as session (session.session_id)}
					{@const status = getStatusStyle(session.status)}
					<tr
						onclick={() => store.openConversation(session.session_id)}
						class="border-t border-surface-700/50 hover:bg-surface-700/30 cursor-pointer transition-colors group"
					>
						<td class="px-5 py-3">
							<span class="font-medium text-slate-200 group-hover:text-white transition-colors">{session.customer_name || '—'}</span>
							{#if session.is_repeat_customer}
								<span class="ml-1.5 text-[10px] text-amber-400/80 bg-amber-500/10 px-1.5 py-0.5 rounded-full">repeat</span>
							{/if}
						</td>
						<td class="px-3 py-3 text-slate-400 text-xs">{session.job_type || '—'}</td>
						<td class="px-3 py-3 text-slate-400 text-xs">{session.plumber_name || '—'}</td>
						<td class="px-3 py-3">
							<span class="{status.bg} {status.text} text-xs font-medium px-2.5 py-1 rounded-full inline-flex items-center gap-1.5">
								<span class="w-1.5 h-1.5 rounded-full {status.dot}"></span>
								{status.label}
							</span>
						</td>
						<td class="px-3 py-3 text-center text-slate-400 text-xs">{session.message_count || 0}</td>
						<td class="px-3 py-3 text-slate-500 text-xs">{formatTime(session.created_at)}</td>
						<td class="px-5 py-3 text-right">
							<button class="text-xs text-emerald-400/60 hover:text-emerald-400 transition-colors cursor-pointer">
								View Chat
							</button>
						</td>
					</tr>
				{:else}
					<tr>
						<td colspan="7" class="px-5 py-12 text-center text-slate-600 text-sm">
							{store.sessionsLoading ? 'Loading...' : 'No customers yet'}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<!-- Mobile card layout -->
	<div class="sm:hidden divide-y divide-surface-700/50">
		{#each store.filteredSessions as session (session.session_id)}
			{@const status = getStatusStyle(session.status)}
			<button
				onclick={() => store.openConversation(session.session_id)}
				class="w-full text-left p-4 hover:bg-surface-700/30 transition-colors cursor-pointer"
			>
				<div class="flex items-center justify-between mb-2">
					<div class="flex items-center gap-2">
						<span class="font-medium text-slate-200">{session.customer_name || '—'}</span>
						{#if session.is_repeat_customer}
							<span class="text-[10px] text-amber-400/80 bg-amber-500/10 px-1.5 py-0.5 rounded-full">repeat</span>
						{/if}
					</div>
					<span class="{status.bg} {status.text} text-[11px] font-medium px-2 py-0.5 rounded-full inline-flex items-center gap-1">
						<span class="w-1.5 h-1.5 rounded-full {status.dot}"></span>
						{status.label}
					</span>
				</div>
				<div class="flex items-center gap-3 text-xs text-slate-500">
					{#if session.job_type}<span>{session.job_type}</span><span>·</span>{/if}
					<span>{session.plumber_name || '—'}</span>
					<span>·</span>
					<span>{session.message_count || 0} msgs</span>
					<span>·</span>
					<span>{formatTime(session.created_at)}</span>
				</div>
			</button>
		{:else}
			<div class="p-8 text-center text-slate-600 text-sm">
				{store.sessionsLoading ? 'Loading...' : 'No customers yet'}
			</div>
		{/each}
	</div>
</div>
