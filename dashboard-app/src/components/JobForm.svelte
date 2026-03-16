<script lang="ts">
	import { getStore } from '$lib/stores.svelte';
	import { api } from '$lib/api';

	const store = getStore();

	let customerName = $state('');
	let customerPhone = $state('');
	let customerEmail = $state('');
	let customerAddress = $state('');
	let customerZip = $state('');
	let referralSource = $state('');
	let plumberName = $state('Eddy');
	let jobDescription = $state('');
	let jobType = $state('');
	let jobTotal = $state('');
	let jobDate = $state('');
	let isRepeatCustomer = $state(false);
	let followUpNotes = $state('');
	let submitting = $state(false);
	let successLink = $state<string | null>(null);
	let successCustomerName = $state('');
	let successPlumberName = $state('');
	let successPhone = $state('');
	let smsSent = $state(false);
	let smsError = $state<string | null>(null);
	let copied = $state(false);
	let showMore = $state(false);

	const inputClass = 'w-full bg-surface-900 border border-surface-600 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-colors';
	const selectClass = `${inputClass} appearance-none cursor-pointer pr-9`;
	const labelClass = 'text-xs font-medium uppercase tracking-wider text-slate-400';

	const jobTypes = [
		'',
		'Drain Cleaning',
		'Leak Repair',
		'Water Heater',
		'Pipe Replacement',
		'Faucet Install',
		'Toilet Repair',
		'Sewer Line',
		'Gas Line',
		'Garbage Disposal',
		'Sump Pump',
		'Other'
	];

	const referralSources = [
		'',
		'Google Search',
		'Google Maps',
		'Referral',
		'Yelp',
		'Facebook',
		'Nextdoor',
		'Repeat Customer',
		'Yard Sign',
		'Other'
	];

	async function handleSubmit(e: Event) {
		e.preventDefault();
		if (!customerName.trim()) return;
		submitting = true;
		successLink = null;
		smsSent = false;
		smsError = null;
		try {
			const result = await api.createJob({
				customer_name: customerName,
				customer_phone: customerPhone,
				customer_email: customerEmail,
				customer_address: customerAddress,
				customer_zip: customerZip,
				referral_source: referralSource,
				plumber_name: plumberName,
				job_description: jobDescription,
				job_type: jobType,
				job_total: jobTotal,
				job_date: jobDate,
				is_repeat_customer: isRepeatCustomer,
				follow_up_notes: followUpNotes
			});
			successLink = result.review_link;
			successCustomerName = customerName;
			successPlumberName = plumberName;
			successPhone = customerPhone;
			smsSent = result.sms_sent;
			smsError = result.sms_error ?? null;
			customerName = '';
			customerPhone = '';
			customerEmail = '';
			customerAddress = '';
			customerZip = '';
			referralSource = '';
			jobDescription = '';
			jobType = '';
			jobTotal = '';
			jobDate = '';
			plumberName = 'Eddy';
			isRepeatCustomer = false;
			followUpNotes = '';
			showMore = false;
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
		<!-- Primary fields — always visible -->
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
			<div class="space-y-1.5">
				<label for="name" class={labelClass}>
					Customer Name <span class="text-red-400">*</span>
				</label>
				<input
					id="name"
					type="text"
					bind:value={customerName}
					required
					placeholder="John Smith"
					class={inputClass}
				/>
			</div>
			<div class="space-y-1.5">
				<label for="phone" class={labelClass}>Phone</label>
				<input
					id="phone"
					type="text"
					bind:value={customerPhone}
					placeholder="(555) 123-4567"
					class={inputClass}
				/>
			</div>
			<div class="space-y-1.5">
				<label for="email" class={labelClass}>Email</label>
				<input
					id="email"
					type="email"
					bind:value={customerEmail}
					placeholder="customer@email.com"
					class={inputClass}
				/>
			</div>
			<div class="space-y-1.5">
				<label for="plumber" class={labelClass}>Plumber</label>
				<div class="relative">
					<select id="plumber" bind:value={plumberName} class={selectClass}>
						<option value="Eddy">Eddy</option>
						<option value="Matt">Matt</option>
						<option value="Ryan">Ryan</option>
					</select>
					<svg class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
				</div>
			</div>
		</div>

		<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
			<div class="space-y-1.5">
				<label for="job-type" class={labelClass}>Job Type</label>
				<div class="relative">
					<select id="job-type" bind:value={jobType} class={selectClass}>
						{#each jobTypes as jt}
							<option value={jt}>{jt || 'Select type...'}</option>
						{/each}
					</select>
					<svg class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
				</div>
			</div>
			<div class="space-y-1.5">
				<label for="desc" class={labelClass}>Job Description</label>
				<input
					id="desc"
					type="text"
					bind:value={jobDescription}
					placeholder="e.g. Fixed kitchen sink leak"
					class={inputClass}
				/>
			</div>
		</div>

		<!-- Expandable section -->
		<button
			type="button"
			onclick={() => { showMore = !showMore; }}
			class="flex items-center gap-2 text-xs text-slate-500 hover:text-slate-300 transition-colors cursor-pointer"
		>
			<svg
				class="w-3.5 h-3.5 transition-transform {showMore ? 'rotate-90' : ''}"
				fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
			>
				<path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
			</svg>
			{showMore ? 'Less details' : 'More details'}
		</button>

		{#if showMore}
			<div class="space-y-4 animate-fade-in">
				<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
					<div class="space-y-1.5">
						<label for="address" class={labelClass}>Address</label>
						<input
							id="address"
							type="text"
							bind:value={customerAddress}
							placeholder="123 Main St, Apt 4"
							class={inputClass}
						/>
					</div>
					<div class="space-y-1.5">
						<label for="zip" class={labelClass}>Zip Code</label>
						<input
							id="zip"
							type="text"
							bind:value={customerZip}
							placeholder="10001"
							class={inputClass}
						/>
					</div>
					<div class="space-y-1.5">
						<label for="referral" class={labelClass}>Referral Source</label>
						<div class="relative">
							<select id="referral" bind:value={referralSource} class={selectClass}>
								{#each referralSources as src}
									<option value={src}>{src || 'How did they find us?'}</option>
								{/each}
							</select>
							<svg class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
						</div>
					</div>
					<div class="space-y-1.5">
						<label for="job-total" class={labelClass}>Job Total</label>
						<input
							id="job-total"
							type="text"
							bind:value={jobTotal}
							placeholder="$250"
							class={inputClass}
						/>
					</div>
					<div class="space-y-1.5">
						<label for="job-date" class={labelClass}>Job Date</label>
						<input
							id="job-date"
							type="date"
							bind:value={jobDate}
							class={inputClass}
						/>
					</div>
					<div class="flex items-end pb-1">
						<label class="flex items-center gap-2.5 cursor-pointer group">
							<input
								type="checkbox"
								bind:checked={isRepeatCustomer}
								class="w-4 h-4 rounded border-surface-600 bg-surface-900 text-emerald-500 focus:ring-emerald-500/20 cursor-pointer accent-emerald-500"
							/>
							<span class="text-sm text-slate-400 group-hover:text-slate-300 transition-colors">Repeat customer</span>
						</label>
					</div>
				</div>
				<div class="space-y-1.5">
					<label for="notes" class={labelClass}>Follow-up Notes</label>
					<textarea
						id="notes"
						bind:value={followUpNotes}
						placeholder="Any notes for follow-up..."
						rows="2"
						class="{inputClass} resize-none"
					></textarea>
				</div>
			</div>
		{/if}

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
			<div class="flex items-center gap-2 mb-3">
				<svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
				</svg>
				<span class="text-sm font-medium text-emerald-400">Review link created!</span>
			</div>

			<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 mb-4">
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

			<!-- SMS Preview -->
			<div class="border border-surface-600 rounded-xl overflow-hidden">
				<div class="bg-surface-700 px-3 py-2 flex items-center gap-2 border-b border-surface-600">
					<svg class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
					</svg>
					<span class="text-[11px] font-medium text-slate-300">SMS via Twilio</span>
					{#if successPhone}
						<span class="text-[11px] text-slate-500 ml-auto">To: {successPhone}</span>
					{/if}
					{#if smsSent}
						<span class="text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded-full ml-2">Delivered</span>
					{:else}
						<span class="text-[10px] text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded-full ml-2">Preview</span>
					{/if}
				</div>
				<div class="bg-surface-900 p-4">
					<!-- Phone mockup bubble -->
					<div class="max-w-[280px]">
						<div class="bg-[#1e88e5] text-white text-[13px] leading-relaxed px-3.5 py-2.5 rounded-2xl rounded-bl-md shadow-sm">
							<p>Hi {successCustomerName}! Thanks for choosing{successPlumberName ? ` ${successPlumberName} at` : ''} R&M Plumbing and Heating. We'd really appreciate a quick Google review — it only takes 60 seconds!</p>
							<p class="mt-2 opacity-90 break-all">{successLink}</p>
						</div>
						<p class="text-[10px] text-slate-600 mt-1.5 ml-1">
							{#if smsSent}
								Sent via Twilio Messaging Service
							{:else}
								SMS will be sent when Twilio A2P registration is complete
							{/if}
						</p>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>
