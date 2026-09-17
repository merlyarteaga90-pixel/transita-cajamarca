export function normalizeVoiceText(text: string): string {
  return text
    .replace(/\*\*/g, '')
    .replace(/•/g, ', ')
    .replace(/➔|→/g, ' hacia ')
    .replace(/S\/\./g, 'soles ')
    .replace(/Cdra\./g, 'cuadra ')
    .replace(/Av\./g, 'avenida ')
    .replace(/Jr\./g, 'jirón ')
    .replace(/C\.P\./g, 'centro poblado ');
}

export function preloadVoices(): void {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.getVoices();
  window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

export function stopVoice(): void {
  if ('speechSynthesis' in window) window.speechSynthesis.cancel();
}

export function speakText(text: string, onStart: () => void, onDone: () => void): void {
  if (!('speechSynthesis' in window)) {
    alert('Tu navegador no soporta síntesis de voz.');
    return;
  }
  if (!text) return;

  window.speechSynthesis.cancel();
  window.speechSynthesis.resume();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'es-PE';
  utterance.pitch = 1.15;
  utterance.rate = 0.98;

  const voices = window.speechSynthesis.getVoices();
  const friendlyVoice = voices.find((voice) =>
    (voice.lang.startsWith('es') || voice.lang.includes('es-')) &&
    ['Sabina', 'Camila', 'Dalia', 'Natural', 'Online', 'Google', 'Paulina', 'Helena'].some((name) =>
      voice.name.includes(name)
    )
  ) || voices.find((voice) =>
    voice.lang.includes('es-PE') || voice.lang.includes('es-419') || voice.lang.includes('es-US') || voice.lang.startsWith('es')
  );

  if (friendlyVoice) utterance.voice = friendlyVoice;
  utterance.onstart = onStart;
  utterance.onend = utterance.onerror = onDone;
  window.speechSynthesis.speak(utterance);
}
