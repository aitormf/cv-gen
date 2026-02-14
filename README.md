# cv-gen

Generador de CVs profesionales en PDF desde archivos Markdown. No es una simple conversion MD a PDF: el programa aplica plantillas con disenos profesionales distintos, generando documentos visualmente atractivos listos para enviar.

Disponible como **CLI** y como **aplicacion web** con previsualizacion en vivo.

## Instalacion

Requiere Python 3.10+, [uv](https://docs.astral.sh/uv/) y [Node.js](https://nodejs.org/) + [pnpm](https://pnpm.io/) (para la web):

```bash
git clone <repo-url> && cd cv-gen
cp .env.example .env          # configurar puertos y CORS si es necesario
uv sync
cd frontend && pnpm install
```

### Dependencias del sistema

WeasyPrint necesita algunas librerias nativas para la generacion de PDF:

- **Arch Linux**: `pacman -S pango cairo gdk-pixbuf2`
- **Ubuntu/Debian**: `apt install libpango-1.0-0 libcairo2 libgdk-pixbuf-2.0-0`
- **macOS**: `brew install pango cairo gdk-pixbuf`

## Configuracion

Toda la configuracion de puertos y URLs se gestiona desde el fichero `.env` en la raiz del proyecto. Copia `.env.example` como punto de partida:

```bash
cp .env.example .env
```

| Variable         | Default                    | Descripcion                                  |
|------------------|----------------------------|----------------------------------------------|
| `BACKEND_PORT`   | `8000`                     | Puerto del servidor FastAPI                  |
| `FRONTEND_PORT`  | `5173`                     | Puerto del dev server de Vite                |
| `CORS_ORIGIN`    | `http://localhost:5173`    | Origen permitido por CORS (URL del frontend) |

## Aplicacion web

La forma mas rapida de arrancar todo:

```bash
./start.sh    # Lee .env, instala deps, arranca backend y frontend
./stop.sh     # Para ambos servidores
```

Abre http://localhost:5173 (o el puerto configurado en `.env`), pega tu Markdown en el editor de la izquierda, selecciona una plantilla y pulsa **Generar PDF**. El PDF real (generado por WeasyPrint) se muestra en el visor integrado. Pulsa **Descargar PDF** para guardarlo.

### Arranque manual (desarrollo)

```bash
# Terminal 1 — Backend FastAPI (lee CORS_ORIGIN del .env)
uv run uvicorn cv_gen.api:app --reload --port 8000

# Terminal 2 — Frontend Svelte (proxy apunta al backend)
VITE_BACKEND_URL=http://localhost:8000 pnpm --dir frontend dev --port 5173
```

### Produccion (servidor unico)

```bash
cd frontend && pnpm build
uv run uvicorn cv_gen.api:app --host 0.0.0.0 --port 8000
```

En modo produccion, FastAPI sirve el frontend compilado directamente desde `frontend/dist/`. No hace falta Node en el servidor. Ajusta `CORS_ORIGIN` en `.env` al dominio real si es necesario.

### API REST

| Metodo | Ruta              | Body                                     | Response          |
|--------|-------------------|------------------------------------------|-------------------|
| `GET`  | `/api/templates`  | —                                        | `{"templates": [...], "default": "modern"}` |
| `POST` | `/api/pdf`        | `{"markdown": "...", "template": "modern"}` | `application/pdf` |

## CLI

```bash
# Generar PDF con plantilla modern (por defecto)
uv run cv-gen resume.md

# Elegir plantilla y nombre de salida
uv run cv-gen resume.md -t minimal -o mi_cv.pdf

# Listar plantillas disponibles
uv run cv-gen --list-templates

# Generar y abrir el PDF directamente
uv run cv-gen resume.md --preview

# Exportar HTML (util para depuracion)
uv run cv-gen resume.md --html
```

### Opciones

| Opcion              | Descripcion                                |
|---------------------|--------------------------------------------|
| `-t`, `--template`  | Nombre de la plantilla (default: `modern`) |
| `-o`, `--output`    | Ruta del archivo de salida                 |
| `--list-templates`  | Lista las plantillas disponibles           |
| `--preview`         | Genera el PDF y lo abre con el visor del sistema |
| `--html`            | Exporta HTML en lugar de PDF               |

## Formato del archivo Markdown

El CV se escribe en Markdown con metadatos YAML en el frontmatter:

```markdown
---
name: Juan Perez Garcia
title: Senior Software Engineer
email: juan@example.com
phone: "+34 612 345 678"
location: Madrid, Espana
linkedin: linkedin.com/in/juanperez
github: github.com/juanperez
website: juanperez.dev
photo: foto.jpg          # opcional
---

## Perfil Profesional
Texto libre describiendo tu perfil...

## Experiencia Laboral
### Senior Developer | Google | 2020 - Presente
- Logro 1
- Logro 2

## Educacion
### Master en Informatica | UPM | 2017

## Habilidades
- Python, Go, Rust
- Docker, Kubernetes

## Idiomas
- Espanol (Nativo)
- Ingles (C1)
```

### Campos del frontmatter

| Campo      | Requerido | Descripcion              |
|------------|-----------|--------------------------|
| `name`     | Si        | Nombre completo          |
| `title`    | Si        | Titulo profesional       |
| `email`    | No        | Correo electronico       |
| `phone`    | No        | Telefono                 |
| `location` | No        | Ciudad, pais             |
| `linkedin` | No        | URL de LinkedIn          |
| `github`   | No        | URL de GitHub            |
| `website`  | No        | Sitio web personal       |
| `photo`    | No        | Ruta a la foto (solo plantilla modern) |

### Deteccion automatica de secciones

El parser detecta automaticamente el tipo de cada seccion (`## Heading`) por keywords en multiples idiomas (ES, EN, FR, DE). Esto permite que las plantillas de dos columnas separen las secciones entre sidebar y area principal.

| Tipo           | Keywords reconocidos                                      |
|----------------|-----------------------------------------------------------|
| profile        | perfil, profile, resumen, summary, sobre mi, about        |
| experience     | experiencia, experience, trabajo, work, erfahrung         |
| education      | educacion, formacion, education, formation, ausbildung    |
| skills         | habilidades, skills, competencias, tecnologias, tools     |
| languages      | idiomas, languages, sprachen, langues                     |
| projects       | proyectos, projects, projekte, portfolio                  |
| certifications | certificaciones, certifications, cursos, courses          |

## Plantillas

### Modern (default)

Diseno de dos columnas con sidebar oscuro y area principal blanca.

- **Layout**: Sidebar izquierdo (30%) con fondo `#2c3e50` + area principal (70%) blanca
- **Colores**: Texto blanco en sidebar, acento `#3498db` (azul) para titulos e iconos
- **Tipografia**: Fira Sans (sans-serif moderna)
- **Sidebar**: Foto circular (opcional), nombre, titulo, contacto con iconos Unicode, secciones de Skills/Idiomas/Certificaciones
- **Area principal**: Perfil, Experiencia, Educacion, Proyectos
- **Ideal para**: Tech, startups, roles modernos

### Minimal

Diseno de una sola columna con margenes generosos y maxima limpieza visual.

- **Layout**: Una columna, margenes de 30mm
- **Colores**: Solo `#333` para cuerpo y `#000` para nombre. Sin bordes, sin fondos
- **Tipografia**: Fira Sans Light (300) para cuerpo, Regular (400) para titulos. Nombre 32pt
- **Cabecera**: Nombre grande y fino, titulo en uppercase con tracking amplio, contacto en linea con separadores middot
- **Ideal para**: Diseno, UX, roles que valoran la limpieza

## Estructura del proyecto

```
cv-gen/
├── .env                     # Configuracion local (no versionado)
├── .env.example             # Plantilla de configuracion
├── pyproject.toml
├── start.sh                 # Arranca backend + frontend
├── stop.sh                  # Para ambos servidores
├── src/
│   └── cv_gen/
│       ├── __init__.py
│       ├── api.py            # FastAPI web app
│       ├── cli.py            # Entry point Click
│       ├── parser.py         # Markdown + frontmatter → CVData
│       ├── models.py         # Dataclasses: ContactInfo, Section, CVData
│       ├── renderer.py       # Jinja2 + WeasyPrint → PDF
│       └── templates/
│           ├── modern/
│           │   ├── template.html
│           │   └── style.css
│           └── minimal/
│               ├── template.html
│               └── style.css
├── frontend/                 # Svelte + Vite
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.svelte
│       ├── components/
│       │   ├── MarkdownEditor.svelte
│       │   ├── TemplateSelector.svelte
│       │   └── Preview.svelte
│       └── lib/
│           └── api.ts
├── examples/
│   └── sample_cv.md
└── tests/
    ├── test_api.py
    ├── test_parser.py
    ├── test_renderer.py
    └── test_cli.py
```

### Arquitectura interna

- **api.py**: FastAPI app con endpoints REST para templates, preview HTML y generacion de PDF. Sirve el frontend compilado en produccion.
- **models.py**: Dataclasses `ContactInfo`, `Section` y `CVData`. `CVData` tiene metodos `sidebar_sections()` y `main_sections()` para que las plantillas de dos columnas separen el contenido.
- **parser.py**: Extrae el frontmatter YAML con `python-frontmatter`, divide el cuerpo por `## ` (h2), detecta el tipo de cada seccion por keywords multilenguaje, y renderiza cada bloque a HTML con `python-markdown`.
- **renderer.py**: Carga la plantilla Jinja2 desde `templates/{nombre}/`, embebe el CSS en un `<style>` para evitar problemas de rutas con WeasyPrint, y genera el PDF.
- **cli.py**: Interfaz Click con todas las opciones documentadas arriba.
- **frontend/**: Aplicacion Svelte 5 con editor Markdown, selector de plantillas y preview en iframe con debounce de 500ms.

## Anadir nuevas plantillas

Crear un directorio en `src/cv_gen/templates/` con dos archivos:

```
src/cv_gen/templates/mi_plantilla/
├── template.html
└── style.css
```

La plantilla Jinja2 recibe estas variables:

| Variable           | Tipo              | Descripcion                          |
|--------------------|-------------------|--------------------------------------|
| `cv`               | `CVData`          | Objeto completo del CV               |
| `contact`          | `ContactInfo`     | Datos de contacto del frontmatter    |
| `sections`         | `list[Section]`   | Todas las secciones                  |
| `sidebar_sections` | `list[Section]`   | Secciones tipo skills/languages/certs |
| `main_sections`    | `list[Section]`   | Secciones tipo profile/experience/etc |
| `css`              | `str`             | Contenido de style.css               |

La nueva plantilla aparecera automaticamente en `--list-templates`.

## Tests

```bash
uv run pytest -v
```

## Stack tecnologico

**Backend**:
- **FastAPI + Uvicorn** — API REST y servidor de produccion
- **Jinja2 + WeasyPrint** — HTML/CSS como sistema de plantillas, PDF de alta calidad
- **python-markdown** — Parseo de Markdown con extensiones (tables, smarty, sane_lists)
- **python-frontmatter** — Extraccion de metadatos YAML
- **Click** — Interfaz CLI
- **uv** — Gestor de paquetes y entornos virtuales

**Frontend**:
- **Svelte 5** — UI reactiva con runes
- **Vite** — Bundler y dev server con proxy al backend
- **pnpm** — Gestor de paquetes Node
