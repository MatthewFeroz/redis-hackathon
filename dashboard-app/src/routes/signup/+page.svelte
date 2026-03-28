<svelte:head>
	<title>Sign up — Plumbly</title>
</svelte:head>

<script lang="ts">
	const signUpHref = '/auth/login?screen_hint=sign-up&return_to=/dashboard';
	const signInHref = '/auth/login?screen_hint=sign-in&return_to=/dashboard';
</script>

<div class="min-h-[100dvh] flex items-center justify-center px-5 py-12">
	<div class="w-full max-w-lg rounded-[28px] border border-white/10 bg-slate-950/80 p-8 sm:p-10 shadow-2xl shadow-emerald-950/20">
		<p class="text-sm uppercase tracking-[0.3em] text-emerald-400/80">Get Started</p>
		<h1 class="mt-3 text-3xl font-bold tracking-tight text-white">Create your Plumbly workspace</h1>
		<p class="mt-3 text-sm leading-6 text-slate-400">
			Account creation is handled by WorkOS AuthKit. Once the organization membership is active, the FastAPI backend will issue your dashboard session automatically.
		</p>

		<div class="mt-8 grid gap-4 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm text-slate-300">
			<div>
				<p class="font-semibold text-white">Included in this setup</p>
				<p class="mt-1 text-slate-400">Single-organization users, org-scoped roles (`owner`, `admin`, `member`), and optional platform `superadmin` support for internal staff.</p>
			</div>
			<div>
				<p class="font-semibold text-white">Enterprise-ready later</p>
				<p class="mt-1 text-slate-400">You can add SSO, domain routing, and directory sync in WorkOS without replacing the app’s session model.</p>
			</div>
		</div>

		<div class="mt-8 space-y-3">
			<a
				class="flex w-full items-center justify-center rounded-2xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-emerald-400"
				href={signUpHref}
			>
				Create account with WorkOS
			</a>
			<a
				class="flex w-full items-center justify-center rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm font-semibold text-slate-200 transition-colors hover:bg-white/[0.06]"
				href={signInHref}
			>
				I already have an account
			</a>
		</div>
	</div>
</div>
