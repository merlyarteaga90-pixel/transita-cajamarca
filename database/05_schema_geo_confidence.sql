-- Migración: calidad geográfica y puntos de abordaje
-- Idempotente: usa IF NOT EXISTS / ALTER TABLE ADD COLUMN

-- 1. Metadatos de confianza para coordenadas existentes
ALTER TABLE puntos_recorrido ADD COLUMN coord_fuente TEXT;
ALTER TABLE puntos_recorrido ADD COLUMN coord_confianza TEXT CHECK (coord_confianza IN ('ALTA', 'MEDIA', 'BAJA'));
ALTER TABLE puntos_recorrido ADD COLUMN coord_precision_m INT;
ALTER TABLE puntos_recorrido ADD COLUMN coord_verificado_at TIMESTAMP;

-- Índice para filtrar por confianza
CREATE INDEX IF NOT EXISTS idx_puntos_confianza ON puntos_recorrido (coord_confianza);

-- 2. Tabla de puntos de abordaje (paraderos y referenciales)
CREATE TABLE IF NOT EXISTS puntos_abordaje (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(255) NOT NULL,
    latitud DECIMAL(10, 7),
    longitud DECIMAL(10, 7),
    tipo TEXT NOT NULL CHECK (tipo IN ('VERIFICADO', 'REFERENCIAL')),
    fuente TEXT,
    fuente_url TEXT,
    confianza TEXT CHECK (confianza IN ('ALTA', 'MEDIA', 'BAJA')),
    fecha_verificacion TIMESTAMP,
    notas TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_abordaje_activo ON puntos_abordaje (activo);
CREATE INDEX IF NOT EXISTS idx_abordaje_tipo ON puntos_abordaje (tipo);

-- 3. Relación sentido -> puntos de abordaje
CREATE TABLE IF NOT EXISTS sentido_puntos_abordaje (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sentido_id INT NOT NULL,
    punto_abordaje_id INT NOT NULL,
    orden INT NOT NULL,
    notas TEXT,
    FOREIGN KEY (sentido_id) REFERENCES sentidos(id) ON DELETE CASCADE,
    FOREIGN KEY (punto_abordaje_id) REFERENCES puntos_abordaje(id) ON DELETE CASCADE,
    UNIQUE (sentido_id, punto_abordaje_id, orden)
);

CREATE INDEX IF NOT EXISTS idx_spa_sentido ON sentido_puntos_abordaje (sentido_id);

-- 4. Caché de hallazgos externos (no oficiales)
CREATE TABLE IF NOT EXISTS hallazgos_externos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_hash VARCHAR(64) NOT NULL,
    origen_normalizado VARCHAR(255),
    destino_normalizado VARCHAR(255),
    proveedor TEXT NOT NULL,
    resultado_json TEXT NOT NULL,
    fuentes_json TEXT,
    consultado_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expira_at TIMESTAMP NOT NULL,
    estado TEXT NOT NULL DEFAULT 'CANDIDATO' CHECK (estado IN ('CANDIDATO', 'VALIDADO', 'RECHAZADO', 'EXPIRADO')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hallazgos_hash ON hallazgos_externos (query_hash);
CREATE INDEX IF NOT EXISTS idx_hallazgos_expira ON hallazgos_externos (expira_at);
CREATE INDEX IF NOT EXISTS idx_hallazgos_estado ON hallazgos_externos (estado);
