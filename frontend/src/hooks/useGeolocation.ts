import { useCallback, useState } from 'react';

export type Geolocation = {
  lat: number;
  lon: number;
};

export type UseGeolocationReturn = {
  location: Geolocation | null;
  error: string | null;
  request: () => void;
};

export function useGeolocation(): UseGeolocationReturn {
  const [location, setLocation] = useState<Geolocation | null>(null);
  const [error, setError] = useState<string | null>(null);

  const request = useCallback(() => {
    if (!('geolocation' in navigator)) {
      setError('La geolocalización no está disponible en este navegador.');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          lat: position.coords.latitude,
          lon: position.coords.longitude
        });
        setError(null);
      },
      (err) => {
        setError(err.message || 'No se pudo obtener la ubicación.');
      }
    );
  }, []);

  return { location, error, request };
}
