<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';

  export let loading = false;
  export let value = '';

  const dispatch = createEventDispatcher<{ submit: string; clear: void }>();
  let textarea: HTMLTextAreaElement;

  onMount(() => textarea?.focus());

  function submit(): void {
    const clean = value.trim();
    if (clean && !loading) dispatch('submit', clean);
  }

  function clear(): void {
    value = '';
    dispatch('clear');
    textarea?.focus();
  }

  export function focus(): void {
    textarea?.focus();
  }

  function handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  }
</script>

<section class="buscador">
  <label for="consulta">¿A dónde quieres ir?</label>
  <div class="input-wrapper">
    <textarea
      id="consulta"
      bind:this={textarea}
      bind:value
      rows="2"
      placeholder='Ejemplo: "cómo voy a Shudal", "tarifa de la ruta 05", "rutas que pasan por el hospital"'
      on:keydown={handleKeydown}
    ></textarea>
    <button type="button" id="btnLimpiar" class="btn-limpiar" title="Borrar texto" on:click={clear}>✕</button>
  </div>

  <div class="buscador-acciones">
  <span class="tip-enter">Presiona <kbd>Enter ↵</kbd> para enviar</span>
    <button id="btnBuscar" type="button" disabled={loading} on:click={submit}>
      <span>Preguntar</span>
      <svg class="icono-enviar" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
      </svg>
    </button>
    
  </div>
</section>
