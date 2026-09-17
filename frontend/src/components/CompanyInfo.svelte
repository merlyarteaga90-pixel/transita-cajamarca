<script lang="ts">
  import type { ApiRoute } from '../lib/types';
  import { safeText } from '../lib/formatters';

  export let route: ApiRoute;

  $: name = safeText(route.nombre_comercial);
  $: businessName = safeText(route.razon_social);
  $: ruc = safeText(route.ruc);
</script>

{#if name || businessName || ruc}
  <div class="empresa-info">
    <span class="empresa-icono">🚌</span>
    <div>
      {#if name}<strong>{name}</strong>{/if}
      {#if businessName && businessName !== name}<span>{businessName}</span>{/if}
      {#if ruc}<small>RUC {ruc}</small>{/if}
    </div>
  </div>
{/if}
