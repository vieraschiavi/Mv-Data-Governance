// Contenido por variante. Cifras IDÉNTICAS en todos los idiomas (salen de model.py).
// Tipos de slide: cover, badcards, table4, tagcards, flow, statscallout, charts, ticklist, closing.

const CHART_SIN = {
  points: {
    pes: "8.0,241.6 124.0,240.6 240.0,238.6 356.0,232.8 472.0,224.4",
    base:"8.0,240.8 124.0,237.9 240.0,232.2 356.0,215.1 472.0,190.3",
    opt: "8.0,239.0 124.0,231.8 240.0,217.9 356.0,178.3 472.0,122.1"
  },
  ends:{pes:["216","29k"],base:["183","86k"],opt:["115","200k"]}
};
const CHART_CON = {
  points:{
    pes:"8.0,241.5 124.0,240.2 240.0,237.6 356.0,229.7 472.0,218.1",
    base:"8.0,239.8 124.0,234.6 240.0,224.5 356.0,195.5 472.0,154.2",
    opt:"8.0,236.6 124.0,223.5 240.0,198.3 356.0,126.7 472.0,25.3"
  },
  ends:{pes:["210","40k"],base:["147","146k"],opt:["20","361k"]}
};

// ---- pptx chart data (miles USD) ----
const CATS=["1m","3m","6m","12m","18m"];
const SERIES_SIN=[
  {name:"pes",values:[0.7,2.4,5.7,15.3,29.3]},
  {name:"base",values:[2.0,6.8,16.4,44.8,86.2]},
  {name:"opt",values:[5.0,17.0,40.2,106.1,199.8]}
];
const SERIES_CON=[
  {name:"pes",values:[0.8,3.0,7.4,20.5,39.9]},
  {name:"base",values:[3.6,12.3,29.2,77.5,146.3]},
  {name:"opt",values:[9.1,30.8,72.8,192.1,361.1]}
];

// ============ ESPAÑOL ============
const es = {
  code:"ES", lang:"es",
  file:{pptx:"MV-Data-Governance-Pitch.pptx", deck:"MV-Data-Governance-Pitch-Deck.pdf", op:"MV-Data-Governance-OnePager.pdf",
        deckHtml:"deck_ES.html", opHtml:"onepager_ES.html"},
  title:"MV Data Governance · Pitch deck",
  deck:[
    {type:"cover", brand:["MV Data Governance","VieraSchiavi · Uruguay"],
     h1:"Gobierno de datos + cobranza,<br>para la LATAM que nadie atiende.",
     sub:"Serio, en español, y corriendo en la infra del cliente. Los grandes venden caro y en inglés; nosotros entramos por la financiera y la PYME mediana — donde el dolor de recupero es concreto y el ciclo es de semanas.",
     foot:[["Etapa","pre-revenue, piloto-ready"],["Modelo","services-led + recurrente"],["Fecha","Julio 2026"]]},
    {type:"badcards", no:"01", kick:"El problema",
     title:"El gobierno de datos está roto para el 95% de las empresas de la región.",
     lead:"Las herramientas que existen resuelven el problema de un banco global, no el de una financiera uruguaya. Y la que gobierna mal su dato, cobra mal: calidad de dato → recupero.",
     cards:[["Caro","Collibra, Alation, Informatica: presupuestos enterprise, licencias en dólares que una PYME no firma."],
            ["En inglés y en la nube","Interfaz y soporte en inglés, y datos sensibles que tienen que salir a un tenant externo — freno inmediato de seguridad."],
            ["O “hágalo usted mismo”","El open-source (OpenMetadata) es gratis pero hay que armarlo, mantenerlo y sin soporte en español."]]},
    {type:"table4", no:"02", kick:"La oportunidad",
     title:"Nadie es dueño de “gobierno + cobranza, en español, corriendo local, para la PYME/financiera de LATAM”.",
     titleMark:"“gobierno + cobranza, en español, corriendo local, para la PYME/financiera de LATAM”",
     lead:"Cuatro frentes compiten alrededor del hueco, ninguno adentro. Ese seam desatendido es la tesis.",
     head:["Frente","Quién manda","Su punto débil","Nuestro ángulo"],
     rows:[["Gobierno de datos","Collibra, Purview, Informatica","caros, inglés, nube, enterprise","barato, local, trilingüe, PYME"],
           ["Gobierno OSS","OpenMetadata","“armalo vos”, sin soporte ES","producto terminado + implementación"],
           ["Cobranza LATAM","Colektia, Moonflow","cobran, no gobiernan el dato","gobernamos el dato del recupero"],
           ["Core bancario UY","Bantotal (~70% banca)","es el core, no juega en PYME","no lo peleamos: al costado, mid-market"]]},
    {type:"tagcards", no:"03", kick:"Producto",
     title:"Tres niveles. Cada uno con un trabajo distinto en el embudo.",
     cards:[["Gratis","g","Demo local","100% sintética, sin internet. El caballo de Troya: el prospecto la prueba sin pedir permiso a seguridad. Un review real dijo que “destrabó la aprobación de seguridad para un piloto sin fricción”."],
            ["Pago","w","Versiones pagas","US$149 Licencia PC (único) · US$390/mes Professional · créditos IA US$9/39/149. Cobrables ya por MercadoPago en USD."],
            ["Interno","b","Versión owner","Código completo + servidor propio. No es un SKU: es el vehículo para entregar implementaciones sobre la BD/ERP de cada cliente. Ahí está el margen."]],
     callout:["Estado del producto","<b>242 tests · autochequeo 46/46 · trilingüe · corre 100% local.</b> El motor (catálogo, calidad, linaje, contratos de datos) está sólido para pilotos hoy. Los cobros online ya están vivos.",
              "242 tests · autochequeo 46/46 · trilingüe · corre 100% local. ","El motor (catálogo, calidad, linaje, contratos de datos) está sólido para pilotos hoy. Los cobros online ya están vivos."]},
    {type:"flow", no:"04", kick:"Modelo de negocio",
     title:"Services-led: el proyecto paga el hoy, la suscripción construye el mañana.",
     lead:"No es “SaaS que se vende solo”. Entramos como especialista que implementa, cobramos el proyecto por adelantado, y dejamos el software corriendo como recurrente.",
     steps:[["01","Demo local","Entra sin fricción de seguridad. Genera el lead."],
            ["02","Proyecto","Implementación sobre su BD/ERP. US$3–8k por adelantado."],
            ["03","Attach","Queda corriendo el Professional. US$390/mes recurrente."],
            ["04","Expansión","Más módulos, más áreas, referido a la próxima financiera."]],
     callout:["Por qué importa","El cobro por adelantado hace el negocio <b>cash-positivo desde el mes 1</b> — sin valle de la muerte. El <b>attach de suscripción</b> es lo que lo convierte de “consultor caro con techo de horas” en un activo que crece mientras dormís.",
              "El cobro por adelantado hace el negocio cash-positivo desde el mes 1"," — sin valle de la muerte. El attach de suscripción es lo que lo convierte de “consultor caro con techo de horas” en un activo que crece mientras dormís."]},
    {type:"statscallout", no:"05", kick:"Los números · caso base",
     title:"Neto US$86–146k a 18 meses. Vos solo. Sin quemar capital.",
     stats:[["US$86–146k","ink","Neto acumulado · 18m","base, sin / con inversión en redes"],
            ["Mes 1","good","Cash-positivo desde","en los 3 escenarios · proyectos cobrados por adelantado"],
            ["US$2,9–5,0k/m","amb","Recurrente vivo @18m","suscripciones que escalan"]],
     callout:["Traducido a ingreso","Base sin redes ≈ <b>US$4.800/mes</b> promedio a 18m — más del doble del salario TI promedio uruguayo (US$2.300). El riesgo no es la caja: es <b>cerrar los deals</b>.",
              "Base sin redes ≈ US$4.800/mes promedio a 18m"," — más del doble del salario TI promedio uruguayo (US$2.300). El riesgo no es la caja: es cerrar los deals."]},
    {type:"charts", no:"06", kick:"Escenarios",
     title:"Tres futuros, misma escala, sin inflar.",
     c1:["Neto acumulado — SIN inversión en redes","orgánico / referidos · USD acumulado"],
     c2:["Neto acumulado — CON inversión en redes","+US$400/mes en ads · USD acumulado"],
     legend:[["Pesimista",""],["Base","(planificamos acá)"],["Optimista","— aspiracional, ya requiere equipo"]]},
    {type:"statscallout", no:"07", kick:"Mercado",
     title:"Uruguay para validar. LATAM es la tesis. El mundo, el viento de cola.",
     stats:[["~120","ink","🇺🇾 Cuentas núcleo UY","11 bancos, ~35 financieras, 34 mutualistas, estatales. +850 grandes privadas (INE)."],
            ["~8.400","ink","🌎 Cuentas núcleo LATAM","~70–80× UY por PIB. Ventaja real: trilingüe y “en criollo”."],
            ["US$12–18bn","ink","🌐 TAM global 2030","data governance creciendo ~19–22%/año. El viento de cola, no la meta."]],
     kAmber:true,
     callout:["Por dónde entramos","Por la <b>financiera / administradora de crédito mediana</b> — ciclo corto, dolor claro de recupero. <b>No</b> por los 11 bancos (ciclo 9–15 meses y piden SOC 2/ISO). Uruguay valida; LATAM escala.",
              "Por la financiera / administradora de crédito mediana"," — ciclo corto, dolor claro de recupero. No por los 11 bancos (ciclo 9–15 meses y piden SOC 2/ISO). Uruguay valida; LATAM escala."]},
    {type:"tagcards", no:"08", kick:"Go-to-market",
     title:"Un motor de contenido que alimenta el embudo, con una sola cara real.",
     lead:"~36 piezas/mes, identidad real (Martín Viera), sin personas falsas ni humo. El contenido no vende solo: construye autoridad y trae leads a la demo, que cierra con implementación.",
     cards:[["Línea A","a","Autoridad","LinkedIn + X. “Gobierno de datos y cobranza en criollo.” Construye la reputación que cierra."],
            ["Línea B · foco","a","Producto B2B","Mini-demos sobre data sintética, problema→insight→CTA, one-pagers. Leads de gerentes de cobranzas/riesgo."],
            ["Línea C","a","Canal educativo","Shorts/Reels 60–90s, guion y voz propios. Alcance hispano, top of funnel."]],
     callout:["Honestidad, no promesa faceless","Con <b>US$400/mes</b> de ads (CPL LATAM US$17–36) compramos ~10–18 leads B2B → ~0,5–1 cliente extra/mes, y un cliente deja US$3–8k. Se paga varias veces <b>si el embudo convierte</b>.",
              "Con US$400/mes de ads (CPL LATAM US$17–36) compramos ~10–18 leads B2B"," → ~0,5–1 cliente extra/mes, y un cliente deja US$3–8k. Se paga varias veces si el embudo convierte."]},
    {type:"ticklist", no:"09", kick:"Cómo se escala",
     title:"De venderlo solo a tener equipo — contratando contra recurrente, no contra esperanza.",
     items:[["Año 1 — Solo.","Entregás todo. Techo ~2 implementaciones/mes. Meta: 5–15 clientes, US$29–146k netos. Cero contrataciones, guardás caja."],
            ["Gatillo de contratación.","Solo cuando (a) el recurrente cubre un sueldo y (b) estás rechazando trabajo. Un implementador mid en UY cuesta all-in ~US$4.500/mes."],
            ["Año 2 — Primer contratado.","En base/optimista el recurrente cruza los US$4.500/mes hacia el mes 10–12. Duplicás capacidad de entrega."],
            ["Año 2–3 — Micro-agencia (3–4).","Vos en venta + arquitectura, 2 implementadores, 1 part-time de contenido. Solo si el recurrente sostiene la nómina."]]},
    {type:"ticklist", no:"10", kick:"Riesgos · abogado del diablo", risk:true,
     title:"Un plan sin esta lámina es marketing. Esto es lo que puede hundirlo.",
     items:[["Bus factor 1.","Todo depende de una persona. Mitigación: documentar, no prometer SLAs insostenibles, contratar apenas el recurrente lo permita."],
            ["Conectores sin probar en vivo.","Purview/Collibra/Tableau/MCP están contra la doc, nunca contra un tenant real. Mitigación: primer enterprise como piloto pago con expectativa de “primera integración”."],
            ["Mercado UY chico.","~120 cuentas núcleo. LATAM no es opcional, es la tesis; la ventaja idiomática es la palanca."],
            ["El optimista es aspiracional.","4 clientes/mes solo a US$8k es irreal sin equipo. Planificamos con base; celebramos si es optimista."]]},
    {type:"closing", no:"11", kick:"El pedido",
     title:"No es capital para no morir. Es la decisión de acelerar.",
     lead:"El negocio es cash-positivo solo, desde el mes 1. La pregunta real es si comprimimos 18 meses en 9: contratar el primer implementador antes y encender el motor de contenido/ads en vez de esperar a que el orgánico lo permita.",
     cards:[["Camino A · bootstrap","g","Solo, orgánico","Cero capital externo. Base sin redes: US$86k netos a 18m, recurrente US$2,9k/m. Más lento, 100% tuyo."],
            ["Camino B · acelerar","a","Ads + hire temprano","~US$30–50k comprarían ~6 meses de un implementador + ads. Base con redes apunta a US$146k a 18m y recurrente US$5,0k/m, antes."]],
     contact:[["Próximo paso concreto:","un piloto pago con una financiera mediana."],["Martín Viera","· VieraSchiavi"],["","vieraschiavi@gmail.com"]]}
  ],
  op:{
    tagline:"Gobierno de datos + implementación de cobranza · ES/PT/EN · corre local",
    rt:[["Etapa:","pre-revenue, listo p/ piloto"],["Modelo:","services-led + software recurrente"],["Mercado:","Uruguay → LATAM"],["","Julio 2026"]],
    thesis:'El gobierno de datos serio hoy es <mark>caro, en inglés y en la nube</mark>. Nosotros lo llevamos a la financiera y la PYME de LATAM: <mark>barato, en español y corriendo en su propia infra</mark> — y gobernamos el dato que alimenta su cobranza.',
    subt:"Entramos como el especialista que implementa cobranza + gobierno sobre la base/ERP del cliente (proyecto cobrado por adelantado) y dejamos el software corriendo (recurrente US$390/mes). El proyecto paga el hoy; la suscripción construye el mañana.",
    kpis:[["Neto 18m · caso base","US$86–146k","num","sin / con inversión en redes"],
          ["Riesgo de capital","Bajo","good","cash-positivo desde el mes 1"],
          ["Recurrente @18m","US$2,9–5,0k/m","amb","suscripciones vivas, base"],
          ["Producto","Piloto-ready","good","242 tests · autochequeo 46/46"]],
    sellsH:"Qué se vende",
    sells:[["Demo local (gratis)"," — 100% sintética, sin internet. El caballo de Troya: el prospecto la prueba sin pedir permiso a seguridad."],
           ["Versiones pagas"," — Licencia PC US$149 (único) · Professional US$390/mes · créditos IA US$9/39/149. Cobrables ya por MercadoPago en USD."],
           ["Implementación a medida"," — cobranza + gobierno sobre la BD/ERP del cliente. Ahí está el margen y la puerta a la suscripción."]],
    seamH:"Por qué ganamos (el seam)",
    seam:'Nadie es dueño de <b>“gobierno de datos + cobranza, para la financiera/PYME mediana de LATAM, en español, corriendo local”</b>. Los enterprise (Collibra, Purview, Informatica) son caros y en inglés; los de cobranza (Colektia, Moonflow) no gobiernan el dato; el open-source es “hágalo usted mismo”. Entramos por la <b>financiera/administradora de crédito mediana</b> —ciclo corto, dolor claro de recupero— no por los 11 bancos (ciclo 9–15 meses).',
    marketH:"Mercado",
    chips:[["🇺🇾 Uruguay","~120","cuentas núcleo · validar"],["🌎 LATAM","~8.400","cuentas núcleo · escalar"],["🌐 TAM global","US$12–18bn","a 2030 · +19–22%/año"]],
    tblH:"Rentabilidad neta — caso base (USD)",
    tblHead:["Horizonte","6 m","12 m","18 m","Recurr."],
    tblRows:[["hl","Base · sin redes","16.386","44.770","86.241","2.875/m"],
             ["hl","Base · con redes","29.171","77.454","146.294","4.998/m"],
             ["","Pesimista · sin","5.691","15.336","29.288","1.100/m"],
             ["","Optimista · con","72.804","192.089","361.144","10.235/m"]],
    tblCap:"Neto después de comisión de cobro (~5%), infra e impuesto efectivo ~20%; antes del retiro del dueño (en fase solo, el neto <b>es</b> tu ingreso). Planificá con el <b>caso base</b>; el optimista (4 clientes/mes solo a US$8k) es aspiracional.",
    modelH:"El dato que cambia todo",
    model:"<b>Cash-positivo desde el mes 1</b> en los tres escenarios: los proyectos se cobran por adelantado, así que no hay “valle de la muerte” ni necesidad de capital. El riesgo no es quedarte sin plata — es que no cierren los deals.",
    statusH:"Estado & lo que falta",
    pills:[["g","Motor sólido"],["g","Cobros en vivo"],["g","Trilingüe"],["w","Conectores sin probar en tenant real"],["b","0 clientes aún"],["b","Sin SOC 2 / ISO"],["b","Bus factor 1"]],
    ctaBig:"El próximo paso: un piloto pago con una financiera mediana.",
    ctaSm:'Demo local sin fricción → proyecto de implementación → software corriendo. No necesitamos capital para arrancar; sí para <b>comprimir 18 meses en 9</b>.',
    who:["Martín Viera","· VieraSchiavi","vieraschiavi@gmail.com"],
    foot:"<b>Metodología.</b> Precios: reales del repositorio. Mercado, competencia, costos y ads: investigados contra fuentes oficiales/públicas (BCU, INE, MSP, CUTI/BPS, Grand View) el 2026-07-20, marcando verificado vs. estimado. Modelo financiero propio y transparente; supuestos completos en el plan de negocio. Cifras de proyección = escenarios de planificación, no garantías. Demo sobre datos 100% sintéticos."
  }
};

module.exports = { es, CHART_SIN, CHART_CON, CATS, SERIES_SIN, SERIES_CON };
