import { MapPin, RefreshCw, Route, Timer } from 'lucide-react';
import type { ApiRoute } from '../api/types';
import { routePath, safeText, withUnit } from '../lib/formatters';
import { CompanyInfo } from './CompanyInfo';
import { MetricsGrid } from './MetricsGrid';
import { RouteHeader } from './RouteHeader';
import { RouteMetaBadges } from './RouteMetaBadges';
import { ServiceStatusBadge } from './ServiceStatusBadge';

export type RouteCardProps = {
  route: ApiRoute;
};

export function RouteCard({ route }: RouteCardProps) {
  const metrics: Array<[React.ReactNode, string, string]> = [
    [<Timer size={16} strokeWidth={2} aria-hidden="true" />, 'Tiempo total de ruta', withUnit(route.tiempo_total_ruta_min ?? route.tiempo_total_min, 'min')],
    [<Route size={16} strokeWidth={2} aria-hidden="true" />, 'Distancia total de ruta', withUnit(route.distancia_total_ruta_km ?? route.distancia_km, 'km')],
    [<RefreshCw size={16} strokeWidth={2} aria-hidden="true" />, 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')],
    [<MapPin size={16} strokeWidth={2} aria-hidden="true" />, 'Recorrido', routePath(route)]
  ];
  const points = (route.puntos ?? []).filter((point) => safeText(point.nombre));

  return (
    <article className="ruta-card">
      <RouteHeader
        route={route}
        meta={<RouteMetaBadges route={route} asHeaderContent />}
      />
      <CompanyInfo route={route} />
      <MetricsGrid metrics={metrics} />
      {route.estado_servicio && (
        <div className="ruta-meta-row">
          <ServiceStatusBadge
            estado_servicio={route.estado_servicio}
            mensaje_servicio={route.mensaje_servicio}
          />
        </div>
      )}

      {points.length > 0 && (
        <div className="recorrido">
          <span className="seccion-label">Puntos del recorrido</span>
          <ol>
            {points.map((point, index) => (
              <li
                key={`${point.orden}-${index}`}
                className="recorrido-punto"
                data-posicion={
                  index === 0 ? 'inicio' : index === points.length - 1 ? 'fin' : 'intermedio'
                }
              >
                <span className="recorrido-dot"></span>
                <span>{safeText(point.nombre)}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </article>
  );
}
