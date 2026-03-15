<script lang="ts">
	import { getStore } from '$lib/stores.svelte';
	import { api } from '$lib/api';

	const store = getStore();

	let customerName = $state('');
	let customerPhone = $state('');
	let customerEmail = $state('');
	let plumberName = $state('Eddy');
	let jobDescription = $state('');
	let submitting = $state(false);
	let successLink = $state<string | null>(null);
	let copied = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		if (!customerName.trim()) return;
		submitting = true;
		successLink = null;
		try {
			const result = await api.createJob({
				customer_name: customerName,
				customer_phone: customerPhone,
				customer_email: customerEmail,
				plumber_name: plumberName,
				job_description: jobDescription
			});
			successLink = result.review_link;
			customerName = '';
			customerPhone = '';
			customerEmail = '';
			jobDescription = '';
			plumberName = 'Eddy';
			store.loadSessions();
			store.loadAnalytics();
		} finally {
			submitting = false;
		}
	}

	async function copyLink() {
		if (successLink) {
			await navigator.clipboard.writeText(successLink);
			copied = true;
			setTimeout(() => { copied = false; }, 2000);
		}
	}
</script>

<div class="card-glow p-4 sm:p-6">
	<div class="flex items-center gap-3 mb-5">
		<div class="bg-emerald-500/10 rounded-lg p-2">
			<svg class="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
				<path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
			</svg>
		</div>
		<h2 class="text-lg font-semibold tracking-tight">New Review Request</h2>
	</div>

	<form onsubmit={handleSubmit} class="space-y-4">
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
			<div class="space-y-1.5">
				<label for="name" class="text-xs font-medium uppercase tracking-wider text-slate-400">
					Customer Name <span class="text-red-400">*</span>
				</label>
				<input
					id="name"
					type="text"
					bind:value={customerName}
					required
					placeholder="John Smith"
					class="w-full bg-surface-900 border border-surface-600 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-colors"
				/>
			</div>
			<div class="space-y-1.5">
				<label for="phone" class="text-xs font-medium uppercase tracking-wider text-slate-400">Phone</label>
				<input
					id="phone"
					type="text"
					bind:value={customerPhone}
					placeholder="(555) 123-4567"
					class="w-full bg-surface-900 border border-surface-600 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-colors"
				/>
			</div>
			<div class="space-y-1.5">
				<label for="email" class="text-xs font-medium uppercase tracking-wider text-slate-400">Email</label>
				<input
					id="email"
					type="email"
					bind:value={customerEmail}
					placeholder="customer@email.com"
					class="w-full bg-surface-900 border border-surface-600 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-colors"
				/>
			</div>
			<div class="space-y-1.5">
				<label for="plumber" class="text-xs font-medium uppercase tracking-wider text-slate-400">Plumber</label>
				<select
					id="plumber"
					bind:value={plumberName}
					class="w-full bg-surface-900 border border-surface-600 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-colors appearance-none cursor-pointer"
				>
					<option value="Eddy">Eddy</option>
					<option value="Matt">Matt</option>
					<option value="Ryan">Ryan</option>
				</select>
			</div>
		</div>
		<div class="space-y-1.5">
			<label for="desc" class="text-xs font-medium uppercase tracking-wider text-slate-400">Job Description</label>
			<input
				id="desc"
				type="text"
				bind:value={jobDescription}
				placeholder="e.g. Fixed kitchen sink leak, replaced garbage disposal"
				class="w-full bg-surface-900 border border-surface-600 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-colors"
			/>
		</div>
		<button
			type="submit"
			disabled={submitting || !customerName.trim()}
			class="w-full sm:w-auto px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-surface-600 disabled:text-slate-500 text-white text-sm font-semibold rounded-lg transition-all duration-200 cursor-pointer disabled:cursor-not-allowed flex items-center justify-center gap-2"
		>
			{#if submitting}
				<svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
				</svg>
				Creating...
			{:else}
				Create Review Link
			{/if}
		</button>
	</form>

	{#if successLink}
		<div class="mt-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-4 animate-fade-in">
			<div class="flex items-center gap-2 mb-2">
				<svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
				</svg>
				<span class="text-sm font-medium text-emerald-400">Review link created!</span>
			</div>
			<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
				<code class="text-xs text-slate-300 bg-surface-900 px-3 py-1.5 rounded flex-1 truncate block min-w-0">{successLink}</code>
				<div class="flex gap-2 shrink-0">
					<button
						onclick={copyLink}
						class="flex-1 sm:flex-none px-3 py-1.5 text-xs font-medium bg-surface-700 hover:bg-surface-600 text-slate-300 rounded transition-colors cursor-pointer"
					>
						{copied ? 'Copied!' : 'Copy'}
					</button>
					<a
						href={successLink}
						target="_blank"
						rel="noopener"
						class="flex-1 sm:flex-none px-3 py-1.5 text-xs font-medium bg-surface-700 hover:bg-surface-600 text-slate-300 rounded transition-colors text-center"
					>
						Open
					</a>
				</div>
			</div>
		</div>
	{/if}
</div>
