-- ============================================================
-- DESCRIPCIONES DE LUGARES (para responder "¿qué es X?")
-- ============================================================

INSERT INTO lugares_info (nombre_oficial, descripcion, tipo, categoria) VALUES
('Cuarto del Rescate', 'Sala donde fue ejecutado Atahualpa en 1533. Es uno de los principales atractivos turísticos históricos del centro de Cajamarca. Tiene una réplica de la marca que el inca dejó en la pared al intentar liberarse del rescate.', 'turistico', 'sitio_historico'),

('Cerro Santa Apolonia', 'Cerro mirador en el centro de Cajamarca, conocido también como "Silla del Inca" o "Rumitiana". Ofrece vistas panorámicas de la Plaza de Armas y la ciudad. Se accede por escalinatas de piedra.', 'turistico', 'mirador'),

('Complejo Arqueológico de Cumbemayo', 'Sitio arqueológico preinca a unos 20 km de Cajamarca. Famoso por sus canales de piedra tallada y petroglifos. Ideal para visitar en medio día.', 'turistico', 'arqueologico'),

('Ventanillas de Otuzco', 'Necrópolis preinca con tumbas excavadas en roca volcánica, ubicada en el distrito de Baños del Inca. Alberga cientos de tumbas con formas de ventanas alineadas en filas.', 'turistico', 'arqueologico'),

('Ventanillas de Combayo', 'Sitio arqueológico funerario similar a las Ventanillas de Otuzco, ubicado en el caserío de Combayo. Menos concurrido pero igualmente interesante.', 'turistico', 'arqueologico'),

('Granja Porcón', 'Comunidad agrícola y turística en las alturas de Cajamarca. Ofrece paseos por bosques de pinos, observación de animales y productos lácteos artesanales.', 'turistico', 'ecoturismo'),

('Alameda de los Incas', 'Complejo turístico recreacional en Cajamarca con áreas verdes, deportes y cultura. Forma parte del Qhapaq Ñan (Camino Inca).', 'turistico', 'recreacion'),

('Hacienda La Colpa', 'Hacienda ganadera tradicional del distrito de Jesús, conocida por su elaboración artesanal de queso y manjar blanco. Se puede visitar para conocer el proceso.', 'turistico', 'gastronomia'),

('Hacienda Tres Molinos', 'Hacienda histórica con molinos de piedra que aún funcionan. Ofrece tours guiados y degustación de productos lácteos.', 'turistico', 'gastronomia'),

('Cataratas de Llacanora', 'Caída de agua de aproximadamente 25 metros en el distrito de Llacanora. Se llega caminando unos 20 minutos desde el pueblo. Ideal para paseos familiares.', 'turistico', 'naturaleza'),

('Laguna de San Nicolás', 'Laguna de origen glaciar en la provincia de Namora, en el distrito de San Nicolás. Rodeada de pajonales y formaciones rocosas. A unas 2 horas de Cajamarca.', 'turistico', 'naturaleza'),

('Los Alpes', 'Fundo agroturístico a las afueras de Cajamarca. Ofrece experiencias rurales, observación de animales y caminatas en medio de la campiña.', 'turistico', 'ecoturismo'),

('Universidad Nacional de Cajamarca', 'Principal universidad pública de la región. Sede principal en Av. Atahualpa Km 3.5. Ofrece carreras de ingeniería, salud, educación y ciencias.', 'educativo', 'universidad'),

('Universidad Privada Antonio Guillermo Urrelo', 'Universidad privada ubicada en el centro de Cajamarca. Ofrece carreras en administración, derecho, ingeniería y salud.', 'educativo', 'universidad'),

('Universidad Privada del Norte', 'Sede cajamarquina de la UPN. Ubicada en una zona accesible de la ciudad. Ofrece carreras técnicas y universitarias en modalidad presencial.', 'educativo', 'universidad'),

('Instituto San Gabriel', 'Instituto educativo privado con sede en Cajamarca. Ofrece formación técnica en distintas especialidades.', 'educativo', 'instituto'),

('Instituto de Educación Superior Tecnológico Público Cajamarca', 'Conocido coloquialmente como "el Tecnológico". Instituto público con carreras técnicas en computación, electrónica, mecánica y más.', 'educativo', 'instituto'),

('Institución Educativa Emblemática San Ramón', 'Colegio emblemático conocido como "El Glorioso San Ramón" o "San Ramón". Uno de los más antiguos y tradicionales de Cajamarca.', 'educativo', 'colegio'),

('Colegio Nuestra Señora del Rosario', 'Colegio religioso parroquial histórico, conocido como "El Rosario". De orientación femenina tradicional.', 'educativo', 'colegio'),

('Catedral de Cajamarca', 'También conocida como Iglesia Santa Catalina o Iglesia Matriz Santa Catalina. Construida sobre el antiguo Templo del Sol. Es el principal templo católico de la ciudad y está en la Plaza de Armas.', 'religioso', 'catedral'),

('Iglesia de San Francisco', 'Conjunto conventual del siglo XVII. Alberga el Santuario de la Virgen de los Dolores, patrona de Cajamarca.', 'religioso', 'iglesia'),

('Conjunto Monumental de Belén', 'Complejo colonial del siglo XVIII que incluye la Iglesia de Belén, antiguos hospitales de hombres y mujeres, y el Museo Arqueológico y Etnográfico de Cajamarca.', 'religioso', 'museo'),

('Iglesia y Convento de La Recoleta', 'Iglesia y convento franciscano del siglo XVII. Reconocida por su arquitectura y colecciones artísticas coloniales.', 'religioso', 'convento'),

('Convento de las Concepcionistas Descalzas', 'Convento de clausura conocido popularmente como "La de las Monjas". Alberga una comunidad de religiosas de vida contemplativa.', 'religioso', 'convento'),

('Hospital Regional Docente Cajamarca', 'Principal hospital público de Cajamarca, conocido como "El Regional". Ubicado en la Vía de Evitamiento Norte. Atiende a toda la región.', 'salud', 'hospital_publico'),

('Hospital II-1 Cajamarca (EsSalud)', 'Hospital de EsSalud, conocido como "El Seguro". Atiende a asegurados del sistema de seguridad social.', 'salud', 'hospital_publico'),

('Clínica Limatambo Cajamarca', 'Clínica privada conocida como "Limatambo". Ofrece atención en distintas especialidades.', 'salud', 'clinica_privada'),

('Clínica San Lorenzo', 'Clínica privada de Cajamarca. Ofrece servicios de salud en varias especialidades.', 'salud', 'clinica_privada'),

('Mercado Central de Cajamarca', 'Principal mercado de abastos de Cajamarca, conocido como "El Central" o "El Mercado". Ofrece productos frescos, abarrotes, comida típica y artesanías.', 'comercial', 'mercado'),

('Mercado San Antonio', 'Mercado zonal del barrio San Antonio. Ofrece productos de abastos y comida regional.', 'comercial', 'mercado'),

('Mercado San Martín', 'Otro mercado zonal de Cajamarca, dedicado principalmente a productos frescos.', 'comercial', 'mercado'),

('Real Plaza Cajamarca', 'Centro comercial moderno conocido como "El Real Plaza". Ofrece tiendas por departamento,电影院, patio de comidas.', 'comercial', 'centro_comercial'),

('El Quinde Shopping Plaza', 'Centro comercial conocido como "El Quinde". Ubicado en la Av. Hoyos Rubio. Ofrece tiendas, restaurantes y entretenimiento.', 'comercial', 'centro_comercial'),

('Aeropuerto Mayor General FAP Armando Revoredo Iglesias', 'Aeropuerto de Cajamarca (código CJA). Recibe vuelos nacionales principalmente desde Lima. Ubicado en la Av. Hoyos Rubio, cerca del Real Plaza.', 'transporte', 'aeropuerto'),

('Plaza de Armas de Cajamarca', 'Plaza principal de la ciudad. Es el corazón histórico y social de Cajamarca. Aquí se produjo la captura de Atahualpa en 1532.', 'otro', 'plaza'),

('Plazuela Bolognesi', 'Plazuela tradicional del centro histórico. Es un punto clave de transbordo de combis y microbuses.', 'otro', 'plaza'),

('Óvalo del Inca', 'Importante óvalo en la ciudad. Funciona como nodo de varias rutas de transporte público.', 'otro', 'plaza'),

('Cinco Esquinas', 'Cruce importante en el sur del centro de Cajamarca. Punto de referencia para tomar rutas hacia distintos distritos.', 'otro', 'interseccion');
