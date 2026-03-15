<script lang="ts">
	import '../app.css';
	import ToastContainer from '../components/ToastContainer.svelte';

	let { children } = $props();
</script>

{@render children()}
<ToastContainer />
