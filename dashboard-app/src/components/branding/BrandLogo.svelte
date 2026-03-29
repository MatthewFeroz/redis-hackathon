<script lang="ts">
	type Props = {
		markClass?: string;
		textClass?: string;
		showText?: boolean;
		text?: string;
	};

	let {
		markClass = 'w-10 h-10',
		textClass = 'text-lg',
		showText = true,
		text = 'Plumbly'
	}: Props = $props();
</script>

<span class="inline-flex items-center gap-3">
	<img src="/brand-star.svg" alt="Plumbly logo" class={markClass} />
	{#if showText}
		<span class={`font-bold tracking-tight text-white ${textClass}`}>{text}</span>
	{/if}
</span>
