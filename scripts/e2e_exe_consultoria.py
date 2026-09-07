# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""Relevamiento y Reuniones del .exe, en un Chromium real contra la API real.

    python scripts/e2e_exe_consultoria.py

Por qué existe
──────────────
Un error de React no rompe el build ni ningún test de unidad: se ve como
una pantalla en blanco recién al abrir el programa. Este guion levanta
`bi_api` de verdad, abre la interfaz que sirve en /app —la misma que carga
la ventana de Electron— y recorre las dos vistas mirando la consola.

No es teoría: en su primera corrida encontró dos bugs que el build, ruff y
554 tests dejaban pasar enteros.

  1. Se escribía la respuesta, se apretaba Guardar y la pregunta quedaba
     "pendiente": el selector de estado seguía en el valor con el que se
     había abierto. La cobertura no subía nunca.
  2. Arreglado eso, escribir la respuesta CERRABA la pregunta que se
     estaba contestando, con el botón de guardar adentro: el `open` del
     `<details>` estaba atado al estado de la respuesta.

Los dos síntomas son de interfaz viva. No hay forma de verlos sin abrir un
navegador de verdad y escribir en la pantalla.
"""
import os
import socket
import subprocess
import sys
import tempfile
import time

REPO = "/home/user/Mv-Data-Governance"
sys.path.insert(0, REPO)

DATOS = tempfile.mkdtemp()
os.environ["MVDG_DATA_DIR"] = DATOS

from mvdg import clients, interview  # noqa: E402

clients.save_client({"client_id": "conaprole-001", "company": "Conaprole",
                     "it_restriction": "exe_ok", "status": "piloto"})
interview.save_answer("conaprole-001", "MDM-01", respuesta="Pasa seguido",
                      responsable="Juan Pérez", area_responsable="Comercial")

VTT = """WEBVTT

00:00:01.000 --> 00:00:06.000
<v Ana García>Quedamos en que el dueño del dataset va a ser Comercial.</v>

00:00:07.000 --> 00:00:14.000
<v Juan Pérez>El problema es que el maestro de clientes se duplica y nadie sabe de dónde sale el segmento.</v>

00:00:15.000 --> 00:00:21.000
<v Martina Rossi>Yo me encargo, te mando el diccionario antes del viernes.</v>
"""


def puerto_libre():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


PUERTO = puerto_libre()
entorno = dict(os.environ, MVDG_API_PORT=str(PUERTO), MVDG_API_HOST="127.0.0.1",
               MVDG_UI_DIR=os.path.join(REPO, "electron", "ui", "dist"))
api = subprocess.Popen([sys.executable, "-m", "bi_api.main"], cwd=REPO, env=entorno,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

BASE = f"http://127.0.0.1:{PUERTO}"
import urllib.request  # noqa: E402

for _ in range(120):
    try:
        urllib.request.urlopen(f"{BASE}/health", timeout=1)
        break
    except Exception:
        time.sleep(0.5)
else:
    print("la API no levantó:", api.stderr.read().decode()[-2000:])
    sys.exit(1)

fallos = []
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("playwright no está instalado")
    api.terminate()
    sys.exit(2)


def kwargs():
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if base and os.path.exists(os.path.join(base, "chromium")):
        return {"executable_path": os.path.join(base, "chromium")}
    return {}


with sync_playwright() as pw:
    nav = pw.chromium.launch(**kwargs())
    pag = nav.new_page(viewport={"width": 1440, "height": 900})
    consola = []
    pag.on("console", lambda m: consola.append((m.type, m.text)) if m.type == "error" else None)
    pag.on("pageerror", lambda e: consola.append(("pageerror", str(e))))

    pag.goto(f"{BASE}/app", wait_until="networkidle")
    pestanas = [b.inner_text() for b in pag.locator("nav.tabs button").all()]
    print("pestañas del .exe:", pestanas)
    for esperada in ("Relevamiento", "Reuniones"):
        if esperada not in pestanas:
            fallos.append(f"falta la pestaña {esperada}")

    # ---------------------------------------------------------- Relevamiento
    pag.get_by_role("button", name="Relevamiento").click()
    pag.wait_for_timeout(1500)
    texto = pag.locator("main").inner_text()
    print("\n--- Relevamiento")
    print("  empresa Conaprole:", "Conaprole" in texto)
    print("  cobertura visible:", "Relevamiento cubierto" in texto)
    kpis = [k.inner_text() for k in pag.locator(".kpi .val").all()]
    print("  KPIs:", kpis)
    if "Conaprole" not in texto:
        fallos.append("el selector de empresa no trajo Conaprole")
    if not any("%" in k for k in kpis):
        fallos.append("no se ve la cobertura")

    # Abrir una pregunta y ver que trae el porqué y las repreguntas
    detalles = pag.locator("details.panel")
    print("  preguntas del área:", detalles.count())
    if detalles.count() == 0:
        fallos.append("no se dibujó ninguna pregunta")
    else:
        primero = detalles.first
        # Las preguntas pendientes se dibujan YA abiertas: clickear el summary
        # sin mirar las cerraba, y el guion medía una pantalla plegada.
        if not primero.evaluate("e => e.open"):
            primero.locator("summary").click()
        pag.wait_for_timeout(1200)
        d = primero.inner_text()
        print("  ¿trae el porqué?:", "Por qué se pregunta" in d)
        print("  ¿trae repreguntas?:", "Qué repreguntar" in d)
        if "Qué repreguntar" not in d:
            fallos.append("la pregunta no muestra el casillero de repreguntas")
        items = primero.locator("ul li")
        print("  repreguntas listadas:", items.count())
        if items.count() == 0:
            fallos.append("el casillero de repreguntas salió vacío")

    # Guardar una respuesta de verdad y ver que la cobertura sube
    antes = interview.overall_coverage("conaprole-001")
    caja = detalles.first.locator("textarea")
    caja.fill("Cada 24 horas, a las 3 de la mañana, lo corre el ERP.")
    detalles.first.get_by_role("button", name="Guardar respuesta").click()
    pag.wait_for_timeout(1500)
    despues = interview.overall_coverage("conaprole-001")
    print(f"  cobertura {antes}% -> {despues}% (guardado real en disco)")
    if despues <= antes:
        fallos.append("guardar desde el .exe no persistió la respuesta")

    # ------------------------------------------------------------- Reuniones
    pag.get_by_role("button", name="Reuniones").click()
    pag.wait_for_timeout(800)
    pag.get_by_role("button", name="Pegar el texto").click()
    pag.wait_for_timeout(400)
    pag.locator("#mtg-pegar").fill(VTT)
    pag.wait_for_timeout(2000)
    texto = pag.locator("main").inner_text()
    print("\n--- Reuniones")
    kpis = [k.inner_text() for k in pag.locator(".kpi .val").all()]
    print("  KPIs (intervenciones / minutos / hallazgos):", kpis)
    for quien in ("Ana García", "Juan Pérez", "Martina Rossi"):
        if quien not in texto:
            fallos.append(f"la minuta no muestra a {quien}")
    print("  oradores en pantalla:", all(q in texto for q in
          ("Ana García", "Juan Pérez", "Martina Rossi")))
    for esperado in ("Decisión", "Compromiso", "Riesgo"):
        if esperado not in texto:
            fallos.append(f"no se ve el hallazgo de tipo {esperado}")
    print("  hallazgos tipados:", all(e in texto for e in
          ("Decisión", "Compromiso", "Riesgo")))
    print("  cruce con el pipeline:",
          "Qué le toca a cada etapa del pipeline" in texto and "MDM" in texto)
    if "MDM" not in texto:
        fallos.append("el cruce con el pipeline no apareció")

    # Que la descarga funcione de verdad (es POST + blob, el camino frágil)
    pag.expect_download(timeout=15000)
    with pag.expect_download() as bajada:
        pag.get_by_role("button", name="PDF").click()
    archivo = bajada.value
    ruta = os.path.join(DATOS, "minuta.pdf")
    archivo.save_as(ruta)
    tam = os.path.getsize(ruta)
    with open(ruta, "rb") as fh:
        cabecera = fh.read(5)
    print(f"  descarga del PDF: {tam:,} bytes · cabecera {cabecera!r}")
    if cabecera != b"%PDF-":
        fallos.append("la descarga de la minuta no es un PDF")

    print("\nerrores de consola:", consola or "ninguno")
    if consola:
        fallos.append(f"la consola reportó {len(consola)} error(es)")
    nav.close()

api.terminate()
print("\nFALLOS:", fallos or "ninguno")
sys.exit(1 if fallos else 0)
