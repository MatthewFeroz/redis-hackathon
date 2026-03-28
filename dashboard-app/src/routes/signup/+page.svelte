<script lang="ts">
	let fullName = $state('');
	let businessName = $state('');
	let email = $state('');
	let password = $state('');
	let showPassword = $state(false);
	let loading = $state(false);
	let error = $state('');
	let selectedIndustry = $state('');

	const industries = [
		'Plumbing', 'HVAC', 'Electrical', 'Restaurant', 'Salon / Spa',
		'Dental', 'Auto Repair', 'Real Estate', 'Landscaping', 'Other'
	];

	function passwordStrength(pw: string): { score: number; label: string; color: string } {
		let score = 0;
		if (pw.length >= 8) score++;
		if (/[A-Z]/.test(pw)) score++;
		if (/[0-9]/.test(pw)) score++;
		if (/[^A-Za-z0-9]/.test(pw)) score++;

		if (score <= 1) return { score, label: 'Weak', color: 'bg-red-500' };
		if (score === 2) return { score, label: 'Fair', color: 'bg-amber-500' };
		if (score === 3) return { score, label: 'Good', color: 'bg-emerald-500' };
		return { score, label: 'Strong', color: 'bg-emerald-400' };
	}

	const strength = $derived(passwordStrength(password));

	async function handleSignup(e: Event) {
		e.preventDefault();
		if (!fullName || !email || !password) {
			error = 'Please fill in all required fields.';
			return;
		}
		if (password.length < 8) {
			error = 'Password must be at least 8 characters.';
			return;
		}
		loading = true;
		error = '';

		// Simulate signup — replace with real API
		await new Promise((r) => setTimeout(r, 1500));
		loading = false;

		window.location.href = '/dashboard';
	}
</script>

<svelte:head>
	<title>Sign up — Plumbly</title>
</svelte:head>

<div class="min-h-[100dvh] flex relative">
	<!-- Background -->
	<div class="auth-bg">
		<div class="auth-gradient-signup"></div>
		<div class="auth-grid-signup"></div>
	</div>

	<!-- Left Panel — Branding -->
	<div class="hidden lg:flex lg:w-[45%] relative z-10 flex-col justify-between p-12 xl:p-16">
		<div>
			<a href="/" class="inline-flex items-center gap-2.5 group">
				<div class="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/25">
					<svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
						<path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
					</svg>
				</div>
				<span class="text-lg font-bold tracking-tight text-white">Plumbly</span>
			</a>
		</div>

		<div class="max-w-md space-y-8">
			<div>
				<h2 class="text-3xl font-extrabold tracking-tight text-white mb-3">
					Start collecting reviews in minutes
				</h2>
				<p class="text-base text-slate-400 leading-relaxed">
					Join 2,400+ service businesses already using Plumbly to automate their review generation.
				</p>
			</div>

			<div class="space-y-4">
				{#each [
					{ text: '14-day free trial, no credit card', icon: 'check' },
					{ text: 'Setup takes less than 5 minutes', icon: 'clock' },
					{ text: 'Works with any Google Business Profile', icon: 'globe' },
				] as item}
					<div class="flex items-center gap-3">
						<div class="w-7 h-7 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0">
							<svg class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
								<path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
							</svg>
						</div>
						<span class="text-sm text-slate-300">{item.text}</span>
					</div>
				{/each}
			</div>
		</div>

		<p class="text-xs text-slate-600">Trusted by plumbers, restaurants, salons, and more</p>
	</div>

	<!-- Right Panel — Signup Form -->
	<div class="flex-1 flex items-center justify-center relative z-10 px-5 sm:px-8 py-12">
		<div class="w-full max-w-[440px]">
			<!-- Mobile logo -->
			<div class="lg:hidden mb-10">
				<a href="/" class="inline-flex items-center gap-2.5">
					<div class="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center">
						<svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
							<path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
						</svg>
					</div>
					<span class="text-lg font-bold tracking-tight text-white">Plumbly</span>
				</a>
			</div>

			<h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">Create your account</h1>
			<p class="mt-2 text-sm text-slate-400">
				Already have an account?
				<a href="/login" class="text-emerald-400 hover:text-emerald-300 font-medium transition-colors">Log in</a>
			</p>

			<!-- OAuth -->
			<div class="mt-8 grid grid-cols-2 gap-3">
				<button class="auth-oauth-btn">
					<svg class="w-4 h-4" viewBox="0 0 24 24">
						<path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
						<path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
						<path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
						<path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
					</svg>
					<span>Google</span>
				</button>
				<button class="auth-oauth-btn">
					<svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
						<path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
					</svg>
					<span>GitHub</span>
				</button>
			</div>

			<div class="relative my-8">
				<div class="absolute inset-0 flex items-center">
					<div class="w-full h-px bg-white/[0.06]"></div>
				</div>
				<div class="relative flex justify-center">
					<span class="px-4 text-xs text-slate-600 bg-surface-900">or continue with email</span>
				</div>
			</div>

			<form onsubmit={handleSignup} class="space-y-4">
				{#if error}
					<div class="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400">
						{error}
					</div>
				{/if}

				<div class="grid grid-cols-2 gap-3">
					<div>
						<label for="fullName" class="block text-sm font-medium text-slate-300 mb-2">Full name</label>
						<input
							id="fullName"
							type="text"
							bind:value={fullName}
							placeholder="Jane Smith"
							class="auth-input"
							required
						/>
					</div>
					<div>
						<label for="businessName" class="block text-sm font-medium text-slate-300 mb-2">Business name</label>
						<input
							id="businessName"
							type="text"
							bind:value={businessName}
							placeholder="Smith Plumbing"
							class="auth-input"
						/>
					</div>
				</div>

				<div>
					<label for="industry" class="block text-sm font-medium text-slate-300 mb-2">Industry</label>
					<select
						id="industry"
						bind:value={selectedIndustry}
						class="auth-input appearance-none cursor-pointer"
					>
						<option value="" disabled>Select your industry</option>
						{#each industries as ind}
							<option value={ind}>{ind}</option>
						{/each}
					</select>
				</div>

				<div>
					<label for="signup-email" class="block text-sm font-medium text-slate-300 mb-2">Work email</label>
					<input
						id="signup-email"
						type="email"
						bind:value={email}
						placeholder="jane@smithplumbing.com"
						class="auth-input"
						required
					/>
				</div>

				<div>
					<label for="signup-password" class="block text-sm font-medium text-slate-300 mb-2">Password</label>
					<div class="relative">
						<input
							id="signup-password"
							type={showPassword ? 'text' : 'password'}
							bind:value={password}
							placeholder="At least 8 characters"
							class="auth-input pr-10"
							required
							minlength="8"
						/>
						<button
							type="button"
							class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
							onclick={() => showPassword = !showPassword}
							aria-label={showPassword ? 'Hide password' : 'Show password'}
						>
							{#if showPassword}
								<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
								</svg>
							{:else}
								<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
									<path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
								</svg>
							{/if}
						</button>
					</div>
					<!-- Password strength -->
					{#if password.length > 0}
						<div class="mt-2.5 flex items-center gap-2">
							<div class="flex-1 h-1 rounded-full bg-white/[0.06] overflow-hidden">
								<div
									class="h-full rounded-full transition-all duration-300 {strength.color}"
									style="width: {(strength.score / 4) * 100}%"
								></div>
							</div>
							<span class="text-[11px] text-slate-500">{strength.label}</span>
						</div>
					{/if}
				</div>

				<button
					type="submit"
					disabled={loading}
					class="group relative w-full flex items-center justify-center gap-2 py-3.5 rounded-xl text-sm font-semibold text-white overflow-hidden transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/20 disabled:opacity-70 disabled:cursor-not-allowed mt-6"
				>
					<div class="absolute inset-0 bg-gradient-to-r from-emerald-500 to-emerald-600 group-hover:from-emerald-400 group-hover:to-emerald-500 transition-all duration-300"></div>
					{#if loading}
						<svg class="relative w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
						</svg>
						<span class="relative">Creating account...</span>
					{:else}
						<span class="relative">Create account</span>
					{/if}
				</button>
			</form>

			<p class="mt-6 text-center text-xs text-slate-600">
				By signing up, you agree to our
				<a href="#" class="text-slate-400 hover:text-slate-300 transition-colors">Terms of Service</a> and
				<a href="#" class="text-slate-400 hover:text-slate-300 transition-colors">Privacy Policy</a>.
			</p>
		</div>
	</div>
</div>

<style>
	.auth-bg {
		position: fixed;
		inset: 0;
		z-index: 0;
	}

	.auth-gradient-signup {
		position: absolute;
		inset: 0;
		background:
			radial-gradient(ellipse 50% 50% at 25% 50%, rgba(16, 185, 129, 0.06) 0%, transparent 70%),
			radial-gradient(ellipse 30% 40% at 75% 30%, rgba(16, 185, 129, 0.03) 0%, transparent 70%);
	}

	.auth-grid-signup {
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(rgba(255,255,255,0.01) 1px, transparent 1px),
			linear-gradient(90deg, rgba(255,255,255,0.01) 1px, transparent 1px);
		background-size: 60px 60px;
		mask-image: radial-gradient(ellipse 70% 60% at 30% 50%, black, transparent);
	}

	select option {
		background: #111827;
		color: #e2e8f0;
	}
</style>
