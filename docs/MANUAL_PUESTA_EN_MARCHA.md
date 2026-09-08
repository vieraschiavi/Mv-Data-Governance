# 🚀 Puesta en marcha · Getting started · Primeiros passos

## 🇪🇸 Español

### Opción 1 · Programa portable (.bat) — recomendada
1. Instalá [Python 3.10+](https://www.python.org/downloads/) marcando
   **"Add Python to PATH"**.
2. Doble clic en **`MV_DataGovernance.bat`**. La primera vez crea el entorno
   e instala dependencias (2–5 min); después abre al instante en tu navegador.
3. *(Opcional)* ¿Querés que el programa aparezca en el **Escritorio** o en el
   **Menú Inicio** de Windows como una app instalada? Doble clic en
   **`MV_Instalar_Accesos.bat`**: pregunta cuál de los dos querés (S/N) y crea
   los accesos con el icono del programa, sin permisos de administrador.
   Para la **barra de tareas**: clic derecho sobre el acceso creado →
   *"Anclar a la barra de tareas"* (Windows no permite que un programa se
   ancle solo — es una restricción de Microsoft, no de este programa).
   Para quitarlos: `MV_Instalar_Accesos.bat quitar`.

### Opción 2 · Ejecutable Windows (.exe)
1. En una PC con Python: doble clic en **`packaging\build_exe.bat`**.
2. Obtenés `dist\MVDataGovernance\MVDataGovernance.exe` (portable, no
   requiere Python en la máquina destino) y, si tenés
   [Inno Setup](https://jrsoftware.org/isdl.php), también el instalador
   `dist\MVDataGovernance_Setup_v<versión>.exe` (instalador profesional
   estilo Windows: el cliente elige la **carpeta de destino** — no queda
   fijo en Archivos de programa —, crea el acceso del **Menú Inicio** y
   ofrece con una casilla el del **Escritorio**, y queda con
   **Agregar o quitar programas** para desinstalar prolijo).

### Opción 3 · Web (servidor de la empresa)
Corré el programa como servidor web para que varios usuarios lo abran desde
el navegador, sin instalar nada en cada PC. Solo arranca en **servidores
autorizados por la empresa**.

```bash
# Windows: doble clic en
MV_DataGovernance_Server.bat
# Linux / macOS:
./run_server.sh
```

- **Host y puerto:** `MVDG_SERVER_HOST` (por defecto `0.0.0.0`, accesible en
  la red interna) y `MVDG_SERVER_PORT` (por defecto `8501`).
- **Servidores autorizados:** definí `MVDG_AUTHORIZED_HOSTS` (hostnames o IPs
  separados por coma) o editá el archivo **`server_authorized.txt`** (un host
  por línea). Si la lista está vacía, corre en modo abierto y avisa. El valor
  `*` autoriza cualquier host (no recomendado en producción).

```bash
# ejemplo: autorizar dos servidores y escuchar en el puerto 8080
export MVDG_AUTHORIZED_HOSTS="srv-datos.empresa.local,10.0.5.20"
export MVDG_SERVER_PORT=8080
./run_server.sh
```

Todo sigue siendo local a la empresa: nada viaja a internet.

**Licencia owner sin pegar nada** (caso: sos el dueño y desplegás en un
servidor del cliente que no es tu máquina — la laptop de trabajo no deja
instalar `.exe`/`.bat`, y los datos del cliente no pueden salir de su
servidor): en vez del instalador owner (que abre en demo ahí, porque su
licencia va atada a TU máquina a propósito), emitís un token owner atado al
id de ESE servidor y lo dejás activado antes de arrancar:

```bash
python packaging/licencias.py maquina                    # en el servidor, una vez
python packaging/licencias.py firmar --plan owner \
    --maquina <id que imprimió el paso anterior> \
    --email <tu-email>                                    # en TU máquina, con tu privada
export MVDG_SERVER_LICENSE_TOKEN="<token que imprimió>"   # en el servidor, antes de arrancar
./run_server.sh
```

El dashboard abre desbloqueado desde el primer navegador que llegue — nadie
toca la pestaña Licencia. Un token vencido, mal copiado o atado a otra
máquina no activa nada: el servidor sigue en el plan que ya tuviera.

### API para BI
Doble clic en **`MV_DataGovernance_API.bat`** → `http://127.0.0.1:8600/docs`.
Guía por herramienta: [`docs/BI_INTEGRATION.md`](BI_INTEGRATION.md).

### ¿Qué es el gobierno de datos? (DAMA-DMBOK)
Explicado para técnicos y no técnicos, con el mapeo de las 11 áreas del
estándar DAMA-DMBOK contra lo que hace esta plataforma:
[`docs/DMBOK.md`](DMBOK.md). Lo mismo se ve en vivo dentro del programa, en
la pestaña **Ayuda**.

---

## 🇬🇧 English

### Option 1 · Portable program (.bat) — recommended
1. Install [Python 3.10+](https://www.python.org/downloads/) ticking
   **"Add Python to PATH"**.
2. Double-click **`MV_DataGovernance.bat`**. First run creates the
   environment and installs dependencies (2–5 min); afterwards it opens
   instantly in your browser.

### Option 2 · Windows executable (.exe)
1. On a PC with Python: double-click **`packaging\build_exe.bat`**.
2. You get `dist\MVDataGovernance\MVDataGovernance.exe` (portable, no Python
   needed on the target machine) and, with
   [Inno Setup](https://jrsoftware.org/isdl.php) installed, also the
   `dist\MVDataGovernance_Setup_v<version>.exe` installer (a professional
   Windows setup: the client picks the **install folder** — not locked to
   Program Files —, creates the **Start Menu** shortcut, offers the
   **Desktop** one as a checkbox, and shows up in **Add or remove
   programs** for a clean uninstall).

### Option 3 · Web (company server)
Run the program as a web server so multiple users open it from their browser,
with nothing installed on each PC. It only starts on **company-authorized
servers**.

```bash
# Windows: double-click
MV_DataGovernance_Server.bat
# Linux / macOS:
./run_server.sh
```

- **Host and port:** `MVDG_SERVER_HOST` (default `0.0.0.0`, reachable on the
  internal network) and `MVDG_SERVER_PORT` (default `8501`).
- **Authorized servers:** set `MVDG_AUTHORIZED_HOSTS` (comma-separated
  hostnames or IPs) or edit **`server_authorized.txt`** (one host per line).
  If the list is empty it runs in open mode with a warning. The value `*`
  authorizes any host (not recommended in production).

Everything stays local to the company: nothing goes to the internet.

**Owner license with nothing to paste** (case: you are the owner deploying on
a client's server that is not your machine — your work laptop won't let you
install an `.exe`/`.bat`, and the client's data cannot leave their server):
instead of the owner installer (which opens in demo there, since its license
is deliberately bound to YOUR machine), issue an owner token bound to THAT
server's id and drop it in before starting:

```bash
python packaging/licencias.py maquina                     # on the server, once
python packaging/licencias.py firmar --plan owner \
    --maquina <id printed above> \
    --email <your-email>                                  # on YOUR machine, with your private key
export MVDG_SERVER_LICENSE_TOKEN="<printed token>"         # on the server, before starting
./run_server.sh
```

The dashboard opens unlocked for the first browser that reaches it — nobody
touches the License tab. An expired, miscopied, or wrongly-bound token
activates nothing: the server keeps whichever plan it already had.

### BI API
Double-click **`MV_DataGovernance_API.bat`** → `http://127.0.0.1:8600/docs`.
Per-tool guide: [`docs/BI_INTEGRATION.md`](BI_INTEGRATION.md).

### What is data governance? (DAMA-DMBOK)
Explained for both technical and non-technical readers, mapping the 11
areas of the DAMA-DMBOK standard against what this platform actually does:
[`docs/DMBOK.md`](DMBOK.md). The same content is live inside the program,
under the **Help** tab.

---

## 🇧🇷 Português

### Opção 1 · Programa portátil (.bat) — recomendada
1. Instale o [Python 3.10+](https://www.python.org/downloads/) marcando
   **"Add Python to PATH"**.
2. Duplo clique em **`MV_DataGovernance.bat`**. Na primeira execução ele cria
   o ambiente e instala dependências (2–5 min); depois abre na hora no
   navegador.

### Opção 2 · Executável Windows (.exe)
1. Em um PC com Python: duplo clique em **`packaging\build_exe.bat`**.
2. Você obtém `dist\MVDataGovernance\MVDataGovernance.exe` (portátil, não
   requer Python na máquina de destino) e, com o
   [Inno Setup](https://jrsoftware.org/isdl.php) instalado, também o
   instalador `dist\MVDataGovernance_Setup_v<versão>.exe` (instalador
   profissional estilo Windows: o cliente escolhe a **pasta de destino**
   — não fica preso em Arquivos de Programas —, cria o atalho do **Menu
   Iniciar**, oferece o da **Área de Trabalho** com uma caixa de seleção,
   e aparece em **Adicionar ou remover programas** para desinstalar
   direitinho).

### Opção 3 · Web (servidor da empresa)
Rode o programa como servidor web para vários usuários abrirem pelo
navegador, sem instalar nada em cada PC. Só inicia em **servidores
autorizados pela empresa**.

```bash
# Windows: duplo clique em
MV_DataGovernance_Server.bat
# Linux / macOS:
./run_server.sh
```

- **Host e porta:** `MVDG_SERVER_HOST` (padrão `0.0.0.0`, acessível na rede
  interna) e `MVDG_SERVER_PORT` (padrão `8501`).
- **Servidores autorizados:** defina `MVDG_AUTHORIZED_HOSTS` (hostnames ou
  IPs separados por vírgula) ou edite **`server_authorized.txt`** (um host por
  linha). Se a lista estiver vazia, roda em modo aberto e avisa. O valor `*`
  autoriza qualquer host (não recomendado em produção).

Tudo continua local à empresa: nada vai para a internet.

**Licença owner sem colar nada** (caso: você é o dono e implanta em um
servidor do cliente que não é sua máquina — o notebook de trabalho não
deixa instalar `.exe`/`.bat`, e os dados do cliente não podem sair do
servidor dele): em vez do instalador owner (que abre em demo ali, pois a
licença dele é atada de propósito à SUA máquina), emita um token owner
atado ao id DESSE servidor e deixe ativado antes de iniciar:

```bash
python packaging/licencias.py maquina                     # no servidor, uma vez
python packaging/licencias.py firmar --plan owner \
    --maquina <id impresso acima> \
    --email <seu-email>                                    # na SUA máquina, com sua privada
export MVDG_SERVER_LICENSE_TOKEN="<token impresso>"        # no servidor, antes de iniciar
./run_server.sh
```

O dashboard abre desbloqueado para o primeiro navegador que chegar —
ninguém toca a aba Licença. Um token vencido, copiado errado ou atado a
outra máquina não ativa nada: o servidor continua no plano que já tinha.

### API para BI
Duplo clique em **`MV_DataGovernance_API.bat`** → `http://127.0.0.1:8600/docs`.
Guia por ferramenta: [`docs/BI_INTEGRATION.md`](BI_INTEGRATION.md).

### O que é governança de dados? (DAMA-DMBOK)
Explicado para técnicos e não técnicos, com o mapeamento das 11 áreas do
padrão DAMA-DMBOK contra o que esta plataforma realmente faz:
[`docs/DMBOK.md`](DMBOK.md). O mesmo conteúdo aparece ao vivo dentro do
programa, na aba **Ajuda**.
