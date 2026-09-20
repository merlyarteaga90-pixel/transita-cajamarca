import { useCallback, useEffect, useState } from 'react';

const SESSION_KEY = 'transita_session_id';

function generateSessionId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

function readStoredSession(): string | undefined {
  try {
    const stored = window.localStorage.getItem(SESSION_KEY);
    return stored || undefined;
  } catch {
    return undefined;
  }
}

function writeStoredSession(id: string | undefined): void {
  try {
    if (id) window.localStorage.setItem(SESSION_KEY, id);
    else window.localStorage.removeItem(SESSION_KEY);
  } catch {
    // Ignore storage errors (e.g. private mode).
  }
}

export type UseSessionReturn = {
  sessionId: string | undefined;
  reset: () => void;
};

export function useSession(): UseSessionReturn {
  const [sessionId, setSessionId] = useState<string | undefined>(() => {
    const stored = readStoredSession();
    return stored ?? generateSessionId();
  });

  useEffect(() => {
    if (sessionId && readStoredSession() !== sessionId) {
      writeStoredSession(sessionId);
    }
  }, [sessionId]);

  const reset = useCallback(() => {
    const next = generateSessionId();
    writeStoredSession(next);
    setSessionId(next);
  }, []);

  return { sessionId, reset };
}
