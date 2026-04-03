<script lang="ts">
	import { getStore } from '$lib/stores.svelte';
	import type { OrganizationSummary } from '$lib/types';

	type Props = {
		organizations: OrganizationSummary[];
		onOrgSwitch: (organizationId: string) => Promise<void>;
		switchingOrg: boolean;
		onLogout: () => Promise<void>;
	};

	let { organizations, onOrgSwitch, switchingOrg, onLogout }: Props = $props();

	const store = getStore();

	let open = $state(false);
	let triggerEl = $state<HTMLButtonElement | undefined>(undefined);

	const initials = $derived(
		store.me
			? ((store.me.first_name?.charAt(0) ?? '') + (store.me.last_name?.charAt(0) ?? '')).toUpperCase() || store.me.email.charAt(0).toUpperCase()
			: '?'
	);

	const displayName = $derived(
		store.me
			? [store.me.first_name, store.me.last_name].filter(Boolean).join(' ') || store.me.email
			: ''
	);

	const firstName = $derived(
		store.me
			? store.me.first_name || store.me.email.split('@')[0]
			: ''
	);

	const orgRole = $derived(
		store.me?.platform_role ?? store.me?.organization?.role ?? store.me?.role ?? ''
	);

	function toggle() {
		open = !open;
	}

	function close() {
		open = false;
		triggerEl?.focus();
	}

	function handleSelectChange(event: Event) {
		const value = (event.currentTarget as HTMLSelectElement).value;
		onOrgSwitch(value);
	}

	/* Click-outside Svelte action */
	function clickOutside(node: HTMLElement) {
		function handleClick(event: MouseEvent) {
			if (!node.contains(event.target as Node)) {
				close();
			}
		}
		document.addEventListener('click', handleClick, true);
		return {
			destroy() {
				document.removeEventListener('click', handleClick, true);
			}
		};
	}
</script>

<svelte:window onkeydown={(e) => { if (e.key === 'Escape' && open) close(); }} />

<div class="relative" use:clickOutside>
	<!-- Trigger button -->
	<button
		bind:this={triggerEl}
		type="button"
		onclick={toggle}
		aria-haspopup="true"
		aria-expanded={open}
		aria-controls="user-profile-menu"
		aria-label="User menu for {displayName}"
		class="group flex items-center gap-2.5 rounded-xl border border-white/10 bg-white/[0.03] px-2.5 py-2 transition-all duration-200 hover:bg-white/[0.06] hover:border-white/[0.15] cursor-pointer"
	>
		<!-- Initials avatar -->
		<div class="relative w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-md shadow-emerald-500/25 shrink-0 transition-shadow duration-200 group-hover:shadow-emerald-500/40">
			<span class="text-[13px] font-bold text-white leading-none tracking-wide">{initials}</span>
			<!-- Online status dot -->
			<span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-surface-900"></span>
		</div>

		<!-- Name (hidden on mobile) -->
		<span class="hidden sm:inline text-sm font-medium text-slate-200 max-w-[120px] truncate">{firstName}</span>

		<!-- Chevron -->
		<svg
			class="w-3.5 h-3.5 text-slate-500 transition-transform duration-200 {open ? 'rotate-180' : ''}"
			fill="none"
			viewBox="0 0 24 24"
			stroke="currentColor"
			stroke-width="2.5"
		>
			<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
		</svg>
	</button>

	<!-- Dropdown panel -->
	{#if open}
		<div
			id="user-profile-menu"
			role="menu"
			class="absolute right-0 top-full mt-2.5 w-72 rounded-2xl border border-white/[0.08] bg-surface-800/[0.97] backdrop-blur-2xl shadow-2xl shadow-black/50 z-40 animate-fade-in overflow-hidden"
		>
			<!-- Subtle top accent line -->
			<div class="h-px bg-gradient-to-r from-transparent via-emerald-500/40 to-transparent"></div>

			<!-- Section 1: User identity -->
			<div class="px-4 pt-4 pb-3">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 shrink-0">
						<span class="text-sm font-bold text-white leading-none tracking-wide">{initials}</span>
					</div>
					<div class="min-w-0 flex-1">
						<p class="text-sm font-semibold text-white truncate">{displayName}</p>
						<p class="text-xs text-slate-500 truncate mt-0.5">{store.me?.email}</p>
					</div>
				</div>
			</div>

			<!-- Divider -->
			<div class="mx-4 h-px bg-gradient-to-r from-surface-700 via-surface-600/50 to-surface-700"></div>

			<!-- Section 2: Organization context -->
			{#if store.me?.organization}
				<div class="px-4 py-3">
					<p class="text-[10px] uppercase tracking-[0.2em] text-slate-500/80 font-medium">Organization</p>
					<div class="flex items-center gap-2 mt-1.5">
						<p class="text-sm font-medium text-slate-200 truncate">{store.me.organization.name}</p>
						<span class="shrink-0 inline-flex items-center rounded-md bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-400 uppercase tracking-wider ring-1 ring-inset ring-emerald-500/20">
							{orgRole}
						</span>
					</div>
				</div>
			{/if}

			<!-- Section 3: Organization switcher (superadmin only) -->
			{#if store.me?.is_superadmin && organizations.length > 0}
				<div class="mx-4 h-px bg-gradient-to-r from-surface-700 via-surface-600/50 to-surface-700"></div>
				<div class="px-4 py-3">
					<p class="text-[10px] uppercase tracking-[0.2em] text-slate-500/80 font-medium mb-2">Switch organization</p>
					<div class="relative">
						<select
							class="w-full appearance-none rounded-lg border border-surface-600/80 bg-surface-900/80 px-3 py-2 pr-8 text-sm text-slate-200 transition-colors duration-150 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 cursor-pointer"
							value={store.me?.organization?.id ?? ''}
							onchange={handleSelectChange}
							disabled={switchingOrg}
						>
							{#each organizations as organization}
								<option value={organization.id}>{organization.name}</option>
							{/each}
						</select>
						<svg class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
							<path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15L12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
						</svg>
					</div>
				</div>
			{/if}

			<!-- Divider -->
			<div class="mx-4 h-px bg-gradient-to-r from-surface-700 via-surface-600/50 to-surface-700"></div>

			<!-- Section 4: Sign out -->
			<div class="p-2">
				<button
					type="button"
					role="menuitem"
					onclick={() => { close(); onLogout(); }}
					class="w-full flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm text-slate-400 transition-all duration-150 hover:text-white hover:bg-white/[0.05] cursor-pointer group/signout"
				>
					<svg class="w-4 h-4 text-slate-500 transition-colors duration-150 group-hover/signout:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
						<path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
					</svg>
					<span class="transition-colors duration-150 group-hover/signout:text-red-300">Sign out</span>
				</button>
			</div>
		</div>
	{/if}
</div>
