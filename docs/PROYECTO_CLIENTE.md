# 📁 Proyecto por cliente — guardar cada etapa sin perder nada

Hasta acá, la ficha de cada empresa (pestaña **🏢 Empresas**) guardaba solo
los datos de contacto, BI, restricción de TI y madurez. El **trabajo de
gobierno** en sí — el dataset que cargaste y perfilaste, el reporte de
duplicados/MDM, el escaneo de Power BI o Tableau, el paquete de tablas para
BI — vivía únicamente en memoria y se perdía al cerrar el programa o al
recargar la página.

La pestaña **📁 Proyecto** resuelve eso: cada cliente tiene su propio
proyecto en disco, y adentro guardás **etapas**. Cada etapa es una foto con
nombre de una o más tablas de tu trabajo, más notas y la fecha. Así podés ir
guardando cada paso (catalogar → medir → deduplicar → escanear el modelo de
BI → publicar) sin perder nada, y volver a abrirlo cuando quieras.

## Cómo se usa

1. **Elegí el cliente** (se toma de la pestaña 🏢 Empresas — primero creá la
   empresa ahí).
2. **Guardá la etapa actual**: el programa te muestra lo que trabajaste en
   esta sesión y que está disponible para capturar:
   - el **dataset que perfilaste** en 🔎 Mis datos (archivo o base de datos),
   - el **reporte de duplicados / MDM**,
   - el **escaneo de Power BI** (catálogo, calidad, linaje),
   - el **escaneo de Tableau** (catálogo, calidad, linaje),
   - el **paquete de gobierno** (catálogo, reglas, glosario, linaje,
     políticas, KPIs — las 9 tablas).

   Marcás lo que quieras incluir, le ponés un nombre (ej. "Catálogo inicial",
   "Después de corregir") y notas, y **Guardar etapa**.
3. **Etapas guardadas**: aparecen de la más nueva a la más vieja. Cada una se
   puede **ver/descargar** (previsualiza cada tabla y la baja en CSV) o
   **eliminar**.
4. **Respaldar / restaurar**: descargás **todo el proyecto del cliente en un
   ZIP** (para respaldarlo o llevarlo a otra máquina) y lo restaurás cuando
   quieras.

## Dónde se guarda

Todo es **100% local**, en el equipo del usuario, en la misma carpeta donde
ya viven las fichas de clientes y las conexiones:

```
<data_dir>/clientes/<client_id>/etapas/<stage_id>/
    manifest.json          ← nombre, tipo, notas, fecha, tablas, meta
    <tabla>.parquet|.csv   ← una por cada DataFrame de la etapa
```

`<data_dir>` es `~/.mv_data_governance` (o lo que indique la variable de
entorno `MVDG_DATA_DIR`). Las tablas se guardan en **Parquet** (preserva los
tipos de dato); si no está disponible el motor de Parquet, caen
automáticamente a **CSV**. Nada viaja a internet — es un almacenamiento de
archivos en tu propia máquina, igual que cualquier programa de escritorio.

## Respaldo y portabilidad

Hay dos formas de no perder nada:

- **Copiar la carpeta** `<data_dir>/clientes/` a otro lugar (un disco
  externo, un recurso de red) — es todo lo que hace falta.
- Usar el botón **⬇️ Descargar proyecto (ZIP)** de cada cliente y guardarlo
  donde quieras; para restaurarlo, **Restaurar desde un ZIP**. Al importar,
  podés **sumar** las etapas del ZIP a las actuales o **reemplazar** las
  actuales por las del ZIP.

## Verificación

`python -m mvdg.selfcheck` incluye el chequeo **"Proyecto por cliente"** que,
sobre una carpeta temporal, confirma el ciclo completo: guardar una etapa →
volver a cargarla (con las tablas idénticas) → exportar el proyecto a ZIP →
borrarlo → importarlo de vuelta desde el ZIP. La suite de tests
(`tests/test_core.py`) cubre además el orden de las etapas, el resumen del
proyecto, el borrado y el rechazo de etapas sin nombre o sin tablas.
