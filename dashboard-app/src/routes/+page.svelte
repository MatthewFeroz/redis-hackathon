<script lang="ts">
	import { onMount } from 'svelte';
	import { getStore } from '$lib/stores.svelte';
	import { connectSSE } from '$lib/sse';
	import StatsBar from '../components/StatsBar.svelte';
	import JobForm from '../components/JobForm.svelte';
	import SessionsTable from '../components/SessionsTable.svelte';
	import ConversationPanel from '../components/ConversationPanel.svelte';
	import AnalyticsCharts from '../components/AnalyticsCharts.svelte';

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
						<path stroke-linecap="round" stroke-linejoin="round" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/>
					</svg>
				</div>
				<div>
					<h1 class="text-xl sm:text-2xl font-bold tracking-tight text-white">Plumbly</h1>
					<p class="text-[11px] sm:text-xs text-slate-500 tracking-wider">R&M Plumbing & Heating</p>
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
