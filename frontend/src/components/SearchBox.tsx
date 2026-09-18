import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';

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
  locationError?: string | null;
};

export const SearchBox = forwardRef<SearchBoxHandle, SearchBoxProps>(function SearchBox(
  { value, loading, onChange, onSubmit, onClear, onRequestLocation, locationError },
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
          onClick={clear}
        >
          ✕
        </button>
      </div>

      {locationError && <p className="location-error">{locationError}</p>}

      <div className="buscador-acciones">
        <span className="tip-enter">
          Presiona <kbd>Enter ↵</kbd> para enviar
        </span>
        <div className="searchbox-actions">
          {onRequestLocation && (
            <button
              type="button"
              className="location-button"
              title="Compartir ubicación"
              onClick={onRequestLocation}
            >
              <span>📍 Compartir ubicación</span>
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
    </section>
  );
});
