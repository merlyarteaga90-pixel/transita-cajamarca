import { useCallback, useState } from 'react';

export type Geolocation = {
  lat: number;
  lon: number;
  accuracy?: number;
  capturedAt?: string;
};

export type GeolocationStatus =
  | 'idle'
  | 'requesting'
  | 'active'
  | 'denied'
  | 'unavailable'
  | 'timeout';

export type UseGeolocationReturn = {
  location: Geolocation | null;
  status: GeolocationStatus;
  error: string | null;
  request: () => void;
  clear: () => void;
};

function _friendlyError(err: GeolocationPositionError): GeolocationStatus {
  switch (err.code) {
    case err.PERMISSION_DENIED:
      return 'denied';
    case err.POSITION_UNAVAILABLE:
      return 'unavailable';
    case err.TIMEOUT:
      return 'timeout';
    default:
      return 'unavailable';
  }
}

export function useGeolocation(): UseGeolocationReturn {
  const [location, setLocation] = useState<Geolocation | null>(null);
  const [status, setStatus] = useState<GeolocationStatus>('idle');
  const [error, setError] = useState<string | null>(null);

  const request = useCallback(() => {
    if (!('geolocation' in navigator)) {
      setStatus('unavailable');
      setError('La geolocalización no está disponible en este navegador.');
      return;
    }

    setStatus('requesting');
    setError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
          accuracy: position.coords.accuracy,
          capturedAt: new Date().toISOString(),
        });
        setStatus('active');
        setError(null);
      },
      (err) => {
        const friendly = _friendlyError(err);
        setStatus(friendly);
        setError(
          friendly === 'denied'
            ? 'Permiso denegado para acceder a tu ubicación.'
            : 'No se pudo obtener la ubicación.'
        );
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000,
      }
    );
  }, []);

  const clear = useCallback(() => {
    setLocation(null);
    setStatus('idle');
    setError(null);
  }, []);

  return { location, status, error, request, clear };
}
