# D&D Companion — Alcance y contexto del proyecto (Fase 0)

> Documento de contexto para Claude Code. Resume todo lo decidido en la planeación.
> Léelo completo antes de proponer o escribir código. Si algo contradice este documento, pregunta antes de actuar.

## 1. Visión general

Aplicación web para gestionar campañas de Dungeons & Dragons (5e), construida sobre la **API pública de D&D 5e** (https://www.dnd5eapi.co), con:

- Un **backend propio en Python (FastAPI)** que consume y cachea la API de D&D y expone la lógica de negocio.
- **Base de datos relacional (PostgreSQL)** para usuarios, campañas, personajes y sesiones.
- **Base de datos vectorial (pgvector, dentro del mismo Postgres)** para búsqueda semántica y RAG.
- **Funcionalidades de IA** usando la API de Claude (modelo Haiku 5.5) con control estricto de costos.
- Frontend en Angular o React (se define en Fase 3).

### Objetivos personales del autor

- Practicar **Python y FastAPI** en un proyecto real (el frontend es su fortaleza; el backend es lo que quiere ejercitar).
- Practicar **modelado relacional** y **bases de datos vectoriales**.
- Aprender a integrar IA en producto con **costos controlados**.
- Construir algo escalable: la v1 es la base de un producto más grande.

## 2. Alcance de la versión 1 (lo que ENTRA)

### Usuarios y cuentas

- Registro y autenticación básica (email + contraseña, JWT).
- Dos roles por campaña: **Dungeon Master (DM)** y **Jugador**. Un mismo usuario puede ser DM en una campaña y jugador en otra.

### Personajes jugadores (PJ)

- Cada usuario crea sus propios personajes.
- Las opciones (raza, clase, trasfondo, hechizos, equipo) salen de la **API de D&D 5e**; el personaje resultante (nombre, nivel, atributos, PV, inventario) es del usuario y vive en nuestra base.
- Hoja de personaje editable.

### Campañas y vinculación (sin tiempo real)

- El DM crea una campaña y obtiene un **código de invitación**.
- El jugador ingresa el código y vincula uno de sus personajes a la campaña.
- El DM ve los personajes vinculados a su campaña. **No hay juego en vivo ni multijugador en tiempo real**; es gestión compartida desde cuentas separadas.

### Sesiones y notas

- El DM registra sesiones de la campaña con notas de lo ocurrido.
- Estas notas alimentan la base vectorial (memoria de la campaña para la IA).

### Monstruos

- Consulta y selección de monstruos desde la API (ya vienen completos con estadísticas).
- Un DM puede armar **encuentros** referenciando monstruos de la API. No se "construyen" monstruos en v1.

### Funcionalidades de IA (3)

1. **Consultor de reglas**: responde preguntas sobre reglas, hechizos, clases, etc., con RAG sobre el contenido de la API indexado en pgvector.
2. **Sugerencia de encuentros**: dado el nivel del grupo, número de PJ y ambiente de la sesión, propone encuentros balanceados con monstruos reales de la API. Usa búsqueda semántica sobre monstruos indexados (ej. "algo aterrador para una cripta, nivel 3").
3. **Semilla de historia**: a partir de tono, ambientación, nivel y cantidad de jugadores, genera un punto de partida (gancho inicial, villano, 2–3 lugares, conflicto). Se guarda como semilla editable de la campaña. **No genera la historia completa.**

## 3. Fuera de alcance de la v1 (NO entra)

- Multijugador en tiempo real (tiradas en vivo, chat, WebSockets).
- Generación de mapas o imágenes.
- Narración completa de Dungeon Master por IA.
- Lectura de hoja de personaje desde foto (OCR con visión). → Candidata a **v2**.
- Combate automatizado / tracker de iniciativa.
- Pagos o suscripciones.

## 4. Stack técnico

| Capa | Decisión |
|---|---|
| Lenguaje backend | Python 3.12+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x (async) + Alembic para migraciones |
| Base de datos | PostgreSQL 16 + extensión pgvector |
| Fuente de datos D&D | API pública D&D 5e (dnd5eapi.co), cacheada localmente |
| IA | API de Claude — modelo `claude-haiku-5-5` para todo en v1 |
| Embeddings | Por definir (opción económica; evaluar Voyage o alternativa) |
| Auth | JWT |
| Frontend | Angular o React (Fase 3) |
| Infra desarrollo | Docker Compose (Postgres + backend) |

### Cuenta de IA

- La API de Claude se usa desde una **cuenta de API separada** (Console), no desde la suscripción personal de Claude.ai. Se cobra por tokens.
- Para desarrollo local se puede usar Ollama o nivel gratis de otro proveedor; en producción, Haiku 5.5.

## 5. Modelo de datos (borrador inicial)

Tablas principales (a refinar en Fase 0 / Fase 1):

- `users` — id, email, password_hash, display_name, created_at
- `campaigns` — id, dm_user_id (FK users), name, description, setting, tone, invite_code (único), story_seed (texto/JSON), created_at
- `characters` — id, owner_user_id (FK users), name, level, race_index, class_index, background_index, abilities (JSON), hp, inventory (JSON), spells (JSON), created_at
- `campaign_characters` — campaign_id (FK), character_id (FK), joined_at — **tabla intermedia** de vinculación
- `sessions` — id, campaign_id (FK), title, session_date, notes (texto)
- `encounters` — id, campaign_id (FK), session_id (FK nullable), name, difficulty, created_at
- `encounter_monsters` — encounter_id (FK), monster_index (índice de la API), quantity
- `dnd_api_cache` — endpoint, index, payload (JSONB), fetched_at — caché de la API de D&D
- `embeddings` — id, source_type (rule | monster | session_note), source_id, content, embedding (vector) — para RAG
- `ai_usage` — id, user_id (FK), feature (rules | encounter | story), tokens_in, tokens_out, cost_usd, created_at — control de cuotas
- `ai_response_cache` — hash de la pregunta normalizada, respuesta, created_at

Nota: `race_index`, `class_index`, `monster_index` referencian los `index` de la API de D&D 5e, no tablas propias.

## 6. Control de costos de IA (obligatorio desde Fase 2)

- **Cuotas por usuario** guardadas en `ai_usage` (ej. 10 consultas de reglas/día, 3 semillas de historia por campaña).
- **Rate limiting** en FastAPI.
- **Caché de respuestas** (`ai_response_cache`) para preguntas repetidas; evaluar detección de preguntas semánticamente iguales vía embeddings.
- **Prompt caching** de Claude para instrucciones de sistema y reglas que se repiten.
- **Límites** de `max_tokens` por funcionalidad; la semilla de historia es la más costosa, mantenerla acotada.
- **Tope de gasto** y alertas configurados en la consola del proveedor (arrancar con ~5 USD de crédito y tope mensual de ~10 USD).
- Registrar `tokens_in`/`tokens_out` de cada llamada.

### Referencia de precios (nov 2026, por millón de tokens)

- Claude Haiku 5.5: ~$0.10 entrada / ~$0.50 salida (prompts ≤100K); entrada cacheada ~$0.01.
- Una consulta de reglas típica (~1.000 in / ~300 out) ≈ $0.00025.

## 7. Plan por fases

| Fase | Contenido | Resultado esperado |
|---|---|---|
| **0 — Planeación** | Este documento, modelo de datos, decisiones técnicas | Alcance cerrado |
| **1 — Backend sin IA** | FastAPI + Postgres + SQLAlchemy, cliente y caché de la API de D&D, auth, CRUD de campañas/personajes, códigos de invitación, sesiones, encuentros | API funcional de punta a punta, probada |
| **2 — IA mínima** | Consultor de reglas, sugerencia de encuentros, semilla de historia; pgvector + RAG; cuotas, caché y control de costos | Las 3 funciones de IA operando con límites |
| **3 — Frontend y despliegue** | UI en Angular/React, despliegue | v1 usable públicamente |

Cada fase debe terminar con algo que **funcione de punta a punta**.

## 8. Estado actual

- Fase 0 en curso. Alcance de v1 definido (secciones 2 y 3).
- Pendiente: cerrar el modelo de datos definitivo y elegir proveedor de embeddings.
- Siguiente paso: iniciar Fase 1 (estructura del proyecto FastAPI + Docker Compose + migración inicial).

## 9. Instrucciones para Claude Code

- Respeta el alcance de la sección 2 y 3; no agregues funcionalidades fuera de v1 sin preguntar.
- El autor está **aprendiendo Python/FastAPI**: prefiere código claro, idiomático y explicado antes que atajos ingeniosos. Explica brevemente decisiones de diseño relevantes.
- Trabaja fase por fase. No introduzcas IA ni pgvector en la Fase 1.
- Usa tipado (type hints), Pydantic v2 para esquemas, y pruebas con pytest.
- Toda llamada a IA debe pasar por una capa que registre uso y aplique cuotas.
