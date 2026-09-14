// frontend/app.js

let textoParaVoz = '';
let reproduciendoVoz = false;
let rutasModal = [];
let rutasModalCargadas = false;
let controladorConsulta = null;
let solicitudActual = 0;

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('consulta');
    const modal = document.getElementById('modalRutas');
    const listaModal = document.getElementById('modalRutasLista');
    const buscadorModal = document.getElementById('modalRutasBuscador');

    document.getElementById('btnBuscar')?.addEventListener('click', buscarRuta);
    document.getElementById('btnLimpiar')?.addEventListener('click', limpiarConsulta);
    document.getElementById('btnAbrirModalRutas')?.addEventListener('click', abrirModalRutas);
    document.getElementById('btnCerrarModalRutas')?.addEventListener('click', cerrarModalRutas);
    document.getElementById('btnVoz')?.addEventListener('click', leerRespuestaEnVozAlta);
    document.getElementById('btnCopiar')?.addEventListener('click', copiarRespuesta);

    input?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            buscarRuta();
        }
    });

    modal?.addEventListener('click', (e) => {
        if (e.target === modal) cerrarModalRutas();
    });

    buscadorModal?.addEventListener('input', filtrarRutasModal);

    listaModal?.addEventListener('click', manejarSeleccionModal);
    listaModal?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            manejarSeleccionModal(e);
        }
    });

    if ('speechSynthesis' in window) {
        window.speechSynthesis.getVoices();
        window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
    }

    comprobarEstadoServicio();
});

function escapaHtml(texto) {
    if (texto === null || texto === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(texto);
    return div.innerHTML;
}

function tieneValor(valor) {
    if (valor === null || valor === undefined) return false;
    if (typeof valor === 'number') return Number.isFinite(valor);
    const texto = String(valor).trim();
    return texto !== '' && !/(^|\s)(undefined|null|nan)(\s|$)/i.test(texto);
}

function textoSeguro(valor, respaldo = '') {
    return tieneValor(valor) ? String(valor).trim() : respaldo;
}

function comoLista(valor) {
    return Array.isArray(valor) ? valor.filter(item => item && typeof item === 'object') : [];
}

function conUnidad(valor, unidad, prefijo = '') {
    const limpio = textoSeguro(valor);
    if (!limpio) return '';
    if (limpio.toLowerCase().includes(unidad.toLowerCase())) return limpio;
    return `${prefijo}${limpio} ${unidad}`.trim();
}

function formatearHorario(ruta) {
    const horario = textoSeguro(ruta?.horario);
    if (horario) return horario;

    const inicio = textoSeguro(ruta?.horario_inicio);
    const fin = textoSeguro(ruta?.horario_fin);
    if (inicio && fin) return `${inicio} - ${fin}`;
    if (inicio) return `Desde ${inicio}`;
    if (fin) return `Hasta ${fin}`;
    return '';
}

function formatearTarifa(valor) {
    if (!tieneValor(valor)) return '';
    if (typeof valor === 'number') return `S/. ${valor.toFixed(2)}`;

    const limpio = String(valor).trim();
    const numero = Number(limpio.replace(',', '.'));
    if (Number.isFinite(numero)) return `S/. ${numero.toFixed(2)}`;
    return limpio;
}

function crearResumen(respuesta, respaldo = 'No se encontraron rutas.') {
    const texto = textoSeguro(respuesta, respaldo);
    return `
        <div class="respuesta-resumen">
            <span class="respuesta-resumen-icono">🚌</span>
            <p>${escapaHtml(texto)}</p>
        </div>
    `;
}

function crearMetrica(icono, etiqueta, valor) {
    if (!tieneValor(valor)) return '';
    return `
        <div class="metrica-card">
            <span class="metrica-icono">${icono}</span>
            <span class="metrica-label">${escapaHtml(etiqueta)}</span>
            <strong class="metrica-valor">${escapaHtml(valor)}</strong>
        </div>
    `;
}

function crearMetricas(metricas) {
    const html = metricas
        .filter(([, , valor]) => tieneValor(valor))
        .map(([icono, etiqueta, valor]) => crearMetrica(icono, etiqueta, valor))
        .join('');
    return html ? `<div class="metricas-grid">${html}</div>` : '';
}

function renderizarEncabezadoRuta(ruta, mostrarProxima = true) {
    const codigo = textoSeguro(ruta.codigo_ruta ?? ruta.codigo, 'Ruta');
    const sentido = textoSeguro(ruta.sentido ?? ruta.tipo);
    const proxima = mostrarProxima ? conUnidad(ruta.proximo_paso_min, 'min', '~') : '';
    const iconoSentido = sentido === 'IDA' ? '→ ' : sentido === 'VUELTA' ? '← ' : '';

    return `
        <div class="ruta-card-header">
            <div class="ruta-identidad">
                <span class="badge-ruta">${escapaHtml(codigo)}</span>
                ${sentido ? `<span class="badge-sentido" data-sentido="${escapaHtml(sentido)}">${iconoSentido}${escapaHtml(sentido)}</span>` : ''}
            </div>
            ${proxima ? `
                <div class="proxima-unidad">
                    <span>Salida desde inicio</span>
                    <strong>${escapaHtml(proxima)}</strong>
                </div>
            ` : ''}
        </div>
    `;
}

function renderizarEmpresa(ruta) {
    const nombre = textoSeguro(ruta.nombre_comercial);
    const razon = textoSeguro(ruta.razon_social);
    const ruc = textoSeguro(ruta.ruc);
    if (!nombre && !razon && !ruc) return '';

    return `
        <div class="empresa-info">
            <span class="empresa-icono">🚌</span>
            <div>
                ${nombre ? `<strong>${escapaHtml(nombre)}</strong>` : ''}
                ${razon && razon !== nombre ? `<span>${escapaHtml(razon)}</span>` : ''}
                ${ruc ? `<small>RUC ${escapaHtml(ruc)}</small>` : ''}
            </div>
        </div>
    `;
}

function renderizarTarifas(ruta) {
    const general = formatearTarifa(ruta.tarifa_general);
    const medio = formatearTarifa(ruta.tarifa_medio_pasaje);
    if (!general && !medio) return '';

    return `
        <div class="tarifas-grid">
            ${general ? `<div class="tarifa-card tarifa-general"><span>Pasaje general</span><strong>${escapaHtml(general)}</strong></div>` : ''}
            ${medio ? `<div class="tarifa-card tarifa-medio"><span>Medio pasaje</span><strong>${escapaHtml(medio)}</strong></div>` : ''}
        </div>
    `;
}

function renderizarRecorrido(ruta) {
    const puntos = comoLista(ruta.puntos).filter(p => tieneValor(p.nombre));
    if (puntos.length === 0) return '';

    const html = puntos.map((punto, indice) => {
        const posicion = indice === 0 ? 'inicio' : indice === puntos.length - 1 ? 'fin' : 'intermedio';
        return `
            <li class="recorrido-punto" data-posicion="${posicion}">
                <span class="recorrido-dot"></span>
                <span>${escapaHtml(punto.nombre)}</span>
            </li>
        `;
    }).join('');

    return `
        <div class="recorrido">
            <span class="seccion-label">Puntos del recorrido</span>
            <ol>${html}</ol>
        </div>
    `;
}

function renderizarTarjetaRuta(ruta) {
    const origen = textoSeguro(ruta.origen);
    const destino = textoSeguro(ruta.destino);
    const trayecto = origen && destino ? `${origen} → ${destino}` : origen || destino;
    const metricas = [
        ['⏱️', 'Tiempo total de ruta', conUnidad(ruta.tiempo_total_ruta_min ?? ruta.tiempo_total_min, 'min')],
        ['📏', 'Distancia total de ruta', conUnidad(ruta.distancia_total_ruta_km ?? ruta.distancia_km, 'km')],
        ['🔄', 'Frecuencia', conUnidad(ruta.frecuencia_min, 'min', 'Cada ')],
        ['🕐', 'Horario', formatearHorario(ruta)],
        ['📍', 'Recorrido', trayecto]
    ];

    return `
        <article class="ruta-card">
            ${renderizarEncabezadoRuta(ruta)}
            ${renderizarEmpresa(ruta)}
            ${crearMetricas(metricas)}
            ${renderizarTarifas(ruta)}
            ${renderizarRecorrido(ruta)}
        </article>
    `;
}

function renderizarResultados(resultados) {
    return `<div class="resultados-lista">${comoLista(resultados).map(renderizarTarjetaRuta).join('')}</div>`;
}

function renderizarTarjetaLugar(ruta) {
    const punto = textoSeguro(ruta.punto);
    const origen = textoSeguro(ruta.origen);
    const destino = textoSeguro(ruta.destino);
    const trayecto = origen && destino ? `${origen} → ${destino}` : origen || destino;
    const metricas = [
        ['📍', 'Pasa por', punto],
        ['🧭', 'Recorrido', trayecto],
        ['🕐', 'Horario', formatearHorario(ruta)],
        ['🔄', 'Frecuencia', conUnidad(ruta.frecuencia_min, 'min', 'Cada ')]
    ];

    return `
        <article class="ruta-card ruta-lugar-card">
            ${renderizarEncabezadoRuta(ruta, false)}
            ${renderizarEmpresa(ruta)}
            ${crearMetricas(metricas)}
        </article>
    `;
}

function renderizarRutasPorLugar(resultados) {
    return `<div class="resultados-lista">${comoLista(resultados).map(renderizarTarjetaLugar).join('')}</div>`;
}

function renderizarTarjetaInfo(ruta) {
    const metricas = [
        ['🕐', 'Horario', formatearHorario(ruta)],
        ['🔄', 'Frecuencia', conUnidad(ruta.frecuencia_min, 'min', 'Cada ')],
        ['🚌', 'Salida teórica', textoSeguro(ruta.proxima_salida)],
        ['⏳', 'Faltan', conUnidad(ruta.proximo_paso_min, 'min', '~')],
        ['⌚', 'Hora actual', textoSeguro(ruta.hora_actual)]
    ];

    return `
        <article class="ruta-card info-card">
            ${renderizarEncabezadoRuta(ruta)}
            ${renderizarEmpresa(ruta)}
            ${crearMetricas(metricas)}
            ${renderizarTarifas(ruta)}
        </article>
    `;
}

function renderizarInfo(resultados) {
    return `<div class="resultados-lista">${comoLista(resultados).map(renderizarTarjetaInfo).join('')}</div>`;
}

function renderizarSelectorRutas(rutas) {
    const tarjetas = comoLista(rutas).map(ruta => {
        const origen = textoSeguro(ruta.origen);
        const destino = textoSeguro(ruta.destino);
        const trayecto = origen && destino ? `${origen} → ${destino}` : origen || destino;
        return `
            <article class="ruta-card selector-ruta-card">
                ${renderizarEncabezadoRuta(ruta, false)}
                ${renderizarEmpresa(ruta)}
                ${crearMetricas([
                    ['📍', 'Recorrido', trayecto],
                    ['🕐', 'Horario', formatearHorario(ruta)],
                    ['🔄', 'Frecuencia', conUnidad(ruta.frecuencia_min, 'min', 'Cada ')]
                ])}
            </article>
        `;
    }).join('');
    return tarjetas ? `<div class="resultados-lista selector-rutas">${tarjetas}</div>` : '';
}

function textoCandidato(candidato) {
    if (candidato === null || candidato === undefined) return '';
    if (typeof candidato !== 'object') return textoSeguro(candidato);

    const codigo = textoSeguro(candidato.codigo_ruta ?? candidato.codigo ?? candidato.ruta);
    const nombre = textoSeguro(
        candidato.nombre ?? candidato.punto ?? candidato.oficial ??
        candidato.nombre_comercial ?? candidato.razon_social
    );
    if (codigo && nombre && codigo !== nombre) return `${codigo} - ${nombre}`;
    return codigo || nombre;
}

function renderizarCandidatos(candidatos) {
    if (!Array.isArray(candidatos)) return '';
    const elementos = candidatos
        .map(textoCandidato)
        .filter(tieneValor)
        .map(candidato => `<li>${escapaHtml(candidato)}</li>`)
        .join('');
    if (!elementos) return '';
    return `<ul class="aclaracion-lista">${elementos}</ul>`;
}

function renderizarRespuesta(data) {
    const resumen = crearResumen(data.respuesta);
    switch (data.tipo) {
        case 'ruta':
            return resumen + renderizarResultados(data.resultados);
        case 'rutas_por_lugar':
            return resumen + renderizarRutasPorLugar(data.resultados);
        case 'info':
            return resumen + renderizarInfo(data.resultados);
        case 'selector_ruta':
            return resumen + renderizarSelectorRutas(data.rutas);
        case 'aclaracion':
            return resumen + renderizarCandidatos(data.candidatos);
        default:
            return resumen;
    }
}

async function comprobarEstadoServicio() {
    const texto = document.getElementById('estadoServicioTexto');
    const pill = texto?.closest('.status-pill');
    if (!texto) return;

    try {
        const controlador = new AbortController();
        const temporizador = setTimeout(() => controlador.abort(), 2500);
        const respuesta = await fetch('/api/health', { signal: controlador.signal });
        clearTimeout(temporizador);
        if (!respuesta.ok) throw new Error('Servicio no disponible');
        const datos = await respuesta.json();
        texto.textContent = datos.modo === 'degradado'
            ? 'Servicio disponible'
            : 'Servicio completo';
        if (pill) {
            pill.dataset.status = datos.status === 'ok' ? 'ok' : 'error';
            pill.title = datos.modo === 'degradado'
                ? 'Las consultas principales funcionan; Ollama no está disponible.'
                : 'MySQL y Ollama disponibles.';
        }
    } catch (_error) {
        texto.textContent = 'Servicio no disponible';
        if (pill) pill.dataset.status = 'error';
    }
}

function prepararSolicitud() {
    controladorConsulta?.abort();
    controladorConsulta = new AbortController();
    const id = ++solicitudActual;

    detenerVoz();
    document.getElementById('error')?.classList.add('oculto');
    document.getElementById('resultado')?.classList.add('oculto');
    document.getElementById('cargando')?.classList.remove('oculto');
    const btnBuscar = document.getElementById('btnBuscar');
    if (btnBuscar) btnBuscar.disabled = true;

    return { id, signal: controladorConsulta.signal };
}

function finalizarSolicitud(id) {
    if (id !== solicitudActual) return;
    document.getElementById('cargando')?.classList.add('oculto');
    const btnBuscar = document.getElementById('btnBuscar');
    if (btnBuscar) btnBuscar.disabled = false;
    controladorConsulta = null;
}

function mostrarError(mensaje) {
    const error = document.getElementById('error');
    if (!error) return;
    error.textContent = mensaje;
    error.classList.remove('oculto');
}

function mostrarRespuesta(data) {
    const resultado = document.getElementById('resultado');
    const respuestaDiv = document.getElementById('respuesta');
    const estadoTexto = document.getElementById('estadoTexto');
    const iconoEstado = document.getElementById('iconoEstado');

    if (estadoTexto) estadoTexto.textContent = textoSeguro(data.estado, 'Respuesta del Asistente');
    if (iconoEstado) iconoEstado.textContent = textoSeguro(data.icono, '🚌');
    if (respuestaDiv) respuestaDiv.innerHTML = renderizarRespuesta(data);

    const respuestaVoz = textoSeguro(data.respuesta) || textoSeguro(respuestaDiv?.textContent);
    textoParaVoz = normalizarTextoParaVoz(respuestaVoz);
    document.getElementById('btnVoz')?.replaceChildren(document.createTextNode('🔊 Escuchar'));
    resultado?.classList.remove('oculto');
}

function normalizarTextoParaVoz(texto) {
    return texto
        .replace(/\*\*/g, '')
        .replace(/•/g, ', ')
        .replace(/➔|→/g, ' hacia ')
        .replace(/S\/\./g, 'soles ')
        .replace(/Cdra\./g, 'cuadra ')
        .replace(/Av\./g, 'avenida ')
        .replace(/Jr\./g, 'jirón ')
        .replace(/C\.P\./g, 'centro poblado ');
}

async function buscarRuta() {
    const input = document.getElementById('consulta');
    const consulta = input ? input.value.trim() : '';
    if (!consulta) return;

    const solicitud = prepararSolicitud();
    try {
        const res = await fetch('/api/consultar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ consulta }),
            signal: solicitud.signal
        });
        if (!res.ok) throw new Error('Error al conectar con el servidor');

        const data = await res.json();
        if (solicitud.id === solicitudActual) mostrarRespuesta(data || {});
    } catch (err) {
        if (err.name !== 'AbortError' && solicitud.id === solicitudActual) {
            mostrarError('Hubo un problema al conectar con el servidor.');
        }
    } finally {
        finalizarSolicitud(solicitud.id);
    }
}

// Modal para "Próxima combi"
function abrirModalRutas() {
    const modal = document.getElementById('modalRutas');
    if (!modal) return;
    modal.classList.remove('oculto');
    cargarRutasEnModal();
}

function cerrarModalRutas() {
    const modal = document.getElementById('modalRutas');
    const buscador = document.getElementById('modalRutasBuscador');
    modal?.classList.add('oculto');
    if (buscador) buscador.value = '';
    if (rutasModalCargadas) renderizarRutasModal(rutasModal);
}

async function cargarRutasEnModal() {
    const contenedor = document.getElementById('modalRutasLista');
    if (!contenedor) return;
    if (rutasModalCargadas) {
        renderizarRutasModal(rutasModal);
        return;
    }

    contenedor.innerHTML = '<p class="modal-mensaje">Cargando rutas...</p>';
    try {
        const res = await fetch('/api/rutas');
        if (!res.ok) throw new Error('No se pudieron cargar las rutas');
        const data = await res.json();
        rutasModal = comoLista(data?.rutas);
        rutasModalCargadas = true;
        renderizarRutasModal(rutasModal);
    } catch (err) {
        contenedor.innerHTML = '<p class="modal-mensaje modal-error">No se pudieron cargar las rutas.</p>';
    }
}

function filtrarRutasModal(e) {
    const busqueda = textoSeguro(e.target?.value).toLowerCase();
    if (!busqueda) {
        renderizarRutasModal(rutasModal);
        return;
    }

    const filtradas = rutasModal.filter(ruta => [
        ruta.codigo,
        ruta.codigo_ruta,
        ruta.nombre_comercial,
        ruta.razon_social,
        ruta.origen,
        ruta.destino,
        ruta.tipo,
        ruta.sentido
    ].some(valor => textoSeguro(valor).toLowerCase().includes(busqueda)));
    renderizarRutasModal(filtradas);
}

function renderizarRutasModal(rutas) {
    const contenedor = document.getElementById('modalRutasLista');
    if (!contenedor) return;
    const lista = comoLista(rutas);

    if (lista.length === 0) {
        contenedor.innerHTML = '<p class="modal-mensaje">No se encontraron rutas.</p>';
        return;
    }

    contenedor.innerHTML = lista.map(ruta => {
        const codigo = textoSeguro(ruta.codigo ?? ruta.codigo_ruta, 'Ruta');
        const sentido = textoSeguro(ruta.tipo ?? ruta.sentido);
        const nombre = textoSeguro(ruta.nombre_comercial ?? ruta.razon_social);
        const origen = textoSeguro(ruta.origen);
        const destino = textoSeguro(ruta.destino);
        const trayecto = origen && destino ? `${origen} → ${destino}` : origen || destino;
        const horario = formatearHorario(ruta);
        const frecuencia = conUnidad(ruta.frecuencia_min, 'min', 'Cada ');
        const detalles = [frecuencia, horario].filter(tieneValor).join(' · ');

        return `
            <div class="ruta-modal-item" role="button" tabindex="0"
                data-codigo="${escapaHtml(codigo)}" data-sentido="${escapaHtml(sentido)}">
                <div class="ruta-modal-top">
                    <span class="ruta-modal-codigo">${escapaHtml(codigo)}</span>
                    ${sentido ? `<span class="ruta-modal-sentido" data-sentido="${escapaHtml(sentido)}">${escapaHtml(sentido)}</span>` : ''}
                </div>
                ${nombre ? `<strong class="ruta-modal-nombre">${escapaHtml(nombre)}</strong>` : ''}
                ${trayecto ? `<span class="ruta-modal-trayecto">${escapaHtml(trayecto)}</span>` : ''}
                ${detalles ? `<span class="ruta-modal-detalles">${escapaHtml(detalles)}</span>` : ''}
            </div>
        `;
    }).join('');
}

function manejarSeleccionModal(e) {
    const item = e.target?.closest?.('.ruta-modal-item');
    if (!item || !document.getElementById('modalRutasLista')?.contains(item)) return;
    seleccionarRutaModal(item.dataset.codigo, item.dataset.sentido);
}

function seleccionarRutaModal(codigo, sentido) {
    if (!tieneValor(codigo)) return;
    cerrarModalRutas();
    const input = document.getElementById('consulta');
    if (input) input.value = '';
    consultarProximaUnidad(codigo, sentido);
}

async function consultarProximaUnidad(codigo, sentido) {
    const solicitud = prepararSolicitud();
    try {
        const res = await fetch('/api/proxima-unidad', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ruta_codigo: codigo }),
            signal: solicitud.signal
        });
        if (!res.ok) throw new Error('Error al conectar con el servidor');

        const data = await res.json();
        if (solicitud.id !== solicitudActual) return;

        const horario = formatearHorario(data || {});
        const proxima = conUnidad(data?.proximo_paso_min, 'min', '~');
        const partes = [`La ruta ${textoSeguro(codigo, 'seleccionada')}`];
        if (horario) partes.push(`opera de ${horario}`);
        if (proxima) partes.push(`la próxima salida teórica desde el inicio es en aproximadamente ${proxima}`);
        else if (tieneValor(data?.mensaje_servicio)) partes.push(textoSeguro(data.mensaje_servicio));

        mostrarRespuesta({
            estado: `Ruta ${textoSeguro(codigo)}${tieneValor(sentido) ? ` - ${textoSeguro(sentido)}` : ''}`,
            icono: '🚌',
            tipo: 'info',
            respuesta: `${partes.join('. ')}.`,
            resultados: [{ ...data, sentido }]
        });
    } catch (err) {
        if (err.name !== 'AbortError' && solicitud.id === solicitudActual) {
            mostrarError('No se pudo obtener la información de la ruta.');
        }
    } finally {
        finalizarSolicitud(solicitud.id);
    }
}

function leerRespuestaEnVozAlta() {
    if (!('speechSynthesis' in window)) {
        alert('Tu navegador no soporta síntesis de voz.');
        return;
    }

    const btnVoz = document.getElementById('btnVoz');
    if (reproduciendoVoz) {
        detenerVoz();
        return;
    }
    if (!textoParaVoz) return;

    window.speechSynthesis.cancel();
    window.speechSynthesis.resume();

    const utterance = new SpeechSynthesisUtterance(textoParaVoz);
    utterance.lang = 'es-PE';
    utterance.pitch = 1.15;
    utterance.rate = 0.98;

    const voces = window.speechSynthesis.getVoices();
    const vozAmigable = voces.find(v =>
        (v.lang.startsWith('es') || v.lang.includes('es-')) &&
        ['Sabina', 'Camila', 'Dalia', 'Natural', 'Online', 'Google', 'Paulina', 'Helena']
            .some(nombre => v.name.includes(nombre))
    ) || voces.find(v =>
        v.lang.includes('es-PE') || v.lang.includes('es-419') ||
        v.lang.includes('es-US') || v.lang.startsWith('es')
    );

    if (vozAmigable) utterance.voice = vozAmigable;

    utterance.onstart = () => {
        reproduciendoVoz = true;
        if (btnVoz) btnVoz.textContent = '⏹️ Detener';
    };
    utterance.onend = utterance.onerror = () => {
        reproduciendoVoz = false;
        if (btnVoz) btnVoz.textContent = '🔊 Escuchar';
    };

    window.speechSynthesis.speak(utterance);
}

function detenerVoz() {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    reproduciendoVoz = false;
    const btnVoz = document.getElementById('btnVoz');
    if (btnVoz) btnVoz.textContent = '🔊 Escuchar';
}

function copiarRespuesta() {
    if (!textoParaVoz || !navigator.clipboard) return;
    navigator.clipboard.writeText(textoParaVoz).then(() => {
        const btnCopiar = document.getElementById('btnCopiar');
        if (!btnCopiar) return;
        btnCopiar.textContent = '✓ ¡Copiado!';
        setTimeout(() => {
            btnCopiar.textContent = '📋 Copiar';
        }, 2000);
    });
}

function limpiarConsulta() {
    controladorConsulta?.abort();
    controladorConsulta = null;
    solicitudActual++;
    document.getElementById('cargando')?.classList.add('oculto');
    const btnBuscar = document.getElementById('btnBuscar');
    if (btnBuscar) btnBuscar.disabled = false;

    const input = document.getElementById('consulta');
    if (input) {
        input.value = '';
        input.focus();
    }
    document.getElementById('resultado')?.classList.add('oculto');
    document.getElementById('error')?.classList.add('oculto');
    detenerVoz();
}
