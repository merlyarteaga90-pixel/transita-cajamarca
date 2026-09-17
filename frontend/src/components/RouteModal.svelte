<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { getRoutes } from '../api/routes';
  import { asRoutes, formatSchedule, hasValue, routeCode, routeDirection, routePath, safeText, withUnit } from '../lib/formatters';
  import type { ApiRoute } from '../lib/types';

  export let open = false;

  const dispatch = createEventDispatcher<{ close: void; select: { codigo: string; sentido: string } }>();
  let routes: ApiRoute[] = [];
  let loaded = false;
  let loading = false;
  let error = '';
  let search = '';

  $: if (open && !loaded && !loading) loadRoutes();
  $: filteredRoutes = filterRoutes(routes, search);

  async function loadRoutes(): Promise<void> {
    loading = true;
    error = '';
    try {
      routes = asRoutes(await getRoutes());
      loaded = true;
    } catch (_error) {
      error = 'No se pudieron cargar las rutas.';
    } finally {
      loading = false;
    }
  }

  function filterRoutes(items: ApiRoute[], term: string): ApiRoute[] {
    const clean = term.trim().toLowerCase();
    if (!clean) return items;

    return items.filter((route) => [
      route.codigo,
      route.codigo_ruta,
      route.nombre_comercial,
      route.razon_social,
      route.origen,
      route.destino,
      route.tipo,
      route.sentido
    ].some((value) => safeText(value).toLowerCase().includes(clean)));
  }

  function close(): void {
    search = '';
    dispatch('close');
  }

  function selectRoute(route: ApiRoute): void {
    const codigo = routeCode(route);
    if (!hasValue(codigo)) return;
    close();
    dispatch('select', { codigo, sentido: routeDirection(route) });
  }

  function handleOverlayClick(event: MouseEvent): void {
    if (event.target === event.currentTarget) close();
  }

  function handleOverlayKeydown(event: KeyboardEvent): void {
    if (event.key === 'Escape') close();
  }

  function handleRouteKeydown(event: KeyboardEvent, route: ApiRoute): void {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      selectRoute(route);
    }
  }
</script>

{#if open}
  <div id="modalRutas" class="modal-overlay" role="presentation" tabindex="-1" on:click={handleOverlayClick} on:keydown={handleOverlayKeydown}>
    <div class="modal-contenido">
      <div class="modal-header">
        <h3>🚌 Seleccionar Ruta</h3>
        <button id="btnCerrarModalRutas" class="modal-cerrar" type="button" aria-label="Cerrar" on:click={close}>✕</button>
      </div>
      <div class="modal-buscador">
        <input type="text" id="modalRutasBuscador" bind:value={search} placeholder="Buscar por código, empresa u origen..." />
      </div>
      <div id="modalRutasLista" class="modal-lista">
        {#if loading}
          <p class="modal-mensaje">Cargando rutas...</p>
        {:else if error}
          <p class="modal-mensaje modal-error">{error}</p>
        {:else if filteredRoutes.length === 0}
          <p class="modal-mensaje">No se encontraron rutas.</p>
        {:else}
          {#each filteredRoutes as route}
            {@const codigo = routeCode(route)}
            {@const sentido = routeDirection(route)}
            {@const nombre = safeText(route.nombre_comercial ?? route.razon_social)}
            {@const trayecto = routePath(route)}
            {@const horario = formatSchedule(route)}
            {@const frecuencia = withUnit(route.frecuencia_min, 'min', 'Cada ')}
            {@const detalles = [frecuencia, horario].filter(hasValue).join(' · ')}
            <div
              class="ruta-modal-item"
              role="button"
              tabindex="0"
              data-codigo={codigo}
              data-sentido={sentido}
              on:click={() => selectRoute(route)}
              on:keydown={(event) => handleRouteKeydown(event, route)}
            >
              <div class="ruta-modal-icono" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M6 17h12" />
                  <path d="M7 17v2" />
                  <path d="M17 17v2" />
                  <path d="M5 8c0-2 1.2-3 3.2-3h7.6C17.8 5 19 6 19 8v7c0 1.1-.9 2-2 2H7c-1.1 0-2-.9-2-2V8Z" />
                  <path d="M8 9h8" />
                  <path d="M8 13h.01" />
                  <path d="M16 13h.01" />
                </svg>
              </div>
              <div class="ruta-modal-info">
                <div class="ruta-modal-top">
                  <span class="ruta-modal-codigo">{codigo}</span>
                  {#if sentido}<span class="ruta-modal-sentido" data-sentido={sentido}>{sentido}</span>{/if}
                </div>
                {#if nombre}<strong class="ruta-modal-nombre">{nombre}</strong>{/if}
                {#if trayecto}<span class="ruta-modal-trayecto">{trayecto}</span>{/if}
                {#if detalles}<span class="ruta-modal-detalles">{detalles}</span>{/if}
              </div>
            </div>
          {/each}
        {/if}
      </div>
    </div>
  </div>
{/if}
