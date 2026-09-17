<script lang="ts">
  import type { ApiResponse } from '../lib/types';
  import { asRoutes, candidateText, safeText } from '../lib/formatters';
  import InfoRouteCard from './InfoRouteCard.svelte';
  import PlaceRouteCard from './PlaceRouteCard.svelte';
  import RouteCard from './RouteCard.svelte';
  import SelectorRouteCard from './SelectorRouteCard.svelte';

  export let data: ApiResponse;
  export let speaking = false;
  export let copied = false;

  export let onSpeak: () => void;
  export let onCopy: () => void;

  $: results = asRoutes(data.resultados);
  $: selectorRoutes = asRoutes(data.rutas);
  $: candidates = Array.isArray(data.candidatos) ? data.candidatos.map(candidateText).filter(Boolean) : [];
</script>

<section id="resultado" class="resultado">
  <div class="resultado-header">
    <div class="resultado-titulo">
      <span id="iconoEstado" class="icono-estado">{safeText(data.icono, '🚌')}</span>
      <h3 id="estadoTexto">{safeText(data.estado, 'Respuesta del Asistente')}</h3>
    </div>
    <div class="resultado-herramientas">
      <button id="btnVoz" class="btn-tool" type="button" title="Escuchar respuesta" on:click={onSpeak}>
        {speaking ? '⏹️ Detener' : '🔊 Escuchar'}
      </button>
      <button id="btnCopiar" class="btn-tool" type="button" title="Copiar texto" on:click={onCopy}>
        {copied ? '✓ ¡Copiado!' : '📋 Copiar'}
      </button>
    </div>
  </div>

  <div id="respuesta" class="respuesta-cuerpo">
    <div class="respuesta-resumen">
      <span class="respuesta-resumen-icono">🚌</span>
      <p>{safeText(data.respuesta, 'No se encontraron rutas.')}</p>
    </div>

    {#if data.tipo === 'ruta'}
      <div class="resultados-lista">
        {#each results as route}
          <RouteCard {route} />
        {/each}
      </div>
    {:else if data.tipo === 'rutas_por_lugar' || data.tipo === 'alternativas'}
      <div class="resultados-lista">
        {#each results as route}
          <PlaceRouteCard {route} />
        {/each}
      </div>
    {:else if data.tipo === 'info'}
      <div class="resultados-lista">
        {#each results as route}
          <InfoRouteCard {route} />
        {/each}
      </div>
    {:else if data.tipo === 'selector_ruta'}
      {#if selectorRoutes.length}
        <div class="resultados-lista selector-rutas">
          {#each selectorRoutes as route}
            <SelectorRouteCard {route} />
          {/each}
        </div>
      {/if}
    {:else if data.tipo === 'aclaracion' && candidates.length}
      <ul class="aclaracion-lista">
        {#each candidates as candidate}
          <li>{candidate}</li>
        {/each}
      </ul>
    {/if}
  </div>
</section>
