import type { ApiRoute } from './types';

export function hasValue(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === 'number') return Number.isFinite(value);
  const text = String(value).trim();
  return text !== '' && !/(^|\s)(undefined|null|nan)(\s|$)/i.test(text);
}

export function safeText(value: unknown, fallback = ''): string {
  return hasValue(value) ? String(value).trim() : fallback;
}

export function withUnit(value: unknown, unit: string, prefix = ''): string {
  const clean = safeText(value);
  if (!clean) return '';
  if (clean.toLowerCase().includes(unit.toLowerCase())) return clean;
  return `${prefix}${clean} ${unit}`.trim();
}

export function formatSchedule(route: ApiRoute): string {
  const schedule = safeText(route?.horario);
  if (schedule) return schedule;

  const start = safeText(route?.horario_inicio);
  const end = safeText(route?.horario_fin);
  if (start && end) return `${start} - ${end}`;
  if (start) return `Desde ${start}`;
  if (end) return `Hasta ${end}`;
  return '';
}

export function formatFare(value: unknown): string {
  if (!hasValue(value)) return '';
  if (typeof value === 'number') return `S/. ${value.toFixed(2)}`;

  const clean = String(value).trim();
  const number = Number(clean.replace(',', '.'));
  if (Number.isFinite(number)) return `S/. ${number.toFixed(2)}`;
  return clean;
}

export function routeCode(route: ApiRoute): string {
  return safeText(route.codigo_ruta ?? route.codigo ?? route.ruta, 'Ruta');
}

export function routeDirection(route: ApiRoute): string {
  return safeText(route.sentido ?? route.tipo);
}

export function routePath(route: ApiRoute): string {
  const origin = safeText(route.origen);
  const destination = safeText(route.destino);
  return origin && destination ? `${origin} → ${destination}` : origin || destination;
}

export function asRoutes(value: unknown): ApiRoute[] {
  return Array.isArray(value) ? value.filter((item): item is ApiRoute => Boolean(item) && typeof item === 'object') : [];
}

export function candidateText(candidate: unknown): string {
  if (!hasValue(candidate)) return '';
  if (typeof candidate !== 'object') return safeText(candidate);

  const item = candidate as ApiRoute;
  const code = safeText(item.codigo_ruta ?? item.codigo ?? item.ruta);
  const name = safeText(item.nombre ?? item.punto ?? item.nombre_comercial ?? item.razon_social);
  if (code && name && code !== name) return `${code} - ${name}`;
  return code || name;
}
