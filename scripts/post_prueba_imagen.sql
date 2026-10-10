-- Post de prueba con imagen de Cloudinary ya subida y verificada.
-- Ejecutar: mysql -u <usuario> -p codigo_femenino < scripts/post_prueba_imagen.sql

USE codigo_femenino;

INSERT INTO articles
  (category_id, slug, title, excerpt, author, published_at, read_time_minutes, status, image_url, image_public_id)
VALUES
  ((SELECT id FROM categories WHERE slug = 'autoestima'),
   'ritual-manana-cafe',
   'El ritual del café de la mañana: un momento solo para vos',
   'Antes de que empiece el día, regalate diez minutos. Cómo convertir el primer café en un acto de cuidado propio.',
   'Redacción Código Femenino', '2026-10-10', 4, 'published',
   'https://res.cloudinary.com/gvamujrm/image/upload/v1791619066/codigo-femenino/articles/ldh50yehwczwvxcsw872.jpg',
   'codigo-femenino/articles/ldh50yehwczwvxcsw872');

INSERT INTO article_sections (article_id, position, heading, content)
SELECT a.id, s.position, s.heading, s.content
FROM articles AS a
JOIN (
  SELECT 1 AS position, NULL AS heading, 'No se trata del café en sí, sino del gesto: sentarte, respirar y empezar el día sin apuro. Ese pequeño ritual marca el tono de todo lo que viene después.' AS content
  UNION ALL SELECT 2, 'Crear el espacio', 'Elegí un rincón con luz natural, dejá el teléfono en otra habitación y usá tu taza favorita. Los detalles convierten un hábito en un ritual.'
  UNION ALL SELECT 3, 'Diez minutos alcanzan', 'No necesitás una hora. Diez minutos de presencia plena antes de las obligaciones reducen la sensación de ir corriendo detrás del día.'
) AS s
WHERE a.slug = 'ritual-manana-cafe';
