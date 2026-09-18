import { useEffect, useMemo, useState } from 'react';
import { getRoutes } from '../api/client';
import type { ApiRoute } from '../api/types';
import {
  formatSchedule,
  hasValue,
  routeCode,
  routeDirection,
  routePath,
  safeText,
  withUnit
} from '../lib/formatters';

export type RouteModalProps = {
  open: boolean;
  onClose: () => void;
  onSelect: (codigo: string, sentido: string) => void;
};

export function RouteModal({ open, onClose, onSelect }: RouteModalProps) {
  const [routes, setRoutes] = useState<ApiRoute[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (!open || loaded || loading) return;

    const controller = new AbortController();
    setLoading(true);
    setError('');
    getRoutes(controller.signal)
      .then((data) => {
        setRoutes(data);
        setLoaded(true);
      })
      .catch(() => setError('No se pudieron cargar las rutas.'))
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [open, loaded, loading]);

  const filteredRoutes = useMemo(() => {
    const clean = search.trim().toLowerCase();
    if (!clean) return routes;

    return routes.filter((route) =>
      [
        route.codigo_ruta,
        route.nombre,
        route.empresa,
        route.origen,
        route.destino,
        route.sentido
      ].some((value) => safeText(value).toLowerCase().includes(clean))
    );
  }, [routes, search]);

  function close(): void {
    setSearch('');
    onClose();
  }

  function selectRoute(route: ApiRoute): void {
    const codigo = routeCode(route);
    if (!hasValue(codigo)) return;
    close();
    onSelect(codigo, routeDirection(route));
  }

  function handleOverlayClick(event: React.MouseEvent<HTMLDivElement>): void {
    if (event.target === event.currentTarget) close();
  }

  function handleOverlayKeyDown(event: React.KeyboardEvent<HTMLDivElement>): void {
    if (event.key === 'Escape') close();
  }

  function handleRouteKeyDown(event: React.KeyboardEvent<HTMLDivElement>, route: ApiRoute): void {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      selectRoute(route);
    }
  }

  if (!open) return null;

  return (
    <div
      id="modalRutas"
      className="modal-overlay"
      role="presentation"
      tabIndex={-1}
      onClick={handleOverlayClick}
      onKeyDown={handleOverlayKeyDown}
    >
      <div className="modal-contenido">
        <div className="modal-header">
          <h3>🚌 Seleccionar Ruta</h3>
          <button
            id="btnCerrarModalRutas"
            className="modal-cerrar"
            type="button"
            aria-label="Cerrar"
            onClick={close}
          >
            ✕
          </button>
        </div>
        <div className="modal-buscador">
          <input
            type="text"
            id="modalRutasBuscador"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por código, empresa u origen..."
          />
        </div>
        <div id="modalRutasLista" className="modal-lista">
          {loading && <p className="modal-mensaje">Cargando rutas...</p>}
          {!loading && error && <p className="modal-mensaje modal-error">{error}</p>}
          {!loading && !error && filteredRoutes.length === 0 && (
            <p className="modal-mensaje">No se encontraron rutas.</p>
          )}
          {!loading &&
            !error &&
            filteredRoutes.map((route) => {
              const codigo = routeCode(route);
              const sentido = routeDirection(route);
              const nombre = safeText(route.nombre ?? route.empresa);
              const trayecto = routePath(route);
              const horario = formatSchedule(route);
              const frecuencia = withUnit(route.frecuencia_min, 'min', 'Cada ');
              const detalles = [frecuencia, horario].filter(hasValue).join(' · ');

              return (
              <div
                key={`${codigo}-${sentido}`}
                className="ruta-modal-item"
                role="button"
                  tabIndex={0}
                  data-codigo={codigo}
                  data-sentido={sentido}
                  onClick={() => selectRoute(route)}
                  onKeyDown={(event) => handleRouteKeyDown(event, route)}
                >
                  <div className="ruta-modal-icono" aria-hidden="true">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.9"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M6 17h12" />
                      <path d="M7 17v2" />
                      <path d="M17 17v2" />
                      <path d="M5 8c0-2 1.2-3 3.2-3h7.6C17.8 5 19 6 19 8v7c0 1.1-.9 2-2 2H7c-1.1 0-2-.9-2-2V8Z" />
                      <path d="M8 9h8" />
                      <path d="M8 13h.01" />
                      <path d="M16 13h.01" />
                    </svg>
                  </div>
                  <div className="ruta-modal-info">
                    <div className="ruta-modal-top">
                      <span className="ruta-modal-codigo">{codigo}</span>
                      {sentido && (
                        <span className="ruta-modal-sentido" data-sentido={sentido}>
                          {sentido}
                        </span>
                      )}
                    </div>
                    {nombre && <strong className="ruta-modal-nombre">{nombre}</strong>}
                    {trayecto && <span className="ruta-modal-trayecto">{trayecto}</span>}
                    {detalles && <span className="ruta-modal-detalles">{detalles}</span>}
                  </div>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
}
