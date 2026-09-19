import { useEffect, useState } from 'react';
import { getHealth } from '../api/client';

export function Header() {
  const [serviceText, setServiceText] = useState('Verificando servicio...');
  const [status, setStatus] = useState<'ok' | 'error'>('ok');
  const [title, setTitle] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 2500);

    getHealth(controller.signal)
      .then((data) => {
        setServiceText(data.modo === 'degradado' ? 'Servicio básico' : 'Gemini activo');
        setStatus((data.estado ?? data.status) === 'ok' ? 'ok' : 'error');
        setTitle(
          data.modo === 'degradado'
            ? 'Gemini no configurado; consultas básicas funcionando.'
            : 'Gemini configurado para respuestas naturales.'
        );
      })
      .catch(() => {
        setServiceText('Servicio no disponible');
        setStatus('error');
      })
      .finally(() => window.clearTimeout(timer));

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, []);

  return (
    <header className="encabezado">
      <div className="header-top">
        <div className="logo-badge">
          <span className="logo-icono">🚌</span>
          <span className="logo-texto">Sistema de rutas urbanas</span>
        </div>
        <div className="status-pill" data-status={status} title={title}>
          <span className="status-dot"></span>
          <span>{serviceText}</span>
        </div>
      </div>

      <div className="hero-identidad">
        <div className="hero-copy">
          <h1>Transita Cajamarca</h1>
          <p className="hero-subtitulo">Asistente inteligente de rutas de transporte público</p>
          <p className="hero-descripcion">
            Consulta rutas, horarios, tarifas y alternativas para moverte mejor por la ciudad.
          </p>
        </div>

        <div className="hero-visual" aria-hidden="true">
          <div className="ruta-diagrama">
            <span className="ruta-nodo nodo-inicio"></span>
            <span className="ruta-linea"></span>
            <span className="ruta-nodo nodo-medio"></span>
            <span className="ruta-linea"></span>
            <span className="ruta-bus">🚌</span>
            <span className="ruta-linea"></span>
            <span className="ruta-nodo nodo-fin"></span>
          </div>
          <div className="panel-datos">
            <span>Datos de ruta</span>
            <strong>horarios · tarifas · recorridos</strong>
          </div>
        </div>
      </div>
    </header>
  );
}
