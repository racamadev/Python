# EA Technology KB

Aplicación de escritorio para la gestión, seguimiento y análisis de
tecnologías y productos de arquitectura empresarial, bajo un modelo
**Maestro-Detalle**.

Construida con **Python 3.10+**, **PySide6**, **MongoDB** y arquitectura por
capas (Presentation → Business → Data → Infrastructure).

## Arquitectura

```
Presentation Layer   →  views/ (MainWindow, tabs, widgets, dialogs) + controllers/
Business Layer       →  services/ (validación, reglas de negocio, orquestación)
Data Layer           →  repositories/ (Repository Pattern sobre PyMongo)
Infrastructure Layer →  infrastructure/ (MongoDB, logging, configuración)
```

Cada capa depende únicamente de la capa inferior: las vistas llaman a los
controladores, los controladores a los servicios, los servicios a los
repositorios y los repositorios a MongoDB. Las excepciones de negocio
(`src/exceptions`) se propagan hacia arriba y los controladores las traducen
en mensajes amigables mediante señales Qt (`error_occurred`,
`success_message`, `data_changed`).

## Estructura de carpetas

```
ea_tecnology_kb/
├── main.py                    # Composition root / entry point
├── .env                       # Configuración de entorno
├── requirements.txt
├── pytest.ini / .coveragerc
├── scripts/
│   └── init_db.py             # Crea colecciones e índices en MongoDB
└── src/
    ├── controllers/           # TechnologyController, NotesController, ...
    ├── services/               # TechnologyService, NotesService, ExportService, ...
    ├── repositories/           # BaseRepository + repos por entidad
    ├── models/                 # Technology, Note, Alternative, Link (dataclasses)
    ├── views/
    │   ├── main_window.py
    │   ├── tabs/                # Las 5 pestañas de la aplicación
    │   ├── widgets/              # SearchBar, ColumnFilterBar, GenericTableModel
    │   └── dialogs/               # Confirmaciones y mensajes
    ├── infrastructure/
    │   ├── database/              # MongoConnection, DatabaseManager
    │   ├── logging/                 # RotatingFileHandler config
    │   └── config/                   # Config (.env loader)
    ├── utils/                    # validators, date_helpers, excel_helpers, constants
    ├── exceptions/                # Jerarquía de excepciones de la aplicación
    ├── resources/                  # icons/, themes/
    ├── exports/                     # Salida de exportaciones Excel
    ├── logs/                        # app.log (rotativo)
    └── tests/                       # pytest + mongomock
```

## Modelo de datos (MongoDB)

Base de datos: **ea_tecnology_kb**

### `technologies` (maestro)

| Campo | Tipo | Notas |
|---|---|---|
| tech_code | string | Obligatorio, único |
| tech_date | datetime | |
| tech_type | string | |
| tech_product | string | Obligatorio |
| tech_std | string | `Yes` / `No` |
| tech_classif | string | |
| tech_lifecycle | string | |
| tech_start_date | datetime | |
| tech_divest_date | datetime | |
| tech_end_date | datetime | |
| tech_trend | string | `Yes` / `No` |

### `tech_notes`, `tech_alternatives`, `tech_links` (detalle)

Relacionadas mediante `technology_id` (ObjectId), según el esquema descrito
en el enunciado del proyecto.

### Índices

* `technologies.tech_code` — único
* `technologies.tech_product`, `technologies.tech_type`
* `tech_notes.technology_id`, `tech_alternatives.technology_id`, `tech_links.technology_id`

Se crean automáticamente al iniciar la aplicación (`main.py`) o ejecutando
`python scripts/init_db.py`.

## Requisitos previos

* Python 3.10+
* Una instancia de MongoDB accesible (local o remota)

## Instalación

```bash
cd ea_tecnology_kb
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # ajustar credenciales/host si es necesario
```

## Ejecución

```bash
python scripts/init_db.py   # crea colecciones e índices (idempotente)
python main.py               # inicia la aplicación
```

## Funcionalidades por pestaña

1. **Technologies List** — tabla con búsqueda global, filtros por columna,
   ordenamiento por encabezado, paginación (50 registros/página) y
   exportación a Excel (Maestro + 3 detalles en un único archivo).
2. **Technology Master** — formulario vertical agrupado, validación en
   tiempo real, Add/Update/Delete/Save/Cancel.
3. **Technology Notes** — lista + formulario (nota multilínea, 6 líneas
   visibles), CRUD, búsqueda y ordenamiento.
4. **Technology Alternatives** — lista + formulario, CRUD, búsqueda y
   ordenamiento.
5. **Technology Links** — lista + formulario, botón **Open Link** que valida
   la URL y la abre con `webbrowser.open`.

Las pestañas 3-5 operan sobre la tecnología seleccionada en la pestaña 1 o 2.

## Configuración (.env)

```
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DATABASE=ea_tecnology_kb

APP_THEME=dark
LOG_LEVEL=INFO
```

Ver `.env.example` para la lista completa de variables soportadas
(pool de conexiones, reintentos de reconexión, tamaño de página, etc.).

## Logging

Configurado en `src/infrastructure/logging/logger_config.py` con un
`RotatingFileHandler` que escribe en `src/logs/app.log` (rotación por
tamaño, configurable vía `LOG_MAX_BYTES` / `LOG_BACKUP_COUNT`), además de
salida por consola.

## Seguridad

* Sanitización de entradas de texto (`src/utils/validators.py`).
* Reconexión automática a MongoDB con backoff exponencial
  (`MongoConnection`).
* Prevención de duplicados vía índice único en `tech_code` + manejo de
  `DuplicateKeyError` traducido a `DuplicateRecordError`.
* Validación de URLs antes de invocar `webbrowser.open`.

## Testing

```bash
pytest
```

Cobertura mínima configurada en `pytest.ini` / `.coveragerc`: **80%** sobre
`services`, `repositories`, `models`, `utils` y `exceptions` (la capa de
presentación y los adaptadores de infraestructura que requieren un servidor
MongoDB real quedan fuera del cálculo de cobertura unitaria, siguiendo el
alcance solicitado: *Services, Repositories, Validators*).

Los tests usan **mongomock** para simular MongoDB sin necesidad de una
instancia real.

## Exportación a Excel

`ExportService` (pandas + openpyxl) genera un único `.xlsx` con 4 hojas
(`Technologies`, `Notes`, `Alternatives`, `Links`), cada una con:

* Encabezado con estilo y congelado (freeze panes).
* Autofiltro.
* Ancho de columna automático.
* Formato de fecha `YYYY-MM-DD`.
