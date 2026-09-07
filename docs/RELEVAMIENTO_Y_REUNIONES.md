# Relevamiento y reuniones · Discovery and meetings · Levantamento e reuniões

**ES:** Los dos módulos que cubren lo que pasa **antes** de tocar un dato: las
preguntas que hay que hacerle al cliente, y lo que se dijo en las reuniones.
Los dos se organizan por las **mismas 12 etapas del pipeline** que documenta
[`mvdg/pipeline_doc.py`](../mvdg/pipeline_doc.py) — no una taxonomía paralela.

---

## 1 · Relevamiento (pestaña «Relevamiento»)

**ES:** 38 preguntas repartidas por área del pipeline, mínimo 3 por área.
Cada una trae:

| Campo | Para qué |
|---|---|
| **Pregunta** | Se lee en voz alta tal cual |
| **Por qué se pregunta** | Qué se rompe si no se sabe. Es lo que permite decidir qué saltear cuando hay 40 minutos y no dos horas |
| **A quién preguntarle** | El rol que suele tener la respuesta. Preguntarle a la persona equivocada no da una respuesta mala: da una inventada |
| **Repreguntas** | Qué volver a preguntar cuando la respuesta quedó a medias |

Se anota **quién respondió** (nombre y área) y **qué respondió**. Todo se
guarda en la carpeta de ese cliente: las respuestas de Conaprole no viajan en
el mismo archivo que las de otra empresa.

### El casillero de repreguntas funciona sin internet

**ES:** Es la decisión de diseño que sostiene el módulo. Una respuesta a
medias tiene formas reconocibles y reconocerlas no necesita un modelo:

- se preguntó *«cada cuánto»* o *«cuántos»* y la respuesta no trae ningún número;
- la respuesta dice *«depende»*, *«más o menos»*, *«creo que»*, *«a veces»*;
- se preguntó por un responsable y no quedó ningún nombre ni área;
- la respuesta tiene menos de seis palabras.

Cada una dispara una repregunta concreta, más las que el banco ya trae
escritas para esa pregunta puntual. Un relevamiento se hace en la sala de
reuniones de un cliente, que es exactamente donde puede no haber red.

Con una clave de IA configurada aparece además el botón **«Pedirle
repreguntas a la IA»**, que genera repreguntas sobre la respuesta exacta. Ese
botón manda la pregunta y la respuesta del cliente al proveedor configurado —
está dicho en el propio botón.

**EN:** 38 questions split by pipeline area, at least 3 per area, each with
why it is asked, who to ask, and follow-ups. The follow-up box is computed
locally and needs no internet: a discovery session happens in the client's
meeting room. An AI button adds generated follow-ups when a key is
configured, and says so.

**PT:** 38 perguntas divididas por área do pipeline, no mínimo 3 por área,
cada uma com por que se pergunta, a quem perguntar e reperguntas. O campo de
reperguntas é calculado localmente e não precisa de internet. Um botão de IA
acrescenta reperguntas geradas quando há chave configurada, e avisa.

---

## 2 · Reuniones (pestaña «Reuniones»)

**ES:** De la reunión a la minuta: **quién dijo qué**, con el minuto de cada
cita, y qué le toca a cada etapa del pipeline.

### De dónde puede salir la reunión

| Camino | Cuándo | Necesita |
|---|---|---|
| **Transcripción de la videollamada** ⭐ | Zoom, Teams, Meet, WebEx | Nada: se lee acá (`.vtt`, `.srt`, `.txt`) |
| **Grabar acá** | Reunión presencial | Micrófono. La transcripción es opcional y con clave |
| **Subir un audio** | Grabación previa | Clave de IA para transcribir |
| **Pegar el texto** | Notas escritas a mano | Nada |

**ES:** El primero es el recomendado y por una razón concreta: la plataforma
**ya sabe quién tenía el micrófono abierto**, así que la transcripción viene
con el orador identificado. Un micrófono de sala da un solo canal y no puede
dar eso.

> **ES:** El programa **no adivina** quién habló cuando la transcripción no lo
> trae. Ponerle en la boca a alguien algo que no dijo es peor que dejar la
> intervención sin asignar — y una minuta que hace eso una vez deja de ser
> creíble entera.

### Qué saca de la reunión

- **Quién habló**: intervenciones, palabras, minutos y peso. Si el 80% lo
  habló el consultor, no fue un relevamiento: fue una presentación.
- **Decisiones, compromisos, riesgos, pendientes y preguntas abiertas**, cada
  uno con la **cita textual** y el minuto. Nunca parafraseados: un
  *«yo no dije eso»* se gana mostrando el minuto, no un resumen.
- **Cruce con las 12 etapas del pipeline**: qué dijeron que toca ingesta,
  calidad, linaje. Es lo que convierte la minuta en trabajo.

### Transcribir manda el audio a un tercero

**ES:** Y en este producto eso no es un detalle técnico: el audio es una
reunión de un cliente, donde se habla de sus sistemas y su gente con nombre y
apellido. Por eso:

- está **apagado** por defecto y no se enciende solo;
- la pantalla lo pide **cada vez**, con el nombre del proveedor adelante — no
  una casilla que alguien marcó hace tres meses;
- sin la clave del usuario esta función no hace nada, y el módulo sigue
  funcionando entero con la transcripción de la plataforma, que es el camino
  recomendado: ahí el audio nunca sale de donde ya estaba.

**ES:** No se transcribe localmente porque un modelo de voz en la PC arrastra
PyTorch: cientos de megas más los pesos, dentro del instalador que baja cada
cliente. La alternativa honesta no es transcribir peor — es no transcribir
nosotros.

**EN:** Transcribing sends the audio to a third party. It is off by default,
asked for every time with the provider named, and does nothing without the
user's own key. Local transcription would drag PyTorch into every client's
installer.

**PT:** Transcrever envia o áudio a um terceiro. Está desligado por padrão, é
pedido a cada vez com o provedor nomeado, e não faz nada sem a chave do
usuário. Transcrição local arrastaria o PyTorch para dentro do instalador de
cada cliente.

---

## Dónde están

**ES:** En las dos interfaces, con las mismas funciones:

- **Panel completo** (`streamlit run app/app.py`, modo servidor): pestañas
  «Relevamiento» y «Reuniones».
- **Escritorio (`.exe` / paquete portable para la VM del cliente)**: vistas
  «Relevamiento» y «Reuniones» en la interfaz React.

**ES:** El motor es **el mismo** en las dos: el banco de preguntas, el
detector de respuestas a medias y el parser de transcripciones viven en
Python y la vista de escritorio los consulta por la API. Hay un test que lo
fija — si alguien copiara el banco de preguntas dentro del JavaScript «para
que ande sin el servidor», el relevamiento que se hace en la VM del cliente
dejaría de ser el mismo trabajo que el del panel, y el que se probaría menos
sería justo el del cliente.

**EN:** Both interfaces, same features, one engine: the desktop view queries
the Python engine over the API. A test enforces it.

**PT:** As duas interfaces, mesmas funções, um só motor: a visão de desktop
consulta o motor Python pela API. Um teste garante isso.

## Salida

**ES:** Los dos módulos exportan a **HTML, Word y PDF** (y a Excel), con los
mismos escritores sin dependencias nuevas que usa la pestaña de Trazabilidad.
En el escritorio los arma el servidor y bajan como una descarga normal: el
escritor de PDF y Word es Python, y reimplementarlo en JavaScript daría dos
escritores que se separan en el primer cambio.

## Desde la API

```
GET  /api/relevamiento/preguntas?lang=es      el banco entero
GET  /api/relevamiento/{client_id}?lang=es    lo respondido + cobertura
POST /api/relevamiento/{client_id}            anotar una respuesta
POST /api/relevamiento/repreguntas            qué repreguntar (local)
POST /api/reuniones/minuta                    transcripción -> minuta
GET  /api/relevamiento/{client_id}/documento  el relevamiento como archivo
POST /api/reuniones/documento                 la minuta como archivo
GET  /api/reuniones/transcripcion             ¿hay clave para transcribir?
POST /api/reuniones/transcribir               audio -> texto (exige confirmo=true)
GET  /api/empresas                            para el selector de empresa
```

**ES:** `/api/reuniones/minuta` recibe **texto, no audio**: transcribir manda
el audio a un tercero y esa decisión se toma en la interfaz, con el aviso
delante, no por una llamada de API que alguien podría encadenar sin darse
cuenta.
