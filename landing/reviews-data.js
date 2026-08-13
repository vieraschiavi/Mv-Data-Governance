// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * MV Data Governance · Datos de reseñas.
 *
 * ESTÁ VACÍO A PROPÓSITO: todavía no hay clientes con el producto en
 * producción, así que no hay ninguna reseña real que mostrar.
 *
 * Antes acá vivían 6 reseñas inventadas ("M. R. · Cooperativa (UY)",
 * "J. S. · Retail (AR)"…) marcadas con `example: true`. Se mostraban con
 * una etiqueta "Ejemplo", pero la landing calculaba con ellas un PROMEDIO
 * DE ESTRELLAS y un contador de reseñas: un visitante veía "4,8 · 6
 * reseñas" derivado enteramente de testimonios que no existen. La etiqueta
 * no alcanza cuando el agregado se presenta como un dato.
 *
 * COMO AGREGAR RESEÑAS REALES:
 *   1. Sumá un objeto al array por cada reseña que te dé un cliente real.
 *   2. Pedile permiso antes de publicar su nombre o el de su empresa.
 *
 * Campos: name (nombre o iniciales), role (cargo/empresa), rating (1 a 5),
 *         comment (texto), date (AAAA-MM).
 *
 * No vuelvas a poner reseñas de ejemplo acá: `tests/test_resenas.py` falla
 * si aparece alguna, justamente para que esto no se repita sin querer.
 */
window.MVDG_REVIEWS = [];
