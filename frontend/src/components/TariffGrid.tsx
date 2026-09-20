import type { ApiRoute } from '../api/types';
import { formatFare } from '../lib/formatters';

export type TariffGridProps = {
  route: ApiRoute;
};

export function TariffGrid({ route }: TariffGridProps) {
  const general = formatFare(route.tarifa_general ?? route.tarifa);
  const half = formatFare(route.tarifa_medio_pasaje);

  if (!general && !half) return null;

  return (
    <div className="tarifas-grid">
      {general && (
        <div className="tarifa-card tarifa-general">
          <span>Pasaje general</span>
          <strong>{general}</strong>
        </div>
      )}
      {half && (
        <div className="tarifa-card tarifa-medio">
          <span>Medio pasaje</span>
          <strong>{half}</strong>
        </div>
      )}
    </div>
  );
}
