<script lang="ts">
  export let message = '';
</script>

{#if message}
  <div id="error" class="error">{message}</div>
{/if}
