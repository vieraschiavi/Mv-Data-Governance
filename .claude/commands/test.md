---
description: Correr la suite de tests y reportar
---

Corré la suite del proyecto:

```bash
pip install -q pytest httpx    # httpx es necesario para el TestClient de FastAPI
pytest tests/ -v
```

Alcance opcional (un test puntual): `pytest tests/test_core.py::$ARGUMENTS -v`

Si fallan:
1. Mostrá el output del fallo.
2. Diagnosticá la causa raíz (ojo con la paridad i18n ES/EN/PT — es la que más rompe al agregar strings).
3. Proponé (o aplicá, si se pide) el fix mínimo y volvé a correr hasta que pase.
