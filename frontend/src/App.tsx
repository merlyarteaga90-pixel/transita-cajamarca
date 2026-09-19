import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { consultRoute, getNextUnit } from './api/client';
import type { ApiResponse, ConversationContext } from './api/types';
import { ErrorMessage } from './components/ErrorMessage';
import { Header } from './components/Header';
import { LoadingState } from './components/LoadingState';
import { QuickActions } from './components/QuickActions';
import { ResponsePanel } from './components/ResponsePanel';
import { RouteModal } from './components/RouteModal';
import { SearchBox, SearchBoxHandle } from './components/SearchBox';
import { formatSchedule, hasValue, safeText, withUnit } from './lib/formatters';
import { normalizeVoiceText, preloadVoices, speakText, stopVoice } from './lib/voice';
import { useAbortController } from './hooks/useAbortController';
import { useGeolocation } from './hooks/useGeolocation';
import { useSession } from './hooks/useSession';

export function App() {
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [copied, setCopied] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const [conversationContext, setConversationContext] = useState<ConversationContext>({});
  const searchBoxRef = useRef<SearchBoxHandle>(null);
  const copyTimerRef = useRef<number | null>(null);

  const { loading, startRequest, finishRequest, reset } = useAbortController();
  const { location, error: locationError, request: requestLocation } = useGeolocation();
  const { sessionId } = useSession();

  const voiceText = useMemo(
    () => normalizeVoiceText(safeText(response?.respuesta)),
    [response?.respuesta]
  );

  useEffect(() => {
    preloadVoices();
  }, []);

  useEffect(() => {
    return () => {
      stopVoice();
      if (copyTimerRef.current) window.clearTimeout(copyTimerRef.current);
    };
  }, []);

  const stopSpeaking = useCallback(() => {
    stopVoice();
    setSpeaking(false);
  }, []);

  const handleSubmit = useCallback(
    async (consulta: string) => {
      const request = startRequest();
      stopSpeaking();
      setError('');
      setResponse(null);

      try {
        const data = await consultRoute({
          consulta,
          contexto: conversationContext,
          user_location: location ?? undefined,
          session_id: sessionId
        }, request.signal);

        if (request.id === undefined) return;
        if (finishRequest(request.id)) {
          setResponse(data ?? null);
          setConversationContext(data?.contexto ?? {});
        }
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          finishRequest(request.id ?? -1);
          setError('Hubo un problema al conectar con el servidor.');
        }
      }
    },
    [conversationContext, finishRequest, location, sessionId, startRequest, stopSpeaking]
  );

  const handleClear = useCallback(() => {
    reset();
    setError('');
    setResponse(null);
    setConversationContext({});
    stopSpeaking();
    searchBoxRef.current?.focus();
  }, [reset, stopSpeaking]);

  const handleExample = useCallback((example: string) => {
    setSearchValue(example);
    searchBoxRef.current?.focus();
  }, []);

  const handleCandidateSelect = useCallback(
    (candidate: string) => {
      setSearchValue(candidate);
      void handleSubmit(candidate);
    },
    [handleSubmit]
  );

  const handleNextUnit = useCallback(
    async (codigo: string, sentido: string) => {
      const request = startRequest();
      stopSpeaking();
      setError('');
      setResponse(null);

      try {
        const data = await getNextUnit(codigo, request.signal);
        if (finishRequest(request.id ?? -1)) {
          const horario = formatSchedule(data);
          const proxima = withUnit(data.proxima_unidad?.minutos_restantes, 'min', '~');
          const parts = [`La ruta ${safeText(codigo, 'seleccionada')}`];
          if (horario) parts.push(`opera de ${horario}`);
          if (proxima)
            parts.push(`la próxima salida teórica desde el inicio es en aproximadamente ${proxima}`);
          else if (hasValue(data.proxima_unidad?.nota))
            parts.push(safeText(data.proxima_unidad?.nota));

          setResponse({
            estado: `Ruta ${safeText(codigo)}${hasValue(sentido) ? ` - ${safeText(sentido)}` : ''}`,
            icono: '🚌',
            tipo: 'info',
            respuesta: `${parts.join('. ')}.`,
            resultados: [{ ...data, sentido: sentido === 'IDA' || sentido === 'VUELTA' ? sentido : data.sentido }]
          });
          setConversationContext({});
        }
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          finishRequest(request.id ?? -1);
          setError('No se pudo obtener la información de la ruta.');
        }
      }
    },
    [finishRequest, startRequest, stopSpeaking]
  );

  const handleSpeak = useCallback(() => {
    if (speaking) {
      stopSpeaking();
      return;
    }
    speakText(voiceText, () => setSpeaking(true), () => setSpeaking(false));
  }, [speaking, stopSpeaking, voiceText]);

  const handleCopy = useCallback(() => {
    if (!voiceText || !navigator.clipboard) return;
    navigator.clipboard.writeText(voiceText).then(() => {
      setCopied(true);
      if (copyTimerRef.current) window.clearTimeout(copyTimerRef.current);
      copyTimerRef.current = window.setTimeout(() => setCopied(false), 2000);
    });
  }, [voiceText]);

  return (
    <>
      <main className="contenedor">
        <Header />
        <SearchBox
          ref={searchBoxRef}
          value={searchValue}
          loading={loading}
          onChange={setSearchValue}
          onSubmit={handleSubmit}
          onClear={handleClear}
          onRequestLocation={requestLocation}
          locationError={locationError}
        />
        <QuickActions onOpenRoutes={() => setModalOpen(true)} onExample={handleExample} />
        {loading && <LoadingState />}
        <ErrorMessage message={error} />
        {response && (
          <ResponsePanel
            data={response}
            speaking={speaking}
            copied={copied}
            onSpeak={handleSpeak}
            onCopy={handleCopy}
            onCandidateSelect={handleCandidateSelect}
          />
        )}
      </main>

      <RouteModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSelect={handleNextUnit}
      />
    </>
  );
}
