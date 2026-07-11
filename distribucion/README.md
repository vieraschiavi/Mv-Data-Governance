# 📦 Distribución · Distribution · Distribuição

**ES:** Dos formas de entregar MV Data Governance según las restricciones de
TI de cada empresa — **mismas funcionalidades en ambas**. La ficha de cada
empresa (pestaña 🏢 Empresas del programa) registra su restricción y
recomienda el paquete automáticamente.

**EN:** Two ways to deliver MV Data Governance depending on each company's IT
restrictions — **same features in both**. Each company's record (🏢 Companies
tab in the program) stores its restriction and recommends the package
automatically.

**PT:** Duas formas de entregar o MV Data Governance conforme as restrições
de TI de cada empresa — **mesmas funcionalidades em ambas**. A ficha de cada
empresa (aba 🏢 Empresas do programa) registra a restrição e recomenda o
pacote automaticamente.

| Carpeta / Folder | Para qué empresa / For which company | Requisitos / Requirements |
|---|---|---|
| [`opcion_A_instalador_exe/`](opcion_A_instalador_exe/LEEME.md) | ES: permite instalar software (.exe) · EN: allows installing software · PT: permite instalar software | ❌ Python **no** requerido / not required |
| [`opcion_B_portable_bat/`](opcion_B_portable_bat/LEEME.md) | ES: bloquea .exe pero permite Python · EN: blocks .exe but allows Python · PT: bloqueia .exe mas permite Python | ✅ Python 3.10+ |

**ES:** ¿Ninguna de las dos? Tercera vía: despliegue 100% web en un servidor
de la empresa (`streamlit run app/app.py`), sin nada instalado en las PCs.

**EN:** Neither fits? Third path: 100% web deployment on a company server
(`streamlit run app/app.py`), nothing installed on PCs.

**PT:** Nenhuma serve? Terceira via: implantação 100% web num servidor da
empresa (`streamlit run app/app.py`), nada instalado nos PCs.

---

Para generar los ZIP de entrega / To build the delivery ZIPs / Para gerar os
ZIPs de entrega:

```bash
python packaging/build_release.py        # → dist/*.zip
```
