import type { ApiRoute } from '../api/types';
import { routeCode, routeDirection, withUnit } from '../lib/formatters';

export type RouteHeaderProps = {
  route: ApiRoute;
  showNext?: boolean;
};

export function RouteHeader({ route, showNext = true }: RouteHeaderProps) {
  const code = routeCode(route);
  const direction = routeDirection(route);
  const next = showNext
    ? withUnit(route.proximo_paso_min ?? route.proxima_unidad?.minutos_restantes, 'min', '~')
    : '';
  const directionIcon = direction === 'IDA' ? '→ ' : direction === 'VUELTA' ? '← ' : '';

  return (
    <div className="ruta-card-header">
      <div className="ruta-identidad">
        <span className="badge-ruta">{code}</span>
        {direction && (
          <span className="badge-sentido" data-sentido={direction}>
            {directionIcon}
            {direction}
          </span>
        )}
      </div>
      {next && (
        <div className="proxima-unidad">
          <span>Salida desde inicio</span>
          <strong>{next}</strong>
        </div>
      )}
    </div>
  );
}
