PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS empresas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_comercial VARCHAR(100),
    razon_social VARCHAR(255) NOT NULL,
    ruc CHAR(11) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rutas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(150),
    empresa_id INTEGER,
    frecuencia_general_min INT,
    horario_inicio TIME,
    horario_fin TIME,
    flota_maxima INT,
    reten_unidades INT,
    velocidad_promedio_kmh DECIMAL(6, 2),
    pasajeros_por_vuelta INT,
    ipk DECIMAL(7, 2),
    tarifa_general DECIMAL(6, 2),
    tarifa_medio_pasaje DECIMAL(6, 2),
    tarifa_es_provisional BOOLEAN NOT NULL DEFAULT FALSE,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS sentidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ruta_id INT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('IDA', 'VUELTA')),
    origen VARCHAR(150),
    destino VARCHAR(150),
    distancia_km DECIMAL(7, 2),
    tiempo_total_min INT,
    frecuencia_override_min INT,
    horario_inicio_override TIME,
    horario_fin_override TIME,
    FOREIGN KEY (ruta_id) REFERENCES rutas(id) ON DELETE CASCADE,
    UNIQUE (ruta_id, tipo)
);

CREATE TABLE IF NOT EXISTS puntos_recorrido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sentido_id INT NOT NULL,
    orden INT NOT NULL,
    nombre_original VARCHAR(255) NOT NULL,
    nombre_normalizado VARCHAR(255) NOT NULL,
    tipo_via VARCHAR(50),
    cuadra VARCHAR(50),
    distrito VARCHAR(100),
    latitud DECIMAL(10, 7),
    longitud DECIMAL(10, 7),
    es_paradero BOOLEAN NOT NULL DEFAULT FALSE,
    tiempo_desde_anterior_min DECIMAL(6, 2),
    distancia_desde_anterior_km DECIMAL(7, 3),
    FOREIGN KEY (sentido_id) REFERENCES sentidos(id) ON DELETE CASCADE,
    UNIQUE (sentido_id, orden)
);

CREATE TABLE IF NOT EXISTS lugares_alias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referencia_original VARCHAR(255) NOT NULL,
    referencia_normalizada VARCHAR(255) NOT NULL,
    ubicacion_oficial VARCHAR(255) NOT NULL,
    ubicacion_normalizada VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_puntos_nombre_normalizado ON puntos_recorrido (nombre_normalizado);
CREATE INDEX IF NOT EXISTS idx_puntos_sentido ON puntos_recorrido (sentido_id);
CREATE INDEX IF NOT EXISTS idx_rutas_codigo ON rutas (codigo);
CREATE INDEX IF NOT EXISTS idx_empresas_ruc ON empresas (ruc);
CREATE INDEX IF NOT EXISTS idx_alias_referencia ON lugares_alias (referencia_normalizada);
CREATE INDEX IF NOT EXISTS idx_alias_ubicacion ON lugares_alias (ubicacion_normalizada);
