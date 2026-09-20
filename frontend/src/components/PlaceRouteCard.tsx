import { Compass, MapPin } from 'lucide-react';
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
  const metrics: Array<[React.ReactNode, string, string]> = [
    [<MapPin size={16} strokeWidth={2} aria-hidden="true" />, 'Pasa por', safeText(route.punto)],
    [<Compass size={16} strokeWidth={2} aria-hidden="true" />, 'Recorrido', routePath(route)]
  ];

  return (
    <article className="ruta-card ruta-lugar-card">
      <RouteHeader
        route={route}
        showNext={false}
        meta={<RouteMetaBadges route={route} asHeaderContent />}
      />
      <CompanyInfo route={route} />
      <MetricsGrid metrics={metrics} />
    </article>
  );
}
