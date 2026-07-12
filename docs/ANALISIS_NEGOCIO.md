# 💼 MV Data Governance · Análisis de negocio

> **Documento interno.** Los números de facturación y ganancia son
> **proyecciones modeladas** con supuestos explícitos, no resultados medidos
> ni promesas. Sirven para dimensionar el negocio y fijar precios, no para
> presentar como ingresos reales. Moneda: dólares estadounidenses (USD).

---

## 1. Precios de las versiones

| Versión | Precio | Para quién | Qué incluye |
|---|---|---|---|
| **Gratis** | **US$ 0** (para siempre) | Prueba y evaluación | Demo 100% operativa con datos sintéticos, 3 idiomas, exportación CSV/Excel/JSON, programa `.bat`/web. Es el **imán de leads**. |
| **Licencia PC** | **US$ 149** (pago único) | PyMEs, consultores, 1 equipo | Programa completo sin límite de tiempo, conectores a BD, fichas de empresas, exportación a BI, actualizaciones menores. **Se descarga pagando por MercadoPago.** |
| **Professional** | **US$ 390 / mes** | Equipos de datos (hasta 25 usuarios) | API REST para BI ilimitada, instalador `.exe`, alertas de calidad y SLA, soporte prioritario. |
| **Enterprise** | **desde US$ 1.900 / mes** (a medida) | Organizaciones reguladas | On-premise / nube privada, SSO y auditoría, cumplimiento (GDPR/LGPD/Ley 18.331 UY), integraciones a medida, usuarios ilimitados. |

### Créditos (opcional, comprables por MercadoPago)

Monetización adicional de bajo compromiso: se venden créditos que el usuario
gasta en **funciones de IA** (sugerencias avanzadas, auto-definiciones de
glosario, análisis) o en **packs embebidos** (ZIPs de ejemplos, datasets,
plantillas de gobierno).

| Pack | Precio | Precio / crédito |
|---|---|---|
| 100 créditos | US$ 9 | US$ 0,090 |
| 550 créditos (+10% bonus) | US$ 39 | US$ 0,071 |
| 2.500 créditos | US$ 149 | US$ 0,060 |

Consumo de referencia: 1 sugerencia IA = 1 crédito · auto-definición de
glosario = 2 créditos · pack de ejemplo (ZIP) = 20 créditos. Los créditos no
vencen. Margen alto: el costo real de una llamada IA es de centavos, y los
packs embebidos tienen costo marginal ≈ 0.

### Por qué estos precios (competencia · barrera · rentabilidad)

- **Licencia US$ 149 (barrera baja):** un pago que una PyME o un consultor
  aprueba sin comité; 1/400 a 1/3.000 del costo anual de Collibra/Alation.
  Con costo marginal ≈ 0, casi todo es margen — rentable desde la primera venta.
- **Professional US$ 390/mes (competitivo):** bajado desde US$ 490 para entrar
  más fácil en medianas de LATAM sin resignar valor; sigue siendo múltiplos
  más barato que cualquier suite enterprise.
- **Créditos (upsell sin fricción):** monetizan a quien no quiere suscripción;
  ticket chico (US$ 9) que sube el LTV sin barrera de entrada.

### Cobro: MercadoPago

Pago con **MercadoPago** (tarjeta, débito, efectivo, dinero en cuenta) — el
medio dominante en Uruguay/Argentina/LATAM. La web usa **links de pago** de
MercadoPago (sin backend): al confirmarse el pago, el cliente vuelve a
`pago.html` y se habilita la descarga. Configuración en `landing/payments-config.js`.

### El verdadero motor: servicio + plataforma

La licencia sola compite contra gigantes (ver §3). El negocio rentable es
**vender el servicio de gobernanza CON la plataforma incluida**:

| Servicio | Precio | Frecuencia |
|---|---|---|
| **Diagnóstico inicial** (perfilado, catálogo, informe ejecutivo) | US$ 1.500 – 3.500 | Único, por cliente |
| **Retainer de steward externo** (gobierno operativo continuo) | US$ 800 – 1.500 / mes | Recurrente |
| **Capacitación / workshops** | US$ 400 – 900 | Por sesión |
| **Conector a medida** (BD productiva, ver roadmap) | US$ 1.200 – 4.000 | Único, por conector |

El precio de lista de la web ancla el valor; el margen real viene del servicio
recurrente sobre la misma plataforma que ya está construida (costo marginal ≈ 0).

---

## 2. Análisis de venta

### 2.1 Propuesta de valor (por qué compran)

1. **Precio disruptivo**: 1/10 a 1/50 del costo de Collibra/Alation, sin
   contratos anuales forzados.
2. **Datos 100% locales**: nada sale de la empresa → llave para banca, salud
   y sector público, donde la nube de terceros es un bloqueante.
3. **Trilingüe (ES/EN/PT)**: mercado natural en LATAM, desatendido por las
   herramientas en inglés.
4. **Time-to-value inmediato**: índice de calidad el día 1, no un proyecto de
   6 meses.
5. **Sin fricción de TI**: 3 formas de desplegar (`.exe`, `.bat`, web) según
   lo que cada empresa permita.

### 2.2 Segmentos objetivo (orden de prioridad)

| Segmento | Tamaño | Dolor | Ticket típico |
|---|---|---|---|
| **PyMEs y medianas LATAM** | Miles | "Cada área tiene su número"; no pueden pagar Collibra | Pro + diagnóstico |
| **Cooperativas / mutualistas / salud UY** | Cientos | Datos personales, no pueden usar nube extranjera | Enterprise + retainer |
| **Sector público / municipios** | Cientos | Transparencia, licencias caras prohibidas | Enterprise on-prem |
| **Consultoras de datos / BI** | Cientos | Necesitan herramienta propia white-label | Licencia + reventa |

### 2.3 Canales

- **Directo**: LinkedIn + demos (la landing con video y descarga sin fricción).
- **Partners**: consultoras de BI que revenden e implementan (comisión 20-30%).
- **Referidos**: cada cliente satisfecho en un rubro abre su cámara/gremio.

### 2.4 Embudo estimado (supuestos)

- 100 visitas a la landing → 12 descargan la demo (12%) → 3 piden diagnóstico
  (25% de descargas) → 1 se convierte en cliente pago (33% de diagnósticos).
- **Costo de adquisición (CAC)** modelado: US$ 150–400 por cliente pago
  (marketing directo, bajo por ser nicho).

---

## 3. Análisis de competencia

| Competidor | Precio aprox. | Fortaleza | Debilidad que explotamos |
|---|---|---|---|
| **Collibra** | US$ 100k–500k / año | Líder enterprise, completo | Carísimo, implementación de meses, overkill para medianas |
| **Alation** | US$ 60k–300k / año | Catálogo + búsqueda potente | Precio, foco enterprise, inglés |
| **Microsoft Purview** | Incluido/consumo Azure | Integrado a Azure | Amarra a Azure; datos en la nube MS |
| **Informatica AXON** | US$ 80k+ / año | Robusto, data quality | Complejo, caro, pesado |
| **Atlan** | US$ 40k–150k / año | UX moderna, cloud | SaaS cloud (dato sale), precio |
| **OpenMetadata / DataHub** | Gratis (open source) | Sin licencia | Requiere equipo técnico que lo opere y mantenga; sin soporte ni servicio |

### Nuestro posicionamiento

> **"El gobierno de datos de los que no pueden pagar Collibra ni operar
> DataHub solos."**

- Contra los **caros** (Collibra, Alation, Informatica): 1/10–1/50 del precio,
  días en vez de meses, en español.
- Contra los **gratis-pero-complejos** (OpenMetadata, DataHub): plataforma
  lista + servicio humano que los opera (los speeches y el steward externo).
- Contra los **cloud** (Purview, Atlan): **datos 100% locales**, el argumento
  que gana en banca/salud/público.

---

## 4. Facturación mensual proyectada (escenarios)

**Supuestos comunes** (estado de madurez ~12 meses, MRR = ingreso mensual
recurrente):
- Professional US$ 490 · Enterprise US$ 1.900 · Retainer US$ 1.100 (promedio).
- Diagnósticos: ingreso único promedio US$ 2.500, contados como flujo mensual.

### 4.1 Uruguay (mercado inicial)

| Escenario | Pro | Ent | Retainers | Diagnósticos/mes | **Facturación mensual** |
|---|---|---|---|---|---|
| Conservador | 3 | 1 | 2 | 1 | **US$ 8.560** |
| Base | 6 | 2 | 4 | 2 | **US$ 16.140** |
| Optimista | 10 | 3 | 6 | 3 | **US$ 25.700** |

### 4.2 LATAM (Argentina, Brasil, Chile, Paraguay, Perú, México…)

Factor ×4–6 sobre Uruguay por tamaño de mercado, con partners locales.

| Escenario | Pro | Ent | Retainers | Diagnósticos/mes | **Facturación mensual** |
|---|---|---|---|---|---|
| Conservador | 15 | 4 | 8 | 4 | **US$ 43.750** |
| Base | 35 | 10 | 20 | 8 | **US$ 108.150** |
| Optimista | 70 | 20 | 40 | 15 | **US$ 213.800** |

### 4.3 Mundo (con red de partners / reventa white-label)

Factor ×3–5 sobre LATAM; requiere estructura de soporte multi-idioma.

| Escenario | Pro | Ent | Retainers | Diagnósticos/mes | **Facturación mensual** |
|---|---|---|---|---|---|
| Conservador | 60 | 15 | 30 | 12 | **US$ 121.400** |
| Base | 150 | 40 | 80 | 25 | **US$ 373.500** |
| Optimista | 350 | 90 | 180 | 50 | **US$ 693.500** |

---

## 5. Ganancia neta mensual real (después de costos)

**Estructura de costos** (proporción sobre facturación, negocio de software +
servicio con costo marginal de plataforma casi nulo):

| Costo | % / monto |
|---|---|
| Procesamiento de pagos | 4% de facturación |
| Marketing y adquisición | 12% de facturación |
| Infraestructura (landing, API demo, backups) | US$ 80–400 / mes fijo |
| Herramientas (dominio, correo, diseño, contable) | US$ 150–500 / mes fijo |
| Personal de soporte/dev | 0 si es operación solo; US$ 2.500 por persona |

### 5.1 Uruguay

| Escenario | Facturación | Costos | **Neto (operación solo)** | Neto (con 1 empleado) |
|---|---|---|---|---|
| Conservador | US$ 8.560 | ~US$ 1.600 | **US$ 6.960** | US$ 4.460 |
| Base | US$ 16.140 | ~US$ 2.810 | **US$ 13.330** | US$ 10.830 |
| Optimista | US$ 25.700 | ~US$ 4.300 | **US$ 21.400** | US$ 16.400 |

### 5.2 LATAM (con equipo de 2–4 personas en base/optimista)

| Escenario | Facturación | Costos | **Neto mensual** |
|---|---|---|---|
| Conservador | US$ 43.750 | ~US$ 9.500 (1 empleado) | **US$ 34.250** |
| Base | US$ 108.150 | ~US$ 27.500 (3 empleados) | **US$ 80.650** |
| Optimista | US$ 213.800 | ~US$ 52.000 (5 empleados) | **US$ 161.800** |

### 5.3 Mundo (estructura de soporte y partners)

| Escenario | Facturación | Costos | **Neto mensual** |
|---|---|---|---|
| Conservador | US$ 121.400 | ~US$ 42.000 | **US$ 79.400** |
| Base | US$ 373.500 | ~US$ 140.000 | **US$ 233.500** |
| Optimista | US$ 693.500 | ~US$ 280.000 | **US$ 413.500** |

> Márgenes netos modelados: **~55–75% en operación chica** (Uruguay solo, costo
> de plataforma marginal), bajando a **~40–60% al escalar** por incorporación
> de personal y estructura. Coherente con negocios de software+servicio.

---

## 6. Recomendación

1. **Empezar por Uruguay, modelo servicio + plataforma.** Con 4–6 clientes
   base ya hay un neto de ~US$ 13k/mes sin empleados.
2. **No vender el software solo** contra Collibra/DataHub: venderlo **incluido
   en el servicio** (diagnóstico + retainer).
3. **Reinvertir en el conector a bases de datos** (roadmap): desbloquea el
   mercado de empresas grandes con datos productivos y sube el ticket.
4. **Sumar partners para LATAM/mundo**: la reventa white-label multiplica sin
   crecer la estructura propia proporcionalmente.

---

*Proyecciones modeladas para planificación. Los resultados reales dependen de
ejecución comercial, mercado y competencia. Revisar trimestralmente contra
facturación efectiva.*
