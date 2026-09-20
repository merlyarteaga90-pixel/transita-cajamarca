import { BusFront, Check, ClipboardCopy, MapPin, Square, Volume2 } from 'lucide-react';
import type { ApiResponse, ApiRoute, SelectorCandidate } from '../api/types';
import { asRoutes, safeText } from '../lib/formatters';
import { InfoRouteCard } from './InfoRouteCard';
import { PlaceRouteCard } from './PlaceRouteCard';
import { RouteCard } from './RouteCard';
import { SelectorRouteCard } from './SelectorRouteCard';
import Markdown from 'react-markdown';

export type ResponsePanelProps = {
  data: ApiResponse;
  speaking: boolean;
  copied: boolean;
  onSpeak: () => void;
  onCopy: () => void;
  onCandidateSelect?: (candidate: string) => void;
};

type CandidateEntry = { label: string; value: string };

function candidateList(candidatos: unknown[]): CandidateEntry[] {
  return candidatos
    .map((candidate): CandidateEntry | null => {
      if (typeof candidate === 'string') return { label: candidate, value: candidate };
      const c = candidate as SelectorCandidate;
      if (typeof c.mostrar === 'string' && typeof c.ruta === 'string') {
        return { label: c.mostrar, value: c.ruta };
      }
      return null;
    })
    .filter((c): c is CandidateEntry => Boolean(c));
}

export function ResponsePanel({
  data,
  speaking,
  copied,
  onSpeak,
  onCopy,
  onCandidateSelect
}: ResponsePanelProps) {
  const results = asRoutes(data.resultados);
  const selectorRoutes = asRoutes(data.rutas);
  const candidates = Array.isArray(data.candidatos) ? candidateList(data.candidatos) : [];

  return (
    <section id="resultado" className="resultado">
      <div className="resultado-header">
        <div className="resultado-titulo">
          <span id="iconoEstado" className="icono-estado" aria-hidden="true">
            <BusFront size={18} strokeWidth={2} />
          </span>
          <h3 id="estadoTexto">{safeText(data.estado, 'Respuesta del Asistente')}</h3>
        </div>
        <div className="resultado-herramientas">
          <button
            id="btnVoz"
            className="btn-tool"
            type="button"
            title={speaking ? 'Detener' : 'Escuchar respuesta'}
            aria-label={speaking ? 'Detener voz' : 'Escuchar respuesta'}
            onClick={onSpeak}
          >
            {speaking ? <Square size={14} fill="currentColor" strokeWidth={0} /> : <Volume2 size={14} strokeWidth={2} />}
            <span>{speaking ? 'Detener' : 'Escuchar'}</span>
          </button>
          <button
            id="btnCopiar"
            className="btn-tool"
            type="button"
            title="Copiar texto"
            aria-label="Copiar texto"
            onClick={onCopy}
          >
            {copied ? <Check size={14} strokeWidth={2.5} /> : <ClipboardCopy size={14} strokeWidth={2} />}
            <span>{copied ? '¡Copiado!' : 'Copiar'}</span>
          </button>
        </div>
      </div>

      <div id="respuesta" className="respuesta-cuerpo">
        <div className="respuesta-resumen">
          <Markdown
            skipHtml
            allowedElements={['p', 'strong', 'em', 'ul', 'ol', 'li', 'br']}
            unwrapDisallowed
          >
            {safeText(data.respuesta, 'No se encontraron rutas.')}
          </Markdown>
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
            <CandidateList candidates={candidates} onSelect={onCandidateSelect} />
          ) : null)}

        {data.tipo === 'aclaracion' && candidates.length > 0 && (
          <CandidateList candidates={candidates} onSelect={onCandidateSelect} />
        )}
      </div>
    </section>
  );
}

function CandidateList({
  candidates,
  onSelect
}: {
  candidates: CandidateEntry[];
  onSelect?: (candidate: string) => void;
}) {
  const layout = candidates.length === 1 ? 'one' : candidates.length === 2 ? 'two' : 'many';

  if (!onSelect) {
    return (
      <ul className="aclaracion-lista">
        {candidates.map((candidate, index) => (
          <li key={index}>{candidate.label}</li>
        ))}
      </ul>
    );
  }

  return (
    <div className="candidatos-bloque">
      <span className="seccion-label">Elige una opción</span>
      <div className="candidatos-grid" data-layout={layout}>
        {candidates.map((candidate, index) => (
          <button
            key={index}
            type="button"
            className="candidato-card"
            onClick={() => onSelect(candidate.value)}
          >
            <span className="candidato-icono" aria-hidden="true"><MapPin size={16} strokeWidth={2} /></span>
            <span className="candidato-texto">{candidate.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function routeKey(route: ApiRoute, index: number): string {
  return `${route.codigo_ruta ?? route.codigo ?? 'ruta'}-${route.sentido ?? route.tipo ?? 'sentido'}-${index}`;
}
