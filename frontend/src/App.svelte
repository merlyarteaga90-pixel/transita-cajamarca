<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import { consultRoute, getNextUnit } from './api/routes';
  import ErrorMessage from './components/ErrorMessage.svelte';
  import Header from './components/Header.svelte';
  import LoadingState from './components/LoadingState.svelte';
  import ResponsePanel from './components/ResponsePanel.svelte';
  import QuickActions from './components/QuickActions.svelte';
  import RouteModal from './components/RouteModal.svelte';
  import SearchBox from './components/SearchBox.svelte';
  import { formatSchedule, hasValue, safeText, withUnit } from './lib/formatters';
  import type { ApiResponse } from './lib/types';
  import { normalizeVoiceText, preloadVoices, speakText, stopVoice } from './lib/voice';

  let response: ApiResponse | null = null;
  let error = '';
  let loading = false;
  let modalOpen = false;
  let speaking = false;
  let copied = false;
  let searchValue = '';
  let controller: AbortController | null = null;
  let conversationContext: Record<string, unknown> = {};
  let requestId = 0;
  let copyTimer: number | null = null;

  $: voiceText = normalizeVoiceText(safeText(response?.respuesta));

  onMount(() => preloadVoices());

  onDestroy(() => {
    controller?.abort();
    stopVoice();
    if (copyTimer) window.clearTimeout(copyTimer);
  });

  function prepareRequest(): { id: number; signal: AbortSignal } {
    controller?.abort();
    controller = new AbortController();
    const id = ++requestId;
    stopSpeaking();
    error = '';
    response = null;
    loading = true;
    return { id, signal: controller.signal };
  }

  function finishRequest(id: number): void {
    if (id !== requestId) return;
    loading = false;
    controller = null;
  }

  async function handleSubmit(consulta: string): Promise<void> {
    const request = prepareRequest();
    try {
      const data = await consultRoute(consulta, conversationContext, request.signal);
      if (request.id === requestId) {
        response = data ?? {};
        conversationContext = data?.contexto ?? {};
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError' && request.id === requestId) {
        error = 'Hubo un problema al conectar con el servidor.';
      }
    } finally {
      finishRequest(request.id);
    }
  }

  function handleClear(): void {
    controller?.abort();
    controller = null;
    requestId++;
    loading = false;
    error = '';
    response = null;
    conversationContext = {};
    stopSpeaking();
  }

  function handleExample(event: CustomEvent<string>): void {
    searchValue = event.detail;
  }

  async function handleNextUnit(event: CustomEvent<{ codigo: string; sentido: string }>): Promise<void> {
    const { codigo, sentido } = event.detail;
    const request = prepareRequest();
    try {
      const data = await getNextUnit(codigo, request.signal);
      if (request.id !== requestId) return;

      const horario = formatSchedule(data || {});
      const proxima = withUnit(data?.proximo_paso_min, 'min', '~');
      const parts = [`La ruta ${safeText(codigo, 'seleccionada')}`];
      if (horario) parts.push(`opera de ${horario}`);
      if (proxima) parts.push(`la próxima salida teórica desde el inicio es en aproximadamente ${proxima}`);
      else if (hasValue(data?.mensaje_servicio)) parts.push(safeText(data.mensaje_servicio));

      response = {
        estado: `Ruta ${safeText(codigo)}${hasValue(sentido) ? ` - ${safeText(sentido)}` : ''}`,
        icono: '🚌',
        tipo: 'info',
        respuesta: `${parts.join('. ')}.`,
        resultados: [{ ...data, sentido }]
      };
      conversationContext = {};
    } catch (err) {
      if ((err as Error).name !== 'AbortError' && request.id === requestId) {
        error = 'No se pudo obtener la información de la ruta.';
      }
    } finally {
      finishRequest(request.id);
    }
  }

  function stopSpeaking(): void {
    stopVoice();
    speaking = false;
  }

  function handleSpeak(): void {
    if (speaking) {
      stopSpeaking();
      return;
    }
    speakText(voiceText, () => (speaking = true), () => (speaking = false));
  }

  function handleCopy(): void {
    if (!voiceText || !navigator.clipboard) return;
    navigator.clipboard.writeText(voiceText).then(() => {
      copied = true;
      if (copyTimer) window.clearTimeout(copyTimer);
      copyTimer = window.setTimeout(() => (copied = false), 2000);
    });
  }
</script>

<main class="contenedor">
  <Header />
  <SearchBox bind:value={searchValue} {loading} on:submit={(event) => handleSubmit(event.detail)} on:clear={handleClear} />
  <QuickActions on:openRoutes={() => (modalOpen = true)} on:example={handleExample} />
  {#if loading}<LoadingState />{/if}
  <ErrorMessage message={error} />
  {#if response}
    <ResponsePanel data={response} {speaking} {copied} onSpeak={handleSpeak} onCopy={handleCopy} />
  {/if}
</main>

<RouteModal open={modalOpen} on:close={() => (modalOpen = false)} on:select={handleNextUnit} />
