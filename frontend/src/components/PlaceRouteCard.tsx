import type { ApiRoute } from '../api/types';
import { formatSchedule, routePath, safeText, withUnit } from '../lib/formatters';
import { CompanyInfo } from './CompanyInfo';
import { MetricsGrid } from './MetricsGrid';
import { RouteHeader } from './RouteHeader';

export type PlaceRouteCardProps = {
  route: ApiRoute;
};

export function PlaceRouteCard({ route }: PlaceRouteCardProps) {
  const metrics: Array<[string, string, string]> = [
    ['📍', 'Pasa por', safeText(route.punto)],
    ['🧭', 'Recorrido', routePath(route)],
    ['🕐', 'Horario', formatSchedule(route)],
    ['🔄', 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')]
  ];

  return (
    <article className="ruta-card ruta-lugar-card">
      <RouteHeader route={route} showNext={false} />
      <CompanyInfo route={route} />
      <MetricsGrid metrics={metrics} />
    </article>
  );
}
