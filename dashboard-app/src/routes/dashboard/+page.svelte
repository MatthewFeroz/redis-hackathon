<script lang="ts">
	import { onMount } from 'svelte';
	import { getStore } from '$lib/stores.svelte';
	import { connectSSE } from '$lib/sse';
	import StatsBar from '../../components/StatsBar.svelte';
	import JobForm from '../../components/JobForm.svelte';
	import SessionsTable from '../../components/SessionsTable.svelte';
	import ConversationPanel from '../../components/ConversationPanel.svelte';
	import AnalyticsCharts from '../../components/AnalyticsCharts.svelte';

	const store = getStore();

	onMount(() => {
		store.refreshAll();

		const interval = setInterval(() => {
			store.loadSessions();
			store.loadAnalytics();
		}, 30000);

		const disconnect = connectSSE((data) => {
			store.addToast(`New review from ${data.customer_name ?? 'a customer'}!`);
			store.refreshAll();
		});

		return () => {
			clearInterval(interval);
			disconnect();
		};
	});
</script>

<svelte:head>
	<title>Plumbly Dashboard</title>
</svelte:head>

<div class="relative min-h-screen">
	<div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent"></div>

	<div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8 space-y-4 sm:space-y-8 relative z-10">
		<!-- Header -->
		<header>
			<div class="flex items-center gap-3 sm:gap-4">
				<div class="w-10 h-10 sm:w-11 sm:h-11 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center shadow-lg shadow-emerald-500/20 shrink-0">
					<svg class="w-5 h-5 sm:w-6 sm:h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
					</svg>
				</div>
				<div>
					<h1 class="text-xl sm:text-2xl font-bold tracking-tight text-white">Plumbly</h1>
					<p class="text-[11px] sm:text-xs text-slate-500 tracking-wider">Review Dashboard</p>
				</div>
			</div>
		</header>

		<JobForm />
		<StatsBar />
		<SessionsTable />
		<AnalyticsCharts />
	</div>
</div>

<ConversationPanel />
