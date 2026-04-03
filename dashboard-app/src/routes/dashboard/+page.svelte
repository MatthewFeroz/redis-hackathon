<script lang="ts">
	import { onMount } from 'svelte';
	import { getStore } from '$lib/stores.svelte';
	import { connectSSE } from '$lib/sse';
	import { api } from '$lib/api';
	import type { OrganizationSummary } from '$lib/types';
	import StatsBar from '../../components/StatsBar.svelte';
	import JobForm from '../../components/JobForm.svelte';
	import SessionsTable from '../../components/SessionsTable.svelte';
	import ConversationPanel from '../../components/ConversationPanel.svelte';
	import AnalyticsCharts from '../../components/AnalyticsCharts.svelte';
	import UserProfileMenu from '../../components/UserProfileMenu.svelte';

	const store = getStore();

	let authLoading = $state(true);
	let authError = $state('');
	let organizations = $state<OrganizationSummary[]>([]);
	let switchingOrg = $state(false);

	async function bootstrap() {
		try {
			store.me = await api.getMe();
			organizations = await api.getOrganizations();
			await store.refreshAll();
		} catch (error) {
			const message = error instanceof Error ? error.message : 'Authentication failed';
			if (message.includes('401')) {
				window.location.href = '/login';
				return;
			}
			authError = message;
		} finally {
			authLoading = false;
		}
	}

	async function handleLogout() {
		await api.logout();
		window.location.href = '/login';
	}

	async function handleOrgSwitch(organizationId: string) {
		switchingOrg = true;
		try {
			store.me = await api.switchOrganization(organizationId);
			await store.refreshAll();
		} finally {
			switchingOrg = false;
		}
	}

	onMount(() => {
		let interval: ReturnType<typeof setInterval> | undefined;
		let disconnect = () => {};

		void (async () => {
			await bootstrap();
			if (!store.me) return;

			interval = setInterval(() => {
				void store.loadSessions();
				void store.loadAnalytics();
			}, 30000);

			disconnect = connectSSE((data) => {
				store.addToast(`New review from ${data.customer_name ?? 'a customer'}!`);
				void store.refreshAll();
			});
		})();

		return () => {
			if (interval) clearInterval(interval);
			disconnect();
		};
	});
</script>

<svelte:head>
	<title>Plumbly Dashboard</title>
</svelte:head>

{#if authLoading}
	<div class="min-h-screen flex items-center justify-center text-slate-300">
		Loading dashboard…
	</div>
{:else if authError}
	<div class="min-h-screen flex items-center justify-center px-6">
		<div class="max-w-md rounded-2xl border border-red-500/20 bg-red-500/10 p-6 text-sm text-red-200">
			<p class="font-semibold">Dashboard unavailable</p>
			<p class="mt-2 text-red-100/80">{authError}</p>
			<a class="mt-4 inline-flex rounded-lg bg-white/10 px-4 py-2 text-white" href="/login">Return to login</a>
		</div>
	</div>
{:else}
	<div class="relative min-h-screen">
		<div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent"></div>

		<div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8 space-y-4 sm:space-y-8 relative z-10">
			<header class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
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

				<UserProfileMenu
					{organizations}
					onOrgSwitch={handleOrgSwitch}
					{switchingOrg}
					onLogout={handleLogout}
				/>
			</header>

			<JobForm />
			<StatsBar />
			<SessionsTable />
			<AnalyticsCharts />
		</div>
	</div>

	<ConversationPanel />
{/if}
