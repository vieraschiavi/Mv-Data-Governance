/*
 * MV Data Governance · Datos de reseñas.
 *
 * COMO AGREGAR RESEÑAS REALES:
 *   1. Sumá un objeto al array de abajo por cada reseña que recibas.
 *   2. Poné "example": false en las reseñas reales (así no muestran la
 *      etiqueta "Ejemplo").
 *   3. Borrá las de ejemplo cuando ya tengas reales.
 *
 * Campos: name (nombre o iniciales), role (cargo/empresa), rating (1 a 5),
 *         comment (texto), date (AAAA-MM), example (true = ilustrativa).
 *
 * Las reseñas marcadas con "example": true se muestran con una etiqueta
 * "Ejemplo" para no presentarlas como testimonios reales.
 */
window.MVDG_REVIEWS = [
  {
    name: "M. R.",
    role: "Responsable de datos · Cooperativa (UY)",
    rating: 5,
    comment: "En una semana teníamos el catálogo y el índice de calidad de toda la cartera. Lo mejor: los datos nunca salieron de nuestro servidor.",
    date: "2026-05",
    example: true
  },
  {
    name: "J. S.",
    role: "Gerente de BI · Retail (AR)",
    rating: 5,
    comment: "Lo conectamos al Power BI en una tarde. Dejamos de discutir qué número era el bueno; ahora todos miran el mismo dato gobernado.",
    date: "2026-04",
    example: true
  },
  {
    name: "A. C.",
    role: "Analista de datos · Salud (BR)",
    rating: 4,
    comment: "Muito bom para diagnóstico e catálogo. A detecção de PII nos poupou horas. Faltou só um conector nativo ao nosso data warehouse — que já está no roadmap.",
    date: "2026-04",
    example: true
  },
  {
    name: "L. F.",
    role: "CTO · Fintech (UY)",
    rating: 5,
    comment: "El auto-diagnóstico y que corra 100% local nos destrabó la aprobación de seguridad. Impecable para un piloto sin fricción.",
    date: "2026-03",
    example: true
  },
  {
    name: "P. G.",
    role: "Consultor de datos independiente",
    rating: 5,
    comment: "Llego a las reuniones con plataforma propia, en español, y cobro el servicio arriba. Cambió cómo vendo gobernanza.",
    date: "2026-03",
    example: true
  },
  {
    name: "R. D.",
    role: "Data steward · Manufactura (CL)",
    rating: 4,
    comment: "Las reglas de calidad y el mapa de calor son muy claros para mostrarle a la gerencia. Curva de aprendizaje mínima.",
    date: "2026-02",
    example: true
  }
];
