import type { ApiRoute } from '../api/types';
import { formatSchedule, routePath, withUnit } from '../lib/formatters';
import { CompanyInfo } from './CompanyInfo';
import { MetricsGrid } from './MetricsGrid';
import { RouteHeader } from './RouteHeader';

export type SelectorRouteCardProps = {
  route: ApiRoute;
};

export function SelectorRouteCard({ route }: SelectorRouteCardProps) {
  const metrics: Array<[string, string, string]> = [
    ['📍', 'Recorrido', routePath(route)],
    ['🕐', 'Horario', formatSchedule(route)],
    ['🔄', 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')]
  ];

  return (
    <article className="ruta-card selector-ruta-card">
      <RouteHeader route={route} showNext={false} />
      <CompanyInfo route={route} />
      <MetricsGrid metrics={metrics} />
    </article>
  );
}
