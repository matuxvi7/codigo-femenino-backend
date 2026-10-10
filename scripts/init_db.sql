-- Requiere MySQL 8.0 o posterior.
CREATE DATABASE IF NOT EXISTS codigo_femenino
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE codigo_femenino;

CREATE TABLE IF NOT EXISTS categories (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  slug VARCHAR(100) NOT NULL,
  name VARCHAR(120) NOT NULL,
  description TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_categories_slug (slug)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS articles (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  category_id BIGINT UNSIGNED NOT NULL,
  slug VARCHAR(180) NOT NULL,
  title VARCHAR(255) NOT NULL,
  excerpt TEXT NOT NULL,
  author VARCHAR(160) NOT NULL,
  published_at DATE NOT NULL,
  read_time_minutes TINYINT UNSIGNED NOT NULL,
  status ENUM('draft', 'published', 'archived') NOT NULL DEFAULT 'draft',
  image_url VARCHAR(500) NULL,
  image_public_id VARCHAR(255) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_articles_slug (slug),
  KEY idx_articles_category_status_date (category_id, status, published_at),
  CONSTRAINT fk_articles_category
    FOREIGN KEY (category_id) REFERENCES categories (id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT chk_articles_read_time CHECK (read_time_minutes > 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS article_sections (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  article_id BIGINT UNSIGNED NOT NULL,
  position SMALLINT UNSIGNED NOT NULL,
  heading VARCHAR(255) NULL,
  content TEXT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_article_sections_position (article_id, position),
  CONSTRAINT fk_article_sections_article
    FOREIGN KEY (article_id) REFERENCES articles (id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS lead_signups (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  email VARCHAR(254) NOT NULL,
  full_name VARCHAR(160) NULL,
  source ENUM('newsletter', 'guia_gratuita') NOT NULL,
  requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_lead_signups_email_source (email, source),
  KEY idx_lead_signups_requested_at (requested_at)
) ENGINE=InnoDB;

INSERT IGNORE INTO categories (slug, name, description) VALUES
  ('relaciones', 'Relaciones', 'Amor, pareja, amistad y vínculos sanos.'),
  ('autoestima', 'Autoestima', 'Confianza, límites y amor propio.'),
  ('psicologia', 'Psicología', 'Emociones y bienestar en el día a día.'),
  ('belleza', 'Belleza', 'Cuidado personal, piel y rutinas reales.');

INSERT IGNORE INTO articles
  (category_id, slug, title, excerpt, author, published_at, read_time_minutes, status)
VALUES
  ((SELECT id FROM categories WHERE slug = 'relaciones'), 'senales-relacion-sana',
   '7 señales de que estás en una relación sana',
   'Más allá de la química: los gestos cotidianos que revelan un vínculo que te hace crecer.',
   'Lucía Herrera', '2026-10-02', 6, 'published'),
  ((SELECT id FROM categories WHERE slug = 'autoestima'), 'poner-limites-sin-culpa',
   'Cómo poner límites sin sentir culpa',
   'Decir «no» también es una forma de cuidarte. Una guía práctica para empezar hoy.',
   'Valentina Ríos', '2026-09-28', 5, 'published'),
  ((SELECT id FROM categories WHERE slug = 'psicologia'), 'ansiedad-domingo',
   'La ansiedad del domingo: por qué ocurre y cómo calmarla',
   'Esa sensación de nudo en el estómago antes del lunes tiene explicación (y solución).',
   'Dra. Mariana Soto', '2026-09-21', 7, 'published'),
  ((SELECT id FROM categories WHERE slug = 'belleza'), 'rutina-piel-minimalista',
   'Rutina de piel minimalista: solo 4 pasos',
   'Menos productos, mejores resultados. Lo esencial para una piel cuidada sin complicarte.',
   'Camila Ortega', '2026-09-15', 4, 'published'),
  ((SELECT id FROM categories WHERE slug = 'relaciones'), 'amistades-adultas',
   'Hacer amigas en la adultez no es imposible',
   'Por qué cuesta más después de los 30 y estrategias reales para crear nuevos vínculos.',
   'Lucía Herrera', '2026-09-08', 5, 'published'),
  ((SELECT id FROM categories WHERE slug = 'autoestima'), 'dialogo-interno',
   'Cambia tu diálogo interno en 3 ejercicios',
   'Cómo te hablas importa. Herramientas sencillas para tratarte con más amabilidad.',
   'Valentina Ríos', '2026-09-01', 6, 'published');

INSERT IGNORE INTO article_sections (article_id, position, heading, content)
SELECT a.id, s.position, s.heading, s.content
FROM articles AS a
JOIN (
  SELECT 1 AS position, NULL AS heading, 'Una relación sana no se mide por la ausencia de conflictos, sino por la forma en que se resuelven. Estas son algunas señales que conviene observar.' AS content
  UNION ALL SELECT 2, '1. Puedes ser tú misma', 'No sientes la necesidad de esconder opiniones, gustos o emociones por miedo a la reacción de tu pareja.'
  UNION ALL SELECT 3, '2. Las discusiones no son batallas', 'Hay desacuerdos, pero el objetivo es entenderse, no ganar. Nadie humilla ni castiga con silencio.'
  UNION ALL SELECT 4, '3. Hay espacio individual', 'Cada uno mantiene amistades, aficiones y tiempo propio sin que eso se viva como una amenaza.'
  UNION ALL SELECT 5, '4. La confianza es la base', 'No hay revisiones del móvil ni interrogatorios. La transparencia surge de forma natural.'
  UNION ALL SELECT 6, NULL, 'Si reconoces la mayoría de estas señales, estás construyendo algo valioso. Si no, no es una sentencia: es una invitación a conversar.'
) AS s
WHERE a.slug = 'senales-relacion-sana';

INSERT IGNORE INTO article_sections (article_id, position, heading, content)
SELECT a.id, s.position, s.heading, s.content
FROM articles AS a
JOIN (
  SELECT 1 AS position, NULL AS heading, 'Muchas mujeres crecimos aprendiendo a complacer. Poner límites se siente incómodo al principio, pero es un músculo que se entrena.' AS content
  UNION ALL SELECT 2, 'Identifica lo que te drena', 'Anota durante una semana las situaciones que te dejan agotada o resentida. Ahí están tus límites pendientes.'
  UNION ALL SELECT 3, 'Usa frases simples', '«Esta vez no puedo», «Necesito pensarlo», «Prefiero no hablar de eso». No necesitas justificar en exceso.'
  UNION ALL SELECT 4, 'Acepta la incomodidad', 'La culpa inicial no significa que estés haciendo algo mal; significa que estás haciendo algo nuevo.'
) AS s
WHERE a.slug = 'poner-limites-sin-culpa';

INSERT IGNORE INTO article_sections (article_id, position, heading, content)
SELECT a.id, s.position, s.heading, s.content
FROM articles AS a
JOIN (
  SELECT 1 AS position, NULL AS heading, 'La llamada «ansiedad dominical» afecta a muchas personas que anticipan la semana laboral con preocupación.' AS content
  UNION ALL SELECT 2, '¿Por qué sucede?', 'El cerebro proyecta tareas pendientes y escenarios negativos. El descanso se interrumpe por la anticipación.'
  UNION ALL SELECT 3, 'Rituales que ayudan', 'Planifica el lunes el viernes, reserva una actividad agradable para el domingo por la tarde y limita el correo laboral.'
  UNION ALL SELECT 4, 'Cuándo pedir ayuda', 'Si la ansiedad es intensa o persistente, hablar con un profesional de salud mental es un acto de cuidado.'
) AS s
WHERE a.slug = 'ansiedad-domingo';

INSERT IGNORE INTO article_sections (article_id, position, heading, content)
SELECT a.id, s.position, s.heading, s.content
FROM articles AS a
JOIN (
  SELECT 1 AS position, NULL AS heading, 'No necesitas diez productos. Una rutina constante y sencilla supera a una complicada que abandonas.' AS content
  UNION ALL SELECT 2, '1. Limpieza suave', 'Un limpiador sin sulfatos por la noche; por la mañana basta con agua o un limpiador ligero.'
  UNION ALL SELECT 3, '2. Hidratación', 'Elige una crema según tu tipo de piel: gel para grasa, crema más rica para seca.'
  UNION ALL SELECT 4, '3. Protector solar', 'Todos los días, incluso nublado. Es el mejor antiedad que existe.'
  UNION ALL SELECT 5, '4. Un activo', 'Introduce uno solo (vitamina C, niacinamida o retinol) y dale tiempo antes de evaluar.'
) AS s
WHERE a.slug = 'rutina-piel-minimalista';

INSERT IGNORE INTO article_sections (article_id, position, heading, content)
SELECT a.id, s.position, s.heading, s.content
FROM articles AS a
JOIN (
  SELECT 1 AS position, NULL AS heading, 'Las amistades adultas requieren intención: ya no compartimos aula ni recreo.' AS content
  UNION ALL SELECT 2, 'Repetición y cercanía', 'Los vínculos nacen de ver a las mismas personas con frecuencia. Un taller o club semanal es ideal.'
  UNION ALL SELECT 3, 'Da el primer paso', 'Proponer un café puede parecer atrevido, pero la mayoría agradece la iniciativa.'
) AS s
WHERE a.slug = 'amistades-adultas';

INSERT IGNORE INTO article_sections (article_id, position, heading, content)
SELECT a.id, s.position, s.heading, s.content
FROM articles AS a
JOIN (
  SELECT 1 AS position, NULL AS heading, 'La voz crítica interior suele ser más dura que cualquier persona externa. Puedes entrenarla.' AS content
  UNION ALL SELECT 2, 'Ejercicio 1: la mejor amiga', 'Pregúntate: ¿le diría esto a mi mejor amiga? Si no, reformúlalo como se lo dirías a ella.'
  UNION ALL SELECT 3, 'Ejercicio 2: nombra al crítico', 'Ponerle nombre a esa voz crea distancia y le resta autoridad.'
  UNION ALL SELECT 4, 'Ejercicio 3: registro de logros', 'Cada noche anota tres cosas que hiciste bien, por pequeñas que sean.'
) AS s
WHERE a.slug = 'dialogo-interno';
