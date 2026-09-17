<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{ openRoutes: void; example: string }>();

  type HelpKey = 'fare' | 'place' | 'how' | null;

  let activeHelp: HelpKey = null;

  function toggleHelp(key: Exclude<HelpKey, null>, example?: string): void {
    activeHelp = activeHelp === key ? null : key;
    if (example) dispatch('example', example);
  }
</script>

<section class="quick-actions" aria-label="Acciones rápidas">
  <div class="quick-actions-header">
    
   <span>Accesos rápidos</span>
  </div>

  <div class="quick-actions-grid">
    <button type="button" class="quick-action-card destacado qa-next" on:click={() => dispatch('openRoutes')}>
      <span class="quick-icon">🕒</span>
      <strong>Próxima combi</strong>
      <small>Busca una ruta y revisa su salida teórica.</small>
    </button>

    <button type="button" class="quick-action-card qa-fare" aria-pressed={activeHelp === 'fare'} on:click={() => toggleHelp('fare', 'tarifa de la ruta 05')}>
      <span class="quick-icon">🎫</span>
      <strong>Tarifa por ruta</strong>
      <small>Pregunta por el pasaje usando el código.</small>
    </button>

    <button type="button" class="quick-action-card qa-place" aria-pressed={activeHelp === 'place'} on:click={() => toggleHelp('place', 'rutas que pasan por Shudal')}>
      <span class="quick-icon">📍</span>
      <strong>Rutas por lugar</strong>
      <small>Encuentra rutas que pasan por una zona.</small>
    </button>

    <button type="button" class="quick-action-card qa-how" aria-pressed={activeHelp === 'how'} on:click={() => toggleHelp('how', 'cómo voy a Shudal')}>
      <span class="quick-icon">⌁</span>
      <strong>Cómo consultar</strong>
      <small>Ejemplos para obtener mejores respuestas.</small>
    </button>
  </div>

  {#if activeHelp}
    <div class="quick-help">
      {#if activeHelp === 'fare'}
        <strong>Consulta tarifas con el número de ruta.</strong>
        <p>Ejemplos: "tarifa de la ruta 05", "cuánto cuesta la ruta 04".</p>
      {:else if activeHelp === 'place'}
        <strong>Busca rutas por referencia o zona.</strong>
        <p>Ejemplos: "rutas que pasan por Shudal", "qué rutas pasan por el hospital".</p>
      {:else}
        <strong>Escribe como hablarías normalmente.</strong>
        <p>Ejemplos: "cómo voy a Shudal", "de Shudal al hospital", "cuál es la ruta 05".</p>
      {/if}
    </div>
  {/if}
</section>
