# 🔑 Kit del Owner — MV Data Governance

**Esta carpeta es tuya (del dueño del producto). No se entrega a clientes.**
A los clientes se les entrega la Opción A (instalador .exe) o la Opción B
(portable .bat) — ver [`../README.md`](../README.md).

El kit del owner junta **las dos versiones en un solo paquete** más todo lo
que necesitás para vender y trabajar dentro de cualquier empresa cliente:

```
dist/MVDataGovernance_Owner_v{versión}.zip
├── LEEME_OWNER.md                        ← este archivo
├── MVDataGovernance_Setup_v{versión}.exe ← versión EXE del owner (si la
│                                            generaste en Windows con
│                                            packaging\build_exe.bat)
└── MVDataGovernance/                     ← versión BAT del owner (portable,
    ├── MV_DataGovernance.bat                completa: programa + API + web
    ├── MV_DataGovernance_API.bat            de venta + video + docs + tests)
    ├── landing/  docs/  app/  mvdg/  …
```

Se genera con:

```bash
python packaging/build_release.py    # → dist/MVDataGovernance_Owner_v{ver}.zip
```

---

## 🛡️ Por qué esta versión pasa la revisión de privacidad de cualquier empresa

La versión del owner no "esquiva" los controles de TI del cliente — **los
cumple por diseño**, y eso es exactamente lo que la hace entrar donde otras
herramientas no entran. Checklist para mostrarle a TI del cliente antes de
empezar:

| Control típico de TI / privacidad | Cómo lo cumple el programa |
|---|---|
| "Nada puede salir a internet" | **Cero telemetría.** El programa no hace ninguna llamada externa por defecto. Las únicas funciones que tocan internet (IA externa, escaneo de tenant Power BI/Tableau) están **apagadas por defecto** y solo se activan si TI del cliente configura sus propias credenciales. |
| "No se puede instalar software" | La **versión BAT es portable**: corre desde una carpeta (o pendrive) con el Python que la empresa ya permite, sin tocar el registro ni instalar nada en el sistema. |
| "Los datos no salen de la máquina" | Todo (conexiones, proyectos por cliente, fichas de empresas) se guarda **localmente** en `~/.mv_data_governance/`. No hay nube, no hay cuenta, no hay login. |
| "Solo acceso de lectura a las bases" | Los conectores ejecutan **solo SELECT** (bloqueado a nivel de código: `run_query()` rechaza cualquier otra sentencia). |
| "Datos personales (PII)" | El programa **detecta** PII para gobernarla — nunca la transmite. Con IA externa activada (opt-in), solo viajan metadatos (nombres de columnas, reglas), jamás filas de datos. |

Si TI del cliente pide evidencia: `python -m mvdg.selfcheck` corre los
chequeos delante de ellos, y el código fuente completo va incluido en la
versión portable — es auditable en el momento.

## 💼 Flujo de trabajo del owner dentro del cliente

1. **Ficha del cliente** (pestaña 🏢 Empresas): registrá contacto, BI que
   usan y su restricción de TI — el programa te recomienda qué paquete
   entregarles (A o B).
2. **Trabajá el gobierno**: cargá sus datos (archivo o conexión de solo
   lectura), perfilá, mediciones de calidad, MDM, escaneo de Power
   BI/Tableau.
3. **Guardá cada etapa** (pestaña 📁 Proyecto): cada paso queda en disco por
   cliente — catalogar → medir → deduplicar → escanear BI → publicar — sin
   perder nada entre sesiones ([`docs/PROYECTO_CLIENTE.md`](../../docs/PROYECTO_CLIENTE.md)).
4. **Vendé**: la web de venta con MercadoPago va incluida en tu paquete
   (`landing/` + [`docs/MERCADOPAGO.md`](../../docs/MERCADOPAGO.md)); el
   análisis de negocio y precios en
   [`docs/ANALISIS_NEGOCIO.md`](../../docs/ANALISIS_NEGOCIO.md); los
   speeches para dirección/TI/comité, en la pestaña ❓ Ayuda del programa.
5. **Entregá al cliente** el paquete que corresponda (A o B) — nunca esta
   carpeta ni tu ZIP de owner, que incluyen tu material de venta.

## 🆚 Owner vs. cliente — qué tiene cada paquete

| | Owner (este kit) | Cliente A (.exe) | Cliente B (.bat) |
|---|---|---|---|
| Programa completo | ✅ | ✅ | ✅ |
| Instalador .exe + portable .bat | ✅ ambos | solo .exe | solo .bat |
| Web de venta (landing + MercadoPago) | ✅ | — | — |
| Video de demo + material comercial | ✅ | — | — |
| Tests + selfcheck auditables | ✅ | — | ✅ |
| Docs completas (negocio incluido) | ✅ | usuario | usuario |

**English:** This folder is the product owner's kit (both installers + sales
site + business docs in one package). It is not delivered to clients — they
get Option A (.exe installer) or Option B (portable .bat). The owner build
passes corporate privacy reviews **by design**: zero telemetry, no network
calls by default, local-only storage, read-only database access.

**Português:** Esta pasta é o kit do dono do produto (os dois instaladores +
site de vendas + docs de negócio num só pacote). Não se entrega a clientes —
eles recebem a Opção A (instalador .exe) ou a Opção B (.bat portátil). A
versão do owner passa nas revisões de privacidade corporativas **por
design**: zero telemetria, sem chamadas de rede por padrão, armazenamento
somente local, acesso de leitura aos bancos.
