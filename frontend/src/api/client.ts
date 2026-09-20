import type {
  ApiResponse,
  ApiRoute,
  ConversationContext,
  HealthResponse,
  ProximaUnidadResponse,
  SelectorCandidate
} from './types';

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) throw new Error('Error al conectar con el servidor');
  return response.json() as Promise<T>;
}

export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return readJson<HealthResponse>(await fetch('/api/health', { signal }));
}

export type ConsultarRequest = {
  consulta: string;
  origen?: string;
  destino?: string;
  intencion?: string;
  ruta_codigo?: string;
  contexto?: ConversationContext;
  user_location?: {
    lat: number;
    lon: number;
    accuracy_m?: number;
    captured_at?: string;
  };
  session_id?: string;
};

export async function consultRoute(
  body: ConsultarRequest,
  signal?: AbortSignal
): Promise<ApiResponse> {
  return readJson<ApiResponse>(
    await fetch('/api/consultar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal
    })
  );
}

export async function getRoutes(signal?: AbortSignal): Promise<ApiRoute[]> {
  const data = await readJson<{ rutas?: ApiRoute[] }>(await fetch('/api/rutas', { signal }));
  return data.rutas ?? [];
}

export async function getNextUnit(
  rutaCodigo: string,
  signal?: AbortSignal
): Promise<ProximaUnidadResponse> {
  return readJson<ProximaUnidadResponse>(
    await fetch('/api/proxima-unidad', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ruta_codigo: rutaCodigo }),
      signal
    })
  );
}

export function isSelectorCandidate(candidate: unknown): candidate is SelectorCandidate {
  return (
    typeof candidate === 'object' &&
    candidate !== null &&
    'ruta' in candidate &&
    typeof (candidate as SelectorCandidate).ruta === 'string'
  );
}
