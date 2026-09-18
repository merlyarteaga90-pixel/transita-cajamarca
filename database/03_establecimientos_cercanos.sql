-- ============================================================
-- ESTABLECIMIENTOS CERCANOS A LUGARES REFERENCIA
-- (Para responder "¿qué hay cerca de X?")
-- ============================================================

-- ---- Cerca de Plaza de Armas de Cajamarca ----
INSERT INTO establecimientos_cercanos (lugar_referencia, nombre, tipo, direccion) VALUES
('Plaza de Armas de Cajamarca', 'Restaurante Salas', 'restaurante', 'Jr. Amalia Puga 637, media cuadra de la Plaza'),
('Plaza de Armas de Cajamarca', 'El Zarco', 'restaurante', 'Jr. Cruz de Piedra 639 / Jr. Amalia Puga 637'),
('Plaza de Armas de Cajamarca', 'Heladería Holanda', 'otro', 'Frente a la Plaza de Armas'),
('Plaza de Armas de Cajamarca', 'Interbank', 'banco', 'Jr. Amalia Puga 661'),
('Plaza de Armas de Cajamarca', 'Banco de Crédito del Perú (BCP)', 'banco', 'Jr. El Comercio 675'),
('Plaza de Armas de Cajamarca', 'BBVA', 'banco', 'Calle 2, esquina Jr. José Sucre - Plaza de Armas');

-- ---- Cerca de Av. Perú ----
INSERT INTO establecimientos_cercanos (lugar_referencia, nombre, tipo, direccion) VALUES
('Av. Perú', 'Churrasquería / Pollería', 'restaurante', 'Av. Perú 891, esquina con Cruz de Piedra'),
('Av. Perú', 'Agente Western Union', 'otro', 'Av. Perú 844, Barrio La Esperanza'),
('Av. Perú', 'UPN Emprendimiento', 'tienda', 'Av. Perú 2934, altura con Universitaria'),
('Av. Perú', 'BBVA Agencia', 'banco', 'Jr. Tarapacá 719-721, cerca de Av. Perú');

-- ---- Cerca de Av. Manco Cápac ----
INSERT INTO establecimientos_cercanos (lugar_referencia, nombre, tipo, direccion) VALUES
('Av. Manco Cápac', 'Mifarma', 'farmacia', 'Av. Manco Cápac 500-524, Tienda 6'),
('Av. Manco Cápac', 'Complejo Turístico Baños del Inca', 'otro', 'Av. Manco Cápac, Baños del Inca'),
('Av. Manco Cápac', 'Apart-Hoteles Turísticos', 'otro', 'Av. Manco Cápac 108, Baños del Inca');

-- ---- Cerca de Jr. Amazonas / Mercado Central ----
INSERT INTO establecimientos_cercanos (lugar_referencia, nombre, tipo, direccion) VALUES
('Jr. Amazonas', 'Mercado Central de Cajamarca', 'otro', 'Jr. Amazonas 679, entre Apurímac y Amazonas'),
('Jr. Amazonas', 'Inkafarma', 'farmacia', 'Jr. Amazonas 580, La Merced'),
('Jr. Amazonas', 'Juguería Mercado Central', 'restaurante', 'Jr. Amazonas 511'),
('Jr. Amazonas', 'Puestos de artesanía y ropa', 'tienda', 'Jr. Amazonas, alrededores del mercado'),
('Mercado Central de Cajamarca', 'Quesos Shugur', 'tienda', 'Jr. Apurímac, calle lateral al mercado'),
('Mercado Central de Cajamarca', 'Puestos de comida típica', 'restaurante', 'Jr. Apurímac 914, Puesto 119'),
('Mercado Central de Cajamarca', 'Farmacia / Botica', 'farmacia', 'Zona Jr. Apurímac / Jr. Amazonas'),
('Mercado Central de Cajamarca', 'Mercado San Antonio', 'otro', 'Jr. José Sabogal, a pocas cuadras');

-- ---- Cerca de Universidad Nacional de Cajamarca ----
INSERT INTO establecimientos_cercanos (lugar_referencia, nombre, tipo, direccion) VALUES
('Universidad Nacional de Cajamarca', 'Paskana Restaurante', 'restaurante', 'Av. Atahualpa Km 2, Carretera a Baños del Inca'),
('Universidad Nacional de Cajamarca', 'Restaurante autorizado (Pueblo Libre)', 'restaurante', 'Av. Atahualpa 201, Barrio Pueblo Libre'),
('Universidad Nacional de Cajamarca', 'Fotocopiadoras y librerías universitarias', 'tienda', 'Av. Atahualpa, frente a sede central'),
('Universidad Nacional de Cajamarca', 'Puestos de comida estudiantil', 'restaurante', 'Alrededores de Av. Atahualpa, cerca del campus');

-- ---- Cerca de Complejo Turístico Baños del Inca ----
INSERT INTO establecimientos_cercanos (lugar_referencia, nombre, tipo, direccion) VALUES
('Complejo Turístico Baños del Inca', 'Hotel & Spa Laguna Seca', 'otro', 'Jr. La Retama 600, Urb. Laguna Seca'),
('Complejo Turístico Baños del Inca', 'Hotel Tartar', 'restaurante', 'Av. Vía Evitamiento 1611-1709, camino a Baños del Inca'),
('Complejo Turístico Baños del Inca', 'Hotel Baños del Inca E.I.R.L.', 'otro', 'Jr. Sinchi Roca 139, Baños del Inca'),
('Complejo Turístico Baños del Inca', 'Casona del Inca', 'restaurante', 'Baños del Inca, zona del complejo'),
('Complejo Turístico Baños del Inca', 'Restaurantes regionales y vegetarianos', 'restaurante', 'Perímetro del Complejo Turístico');
