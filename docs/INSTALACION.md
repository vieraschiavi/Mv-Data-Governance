# Instalación · Installation · Instalação

**ES:** Dos formas de instalar, bien separadas, con el **mismo programa** en
las dos. La diferencia no es qué funciones tenés: es **dónde queda guardado
lo que hacés**.

**EN:** Two ways to install, clearly separated, with the **same program** in
both. The difference is not which features you get: it is **where your work
is stored**.

**PT:** Duas formas de instalar, bem separadas, com o **mesmo programa** nas
duas. A diferença não é quais funções você tem: é **onde fica guardado o que
você faz**.

---

## Cuál me toca / Which one is mine / Qual é a minha

| | **Instalación normal** | **VM o equipo del cliente (portable)** |
|---|---|---|
| **ES** — Cuándo | Tu laptop, o la de la consultora que te contrata | La VM o la PC del cliente al que le estás haciendo el trabajo |
| **EN** — When | Your laptop, or the one from the consultancy that hired you | The VM or PC of the client you are doing the work for |
| **PT** — Quando | Seu notebook, ou o da consultoria que te contrata | A VM ou o PC do cliente para quem você faz o trabalho |
| Archivo / File | `MVDataGovernance_Setup_<ver>.exe` | `MVDataGovernance_VM_<ver>.zip` |
| ¿Se instala? | Sí (instalador de Windows) | No: se descomprime y se abre |
| ¿Administrador? | No (instala por usuario) | No |
| ¿Internet? | No | No |
| ¿Toca el registro? | Sí (para el desinstalador) | No |
| Accesos directos | Escritorio + menú Inicio | Ninguno (se abre el `.exe` de la carpeta) |
| Tus datos van a | Tu perfil de usuario | La subcarpeta `Datos`, dentro de la carpeta del programa |
| Para desinstalar | Agregar o quitar programas | Borrar la carpeta |

Los dos se bajan del mismo lugar:
<https://github.com/vieraschiavi/Mv-Data-Governance/releases/tag/cliente-latest>

---

## Ejemplo real / Real example / Exemplo real

**ES:** Sos consultor de Practia y te asignan a Conaprole.

1. En **tu laptop de Practia**: `MVDataGovernance_Setup_<ver>.exe`. Doble
   clic, elegís carpeta, y queda instalado como cualquier programa. Ahí
   preparás la demo, cargás tus datasets de prueba y guardás tus conexiones.
2. En **la VM de Conaprole**: `MVDataGovernance_VM_<ver>.zip`. Lo
   descomprimís en una carpeta donde tengas permiso de escribir (Documentos,
   `D:\`, un disco de red) y abrís `MV Data Governance.exe`. No pide
   administrador, no necesita internet y no deja nada fuera de esa carpeta.
   Cuando terminás el proyecto: copiás la subcarpeta `Datos` si te querés
   llevar el trabajo, y borrás la carpeta entera. En la VM no queda nada.

**EN:** You are a consultant at Practia assigned to Conaprole. On **your
Practia laptop**, the installer. On **Conaprole's VM**, the portable ZIP,
unzipped anywhere you can write. When the project ends, copy the `Datos`
subfolder if you want to keep the work, then delete the whole folder —
nothing is left on the VM.

**PT:** Você é consultor da Practia alocado na Conaprole. No **seu notebook
da Practia**, o instalador. Na **VM da Conaprole**, o ZIP portátil,
descompactado em qualquer lugar onde você possa escrever. Ao terminar o
projeto, copie a subpasta `Datos` se quiser guardar o trabalho e apague a
pasta inteira — não sobra nada na VM.

---

## Cómo sabe el programa en qué modo está

**ES:** Lo trae el paquete, no lo configura nadie. El ZIP portable incluye un
archivo `MODO_VM_CLIENTE.txt` en su carpeta raíz; el instalador no lo
incluye. El programa lo busca al arrancar (`mvdg/install_mode.py`) y decide
dónde guardar. En la pestaña **Ayuda → Cómo está instalado** (o en la
pestaña **Licencia** de la versión `.exe`) siempre se ve el modo vigente y
la carpeta exacta donde están tus datos.

**EN:** The package carries it, nobody configures it. The portable ZIP ships
a `MODO_VM_CLIENTE.txt` file in its root folder; the installer does not. The
program looks for it at startup (`mvdg/install_mode.py`) and decides where to
store. The **Help → How this is installed** tab (or the **License** tab in
the `.exe` version) always shows the current mode and the exact folder where
your data lives.

**PT:** O pacote traz isso, ninguém configura. O ZIP portátil inclui um
arquivo `MODO_VM_CLIENTE.txt` na pasta raiz; o instalador não. O programa o
procura ao iniciar (`mvdg/install_mode.py`) e decide onde guardar. Na aba
**Ajuda → Como está instalado** (ou na aba **Licença** da versão `.exe`)
sempre se vê o modo atual e a pasta exata onde ficam seus dados.

> **ES:** Si descomprimís el portable en una carpeta de solo lectura (por
> ejemplo `C:\Archivos de programa`), el programa **abre igual** pero guarda
> en tu perfil de usuario, y te avisa en pantalla. En una VM que se resetea
> al cerrar sesión eso significa perder el trabajo: movelo a una carpeta
> donde puedas escribir.
>
> **EN:** If you unzip the portable into a read-only folder, the program
> **still opens** but stores in your user profile, and says so on screen. On
> a VM that resets at logoff that means losing the work: move it to a folder
> you can write to.
>
> **PT:** Se você descompactar o portátil em uma pasta somente leitura, o
> programa **abre mesmo assim**, mas guarda no seu perfil de usuário e avisa
> na tela. Numa VM que se reinicia ao sair isso significa perder o trabalho:
> mova para uma pasta onde possa escrever.

---

## Licencia / License / Licença

**ES:** Las dos formas arrancan en plan demo y se desbloquean con la misma
clave, pegada en la pestaña Licencia. La licencia queda guardada donde guarda
el modo: en el portable, dentro de `Datos`, así que la activás una vez por
carpeta y viaja con ella.

Ojo con una cosa: el instalador **OWNER** (el tuyo, que abre desbloqueado sin
pegar nada) lleva la licencia **atada a tu máquina**. En la VM de un cliente
ese `.exe` abre en plan demo, y está bien que así sea. Para trabajar en la VM
del cliente usá el paquete portable con tu clave comercial.

**EN:** Both ways start in demo and unlock with the same key, pasted in the
License tab. The license is stored wherever the mode stores: inside `Datos`
for the portable, so you activate it once per folder and it travels with it.
One caveat: the **OWNER** installer carries a license **bound to your
machine**, so on a client's VM it opens in demo — by design. Use the portable
package with your commercial key there.

**PT:** As duas formas iniciam no plano demo e são desbloqueadas com a mesma
chave, colada na aba Licença. A licença fica guardada onde o modo guarda:
dentro de `Datos` no portátil, então você ativa uma vez por pasta e ela viaja
junto. Uma ressalva: o instalador **OWNER** leva uma licença **atada à sua
máquina**, então na VM de um cliente ele abre em demo — de propósito. Ali use
o pacote portátil com sua chave comercial.

---

## Tercera vía / Third path / Terceira via

**ES:** Si el cliente no deja copiar ni un `.exe` a la VM, queda el despliegue
web en un servidor de la empresa (`python -m mvdg.server`), sin nada
instalado en las PCs. Ver [`MANUAL_PUESTA_EN_MARCHA.md`](MANUAL_PUESTA_EN_MARCHA.md).

**EN:** If the client will not allow even copying an `.exe` onto the VM,
there is the web deployment on a company server (`python -m mvdg.server`),
with nothing installed on the PCs.

**PT:** Se o cliente não permitir nem copiar um `.exe` para a VM, resta a
implantação web em um servidor da empresa (`python -m mvdg.server`), sem nada
instalado nos PCs.
