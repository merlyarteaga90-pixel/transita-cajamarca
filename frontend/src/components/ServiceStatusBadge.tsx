export type ServiceStatusBadgeProps = {
  estado_servicio?: string;
  mensaje_servicio?: string | null;
};

const STATUS_MAP: Record<string, { label: string; variant: 'success' | 'warning' | 'neutral' | 'error' }> = {
  SERVICIO_ACTIVO:        { label: 'En servicio',          variant: 'success' },
  ANTES_DE_INICIO:        { label: 'Aún no inicia',       variant: 'warning' },
  SERVICIO_FINALIZADO:    { label: 'Servicio finalizado', variant: 'neutral' },
  SIN_MAS_SALIDAS:       { label: 'Sin más salidas',     variant: 'neutral' },
  DATOS_INSUFICIENTES:    { label: 'Horario no disponible', variant: 'neutral' },
};

export function ServiceStatusBadge({ estado_servicio, mensaje_servicio }: ServiceStatusBadgeProps) {
  if (!estado_servicio) return null;
  const entry = STATUS_MAP[estado_servicio];
  const label = entry?.label ?? estado_servicio ?? '';
  const variant = entry?.variant ?? 'neutral';

  return (
    <span className={`service-badge service-badge--${variant}`} title={mensaje_servicio ?? undefined}>
      <span className="service-badge__dot" />
      {label}
    </span>
  );
}
