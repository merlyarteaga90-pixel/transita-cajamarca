import { MapPin, X } from 'lucide-react';
import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import type { GeolocationStatus } from '../hooks/useGeolocation';

export type SearchBoxHandle = {
  focus: () => void;
};

export type SearchBoxProps = {
  value: string;
  loading: boolean;
  onChange: (value: string) => void;
  onSubmit: (value: string) => void;
  onClear: () => void;
  onRequestLocation?: () => void;
  onClearLocation?: () => void;
  locationStatus?: GeolocationStatus;
  locationError?: string | null;
};

const LOCATION_LABELS: Record<GeolocationStatus, { text: string; title: string }> = {
  idle: { text: 'Compartir ubicación', title: 'Usar mi ubicación para recomendar rutas cercanas' },
  requesting: { text: 'Obteniendo ubicación…', title: 'Solicitando permiso de ubicación' },
  active: { text: 'Ubicación compartida', title: 'Dejar de compartir ubicación' },
  denied: { text: 'Permiso denegado · Reintentar', title: 'Intentar nuevamente' },
  unavailable: { text: 'No disponible · Reintentar', title: 'Intentar nuevamente' },
  timeout: { text: 'Tiempo agotado · Reintentar', title: 'Intentar nuevamente' },
};

export const SearchBox = forwardRef<SearchBoxHandle, SearchBoxProps>(function SearchBox(
  { value, loading, onChange, onSubmit, onClear, onRequestLocation, onClearLocation, locationStatus, locationError },
  ref
) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useImperativeHandle(ref, () => ({
    focus: () => textareaRef.current?.focus()
  }));

  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  function submit(): void {
    const clean = value.trim();
    if (clean && !loading) onSubmit(clean);
  }

  function clear(): void {
    onChange('');
    onClear();
    textareaRef.current?.focus();
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  }

  const status = locationStatus || 'idle';
  const label = LOCATION_LABELS[status];
  const isActive = status === 'active';
  const isRequesting = status === 'requesting';

  function handleLocationClick(): void {
    if (isActive && onClearLocation) {
      onClearLocation();
    } else if (onRequestLocation) {
      onRequestLocation();
    }
  }

  return (
    <section className="buscador">
      <label htmlFor="consulta">¿A dónde quieres ir?</label>
      <div className="input-wrapper">
        <textarea
          id="consulta"
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={2}
          placeholder='Ejemplo: "cómo voy a Shudal", "tarifa de la ruta 05", "rutas que pasan por el hospital"'
          onKeyDown={handleKeyDown}
        ></textarea>
        <button
          type="button"
          id="btnLimpiar"
          className="btn-limpiar"
          title="Borrar texto"
          aria-label="Borrar texto"
          onClick={clear}
        >
          <X size={16} strokeWidth={2.5} />
        </button>
      </div>

      {locationError && <p className="location-error">{locationError}</p>}

      <div className="buscador-acciones">
        <span className="tip-enter">
          Presiona <kbd>Enter ↵</kbd> para enviar
        </span>
        <div className="searchbox-actions">
          {(onRequestLocation || onClearLocation) && (
            <button
              type="button"
              className={`location-button ${isActive ? 'location-active' : ''}`}
              title={label.title}
              onClick={handleLocationClick}
              disabled={isRequesting}
              aria-pressed={isActive}
            >
              <MapPin size={14} strokeWidth={2.5} aria-hidden="true" />
              <span>{label.text}</span>
            </button>
          )}
          <button id="btnBuscar" type="button" disabled={loading} onClick={submit}>
            <span>Preguntar</span>
            <svg
              className="icono-enviar"
              viewBox="0 0 24 24"
              width="16"
              height="16"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
            >
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>
      {isActive && (
        <p className="location-privacy">
          Se usa para recomendar rutas cercanas. No se guarda.
        </p>
      )}
    </section>
  );
});
