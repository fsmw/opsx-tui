# add-local-change-metadata

## Why

Los cambios OpenSpec carecen de metadata operativa local: prioridad, tags, favorito, notas y orden visual. El usuario no puede marcar un cambio como importante, agruparlos por tag, ni mantener notas sin modificar los artefactos OpenSpec.

OPSX TUI necesita estos datos para el tablero Kanban (ordenamiento, filtros, indicadores visuales) y para la gestión de bloqueos (blocked_reason) sin contaminar la fuente de verdad metodológica.

## What

Agregar un sistema de metadata sidecar para cambios OpenSpec, almacenado fuera de los artefactos canónicos. Cada cambio obtiene un modelo `ChangeMetadata` con:

- **priority**: entero 0-4 (normal, low, medium, high, urgent)
- **tags**: lista de strings
- **favorite**: booleano
- **blocked_reason**: string opcional
- **notes**: string opcional
- **order**: entero para orden visual

La metadata se persiste en un archivo TOML por proyecto en el directorio de datos de OPSX TUI (platformdirs), se carga durante el workspace scan y se fusiona en el modelo `Change` como campo opcional.

Se agrega un modal de edición en la vista de cambios para modificar metadata, con atajos rápidos (favorito, prioridad) y un formulario completo para tags, notas y blocked_reason.

## Capabilities

- **ChangeMetadata model**: modelo Pydantic frozen con los 6 campos permitidos, validación de rango priority y tags únicas.
- **MetadataStore Protocol**: puerto en domain/ports.py con load_all/save/delete.
- **TomlMetadataStore**: adaptador infrastructure que persiste en `~/.local/share/opsx-tui/metadata/<project-hash>.toml`.
- **Fusión en Change**: campo `metadata: ChangeMetadata | None` en el modelo Change, poblado durante workspace scan.
- **Indicadores en ChangesView**: priority color, favorite star, tags truncadas en el listado.
- **Metadata en Overview tab**: sección de metadata en el panel de detalle.
- **MetadataEditModal**: modal con campos editables y atajos (f=favorite, 1-4=priority).
- **Orden visual persistente**: reordenamiento de la lista según campo `order`.

## Impact

- Change model crece con un campo opcional (no rompe serialización existente).
- workspace_reader.py necesita un MetadataStore opcional o un nuevo servicio de fusión.
- platformdirs se usa ya para config — mismo patrón.
- No hay cambios en OpenSpec — la metadata es puramente OPSX TUI.
- Las vistas existentes (Overview, changes list) se benefician sin cambios arquitectónicos profundos.
