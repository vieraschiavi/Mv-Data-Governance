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

## 🔓 Sacarte las restricciones (plan "owner")

El kit del owner trae el mismo programa que un cliente, con las mismas
funciones pagas apagadas hasta activar una licencia (pestaña Ayuda) — a
propósito: es el mismo circuito que se audita, no una versión distinta con
menos controles. Vos no comprás una licencia, te **auto-emitís** una con plan
`owner`, que `has_feature()` trata como comodín: desbloquea todo, hoy y lo
que se agregue después a `FUNCIONES_PAGAS`.

Además del paso manual, ahora existe un **instalador del owner ya
desbloqueado** que bajás de GitHub — ver abajo.

---

## 💿 Instalador del owner (.exe ya desbloqueado, solo para vos)

Es **el mismo programa** que compra un cliente: mismo `mvdg.spec`, mismo
`instalador.iss`, mismo código. Lo único distinto es que trae un archivo
`licencia_owner.txt` al lado del `.exe`, así abre desbloqueado sin que
pegues el token cada vez que reinstalás. Ese token pasa por la **misma**
verificación Ed25519 que la licencia de cualquier comprador — no es un build
con menos controles.

### Preparación (una sola vez)

```bash
# 1. En TU PC — el id de tu máquina
python packaging/licencias.py maquina

# 2. Firmá el token ATÁNDOLO a esa máquina (con tu clave privada)
python packaging/licencias.py firmar --plan owner \
    --email <tu-email> --maquina <id-del-paso-1>
```

3. Guardá el token como secreto **`MVDG_OWNER_TOKEN`** en
   *Settings → Secrets and variables → Actions*.

### Cada vez que quieras el instalador

*Actions* → **Instalador Escritorio (Electron)** → *Run workflow* →
`version: owner`. Queda publicado en la Release `owner-latest` como
`MVDataGovernance_OWNER_Setup_v{versión}.exe`.

Es el **mismo workflow** que arma el instalador del cliente: un solo binario
que se audita, se testea y se firma, y lo único que cambia entre las dos
ediciones es un `.txt` con la licencia. (Antes había además dos workflows de
PyInstaller + Inno Setup haciendo lo mismo; se eliminaron.)

### Por qué no lo pueden usar los clientes

**La licencia va atada a tu máquina** (`mvdg/machine.py`): en cualquier otra
PC el id no coincide, `licensing.verify()` la descarta y el programa abre en
**plan demo**. Verificado con el binario real — mismo `.exe`, `owner` en tu
PC y `demo` en otra.

> **Ojo con dónde queda.** Este `.exe` se publica en una Release, no como
> artefacto que vence: fue una decisión explícita para que siempre haya un
> instalador owner descargable. Un asset de Release queda pegado al repo
> para siempre, así que **mientras el repo sea público ese archivo lo puede
> bajar cualquiera**. No sirve en otra PC por lo de arriba, pero el único
> candado que queda de pie es ése. Pasar el repo a privado es lo que
> restaura el segundo.

> **Límite honesto:** esto no es DRM. El id de máquina se calcula de datos
> que alguien decidido puede falsificar, y un binario siempre se puede
> parchear. Lo que frena es el caso realista —que un `.exe` desbloqueado
> circule y funcione—, no a un atacante con tiempo. Contra eso protege el
> contrato, no el código.

Si cambiás de PC: repetí los pasos 1 y 2 con el id nuevo y actualizá el
secreto.

1. Si todavía no generaste el par de claves del emisor de licencias:

   ```bash
   python packaging/licencias.py keygen
   ```

   Pegá la pública impresa en `PUBLIC_KEY_B64` (`mvdg/licensing.py`) y cargá
   la privada como `LICENSE_PRIVATE_KEY` en Vercel (para las licencias que sí
   se venden). **Sin este paso ninguna licencia valida — ni la de un cliente
   ni la tuya —, a propósito: falla cerrado.**

2. Auto-emitite una licencia `owner` perpetua (sin `--dias` = no vence):

   ```bash
   python packaging/licencias.py firmar --plan owner --email tu-email@dominio.com
   ```

3. Copiá el token `MVDG2....` que imprime y pegalo una vez en la pestaña
   ❓ Ayuda → Licencia del programa (cualquiera de las 3 versiones: .exe,
   .bat o web). Queda guardado en `~/.mv_data_governance/licencia.json` — no
   hay que repetirlo cada vez que abrís el programa.

4. **Por qué esto y no un ZIP "owner" ya desbloqueado en un Release de
   GitHub**: el repo es público. Cualquiera que lo descargue tendría Purview,
   Collibra y el escaneo de tenant BI gratis — exactamente lo que el plan de
   licencias existe para evitar. El token `owner` requiere tu clave PRIVADA
   para emitirse (no está en el código fuente ni se puede fabricar leyéndolo),
   así que es seguro guardarlo vos y activarlo localmente en tus propias
   instalaciones, pero no es algo que tenga sentido publicar.

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
