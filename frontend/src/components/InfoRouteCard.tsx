import { BusFront, Clock, Hourglass, RefreshCw, Watch } from 'lucide-react';
import type { ApiRoute } from '../api/types';
import { formatSchedule, safeText, withUnit } from '../lib/formatters';
import { CompanyInfo } from './CompanyInfo';
import { MetricsGrid } from './MetricsGrid';
import { RouteHeader } from './RouteHeader';
import { ServiceStatusBadge } from './ServiceStatusBadge';
import { TariffGrid } from './TariffGrid';

export type InfoRouteCardProps = {
  route: ApiRoute;
};

export function InfoRouteCard({ route }: InfoRouteCardProps) {
  const tipo = (route as ApiRoute & { consulta_tipo?: string }).consulta_tipo;

  let metrics: Array<[React.ReactNode, string, string]> = [];

  if (tipo === 'TARIFA') {
    return (
      <article className="ruta-card info-card">
        <RouteHeader route={route} />
        <CompanyInfo route={route} />
        <TariffGrid route={route} />
      </article>
    );
  }

  if (tipo === 'HORARIO') {
    metrics = [];
    if (route.horario_inicio || route.horario_fin) {
      metrics.push([<Clock size={16} strokeWidth={2} aria-hidden="true" />, 'Horario', formatSchedule(route)]);
    }
    if (route.frecuencia_min) {
      metrics.push([<RefreshCw size={16} strokeWidth={2} aria-hidden="true" />, 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')]);
    }
  } else if (tipo === 'FRECUENCIA') {
    metrics = [];
    if (route.frecuencia_min) {
      metrics.push([<RefreshCw size={16} strokeWidth={2} aria-hidden="true" />, 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')]);
    }
    if (route.horario_inicio || route.horario_fin) {
      metrics.push([<Clock size={16} strokeWidth={2} aria-hidden="true" />, 'Horario', formatSchedule(route)]);
    }
  } else if (tipo === 'PROXIMA_UNIDAD') {
    metrics = [
      [<BusFront size={16} strokeWidth={2} aria-hidden="true" />, 'Próxima salida', safeText(route.proxima_salida)],
      [<Hourglass size={16} strokeWidth={2} aria-hidden="true" />, 'Faltan', withUnit(route.proximo_paso_min, 'min', '~')],
    ];
    if (route.frecuencia_min) {
      metrics.push([<RefreshCw size={16} strokeWidth={2} aria-hidden="true" />, 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')]);
    }
  } else {
    metrics = [
      [<Clock size={16} strokeWidth={2} aria-hidden="true" />, 'Horario', formatSchedule(route)],
      [<RefreshCw size={16} strokeWidth={2} aria-hidden="true" />, 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')],
      [<BusFront size={16} strokeWidth={2} aria-hidden="true" />, 'Salida teórica', safeText(route.proxima_salida)],
      [<Hourglass size={16} strokeWidth={2} aria-hidden="true" />, 'Faltan', withUnit(route.proximo_paso_min, 'min', '~')],
      [<Watch size={16} strokeWidth={2} aria-hidden="true" />, 'Hora actual', safeText(route.hora_actual)],
    ];
  }

  return (
    <article className="ruta-card info-card">
      <RouteHeader route={route} />
      <CompanyInfo route={route} />
      <MetricsGrid metrics={metrics} />
      <TariffGrid route={route} />
      {route.estado_servicio && (
        <div className="ruta-meta-row">
          <ServiceStatusBadge
            estado_servicio={route.estado_servicio}
            mensaje_servicio={route.mensaje_servicio}
          />
        </div>
      )}
    </article>
  );
}
