<script lang="ts">
  import type { ApiRoute } from '../lib/types';
  import { asRoutes, formatSchedule, routePath, safeText, withUnit } from '../lib/formatters';
  import CompanyInfo from './CompanyInfo.svelte';
  import MetricsGrid from './MetricsGrid.svelte';
  import RouteHeader from './RouteHeader.svelte';
  import TariffGrid from './TariffGrid.svelte';

  export let route: ApiRoute;

  $: metrics = [
    ['⏱️', 'Tiempo total de ruta', withUnit(route.tiempo_total_ruta_min ?? route.tiempo_total_min, 'min')],
    ['📏', 'Distancia total de ruta', withUnit(route.distancia_total_ruta_km ?? route.distancia_km, 'km')],
    ['🔄', 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')],
    ['🕐', 'Horario', formatSchedule(route)],
    ['📍', 'Recorrido', routePath(route)]
  ] as Array<[string, string, string]>;
  $: points = asRoutes(route.puntos).filter((point) => safeText(point.nombre));
</script>

<article class="ruta-card">
  <RouteHeader {route} />
  <CompanyInfo {route} />
  <MetricsGrid {metrics} />
  <TariffGrid {route} />

  {#if points.length}
    <div class="recorrido">
      <span class="seccion-label">Puntos del recorrido</span>
      <ol>
        {#each points as point, index}
          <li class="recorrido-punto" data-posicion={index === 0 ? 'inicio' : index === points.length - 1 ? 'fin' : 'intermedio'}>
            <span class="recorrido-dot"></span>
            <span>{safeText(point.nombre)}</span>
          </li>
        {/each}
      </ol>
    </div>
  {/if}
</article>
