import { hasValue } from '../lib/formatters';

export type MetricsGridProps = {
  metrics: Array<[string, string, string]>;
};

export function MetricsGrid({ metrics }: MetricsGridProps) {
  const visibleMetrics = metrics.filter(([, , value]) => hasValue(value));

  if (!visibleMetrics.length) return null;

  return (
    <div className="metricas-grid">
      {visibleMetrics.map(([icon, label, value], index) => (
        <div key={`${label}-${index}`} className="metrica-card">
          <span className="metrica-icono">{icon}</span>
          <span className="metrica-label">{label}</span>
          <strong className="metrica-valor">{value}</strong>
        </div>
      ))}
    </div>
  );
}
