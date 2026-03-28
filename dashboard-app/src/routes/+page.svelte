<script lang="ts">
	import { onMount } from 'svelte';
	import Navbar from '../components/landing/Navbar.svelte';

	let heroVisible = $state(false);
	let statsVisible = $state(false);
	let featuresVisible = $state(false);
	let howVisible = $state(false);
	let pricingVisible = $state(false);
	let currentIndustry = $state(0);

	onMount(() => {
		// Always start at the top on page load/refresh
		if (history.scrollRestoration) {
			history.scrollRestoration = 'manual';
		}
		window.scrollTo(0, 0);

		// Clear any hash fragment so refresh won't auto-scroll to an anchor
		if (window.location.hash) {
			history.replaceState(null, '', window.location.pathname + window.location.search);
		}

		// Staggered hero entrance
		setTimeout(() => heroVisible = true, 100);

		// Rotate industries every 2.5s
		const industryInterval = setInterval(() => {
			currentIndustry = (currentIndustry + 1) % industries.length;
		}, 2500);

		const observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting) {
						const id = entry.target.getAttribute('data-animate');
						if (id === 'stats') statsVisible = true;
						if (id === 'features') featuresVisible = true;
						if (id === 'how') howVisible = true;
						if (id === 'pricing') pricingVisible = true;
					}
				});
			},
			{ threshold: 0.15 }
		);

		document.querySelectorAll('[data-animate]').forEach((el) => observer.observe(el));

		return () => {
			observer.disconnect();
			clearInterval(industryInterval);
		};
	});

	const industries = [
		{ icon: '🔧', label: 'Plumbing' },
		{ icon: '🍽️', label: 'Restaurants' },
		{ icon: '❄️', label: 'HVAC' },
		{ icon: '💇', label: 'Salons' },
		{ icon: '🦷', label: 'Dental' },
		{ icon: '🏠', label: 'Real Estate' },
		{ icon: '⚡', label: 'Electricians' },
		{ icon: '🚗', label: 'Auto Repair' },
	];

	const features = [
		{
			title: 'AI Conversations',
			description: 'Our AI agent chats naturally with your customers, guiding them through the review process without friction or awkwardness.',
			icon: 'chat',
			accent: 'emerald'
		},
		{
			title: 'Smart Timing',
			description: 'Automatically reach out at the perfect moment — right after service completion when satisfaction is highest.',
			icon: 'clock',
			accent: 'blue'
		},
		{
			title: 'Real-time Dashboard',
			description: 'Track every review in your pipeline. See who\'s engaged, who\'s submitted, and where to follow up.',
			icon: 'chart',
			accent: 'amber'
		},
		{
			title: 'SMS & Link Delivery',
			description: 'Send personalized review links via SMS or email. Customers tap once and the AI handles the rest.',
			icon: 'send',
			accent: 'violet'
		},
		{
			title: 'Sentiment Analysis',
			description: 'Catch unhappy customers before they post negative reviews. Route concerns to your team instantly.',
			icon: 'shield',
			accent: 'rose'
		},
		{
			title: 'Google Integration',
			description: 'Direct connection to Google Business Profile. Reviews land exactly where they matter most for your SEO.',
			icon: 'globe',
			accent: 'cyan'
		},
	];

	const steps = [
		{
			number: '01',
			title: 'Complete a job',
			description: 'Log the customer info in Plumbly after finishing a service call, appointment, or visit.'
		},
		{
			number: '02',
			title: 'Customer gets a link',
			description: 'An SMS or email is automatically sent with a personalized link to your AI review assistant.'
		},
		{
			number: '03',
			title: 'AI guides the review',
			description: 'Our AI agent has a friendly conversation, making it effortless for customers to leave a detailed, genuine review.'
		},
		{
			number: '04',
			title: 'Review goes live',
			description: 'The review is posted directly to Google. You see it instantly in your dashboard with full analytics.'
		}
	];

	const plans = [
		{
			name: 'Starter',
			price: '29',
			description: 'For solo operators just getting started with review generation.',
			features: ['50 review requests/mo', 'AI review assistant', 'SMS delivery', 'Basic dashboard', 'Google integration'],
			cta: 'Start free trial',
			popular: false
		},
		{
			name: 'Pro',
			price: '79',
			description: 'For growing businesses that want to dominate local search.',
			features: ['Unlimited review requests', 'AI review assistant', 'SMS + Email delivery', 'Advanced analytics', 'Sentiment filtering', 'Priority support', 'Custom branding'],
			cta: 'Start free trial',
			popular: true
		},
		{
			name: 'Agency',
			price: '199',
			description: 'For agencies managing reviews across multiple locations.',
			features: ['Everything in Pro', 'Up to 10 locations', 'White-label dashboard', 'API access', 'Team management', 'Dedicated account manager', 'Custom integrations'],
			cta: 'Contact sales',
			popular: false
		}
	];

	const testimonials = [
		{
			quote: "We went from 12 Google reviews to 89 in three months. Plumbly basically runs itself.",
			name: "Marcus Rodriguez",
			role: "Owner, Rodriguez Plumbing",
			rating: 5
		},
		{
			quote: "Our customers actually enjoy the process. The AI is friendly, not pushy. That makes all the difference.",
			name: "Sarah Chen",
			role: "Manager, Sakura Bistro",
			rating: 5
		},
		{
			quote: "The ROI is insane. We spend $79/mo and get reviews that would cost thousands in marketing to replicate.",
			name: "James Thornton",
			role: "CEO, Comfort Air HVAC",
			rating: 5
		}
	];
</script>

<svelte:head>
	<title>Plumbly — AI-Powered Review Generation for Service Businesses</title>
	<meta name="description" content="Turn every happy customer into a 5-star Google review. Plumbly's AI assistant makes review generation effortless for plumbers, restaurants, HVAC, salons, and more." />
</svelte:head>

<Navbar />

<main class="relative overflow-hidden">
	<!-- =========== HERO =========== -->
	<section class="relative min-h-[100dvh] flex items-center pt-20">
		<!-- Background Effects -->
		<div class="hero-bg">
			<div class="hero-gradient"></div>
			<div class="hero-grid"></div>
			<div class="hero-orb hero-orb--1"></div>
			<div class="hero-orb hero-orb--2"></div>
		</div>

		<div class="max-w-7xl mx-auto px-5 sm:px-8 py-16 sm:py-24 relative z-10 w-full">
			<div class="max-w-4xl">
				<!-- Headline -->
				<h1
					class="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.05] transition-all duration-700 delay-100"
					class:opacity-0={!heroVisible}
					class:translate-y-6={!heroVisible}
					class:opacity-100={heroVisible}
					class:translate-y-0={heroVisible}
				>
					<span class="text-white">Turn happy customers into </span>
					<span class="hero-gradient-text">5-star reviews</span>
				</h1>

				<!-- Subheadline -->
				<p
					class="mt-6 sm:mt-8 text-lg sm:text-xl text-slate-400 max-w-2xl leading-relaxed transition-all duration-700 delay-200"
					class:opacity-0={!heroVisible}
					class:translate-y-6={!heroVisible}
					class:opacity-100={heroVisible}
					class:translate-y-0={heroVisible}
				>
					Plumbly's AI assistant chats with your customers after every job, guiding them to leave genuine Google reviews — no awkward asks, no forgotten follow-ups.
				</p>

				<!-- CTA Row -->
				<div
					class="mt-10 sm:mt-12 flex flex-col sm:flex-row items-start sm:items-center gap-4 transition-all duration-700 delay-300"
					class:opacity-0={!heroVisible}
					class:translate-y-6={!heroVisible}
					class:opacity-100={heroVisible}
					class:translate-y-0={heroVisible}
				>
					<a
						href="/signup"
						class="group relative inline-flex items-center gap-2 px-7 py-4 text-base font-semibold text-white rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-emerald-500/25 hover:-translate-y-0.5"
					>
						<div class="absolute inset-0 bg-gradient-to-r from-emerald-500 to-emerald-600 group-hover:from-emerald-400 group-hover:to-emerald-500 transition-all duration-300"></div>
						<span class="relative">Start free trial</span>
						<svg class="relative w-4 h-4 group-hover:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
							<path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
						</svg>
					</a>
					<span class="text-sm text-slate-500">No credit card required &middot; 14-day free trial</span>
				</div>

				<!-- Industry Carousel -->
				<div
					class="mt-16 sm:mt-20 transition-all duration-700 delay-[400ms]"
					class:opacity-0={!heroVisible}
					class:translate-y-6={!heroVisible}
					class:opacity-100={heroVisible}
					class:translate-y-0={heroVisible}
				>
					<div class="flex items-center gap-3">
						<p class="text-sm text-slate-500">Built for</p>
						<div style="position: relative; height: 2rem; min-width: 10rem; overflow: hidden;">
							{#each industries as ind, i}
								<div
									style="position: absolute; top: 0; left: 0; display: flex; align-items: center; gap: 0.5rem; height: 2rem; white-space: nowrap; transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1); opacity: {i === currentIndustry ? 1 : 0}; transform: translateY({i === currentIndustry ? '0%' : '100%'}); pointer-events: {i === currentIndustry ? 'auto' : 'none'};"
								>
									<span class="text-lg">{ind.icon}</span>
									<span class="text-sm font-semibold text-emerald-300">{ind.label}</span>
								</div>
							{/each}
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- =========== SOCIAL PROOF STRIP =========== -->
	<section
		class="relative py-16 sm:py-20 border-y border-white/[0.04]"
		data-animate="stats"
	>
		<div class="max-w-7xl mx-auto px-5 sm:px-8">
			<div
				class="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12 transition-all duration-700"
				class:opacity-0={!statsVisible}
				class:translate-y-8={!statsVisible}
				class:opacity-100={statsVisible}
				class:translate-y-0={statsVisible}
			>
				{#each [
					{ value: '50K+', label: 'Reviews generated' },
					{ value: '2,400+', label: 'Active businesses' },
					{ value: '4.8', label: 'Avg review rating' },
					{ value: '89%', label: 'Completion rate' },
				] as stat, i}
					<div class="text-center" style="transition-delay: {i * 100}ms">
						<p class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">{stat.value}</p>
						<p class="text-sm text-slate-500 mt-1">{stat.label}</p>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- =========== FEATURES =========== -->
	<section id="features" class="relative py-24 sm:py-32" data-animate="features">
		<div class="max-w-7xl mx-auto px-5 sm:px-8">
			<div
				class="text-center max-w-2xl mx-auto mb-16 sm:mb-20 transition-all duration-700"
				class:opacity-0={!featuresVisible}
				class:translate-y-8={!featuresVisible}
				class:opacity-100={featuresVisible}
				class:translate-y-0={featuresVisible}
			>
				<p class="text-xs font-semibold text-emerald-400 uppercase tracking-widest mb-4">Features</p>
				<h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white">
					Everything you need to<br />
					<span class="hero-gradient-text">own your reputation</span>
				</h2>
				<p class="mt-5 text-lg text-slate-400">
					From the first SMS to a live Google review — Plumbly handles the entire journey automatically.
				</p>
			</div>

			<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
				{#each features as feature, i}
					{@const accentMap: Record<string, string> = {
						emerald: 'from-emerald-500/20 to-emerald-500/0 text-emerald-400 border-emerald-500/20',
						blue: 'from-blue-500/20 to-blue-500/0 text-blue-400 border-blue-500/20',
						amber: 'from-amber-500/20 to-amber-500/0 text-amber-400 border-amber-500/20',
						violet: 'from-violet-500/20 to-violet-500/0 text-violet-400 border-violet-500/20',
						rose: 'from-rose-500/20 to-rose-500/0 text-rose-400 border-rose-500/20',
						cyan: 'from-cyan-500/20 to-cyan-500/0 text-cyan-400 border-cyan-500/20',
					}}
					{@const colors = accentMap[feature.accent] ?? accentMap.emerald}
					<div
						class="group card-glow p-6 sm:p-7 hover:border-white/[0.1] transition-all duration-500"
						style="transition-delay: {i * 80}ms"
						class:opacity-0={!featuresVisible}
						class:translate-y-6={!featuresVisible}
						class:opacity-100={featuresVisible}
						class:translate-y-0={featuresVisible}
					>
						<div class="w-10 h-10 rounded-xl bg-gradient-to-b {colors.split(' ').slice(0, 2).join(' ')} border {colors.split(' ').slice(-1)[0]} flex items-center justify-center mb-5">
							{#if feature.icon === 'chat'}
								<svg class="w-5 h-5 {colors.split(' ')[2]}" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
								</svg>
							{:else if feature.icon === 'clock'}
								<svg class="w-5 h-5 {colors.split(' ')[2]}" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
							{:else if feature.icon === 'chart'}
								<svg class="w-5 h-5 {colors.split(' ')[2]}" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
								</svg>
							{:else if feature.icon === 'send'}
								<svg class="w-5 h-5 {colors.split(' ')[2]}" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
								</svg>
							{:else if feature.icon === 'shield'}
								<svg class="w-5 h-5 {colors.split(' ')[2]}" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
								</svg>
							{:else}
								<svg class="w-5 h-5 {colors.split(' ')[2]}" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
								</svg>
							{/if}
						</div>
						<h3 class="text-lg font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors duration-300">{feature.title}</h3>
						<p class="text-sm text-slate-400 leading-relaxed">{feature.description}</p>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- =========== HOW IT WORKS =========== -->
	<section id="how-it-works" class="relative py-24 sm:py-32" data-animate="how">
		<!-- Subtle divider -->
		<div class="absolute top-0 left-1/2 -translate-x-1/2 w-[60%] h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent"></div>

		<div class="max-w-7xl mx-auto px-5 sm:px-8">
			<div
				class="text-center max-w-2xl mx-auto mb-16 sm:mb-20 transition-all duration-700"
				class:opacity-0={!howVisible}
				class:translate-y-8={!howVisible}
				class:opacity-100={howVisible}
				class:translate-y-0={howVisible}
			>
				<p class="text-xs font-semibold text-emerald-400 uppercase tracking-widest mb-4">How it works</p>
				<h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white">
					Four steps to<br />
					<span class="hero-gradient-text">review autopilot</span>
				</h2>
			</div>

			<div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
				{#each steps as step, i}
					<div
						class="relative transition-all duration-700"
						style="transition-delay: {i * 120}ms"
						class:opacity-0={!howVisible}
						class:translate-y-8={!howVisible}
						class:opacity-100={howVisible}
						class:translate-y-0={howVisible}
					>
						<!-- Connector line (not on last) -->
						{#if i < steps.length - 1}
							<div class="hidden lg:block absolute top-8 left-[calc(100%+0.25rem)] w-[calc(100%-2rem)] h-px bg-gradient-to-r from-emerald-500/30 to-transparent"></div>
						{/if}
						<div class="relative p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-emerald-500/20 transition-colors duration-300">
							<span class="text-5xl font-black text-white/[0.04] absolute top-3 right-4 select-none">{step.number}</span>
							<div class="w-10 h-10 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-5">
								<span class="text-sm font-bold text-emerald-400">{step.number}</span>
							</div>
							<h3 class="text-base font-bold text-white mb-2">{step.title}</h3>
							<p class="text-sm text-slate-400 leading-relaxed">{step.description}</p>
						</div>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- =========== TESTIMONIALS =========== -->
	<section class="relative py-24 sm:py-32">
		<div class="absolute top-0 left-1/2 -translate-x-1/2 w-[60%] h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent"></div>

		<div class="max-w-7xl mx-auto px-5 sm:px-8">
			<div class="text-center max-w-2xl mx-auto mb-16">
				<p class="text-xs font-semibold text-emerald-400 uppercase tracking-widest mb-4">Testimonials</p>
				<h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
					Loved by service businesses
				</h2>
			</div>

			<div class="grid md:grid-cols-3 gap-5">
				{#each testimonials as t, i}
					<div class="card-glow p-6 sm:p-8 flex flex-col">
						<!-- Stars -->
						<div class="flex gap-0.5 mb-5">
							{#each Array(t.rating) as _}
								<svg class="w-4 h-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
									<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
								</svg>
							{/each}
						</div>
						<blockquote class="text-base text-slate-300 leading-relaxed flex-1">"{t.quote}"</blockquote>
						<div class="mt-6 pt-5 border-t border-white/[0.06]">
							<p class="text-sm font-semibold text-white">{t.name}</p>
							<p class="text-xs text-slate-500 mt-0.5">{t.role}</p>
						</div>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- =========== PRICING =========== -->
	<section id="pricing" class="relative py-24 sm:py-32" data-animate="pricing">
		<div class="absolute top-0 left-1/2 -translate-x-1/2 w-[60%] h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent"></div>

		<div class="max-w-7xl mx-auto px-5 sm:px-8">
			<div
				class="text-center max-w-2xl mx-auto mb-16 sm:mb-20 transition-all duration-700"
				class:opacity-0={!pricingVisible}
				class:translate-y-8={!pricingVisible}
				class:opacity-100={pricingVisible}
				class:translate-y-0={pricingVisible}
			>
				<p class="text-xs font-semibold text-emerald-400 uppercase tracking-widest mb-4">Pricing</p>
				<h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white">
					Simple, transparent pricing
				</h2>
				<p class="mt-5 text-lg text-slate-400">
					Start free. Upgrade when you're ready. Cancel anytime.
				</p>
			</div>

			<div class="grid md:grid-cols-3 gap-5 lg:gap-6 max-w-5xl mx-auto">
				{#each plans as plan, i}
					<div
						class="relative rounded-2xl transition-all duration-700 {plan.popular ? 'ring-2 ring-emerald-500/50' : ''}"
						style="transition-delay: {i * 100}ms"
						class:opacity-0={!pricingVisible}
						class:translate-y-8={!pricingVisible}
						class:opacity-100={pricingVisible}
						class:translate-y-0={pricingVisible}
					>
						{#if plan.popular}
							<div class="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3 py-1 bg-emerald-500 rounded-full text-[11px] font-bold text-white uppercase tracking-wider">
								Most popular
							</div>
						{/if}
						<div class="card-glow p-6 sm:p-8 h-full flex flex-col {plan.popular ? 'border-emerald-500/30' : ''}">
							<div class="mb-6">
								<h3 class="text-lg font-bold text-white">{plan.name}</h3>
								<p class="text-sm text-slate-400 mt-1">{plan.description}</p>
							</div>
							<div class="flex items-baseline gap-1 mb-6">
								<span class="text-4xl font-extrabold text-white">${plan.price}</span>
								<span class="text-sm text-slate-500">/mo</span>
							</div>
							<ul class="space-y-3 mb-8 flex-1">
								{#each plan.features as feat}
									<li class="flex items-center gap-2.5 text-sm text-slate-300">
										<svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
											<path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
										</svg>
										{feat}
									</li>
								{/each}
							</ul>
							<a
								href="/signup"
								class="block w-full text-center py-3 rounded-xl text-sm font-semibold transition-all duration-300 {plan.popular
									? 'bg-emerald-500 text-white hover:bg-emerald-400 shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/30'
									: 'bg-white/[0.06] text-slate-300 hover:bg-white/[0.1] hover:text-white border border-white/[0.08]'
								}"
							>
								{plan.cta}
							</a>
						</div>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- =========== FINAL CTA =========== -->
	<section class="relative py-24 sm:py-32">
		<div class="absolute top-0 left-1/2 -translate-x-1/2 w-[60%] h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent"></div>

		<div class="max-w-7xl mx-auto px-5 sm:px-8">
			<div class="relative card-glow p-10 sm:p-16 text-center overflow-hidden">
				<!-- Background glow -->
				<div class="absolute inset-0 bg-gradient-to-b from-emerald-500/[0.08] via-transparent to-transparent pointer-events-none"></div>
				<div class="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-40 bg-emerald-500/20 blur-[100px] rounded-full pointer-events-none"></div>

				<div class="relative">
					<h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white mb-5">
						Start collecting reviews today
					</h2>
					<p class="text-lg text-slate-400 max-w-xl mx-auto mb-10">
						Join thousands of service businesses using Plumbly to build their reputation on autopilot. Set up takes less than 5 minutes.
					</p>
					<div class="flex flex-col sm:flex-row items-center justify-center gap-4">
						<a
							href="/signup"
							class="group relative inline-flex items-center gap-2 px-8 py-4 text-base font-semibold text-white rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-emerald-500/25 hover:-translate-y-0.5"
						>
							<div class="absolute inset-0 bg-gradient-to-r from-emerald-500 to-emerald-600 group-hover:from-emerald-400 group-hover:to-emerald-500 transition-all duration-300"></div>
							<span class="relative">Get started free</span>
							<svg class="relative w-4 h-4 group-hover:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
								<path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
							</svg>
						</a>
						<a
							href="#how-it-works"
							class="inline-flex items-center gap-2 px-6 py-4 text-sm font-medium text-slate-400 hover:text-white transition-colors duration-200"
						>
							See how it works
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
								<path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
							</svg>
						</a>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- =========== FOOTER =========== -->
	<footer class="relative py-12 sm:py-16 border-t border-white/[0.04]">
		<div class="max-w-7xl mx-auto px-5 sm:px-8">
			<div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
				<!-- Brand -->
				<div class="sm:col-span-2 lg:col-span-1">
					<div class="flex items-center gap-2.5 mb-4">
						<div class="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center">
							<svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
								<path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
							</svg>
						</div>
						<span class="text-base font-bold text-white">Plumbly</span>
					</div>
					<p class="text-sm text-slate-500 leading-relaxed max-w-xs">
						AI-powered review generation for service businesses. Turn every happy customer into a 5-star advocate.
					</p>
				</div>

				<!-- Links -->
				<div>
					<p class="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-4">Product</p>
					<ul class="space-y-2.5">
						<li><a href="#features" class="text-sm text-slate-500 hover:text-slate-300 transition-colors">Features</a></li>
						<li><a href="#pricing" class="text-sm text-slate-500 hover:text-slate-300 transition-colors">Pricing</a></li>
						<li><a href="#how-it-works" class="text-sm text-slate-500 hover:text-slate-300 transition-colors">How it works</a></li>
						<li><a href="/dashboard" class="text-sm text-slate-500 hover:text-slate-300 transition-colors">Dashboard</a></li>
					</ul>
				</div>
				<div>
					<p class="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-4">Company</p>
					<ul class="space-y-2.5">
						<li><a href="#" class="text-sm text-slate-500 hover:text-slate-300 transition-colors">About</a></li>
						<li><a href="#" class="text-sm text-slate-500 hover:text-slate-300 transition-colors">Blog</a></li>
						<li><a href="#" class="text-sm text-slate-500 hover:text-slate-300 transition-colors">Careers</a></li>
						<li><a href="#" class="text-sm text-slate-500 hover:text-slate-300 transition-colors">Contact</a></li>
					</ul>
				</div>
				<div>
					<p class="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-4">Legal</p>
					<ul class="space-y-2.5">
						<li><a href="#" class="text-sm text-slate-500 hover:text-slate-300 transition-colors">Privacy</a></li>
						<li><a href="#" class="text-sm text-slate-500 hover:text-slate-300 transition-colors">Terms</a></li>
						<li><a href="#" class="text-sm text-slate-500 hover:text-slate-300 transition-colors">Security</a></li>
					</ul>
				</div>
			</div>

			<div class="mt-12 pt-8 border-t border-white/[0.04] flex flex-col sm:flex-row items-center justify-between gap-4">
				<p class="text-xs text-slate-600">&copy; 2026 Plumbly. All rights reserved.</p>
				<div class="flex items-center gap-5">
					<!-- Twitter/X -->
					<a href="#" class="text-slate-600 hover:text-slate-400 transition-colors" aria-label="Twitter">
						<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
					</a>
					<!-- LinkedIn -->
					<a href="#" class="text-slate-600 hover:text-slate-400 transition-colors" aria-label="LinkedIn">
						<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
					</a>
					<!-- GitHub -->
					<a href="#" class="text-slate-600 hover:text-slate-400 transition-colors" aria-label="GitHub">
						<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
					</a>
				</div>
			</div>
		</div>
	</footer>
</main>

<style>
	/* Hero Background Effects */
	.hero-bg {
		position: absolute;
		inset: 0;
		overflow: hidden;
		z-index: 0;
	}

	.hero-gradient {
		position: absolute;
		inset: 0;
		background:
			radial-gradient(ellipse 60% 50% at 20% 40%, rgba(16, 185, 129, 0.08) 0%, transparent 70%),
			radial-gradient(ellipse 40% 60% at 80% 20%, rgba(16, 185, 129, 0.04) 0%, transparent 70%);
	}

	.hero-grid {
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
			linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
		background-size: 80px 80px;
		mask-image: radial-gradient(ellipse 70% 60% at 50% 40%, black, transparent);
	}

	.hero-orb {
		position: absolute;
		border-radius: 50%;
		filter: blur(80px);
		opacity: 0.5;
	}

	.hero-orb--1 {
		width: 500px;
		height: 500px;
		top: -100px;
		left: -100px;
		background: radial-gradient(circle, rgba(16, 185, 129, 0.12), transparent 70%);
		animation: orb-drift-1 20s ease-in-out infinite;
	}

	.hero-orb--2 {
		width: 400px;
		height: 400px;
		bottom: -50px;
		right: -50px;
		background: radial-gradient(circle, rgba(16, 185, 129, 0.08), transparent 70%);
		animation: orb-drift-2 25s ease-in-out infinite;
	}

	@keyframes orb-drift-1 {
		0%, 100% { transform: translate(0, 0); }
		33% { transform: translate(30px, 20px); }
		66% { transform: translate(-20px, 30px); }
	}

	@keyframes orb-drift-2 {
		0%, 100% { transform: translate(0, 0); }
		33% { transform: translate(-25px, -15px); }
		66% { transform: translate(15px, -25px); }
	}

	/* Gradient text */
	.hero-gradient-text {
		background: linear-gradient(135deg, #34d399 0%, #10b981 50%, #6ee7b7 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

</style>
