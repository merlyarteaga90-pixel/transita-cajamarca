import type { ApiRoute } from '../api/types';
import { formatSchedule, routePath, safeText, withUnit } from '../lib/formatters';
import { CompanyInfo } from './CompanyInfo';
import { MetricsGrid } from './MetricsGrid';
import { RouteHeader } from './RouteHeader';
import { TariffGrid } from './TariffGrid';

export type RouteCardProps = {
  route: ApiRoute;
};

export function RouteCard({ route }: RouteCardProps) {
  const metrics: Array<[string, string, string]> = [
    ['⏱️', 'Tiempo total de ruta', withUnit(route.tiempo_total_ruta_min ?? route.tiempo_total_min, 'min')],
    ['📏', 'Distancia total de ruta', withUnit(route.distancia_total_ruta_km ?? route.distancia_km, 'km')],
    ['🔄', 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')],
    ['🕐', 'Horario', formatSchedule(route)],
    ['📍', 'Recorrido', routePath(route)]
  ];
  const points = (route.puntos ?? []).filter((point) => safeText(point.nombre));

  return (
    <article className="ruta-card">
      <RouteHeader route={route} />
      <CompanyInfo route={route} />
      <MetricsGrid metrics={metrics} />
      <TariffGrid route={route} />

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
