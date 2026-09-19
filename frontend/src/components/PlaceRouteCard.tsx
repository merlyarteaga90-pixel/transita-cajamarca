import type { ApiRoute } from '../api/types';
import { routePath, safeText } from '../lib/formatters';
import { CompanyInfo } from './CompanyInfo';
import { MetricsGrid } from './MetricsGrid';
import { RouteHeader } from './RouteHeader';
import { RouteMetaBadges } from './RouteMetaBadges';

export type PlaceRouteCardProps = {
  route: ApiRoute;
};

export function PlaceRouteCard({ route }: PlaceRouteCardProps) {
  const metrics: Array<[string, string, string]> = [
    ['📍', 'Pasa por', safeText(route.punto)],
    ['🧭', 'Recorrido', routePath(route)]
  ];

  return (
    <article className="ruta-card ruta-lugar-card">
      <RouteHeader route={route} showNext={false} />
      <CompanyInfo route={route} />
      <MetricsGrid metrics={metrics} />
      <RouteMetaBadges route={route} />
    </article>
  );
}
