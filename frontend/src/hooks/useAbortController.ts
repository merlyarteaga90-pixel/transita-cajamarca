import { useCallback, useRef, useState } from 'react';

export type RequestController = {
  abort: () => void;
  signal: AbortSignal;
};

export function useAbortController() {
  const controllerRef = useRef<AbortController | null>(null);
  const requestIdRef = useRef(0);
  const [loading, setLoading] = useState(false);

  const abortCurrent = useCallback(() => {
    controllerRef.current?.abort();
    controllerRef.current = null;
  }, []);

  const startRequest = useCallback(() => {
    abortCurrent();
    const controller = new AbortController();
    controllerRef.current = controller;
    const id = ++requestIdRef.current;
    setLoading(true);
    return { id, signal: controller.signal };
  }, [abortCurrent]);

  const finishRequest = useCallback(
    (id: number) => {
      if (id !== requestIdRef.current) return false;
      setLoading(false);
      controllerRef.current = null;
      return true;
    },
    []
  );

  const reset = useCallback(() => {
    abortCurrent();
    requestIdRef.current++;
    setLoading(false);
  }, [abortCurrent]);

  return {
    loading,
    startRequest,
    finishRequest,
    reset,
    abortCurrent
  };
}
