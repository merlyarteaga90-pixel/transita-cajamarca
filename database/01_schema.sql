CREATE DATABASE IF NOT EXISTS asistente_rutas CHARACTER
SET
    utf8mb4 COLLATE utf8mb4_unicode_ci;

USE asistente_rutas;

CREATE TABLE
    IF NOT EXISTS empresas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre_comercial VARCHAR(100) NULL,
        razon_social VARCHAR(255) NOT NULL,
        ruc CHAR(11) NOT NULL UNIQUE,
        observaciones TEXT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE
    IF NOT EXISTS rutas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        codigo VARCHAR(30) NOT NULL UNIQUE COMMENT 'Codigo interno: R-01, R-02',
        nombre VARCHAR(150) NULL COMMENT 'Nombre visible: Ruta 01, Ruta 02',
        empresa_id INT NULL,
        frecuencia_general_min INT NULL,
        horario_inicio TIME NULL,
        horario_fin TIME NULL,
        flota_maxima INT NULL,
        reten_unidades INT NULL,
        velocidad_promedio_kmh DECIMAL(6, 2) NULL,
        pasajeros_por_vuelta INT NULL,
        ipk DECIMAL(7, 2) NULL,
        tarifa_general DECIMAL(6, 2) NULL,
        tarifa_medio_pasaje DECIMAL(6, 2) NULL,
        tarifa_es_provisional BOOLEAN NOT NULL DEFAULT FALSE,
        activo BOOLEAN NOT NULL DEFAULT TRUE,
        fuente VARCHAR(50) NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_ruta_empresa FOREIGN KEY (empresa_id) REFERENCES empresas (id) ON DELETE SET NULL
    );

CREATE TABLE
    IF NOT EXISTS sentidos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ruta_id INT NOT NULL,
        tipo ENUM ('IDA', 'VUELTA') NOT NULL,
        origen VARCHAR(150) NULL,
        destino VARCHAR(150) NULL,
        distancia_km DECIMAL(7, 2) NULL,
        tiempo_total_min INT NULL,
        frecuencia_override_min INT NULL COMMENT 'Si es NULL, se usa la frecuencia_general de la ruta',
        horario_inicio_override TIME NULL COMMENT 'Si es NULL, se usa el horario de la ruta',
        horario_fin_override TIME NULL,
        UNIQUE KEY uq_ruta_tipo (ruta_id, tipo),
        CONSTRAINT fk_sentido_ruta FOREIGN KEY (ruta_id) REFERENCES rutas (id) ON DELETE CASCADE
    );

CREATE TABLE
    IF NOT EXISTS puntos_recorrido (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sentido_id INT NOT NULL,
        orden INT NOT NULL,
        nombre_original VARCHAR(255) NOT NULL COMMENT 'Valor tal cual viene del Excel',
        nombre_normalizado VARCHAR(255) NOT NULL COMMENT 'Valor normalizado para busqueda',
        tipo_via VARCHAR(50) NULL,
        cuadra VARCHAR(50) NULL,
        distrito VARCHAR(100) NULL,
        latitud DECIMAL(10, 7) NULL,
        longitud DECIMAL(10, 7) NULL,
        es_paradero BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Sin uso en la primera version',
        tiempo_desde_anterior_min DECIMAL(6, 2) NULL,
        distancia_desde_anterior_km DECIMAL(7, 3) NULL,
        UNIQUE KEY uq_sentido_orden (sentido_id, orden),
        CONSTRAINT fk_punto_sentido FOREIGN KEY (sentido_id) REFERENCES sentidos (id) ON DELETE CASCADE
    );

CREATE INDEX idx_puntos_nombre_normalizado ON puntos_recorrido (nombre_normalizado);

CREATE INDEX idx_puntos_sentido ON puntos_recorrido (sentido_id);

CREATE INDEX idx_rutas_codigo ON rutas (codigo);

CREATE INDEX idx_empresas_ruc ON empresas (ruc);