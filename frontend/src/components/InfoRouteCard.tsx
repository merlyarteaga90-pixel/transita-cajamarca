import type { ApiRoute } from '../api/types';
import { formatFare, formatSchedule, safeText, withUnit } from '../lib/formatters';
import { CompanyInfo } from './CompanyInfo';
import { MetricsGrid } from './MetricsGrid';
import { RouteHeader } from './RouteHeader';
import { TariffGrid } from './TariffGrid';

export type InfoRouteCardProps = {
  route: ApiRoute;
};

export function InfoRouteCard({ route }: InfoRouteCardProps) {
  const tipo = (route as ApiRoute & { consulta_tipo?: string }).consulta_tipo;

  let metrics: Array<[string, string, string]> = [];

  if (tipo === 'TARIFA') {
    metrics = [
      ['🪙', 'Pasaje general', formatFare(route.tarifa_general ?? route.tarifa)],
      ['🎓', 'Medio pasaje', formatFare(route.tarifa_medio_pasaje)],
    ];
    if (route.frecuencia_min) {
      metrics.push(['🔄', 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')]);
    }
  } else if (tipo === 'HORARIO') {
    metrics = [
      ['🕐', 'Horario', formatSchedule(route)],
    ];
    if (route.frecuencia_min) {
      metrics.push(['🔄', 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')]);
    }
  } else if (tipo === 'FRECUENCIA') {
    metrics = [
      ['🔄', 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')],
    ];
    if (route.horario_inicio || route.horario_fin) {
      metrics.push(['🕐', 'Horario', formatSchedule(route)]);
    }
  } else if (tipo === 'PROXIMA_UNIDAD') {
    metrics = [
      ['🚌', 'Próxima salida', safeText(route.proxima_salida)],
      ['⏳', 'Faltan', withUnit(route.proximo_paso_min, 'min', '~')],
      ['ℹ️', 'Estado', safeText(route.estado_servicio ?? route.mensaje_servicio)],
      ['⌚', 'Hora actual', safeText(route.hora_actual)],
    ];
    if (route.frecuencia_min) {
      metrics.push(['🔄', 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')]);
    }
  } else {
    metrics = [
      ['🕐', 'Horario', formatSchedule(route)],
      ['🔄', 'Frecuencia', withUnit(route.frecuencia_min, 'min', 'Cada ')],
      ['🚌', 'Salida teórica', safeText(route.proxima_salida)],
      ['⏳', 'Faltan', withUnit(route.proximo_paso_min, 'min', '~')],
      ['⌚', 'Hora actual', safeText(route.hora_actual)],
      ['ℹ️', 'Estado', safeText(route.estado_servicio ?? route.mensaje_servicio)],
    ];
  }

  return (
    <article className="ruta-card info-card">
      <RouteHeader route={route} />
      <CompanyInfo route={route} />
      <MetricsGrid metrics={metrics} />
      {tipo !== 'TARIFA' && <TariffGrid route={route} />}
    </article>
  );
}
