export function LoadingState() {
  return (
    <section id="cargando" className="cargando">
      <div className="spinner-ia"></div>
      <div className="cargando-info">
        <strong>Analizando tu consulta...</strong>
        <span>Clasificando intención y buscando rutas...</span>
      </div>
    </section>
  );
}
