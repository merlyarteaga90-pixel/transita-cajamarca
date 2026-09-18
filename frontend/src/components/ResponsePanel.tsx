import type { ApiResponse, ApiRoute } from '../api/types';
import { isSelectorCandidate } from '../api/client';
import { asRoutes, candidateText, safeText } from '../lib/formatters';
import { InfoRouteCard } from './InfoRouteCard';
import { PlaceRouteCard } from './PlaceRouteCard';
import { RouteCard } from './RouteCard';
import { SelectorRouteCard } from './SelectorRouteCard';

export type ResponsePanelProps = {
  data: ApiResponse;
  speaking: boolean;
  copied: boolean;
  onSpeak: () => void;
  onCopy: () => void;
};

function candidateList(candidatos: unknown[]): string[] {
  return candidatos
    .map((candidate) => {
      if (typeof candidate === 'string') return candidate;
      if (isSelectorCandidate(candidate)) return candidate.mostrar;
      return candidateText(candidate);
    })
    .filter(Boolean);
}

export function ResponsePanel({ data, speaking, copied, onSpeak, onCopy }: ResponsePanelProps) {
  const results = asRoutes(data.resultados);
  const selectorRoutes = asRoutes(data.rutas);
  const candidates = Array.isArray(data.candidatos) ? candidateList(data.candidatos) : [];

  return (
    <section id="resultado" className="resultado">
      <div className="resultado-header">
        <div className="resultado-titulo">
          <span id="iconoEstado" className="icono-estado">
            {safeText(data.icono, '🚌')}
          </span>
          <h3 id="estadoTexto">{safeText(data.estado, 'Respuesta del Asistente')}</h3>
        </div>
        <div className="resultado-herramientas">
          <button
            id="btnVoz"
            className="btn-tool"
            type="button"
            title="Escuchar respuesta"
            onClick={onSpeak}
          >
            {speaking ? '⏹️ Detener' : '🔊 Escuchar'}
          </button>
          <button
            id="btnCopiar"
            className="btn-tool"
            type="button"
            title="Copiar texto"
            onClick={onCopy}
          >
            {copied ? '✓ ¡Copiado!' : '📋 Copiar'}
          </button>
        </div>
      </div>

      <div id="respuesta" className="respuesta-cuerpo">
        <div className="respuesta-resumen">
          <span className="respuesta-resumen-icono">🚌</span>
          <p>{safeText(data.respuesta, 'No se encontraron rutas.')}</p>
        </div>

        {data.tipo === 'ruta' && (
          <div className="resultados-lista">
            {results.map((route, index) => (
              <RouteCard key={routeKey(route, index)} route={route} />
            ))}
          </div>
        )}

        {(data.tipo === 'alternativas' || data.tipo === 'rutas_por_lugar') && (
          <div className="resultados-lista">
            {results.map((route, index) => (
              <PlaceRouteCard key={routeKey(route, index)} route={route} />
            ))}
          </div>
        )}

        {(data.tipo === 'info' || data.tipo === 'proximas_unidades') && (
          <div className="resultados-lista">
            {results.map((route, index) => (
              <InfoRouteCard key={routeKey(route, index)} route={route} />
            ))}
          </div>
        )}

        {(data.tipo === 'selector' || data.tipo === 'selector_ruta') &&
          (selectorRoutes.length ? (
            <div className="resultados-lista selector-rutas">
              {selectorRoutes.map((route, index) => (
                <SelectorRouteCard key={routeKey(route, index)} route={route} />
              ))}
            </div>
          ) : candidates.length ? (
            <ul className="aclaracion-lista">
              {candidates.map((candidate, index) => (
                <li key={index}>{candidate}</li>
              ))}
            </ul>
          ) : null)}

        {data.tipo === 'aclaracion' && candidates.length > 0 && (
          <ul className="aclaracion-lista">
            {candidates.map((candidate, index) => (
              <li key={index}>{candidate}</li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}

function routeKey(route: ApiRoute, index: number): string {
  return `${route.codigo_ruta ?? route.codigo ?? 'ruta'}-${route.sentido ?? route.tipo ?? 'sentido'}-${index}`;
}
