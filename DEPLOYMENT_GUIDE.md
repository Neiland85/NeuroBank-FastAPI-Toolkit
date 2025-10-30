# Guía de despliegue y consolidación de migraciones (Alembic)

## Objetivo

Consolidar múltiples migraciones de normalización/conversión de timestamps y merges en un único head estable, reduciendo complejidad y riesgos en despliegues.

## Requisitos previos

- Base de datos de staging disponible.
- Copia de seguridad reciente de staging y producción.
- Entorno virtual y variables de entorno configuradas.

## Comprobación de estado actual

1. Verificar heads actuales:

```bash
alembic heads
```

1. Revisar árbol de migraciones:

```bash
alembic history --verbose
```

Si aparecen múltiples heads (p.ej., migraciones repetidas de normalización de timestamps y archivos de "merge_heads"), proceder con el plan controlado.

## Plan recomendado (rama de mantenimiento)

1. Crear rama de mantenimiento:

```bash
git checkout -b chore/alembic-squash-timestamps
```

1. Asegurar que la base de datos de desarrollo/staging está en el último head actual:

```bash
alembic upgrade head
```

1. Crear una migración de squash que represente el estado actual del modelo:

```bash
alembic revision --autogenerate -m "squash: normalize timestamps and merge heads"
```

1. Editar la nueva revisión para convertirla en punto de consolidación:

- Establecer `down_revision = None` en el archivo recién creado.
- Confirmar que `upgrade()` refleja completamente el esquema actual.

1. Opcional (limpieza): eliminar o archivar migraciones antiguas relacionadas con normalización/merges que quedan obsoletas en esta rama. Alternativamente, mantenerlas pero no usarlas en nuevos entornos.

1. En bases de datos ya migradas (staging), marcar el estado como el del nuevo squash sin volver a aplicar cambios:

```bash
alembic stamp <nueva_revision_squash>
```

1. En entornos limpios (nuevas instalaciones), aplicar directamente la migración squash:

```bash
alembic upgrade head
```

1. Verificación en staging:

- Ejecutar pruebas de aplicación.
- Validar integridad de datos y consultas sobre columnas de timestamp.
- Auditar logs de migración.

1. Merge a la rama principal sólo tras validar en staging y con ventana de mantenimiento planificada.

## Alternativa: unir heads sin squash

Si sólo hay múltiples heads pero no se desea squash todavía:

```bash
alembic merge -m "merge heads" <head1> <head2> [<headN>]
```

Verificar luego con `alembic heads` que sólo queda un head.

## Consideraciones

- No ejecutar squash directamente en producción sin validar en staging.
- Realizar backup antes de aplicar merges o stamps.
- Documentar hash de la nueva revisión squash y comunicarlo al equipo.
