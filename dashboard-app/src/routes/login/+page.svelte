<svelte:head>
	<title>Log in — Plumbly</title>
</svelte:head>

<script lang="ts">
	const signInHref = '/auth/login?screen_hint=sign-in&return_to=/dashboard';
	const signUpHref = '/auth/login?screen_hint=sign-up&return_to=/dashboard';
</script>

<div class="min-h-[100dvh] flex items-center justify-center px-5 py-12">
	<div class="w-full max-w-md rounded-[28px] border border-white/10 bg-slate-950/80 p-8 sm:p-10 shadow-2xl shadow-emerald-950/20">
		<a href="/" class="inline-flex items-center gap-3">
			<div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600">
				<svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
					<path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
				</svg>
			</div>
			<div>
				<p class="text-sm font-semibold text-white">Plumbly</p>
				<p class="text-xs text-slate-500">WorkOS protected dashboard</p>
			</div>
		</a>

		<div class="mt-10">
			<p class="text-sm uppercase tracking-[0.3em] text-emerald-400/80">Dashboard Access</p>
			<h1 class="mt-3 text-3xl font-bold tracking-tight text-white">Sign in to your workspace</h1>
			<p class="mt-3 text-sm leading-6 text-slate-400">
				Authentication is handled by WorkOS. Your browser session is stored in a secure HTTP-only cookie managed by the backend.
			</p>
		</div>

		<div class="mt-8 space-y-3">
			<a
				class="flex w-full items-center justify-center rounded-2xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-emerald-400"
				href={signInHref}
			>
				Continue with WorkOS
			</a>
			<a
				class="flex w-full items-center justify-center rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm font-semibold text-slate-200 transition-colors hover:bg-white/[0.06]"
				href={signUpHref}
			>
				Create account
			</a>
		</div>

		<div class="mt-8 rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-sm text-slate-400">
			<p class="font-medium text-slate-200">First release defaults</p>
			<p class="mt-2">Users belong to a single organization. Internal staff can be promoted to the platform-level `superadmin` role through configuration.</p>
		</div>
	</div>
</div>
