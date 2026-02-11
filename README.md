# cv-gen

Generador de CVs profesionales en PDF desde archivos Markdown. No es una simple conversion MD a PDF: el programa aplica plantillas con disenos profesionales distintos, generando documentos visualmente atractivos listos para enviar.

## Instalacion

Requiere Python 3.10+ y [uv](https://docs.astral.sh/uv/):

```bash
git clone <repo-url> && cd cv-gen
uv sync
```

### Dependencias del sistema

WeasyPrint necesita algunas librerias nativas para la generacion de PDF:

- **Arch Linux**: `pacman -S pango cairo gdk-pixbuf2`
- **Ubuntu/Debian**: `apt install libpango-1.0-0 libcairo2 libgdk-pixbuf-2.0-0`
- **macOS**: `brew install pango cairo gdk-pixbuf`

## Uso

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
├── pyproject.toml
├── src/
│   └── cv_gen/
│       ├── __init__.py
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
├── examples/
│   └── sample_cv.md
└── tests/
    ├── test_parser.py
    ├── test_renderer.py
    └── test_cli.py
```

### Arquitectura interna

- **models.py**: Dataclasses `ContactInfo`, `Section` y `CVData`. `CVData` tiene metodos `sidebar_sections()` y `main_sections()` para que las plantillas de dos columnas separen el contenido.
- **parser.py**: Extrae el frontmatter YAML con `python-frontmatter`, divide el cuerpo por `## ` (h2), detecta el tipo de cada seccion por keywords multilenguaje, y renderiza cada bloque a HTML con `python-markdown`.
- **renderer.py**: Carga la plantilla Jinja2 desde `templates/{nombre}/`, embebe el CSS en un `<style>` para evitar problemas de rutas con WeasyPrint, y genera el PDF.
- **cli.py**: Interfaz Click con todas las opciones documentadas arriba.

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

- **uv** — Gestor de paquetes y entornos virtuales
- **Jinja2 + WeasyPrint** — HTML/CSS como sistema de plantillas, PDF de alta calidad
- **python-markdown** — Parseo de Markdown con extensiones (tables, smarty, sane_lists)
- **python-frontmatter** — Extraccion de metadatos YAML
- **Click** — Interfaz CLI
