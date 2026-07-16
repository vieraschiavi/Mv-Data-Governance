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
   `dist\MVDataGovernance_Setup_v1.0.0.exe`, que durante la instalación
   crea el acceso del **Menú Inicio** y ofrece con una casilla el del
   **Escritorio** — el cliente elige.

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
   `dist\MVDataGovernance_Setup_v1.0.0.exe` installer with shortcuts.

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
   instalador `dist\MVDataGovernance_Setup_v1.0.0.exe` com atalhos.

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

### API para BI
Duplo clique em **`MV_DataGovernance_API.bat`** → `http://127.0.0.1:8600/docs`.
Guia por ferramenta: [`docs/BI_INTEGRATION.md`](BI_INTEGRATION.md).

### O que é governança de dados? (DAMA-DMBOK)
Explicado para técnicos e não técnicos, com o mapeamento das 11 áreas do
padrão DAMA-DMBOK contra o que esta plataforma realmente faz:
[`docs/DMBOK.md`](DMBOK.md). O mesmo conteúdo aparece ao vivo dentro do
programa, na aba **Ajuda**.
