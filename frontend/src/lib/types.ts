export type ResponseType =
  | 'ruta'
  | 'alternativas'
  | 'rutas_por_lugar'
  | 'info'
  | 'selector_ruta'
  | 'aclaracion'
  | 'sin_resultados'
  | 'saludo'
  | 'error';

export interface ApiRoute {
  [key: string]: unknown;
  codigo?: string | number | null;
  codigo_ruta?: string | number | null;
  ruta?: string | number | null;
  ruta_nombre?: string | null;
  nombre?: string | null;
  nombre_comercial?: string | null;
  razon_social?: string | null;
  ruc?: string | number | null;
  sentido?: string | null;
  tipo?: string | null;
  origen?: string | null;
  destino?: string | null;
  punto?: string | null;
  orden?: string | number | null;
  puntos?: Array<{ nombre?: string | null; orden?: string | number | null }>;
  horario?: string | null;
  horario_inicio?: string | null;
  horario_fin?: string | null;
  frecuencia_min?: string | number | null;
  tarifa_general?: string | number | null;
  tarifa_medio_pasaje?: string | number | null;
  tiempo_total_ruta_min?: string | number | null;
  tiempo_total_min?: string | number | null;
  distancia_total_ruta_km?: string | number | null;
  distancia_km?: string | number | null;
  proxima_salida?: string | null;
  proximo_paso_min?: string | number | null;
  hora_actual?: string | null;
  mensaje_servicio?: string | null;
}

export interface ApiResponse {
  estado?: string;
  icono?: string;
  tipo?: ResponseType;
  respuesta?: string;
  resultados?: ApiRoute[];
  candidatos?: unknown[];
  rutas?: ApiRoute[];
  intencion_solicitada?: string | null;
  contexto?: Record<string, unknown>;
}

export interface HealthResponse {
  status?: string;
  modo?: string;
  ollama?: string;
}
