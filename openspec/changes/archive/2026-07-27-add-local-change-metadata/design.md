# add-local-change-metadata — Design

## D1 — Storage location: platformdirs (no OpenSpec)

La metadata vive en `~/.local/share/opsx-tui/metadata/<project-hash>.toml`. Esto garantiza que OPSX TUI nunca escribe dentro de `openspec/` ni modifica artefactos canónicos.

Alternativa descartada: sidecar dentro de cada change dir (`.opsx-meta.toml`). Riesgo de interferencia con OpenSpec y loss al mover directorios.

## D2 — Format: TOML

Consistente con la configuración existente (`config.toml`). `tomllib` ya disponible sin dependencias extra. JSON descartado por inconsistencia con el ecosistema del proyecto.

## D3 — File structure

```toml
[change-name]
priority = 3          # 0-4
tags = ["frontend", "urgent"]
favorite = true
blocked_reason = ""
notes = "Needs design review first"
order = 1
```

Una sola sección por cambio. Si un cambio no aparece en el archivo, metadata = None.

## D4 — Project identity

Hash SHA256 del `openspec_root` absoluto → primeros 12 chars como key. Determinista, portable, no colisiona.

## D5 — ChangeMetadata model

```python
class Priority(IntEnum):
    NORMAL = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class ChangeMetadata(BaseModel, frozen=True):
    priority: Priority = Priority.NORMAL
    tags: tuple[str, ...] = ()
    favorite: bool = False
    blocked_reason: str | None = None
    notes: str | None = None
    order: int = 0
```

Frozen para consistencia con el resto del dominio. Priority como IntEnum para type safety.

Se agrega campo opcional al modelo Change:
```python
class Change(BaseModel, frozen=True):
    ...
    metadata: ChangeMetadata | None = None
```

## D6 — MetadataStore Protocol + TomlMetadataStore

Protocol en `domain/ports.py`:

```python
class MetadataStore(Protocol):
    def load_all(self) -> dict[str, ChangeMetadata]: ...
    def save(self, change_name: str, metadata: ChangeMetadata) -> None: ...
    def delete(self, change_name: str) -> None: ...
```

`TomlMetadataStore(project_key: str)` en `infrastructure/metadata_store.py`:
- `load_all`: lee el TOML sidecar, parsea cada sección como ChangeMetadata
- `save`: mergea in-memory y escribe TOML completo
- `delete`: remueve sección y escribe

El store recibe `project_key` en el constructor, resuelto desde el `openspec_root` una sola vez.

## D7 — Fusión con Change

La fusión ocurre en `application/change_metadata_service.py` como un paso posterior al workspace scan:

```python
def merge_metadata(
    snapshot: WorkspaceSnapshot, metadata: dict[str, ChangeMetadata]
) -> WorkspaceSnapshot:
    def _merge(changes: tuple[Change, ...]) -> tuple[Change, ...]:
        return tuple(
            change.model_copy(update={"metadata": metadata.get(change.name)})
            for change in changes
        )
    return snapshot.model_copy(update={
        "active_changes": _merge(snapshot.active_changes),
        "archived_changes": _merge(snapshot.archived_changes),
    })
```

Es puro, determinista, no toca el filesystem. Se llama desde el Container o desde el WorkspaceWatcher callback.

Alternativa descartada: carga dentro de FilesystemWorkspaceReader. El reader no debe tener dependencias de persistencia OPSX.

## D8 — UI indicators in ChangesView

El `_format_change_item` se extiende para mostrar:
- `[H]` prefix para high priority (≥3), `[U]` para urgent (4)
- `★` para favorito
- Primer tag truncado a 10 chars si hay tags
- Orden: lista ordenada por `metadata.order` ascendente, después por nombre

```python
def _format_change_item(change: Change) -> str:
    prefix = ""
    meta = change.metadata
    if meta:
        if meta.priority >= Priority.HIGH:
            prefix += f"[{'U' if meta.priority == 4 else 'H'}]"
        if meta.favorite:
            prefix += "★ "
        if meta.tags:
            prefix += f"[{meta.tags[0][:10]}] "
    ...
```

## D9 — Overview tab metadata section

Nueva sección en `_overview_content` después de Progress:

```python
if change.metadata:
    m = change.metadata
    lines.append(f"**Priority:** {m.priority.name}")
    if m.favorite: lines.append("**Favorite:** ★")
    if m.tags: lines.append(f"**Tags:** {', '.join(m.tags)}")
    if m.blocked_reason: lines.append(f"**Blocked:** {m.blocked_reason}")
    if m.notes: lines.append(f"**Notes:** {m.notes}")
```

## D10 — MetadataEditModal

Modal tipo Screen con:
- Inputs editables para tags (comma-separated), notes, blocked_reason
- Botones de toggle para priority (0-4 cycler) y favorite
- Atajos: `f` toggle favorite, `1-4` set priority
- Guardar al confirmar → llama a MetadataStore.save
- Cancelar con Escape descarta cambios
- Refresca ChangesView después de guardar

## D11 — Ordering

El campo `order` no tiene semántica de arrastrar (drag-drop es complejo en TUI). Se edita numéricamente desde el modal o se asigna automáticamente al cambiar prioridad a favorito. La vista de cambios ordena por `(metadata.order if metadata else 0, change.name)` ascendente.

## D12 — No new dependencies

`tomllib` está en stdlib ≥3.11. `platformdirs` ya es dependencia existente. `hashlib` es stdlib. No se agregan nuevos paquetes.
