# 🪟 Opción A · Instalador Windows (.exe)

**Para empresas que permiten instalar software.** No requiere Python en la
máquina del usuario: el instalador trae todo adentro.

**For companies that allow installing software.** No Python required on the
user's machine: the installer bundles everything.

**Para empresas que permitem instalar software.** Não requer Python na
máquina do usuário: o instalador traz tudo dentro.

---

## 🇪🇸 Cómo generar el instalador (una sola vez, en una PC con Python)

1. Doble clic en **`packaging\build_exe.bat`** (en la raíz del proyecto).
2. Salida:
   - `dist\MVDataGovernance\MVDataGovernance.exe` — programa standalone
     (carpeta portable, se puede copiar a un pendrive).
   - `dist\MVDataGovernance_Setup_v1.0.0.exe` — instalador con asistente
     **trilingüe (ES/EN/PT)**, accesos directos en escritorio y menú Inicio
     (requiere [Inno Setup 6](https://jrsoftware.org/isdl.php) instalado).
3. Entregá el `Setup.exe` a la empresa. El usuario final: doble clic →
   siguiente → siguiente → listo. Sin Python, sin consola, sin internet.

## 🇬🇧 How to build the installer (once, on a PC with Python)

1. Double-click **`packaging\build_exe.bat`** (at the project root).
2. Output:
   - `dist\MVDataGovernance\MVDataGovernance.exe` — standalone program
     (portable folder, can be copied to a USB drive).
   - `dist\MVDataGovernance_Setup_v1.0.0.exe` — **trilingual (ES/EN/PT)**
     wizard installer with desktop and Start-menu shortcuts (requires
     [Inno Setup 6](https://jrsoftware.org/isdl.php)).
3. Hand the `Setup.exe` to the company. End user: double-click → next →
   next → done. No Python, no console, no internet.

## 🇧🇷 Como gerar o instalador (uma vez, num PC com Python)

1. Duplo clique em **`packaging\build_exe.bat`** (na raiz do projeto).
2. Saída:
   - `dist\MVDataGovernance\MVDataGovernance.exe` — programa standalone
     (pasta portátil, pode ser copiada para um pendrive).
   - `dist\MVDataGovernance_Setup_v1.0.0.exe` — instalador com assistente
     **trilíngue (ES/EN/PT)**, atalhos na área de trabalho e no menu Iniciar
     (requer [Inno Setup 6](https://jrsoftware.org/isdl.php)).
3. Entregue o `Setup.exe` à empresa. Usuário final: duplo clique → avançar →
   avançar → pronto. Sem Python, sem console, sem internet.
