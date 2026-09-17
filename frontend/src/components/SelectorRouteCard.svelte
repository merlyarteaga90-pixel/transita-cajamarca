<script lang="ts">
  import type { ApiRoute } from '../lib/types';
  import { formatSchedule, routePath, withUnit } from '../lib/formatters';
  import CompanyInfo from './CompanyInfo.svelte';
  import MetricsGrid from './MetricsGrid.svelte';
  import RouteHeader from './RouteHeader.svelte';

  export let route: ApiRoute;

  $: metrics = [
    ['📍', 'Recorrido', routePath(route)],
    ['🕐', 'Horario', formatSchedule(route)],
    ['🔄', 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')]
  ] as Array<[string, string, string]>;
</script>

<article class="ruta-card selector-ruta-card">
  <RouteHeader {route} showNext={false} />
  <CompanyInfo {route} />
  <MetricsGrid {metrics} />
</article>
