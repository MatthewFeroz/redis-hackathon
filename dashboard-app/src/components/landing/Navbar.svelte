<script lang="ts">
	let scrolled = $state(false);
	let mobileOpen = $state(false);

	function handleScroll() {
		scrolled = window.scrollY > 20;
	}

	const navLinks = [
		{ label: 'Features', href: '#features' },
		{ label: 'How it works', href: '#how-it-works' },
		{ label: 'Pricing', href: '#pricing' }
	];
</script>

<svelte:window onscroll={handleScroll} />

<nav
	class="fixed top-0 left-0 right-0 z-50 transition-all duration-500"
	class:scrolled
>
	<div class="max-w-7xl mx-auto px-5 sm:px-8">
		<div class="flex items-center justify-between h-16 sm:h-20">
			<!-- Logo -->
			<a href="/" class="flex items-center gap-3 group">
				<div class="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/25 group-hover:shadow-emerald-500/40 transition-shadow duration-300">
					<svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
						<path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
					</svg>
				</div>
				<span class="text-lg font-bold tracking-tight text-white">Plumbly</span>
			</a>

			<!-- Desktop Nav -->
			<div class="hidden md:flex items-center gap-1">
				{#each navLinks as link}
					<a
						href={link.href}
						class="px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors duration-200 rounded-lg hover:bg-white/[0.04]"
					>
						{link.label}
					</a>
				{/each}
			</div>

			<!-- Auth Buttons -->
			<div class="hidden md:flex items-center gap-3">
				<a
					href="/login"
					class="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors duration-200"
				>
					Log in
				</a>
				<a
					href="/signup"
					class="group relative px-5 py-2.5 text-sm font-semibold text-white rounded-xl overflow-hidden transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/25"
				>
					<div class="absolute inset-0 bg-gradient-to-r from-emerald-500 to-emerald-600 transition-all duration-300 group-hover:from-emerald-400 group-hover:to-emerald-500"></div>
					<span class="relative">Start free trial</span>
				</a>
			</div>

			<!-- Mobile Toggle -->
			<button
				class="md:hidden w-10 h-10 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.06] transition-colors"
				onclick={() => mobileOpen = !mobileOpen}
				aria-label="Toggle menu"
			>
				{#if mobileOpen}
					<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
					</svg>
				{:else}
					<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				{/if}
			</button>
		</div>
	</div>

	<!-- Mobile Menu -->
	{#if mobileOpen}
		<div class="md:hidden border-t border-white/[0.06] bg-surface-900/98 backdrop-blur-xl">
			<div class="px-5 py-4 space-y-1">
				{#each navLinks as link}
					<a
						href={link.href}
						class="block px-4 py-3 text-sm text-slate-400 hover:text-white rounded-lg hover:bg-white/[0.04] transition-colors"
						onclick={() => mobileOpen = false}
					>
						{link.label}
					</a>
				{/each}
				<div class="pt-3 mt-3 border-t border-white/[0.06] flex flex-col gap-2">
					<a href="/login" class="px-4 py-3 text-sm text-slate-300 hover:text-white rounded-lg hover:bg-white/[0.04] transition-colors">Log in</a>
					<a href="/signup" class="px-4 py-3 text-sm font-semibold text-white bg-emerald-500 rounded-xl text-center hover:bg-emerald-400 transition-colors">Start free trial</a>
				</div>
			</div>
		</div>
	{/if}
</nav>

<style>
	nav {
		background: transparent;
	}
	nav.scrolled {
		background: rgba(10, 15, 26, 0.85);
		backdrop-filter: blur(20px) saturate(1.2);
		border-bottom: 1px solid rgba(255,255,255,0.04);
	}
</style>
