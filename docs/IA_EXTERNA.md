# ✨ IA externa opcional para sugerencias de corrección

Cada falla de calidad que detecta el programa ya trae, al lado, una
**sugerencia de corrección 100% local** (`mvdg/remediation.py`): causa
probable, qué hacer con las filas ya cargadas, cómo evitar que vuelva a
pasar y a qué rol asignarlo. Esto funciona **siempre**, sin conexión a
internet, y es el comportamiento por defecto.

Además, de forma **opcional**, el programa puede pedir una segunda
sugerencia generada en vivo por un modelo de IA externo (Claude, ChatGPT o
Gemini), si vos configurás tu propia API key. Sin esa configuración, el
programa funciona exactamente igual que siempre — la IA externa nunca se
activa sola.

## Reglas de diseño (no negociables)

- **Apagado por defecto.** Sin ninguna variable de entorno configurada, no
  se hace ninguna llamada externa. La app ni siquiera muestra el botón.
- **La API key la ponés vos**, como variable de entorno en tu propia
  máquina o servidor. El programa nunca la pide, nunca la guarda en disco,
  nunca la manda a ningún lado más que al proveedor que elegiste.
  **Nunca la pegues en el chat conmigo ni la subas al repositorio.**
- **Solo se manda metadato de la falla** (dataset, columna, dimensión DAMA,
  descripción de la regla, cantidad de filas afectadas) — **nunca datos
  reales de tus filas**. La llamada solo ocurre cuando vos hacés clic en el
  botón "Pedir sugerencia a…" de una regla puntual, nunca automáticamente.
- **Cualquier error** (sin conexión, key inválida, timeout, respuesta rara)
  cae en silencio a la sugerencia local; nunca rompe la pantalla.

## Cómo activarla

Configurá **una** de estas variables de entorno con tu propia API key antes
de arrancar el programa:

| Variable | Proveedor | Modelo por defecto | Override de modelo |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Claude (Anthropic) | `claude-sonnet-5` | `MVDG_AI_MODEL_CLAUDE` |
| `OPENAI_API_KEY` | ChatGPT (OpenAI) | `gpt-4o-mini` | `MVDG_AI_MODEL_OPENAI` |
| `GEMINI_API_KEY` | Gemini (Google) | `gemini-1.5-flash` | `MVDG_AI_MODEL_GEMINI` |

Si cargás más de una, el programa usa la de mayor prioridad (Claude >
ChatGPT > Gemini) salvo que fuerces una en particular con:

| Variable | Qué hace |
|---|---|
| `MVDG_AI_PROVIDER` | Fuerza un proveedor puntual (`claude`, `openai` o `gemini`) entre los que tengan key cargada. |

Ejemplo (Linux/macOS):

```bash
export ANTHROPIC_API_KEY="tu-api-key-de-anthropic"
./run.sh
```

Ejemplo (Windows, `.bat`):

```bat
set ANTHROPIC_API_KEY=tu-api-key-de-anthropic
MV_DataGovernance.bat
```

Con la key cargada, en la pestaña **Calidad** (y en "Mis datos → Dataset de
ejemplo") cada falla muestra, además de la sugerencia local, un botón
**"✨ Pedir sugerencia a Claude (Anthropic)"** (o ChatGPT/Gemini según
corresponda) que trae una segunda opinión generada en vivo.

## También audita y refactoriza DAX (pestaña 🔷 Power BI)

La misma key opcional habilita un segundo uso: en la pestaña **🔷 Power BI**,
cada medida de tu modelo `.pbip` trae un botón **"✨ Refactor DAX con
{proveedor}"** que le pide al modelo evaluar anti-patrones (iteradores
innecesarios, `FILTER` sobre tablas enteras, columnas calculadas que
deberían ser medidas, falta de variables) y proponer una versión mejorada.
Mismas reglas de diseño: solo se manda el nombre de la medida, la tabla y su
expresión DAX — **nunca datos reales** — y cualquier error cae en silencio
sin bloquear la pantalla.

## ¿Por qué no está GitHub Copilot en la lista?

Copilot no expone una API REST simple de "pedime un texto" con solo una API
key, como sí tienen Claude/OpenAI/Gemini — se integra vía OAuth de GitHub
dentro de un IDE, no como llamada directa de servidor a servidor. Si en el
futuro GitHub publica una API de ese tipo, se puede agregar con el mismo
patrón (`mvdg/ai_provider.py`).

## Verificación

`python -m mvdg.selfcheck` incluye un chequeo ("IA externa opcional")
que confirma que, sin ninguna key configurada, el comportamiento es
idéntico al de antes de que existiera esta función.
