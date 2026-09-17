import type { ApiResponse, ApiRoute, HealthResponse } from '../lib/types';

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) throw new Error('Error al conectar con el servidor');
  return response.json() as Promise<T>;
}

export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return readJson<HealthResponse>(await fetch('/api/health', { signal }));
}

export async function consultRoute(consulta: string, contexto?: Record<string, unknown>, signal?: AbortSignal): Promise<ApiResponse> {
  return readJson<ApiResponse>(await fetch('/api/consultar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ consulta, contexto }),
    signal
  }));
}

export async function getRoutes(signal?: AbortSignal): Promise<ApiRoute[]> {
  const data = await readJson<{ rutas?: ApiRoute[] }>(await fetch('/api/rutas', { signal }));
  return data.rutas ?? [];
}

export async function getNextUnit(rutaCodigo: string, signal?: AbortSignal): Promise<ApiRoute> {
  return readJson<ApiRoute>(await fetch('/api/proxima-unidad', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ruta_codigo: rutaCodigo }),
    signal
  }));
}
