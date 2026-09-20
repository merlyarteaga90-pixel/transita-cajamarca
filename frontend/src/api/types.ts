export type ApiRoutePoint = {
  nombre: string;
  orden: number;
  distrito?: string;
};

export type ProximaUnidad = {
  minutos_restantes: number;
  ventana: string;
  proxima_salida: string;
  nota?: string;
};

export type ApiRoute = {
  // Identificación
  codigo?: string;
  codigo_ruta?: string;
  ruta?: string;
  ruta_nombre?: string;
  nombre?: string;
  nombre_comercial?: string;
  razon_social?: string;
  empresa?: string;
  ruc?: string | number;

  // Sentido / recorrido
  sentido?: 'IDA' | 'VUELTA';
  tipo?: 'IDA' | 'VUELTA';
  origen?: string;
  destino?: string;
  punto?: string;
  puntos?: ApiRoutePoint[];

  // Distancia / tiempo
  distancia_km?: number;
  distancia_total_ruta_km?: number;
  tiempo_total_min?: number;
  tiempo_total_ruta_min?: number;

  // Horarios / frecuencia
  horario?: string;
  horario_inicio?: string;
  horario_fin?: string;
  frecuencia_min?: number;

  // Tarifas
  tarifa?: number;
  tarifa_general?: number;
  tarifa_medio_pasaje?: number;

  // Próxima unidad (información plana y estructurada)
  proxima_unidad?: ProximaUnidad;
  proxima_salida?: string | null;
  proximo_paso_min?: number | null;
  hora_actual?: string;
  estado_servicio?: string;
  mensaje_servicio?: string;

  // Tipo de consulta que originó la respuesta (TARIFA, HORARIO, etc.)
  consulta_tipo?: string;
};

export type ApiResponseTipo =
  | 'ruta'
  | 'alternativas'
  | 'aclaracion'
  | 'saludo'
  | 'info'
  | 'sin_resultados'
  | 'error'
  | 'selector'
  | 'proximas_unidades'
  // Alias usados por versiones anteriores del backend
  | 'rutas_por_lugar'
  | 'selector_ruta';

export type SelectorCandidate = {
  mostrar: string;
  ruta: string;
  sentido: string;
};

export type ConversationContext = {
  origen?: string;
  destino?: string;
  pendiente?: 'origen' | 'destino' | null;
};

export type ApiResponse = {
  estado: string;
  tipo: ApiResponseTipo;
  respuesta: string;
  resultados?: ApiRoute[];
  candidatos?: SelectorCandidate[] | string[];
  icono?: string;
  pendiente?: 'origen' | 'destino' | null;
  contexto?: ConversationContext;
  session_id?: string;
  rutas?: ApiRoute[];
};

export type HealthResponse = {
  estado: string;
  status?: string;
  db?: string;
  modo: string;
  gemini?: string;
  gemini_model?: string | null;
  counts?: Record<string, number>;
  version?: string;
};

export type ProximaUnidadResponse = ApiRoute;
