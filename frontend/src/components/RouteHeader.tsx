import type { ReactNode } from 'react';
import { MoveRight, MoveLeft } from 'lucide-react';
import type { ApiRoute } from '../api/types';
import { routeCode, routeDirection, withUnit } from '../lib/formatters';

export type RouteHeaderProps = {
  route: ApiRoute;
  showNext?: boolean;
  meta?: ReactNode;
};

export function RouteHeader({ route, showNext = true, meta }: RouteHeaderProps) {
  const code = routeCode(route);
  const direction = routeDirection(route);
  const next = showNext
    ? withUnit(route.proximo_paso_min ?? route.proxima_unidad?.minutos_restantes, 'min', '~')
    : '';
  const DirectionIcon = direction === 'IDA' ? MoveRight : direction === 'VUELTA' ? MoveLeft : null;

  return (
    <div className="ruta-card-header">
      <div className="ruta-identidad">
        <span className="badge-ruta">{code}</span>
        {direction && (
          <span className="badge-sentido" data-sentido={direction}>
            {DirectionIcon && <DirectionIcon size={12} strokeWidth={2.5} aria-hidden="true" />}
            {direction}
          </span>
        )}
      </div>
      {(meta || (next && showNext)) && (
        <div className="ruta-header-aside">
          {meta}
          {next && showNext && (
            <div className="proxima-unidad">
              <span>Salida desde inicio</span>
              <strong>{next}</strong>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
