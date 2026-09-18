import type { ApiRoute } from '../api/types';
import { safeText } from '../lib/formatters';

export type CompanyInfoProps = {
  route: ApiRoute;
};

export function CompanyInfo({ route }: CompanyInfoProps) {
  const name = safeText(route.nombre_comercial ?? route.nombre ?? route.ruta_nombre);
  const businessName = safeText(route.razon_social);
  const ruc = safeText(route.ruc);

  if (!name && !businessName && !ruc) return null;

  return (
    <div className="empresa-info">
      <span className="empresa-icono">🚌</span>
      <div>
        {name && <strong>{name}</strong>}
        {businessName && businessName !== name && <span>{businessName}</span>}
        {ruc && <small>RUC {ruc}</small>}
      </div>
    </div>
  );
}
