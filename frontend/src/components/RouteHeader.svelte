<script lang="ts">
  import type { ApiRoute } from '../lib/types';
  import { routeCode, routeDirection, withUnit } from '../lib/formatters';

  export let route: ApiRoute;
  export let showNext = true;

  $: code = routeCode(route);
  $: direction = routeDirection(route);
  $: next = showNext ? withUnit(route.proximo_paso_min, 'min', '~') : '';
  $: directionIcon = direction === 'IDA' ? '→ ' : direction === 'VUELTA' ? '← ' : '';
</script>

<div class="ruta-card-header">
  <div class="ruta-identidad">
    <span class="badge-ruta">{code}</span>
    {#if direction}
      <span class="badge-sentido" data-sentido={direction}>{directionIcon}{direction}</span>
    {/if}
  </div>
  {#if next}
    <div class="proxima-unidad">
      <span>Salida desde inicio</span>
      <strong>{next}</strong>
    </div>
  {/if}
</div>
