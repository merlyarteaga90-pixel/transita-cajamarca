export function LoadingState() {
  return (
    <section id="cargando" className="cargando">
      <div className="spinner-ia"></div>
      <div className="cargando-info">
        <strong>Consultando itinerario...</strong>
        <span>Consultando rutas y horarios...</span>
      </div>
    </section>
  );
}
