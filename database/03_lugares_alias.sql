USE asistente_rutas;

CREATE TABLE IF NOT EXISTS lugares_alias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    referencia_original VARCHAR(255) NOT NULL COMMENT 'Referencia coloquial tal como se escribe',
    referencia_normalizada VARCHAR(255) NOT NULL COMMENT 'Referencia normalizada para busqueda exacta',
    ubicacion_oficial VARCHAR(255) NOT NULL COMMENT 'Nombre oficial del punto en puntos_recorrido',
    ubicacion_normalizada VARCHAR(255) NOT NULL COMMENT 'Ubicacion normalizada para busqueda',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fuente VARCHAR(50) NULL COMMENT 'Origen del dato: EXCEL_DICCIONARIO, MANUAL',
    observaciones TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alias_referencia ON lugares_alias (referencia_normalizada);
CREATE INDEX idx_alias_ubicacion ON lugares_alias (ubicacion_normalizada);
