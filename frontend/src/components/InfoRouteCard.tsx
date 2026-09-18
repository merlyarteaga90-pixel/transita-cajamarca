import type { ApiRoute } from '../api/types';
import { formatSchedule, safeText, withUnit } from '../lib/formatters';
import { CompanyInfo } from './CompanyInfo';
import { MetricsGrid } from './MetricsGrid';
import { RouteHeader } from './RouteHeader';
import { TariffGrid } from './TariffGrid';

export type InfoRouteCardProps = {
  route: ApiRoute;
};

export function InfoRouteCard({ route }: InfoRouteCardProps) {
  const metrics: Array<[string, string, string]> = [
    ['🕐', 'Horario', formatSchedule(route)],
    ['🔄', 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')],
    ['🚌', 'Salida teórica', safeText(route.proxima_salida)],
    ['⏳', 'Faltan', withUnit(route.proximo_paso_min, 'min', '~')],
    ['⌚', 'Hora actual', safeText(route.hora_actual)],
    ['ℹ️', 'Estado', safeText(route.estado_servicio ?? route.mensaje_servicio)]
  ];

  return (
    <article className="ruta-card info-card">
      <RouteHeader route={route} />
      <CompanyInfo route={route} />
      <MetricsGrid metrics={metrics} />
      <TariffGrid route={route} />
    </article>
  );
}
