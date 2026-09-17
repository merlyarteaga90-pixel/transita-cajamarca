<script lang="ts">
  import type { ApiRoute } from '../lib/types';
  import { formatFare } from '../lib/formatters';

  export let route: ApiRoute;

  $: general = formatFare(route.tarifa_general);
  $: half = formatFare(route.tarifa_medio_pasaje);
</script>

{#if general || half}
  <div class="tarifas-grid">
    {#if general}
      <div class="tarifa-card tarifa-general"><span>Pasaje general</span><strong>{general}</strong></div>
    {/if}
    {#if half}
      <div class="tarifa-card tarifa-medio"><span>Medio pasaje</span><strong>{half}</strong></div>
    {/if}
  </div>
{/if}
