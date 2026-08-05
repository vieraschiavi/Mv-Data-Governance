# 🪟 Opción A · Instalador Windows (.exe)

**Para empresas que permiten instalar software.** No requiere Python en la
máquina del usuario: el instalador trae todo adentro.

**For companies that allow installing software.** No Python required on the
user's machine: the installer bundles everything.

**Para empresas que permitem instalar software.** Não requer Python na
máquina do usuário: o instalador traz tudo dentro.

---

## ⬇️ Descargar el instalador ya construido (lo más rápido)

El `.exe` **no vive dentro del repositorio**: pesa cientos de MB y GitHub
rechaza archivos de más de 100 MB — y aunque entrara, quedaría en el
historial de git para siempre y cada `git clone` tendría que bajarlo. El
lugar que GitHub provee para binarios grandes son las **Releases** (hasta
2 GB por archivo, con URL de descarga estable):

👉 **https://github.com/vieraschiavi/Mv-Data-Governance/releases/latest**

Ahí está `MVDataGovernance_Setup_v{versión}.exe`, construido automáticamente
por [`.github/workflows/instalador.yml`](../../.github/workflows/instalador.yml)
en un runner **Windows real** cada vez que se publica una versión. Ese link
es el que se le pasa a un comprador.

**Publicar una versión nueva** (crea la Release y adjunta el `.exe` solo):

```bash
git tag v1.1.0 && git push origin v1.1.0
```

**Probar un build sin publicar nada:** pestaña *Actions* → *Instalador
Windows* → *Run workflow*. Deja el `.exe` como artefacto descargable 90 días.

> El workflow verifica que el `.exe` generado pese más de 20 MB antes de
> publicarlo: un Inno Setup que falla a medias puede dejar un stub de pocos
> KB, y sin ese chequeo se publicaría igual.

---

## 🇪🇸 Cómo generar el instalador a mano (en tu PC con Windows)

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
