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
          className="quick-action-card destacado qa-next"
          onClick={onOpenRoutes}
        >
          <span className="quick-icon">🕒</span>
          <strong>Próxima combi</strong>
          <small>Busca una ruta y revisa su salida teórica.</small>
        </button>

        <button
          type="button"
          className="quick-action-card qa-fare"
          aria-pressed={activeHelp === 'fare'}
          onClick={() => toggleHelp('fare', 'tarifa de la ruta 05')}
        >
          <span className="quick-icon">🎫</span>
          <strong>Tarifa por ruta</strong>
          <small>Pregunta por el pasaje usando el código.</small>
        </button>

        <button
          type="button"
          className="quick-action-card qa-place"
          aria-pressed={activeHelp === 'place'}
          onClick={() => toggleHelp('place', 'rutas que pasan por Shudal')}
        >
          <span className="quick-icon">📍</span>
          <strong>Rutas por lugar</strong>
          <small>Encuentra rutas que pasan por una zona.</small>
        </button>

        <button
          type="button"
          className="quick-action-card qa-how"
          aria-pressed={activeHelp === 'how'}
          onClick={() => toggleHelp('how', 'cómo voy a Shudal')}
        >
          <span className="quick-icon">⌁</span>
          <strong>Cómo consultar</strong>
          <small>Ejemplos para obtener mejores respuestas.</small>
        </button>
      </div>

      {activeHelp && (
        <div className="quick-help">
          {activeHelp === 'fare' && (
            <>
              <strong>Consulta tarifas con el número de ruta.</strong>
              <p>Ejemplos: "tarifa de la ruta 05", "cuánto cuesta la ruta 04".</p>
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
              <strong>Escribe como hablarías normalmente.</strong>
              <p>Ejemplos: "cómo voy a Shudal", "de Shudal al hospital", "cuál es la ruta 05".</p>
            </>
          )}
        </div>
      )}
    </section>
  );
}
