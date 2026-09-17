<script lang="ts">
  import type { ApiRoute } from '../lib/types';
  import { formatSchedule, safeText, withUnit } from '../lib/formatters';
  import CompanyInfo from './CompanyInfo.svelte';
  import MetricsGrid from './MetricsGrid.svelte';
  import RouteHeader from './RouteHeader.svelte';
  import TariffGrid from './TariffGrid.svelte';

  export let route: ApiRoute;

  $: metrics = [
    ['🕐', 'Horario', formatSchedule(route)],
    ['🔄', 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')],
    ['🚌', 'Salida teórica', safeText(route.proxima_salida)],
    ['⏳', 'Faltan', withUnit(route.proximo_paso_min, 'min', '~')],
    ['⌚', 'Hora actual', safeText(route.hora_actual)]
  ] as Array<[string, string, string]>;
</script>

<article class="ruta-card info-card">
  <RouteHeader {route} />
  <CompanyInfo {route} />
  <MetricsGrid {metrics} />
  <TariffGrid {route} />
</article>
