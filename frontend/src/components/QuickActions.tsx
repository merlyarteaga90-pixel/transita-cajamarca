import { Clock, MapPin, Route, Ticket } from 'lucide-react';
import { useState } from 'react';

export type QuickActionsProps = {
  onOpenRoutes: () => void;
  onExample: (example: string) => void;
};

type HelpKey = 'fare' | 'place' | 'how' | null;

export function QuickActions({ onOpenRoutes, onExample }: QuickActionsProps) {
  const [activeHelp, setActiveHelp] = useState<HelpKey>(null);

  function toggleHelp(key: Exclude<HelpKey, null>, example?: string): void {
    setActiveHelp((prev) => (prev === key ? null : key));
    if (example) onExample(example);
  }

  return (
    <section className="quick-actions" aria-label="Acciones rápidas">
      <div className="quick-actions-header">
        <span>Accesos rápidos</span>
      </div>

      <div className="quick-actions-grid">
        <button
          type="button"
          className="quick-action-card qa-how"
          aria-pressed={activeHelp === 'how'}
          onClick={() => toggleHelp('how', 'de Av. Perú a Jr. 11 de Febrero')}
        >
          <span className="quick-icon" aria-hidden="true"><Route size={20} strokeWidth={2} /></span>
          <strong>Cómo llegar</strong>
          <small>Consulta qué combi tomar entre dos lugares.</small>
        </button>

        <button
          type="button"
          className="quick-action-card destacado qa-next"
          onClick={onOpenRoutes}
        >
          <span className="quick-icon" aria-hidden="true"><Clock size={20} strokeWidth={2} /></span>
          <strong>Próxima combi</strong>
          <small>Busca una ruta y revisa su salida teórica.</small>
        </button>

        <button
          type="button"
          className="quick-action-card qa-place"
          aria-pressed={activeHelp === 'place'}
          onClick={() => toggleHelp('place', 'rutas que pasan por Shudal')}
        >
          <span className="quick-icon" aria-hidden="true"><MapPin size={20} strokeWidth={2} /></span>
          <strong>Rutas por lugar</strong>
          <small>Encuentra rutas que pasan por una zona.</small>
        </button>

        <button
          type="button"
          className="quick-action-card qa-fare"
          aria-pressed={activeHelp === 'fare'}
          onClick={() => toggleHelp('fare', 'tarifa y horario de la ruta 05')}
        >
          <span className="quick-icon" aria-hidden="true"><Ticket size={20} strokeWidth={2} /></span>
          <strong>Tarifa y horario</strong>
          <small>Pregunta por el pasaje y horarios de una ruta.</small>
        </button>
      </div>

      {activeHelp && (
        <div className="quick-help">
          {activeHelp === 'fare' && (
            <>
              <strong>Consulta tarifa y horario con el código de ruta.</strong>
              <p>Ejemplos: "tarifa y horario de la ruta 05", "cuánto cuesta la ruta 04 y a qué hora sale".</p>
            </>
          )}
          {activeHelp === 'place' && (
            <>
              <strong>Busca rutas por referencia o zona.</strong>
              <p>Ejemplos: "rutas que pasan por Shudal", "qué rutas pasan por el hospital".</p>
            </>
          )}
          {activeHelp === 'how' && (
            <>
              <strong>Escribe el origen y destino.</strong>
              <p>Ejemplos: "de Av. Perú a Jr. 11 de Febrero", "de Yanacocha al Penal de Huacariz".</p>
            </>
          )}
        </div>
      )}
    </section>
  );
}
