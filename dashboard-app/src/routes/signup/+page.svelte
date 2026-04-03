<script lang="ts">
	import { onMount } from 'svelte';

	onMount(() => {
		window.location.href = '/auth/login?screen_hint=sign-up&return_to=/dashboard';
	});
</script>
