<script lang="ts">
  import { onMount } from 'svelte';
  import { getHealth } from '../api/routes';

  let serviceText = 'Verificando servicio...';
  let status: 'ok' | 'error' = 'ok';
  let title = '';

  onMount(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 2500);

    getHealth(controller.signal)
      .then((data) => {
        serviceText = data.modo === 'degradado' ? 'Servicio disponible' : 'Conectado ';
        status = data.status === 'ok' ? 'ok' : 'error';
        title = data.modo === 'degradado'
          ? 'Las consultas principales funcionan; Ollama no está disponible.'
          : 'MySQL y Ollama disponibles.';
      })
      .catch(() => {
        serviceText = 'Servicio no disponible';
        status = 'error';
      })
      .finally(() => window.clearTimeout(timer));

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  });
</script>

<header class="encabezado">
  <div class="header-top">
    <div class="logo-badge">
      <span class="logo-icono">🚌</span>
      <span class="logo-texto">Sistema de rutas urbanas</span>
    </div>
    <div class="status-pill" data-status={status} {title}>
      <span class="status-dot"></span>
      <span>{serviceText}</span>
    </div>
  </div>

  <div class="hero-identidad">
    <div class="hero-copy">
      <h1>Transita Cajamarca</h1>
      <p class="hero-subtitulo">Asistente inteligente de rutas de transporte público</p>
      <p class="hero-descripcion">Consulta rutas, horarios, tarifas y alternativas para moverte mejor por la ciudad.</p>
    </div>

    <div class="hero-visual" aria-hidden="true">
      <div class="ruta-diagrama">
        <span class="ruta-nodo nodo-inicio"></span>
        <span class="ruta-linea"></span>
        <span class="ruta-nodo nodo-medio"></span>
        <span class="ruta-linea"></span>
        <span class="ruta-bus">🚌</span>
        <span class="ruta-linea"></span>
        <span class="ruta-nodo nodo-fin"></span>
      </div>
      <div class="panel-datos">
        <span>Datos de ruta</span>
        <strong>horarios · tarifas · recorridos</strong>
      </div>
    </div>
  </div>
</header>
