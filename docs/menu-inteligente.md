# Importacion inteligente del catalogo

El gerente abre **Productos > Importar con IA**, pega una lista o sube una foto
JPG/PNG. FastAPI solicita una extraccion a OpenAI y compara la propuesta con el
catalogo de la empresa autenticada. Preparar y revisar no guardan productos.

La tabla permite corregir nombres, categorias y precios; desmarcar filas; y elegir
entre crear un producto o utilizar uno existente. Tras editar datos hay que pulsar
**Revisar cambios** y confirmar que se revisaron los productos y sus precios.
La confirmacion crea las categorias necesarias y los productos seleccionados en
una unica transaccion, asignandolos a la sucursal seleccionada. Utilizar un producto
existente conserva su nombre, categoria y precio; solo habilita su disponibilidad
en esa sucursal. No modifica pedidos historicos.

## Configuracion

Desde `/home/kevstpg/Documents/Personal Projects/TurnoGroup`, agrega en
`.env.pruebas` para el arranque local con `./iniciar.sh`:

```dotenv
OPENAI_API_KEY=tu_clave_de_api
OPENAI_MODELO_CATALOGO=gpt-4.1-mini-2025-04-14
LIMITE_MENU_IA=3
LIMITE_MENU_IA_DIARIO=50
```

No guardes una clave real en Git ni en variables `NEXT_PUBLIC_*`. La clave de API
requiere acceso al modelo y facturacion/saldo en la plataforma de OpenAI. La
suscripcion de ChatGPT/Codex no sustituye la autenticacion de esta llamada.
El modelo es configurable; el elegido debe admitir imagenes, Responses API y
Structured Outputs con este esquema. Reinicia la API despues de editar el entorno:
detenla con Ctrl+C en su terminal y ejecuta `./iniciar.sh`. El frontend se inicia
en otra terminal, desde la misma carpeta, con `./start.sh`.

Docker utiliza el `.env` de la raiz como indica el Compose existente; configura
alli las variables si ese es tu entorno. No cambies la base de datos para activar
IA. No se agregaron tablas ni migraciones para esta entrega.

Sin clave la funcion devuelve 503 y explica que falta configurarla; el resto del
catalogo y la importacion CSV/Excel siguen disponibles. No hay respuestas ficticias
en la aplicacion para disimular una configuracion incompleta.

## Flujo y limites

- `POST /productos/menu-inteligente/preparar`: texto de hasta 12000 caracteres o
  una foto de hasta 3 MB y 12 megapixeles. Hasta 100 productos por propuesta.
- `POST /productos/menu-inteligente/revisar`: vuelve a comprobar coincidencias
  despues de editar, sin llamar a OpenAI.
- `POST /productos/menu-inteligente/confirmar`: valida otra vez y guarda lo
  confirmado. Requiere seleccionar una sucursal autorizada.

Las tres rutas requieren sesion de gerente, empresa y suscripcion vigentes. La
empresa sale del contexto de sesion, nunca del texto ni de un ID propuesto por el
modelo. El acceso conserva la autorizacion existente: no introduce JWT de Supabase
ni afirma que exista RLS. El modelo no recibe el catalogo existente, credenciales,
herramientas ni acceso SQL. Solo recibe el documento y la moneda del negocio.

La imagen se valida, orienta y convierte a JPEG sin metadatos antes de enviarla.
No se persiste en el servidor. `store=false` evita almacenar la respuesta como un
recurso recuperable de Responses; no equivale a una garantia de retencion cero del
proveedor. La interfaz informa al usuario antes de enviar el documento.

Las coincidencias exactas normalizan acentos, espacios y mayusculas. Las
aproximadas usan similitud textual y requieren decision del gerente. No se fusionan
productos automaticamente. Las categorias inactivas y los productos desactivados
requieren revision. Se dejan vacios los precios que el modelo declara desconocidos.
El esquema valida la estructura, pero no garantiza que se haya leido bien una foto.

La confirmacion bloquea la fila de empresa en PostgreSQL para serializar las
confirmaciones inteligentes concurrentes. Las restricciones UNIQUE existentes
siguen protegiendo los nombres exactos. Un conflicto o error revierte toda la
transaccion. Un reintento del mismo catalogo nuevo devuelve 409 sin duplicarlo;
no es un protocolo de idempotencia con recuperacion automatica de respuestas.
La normalizacion no es una restriccion UNIQUE global de todos los CRUD: otros
escritores concurrentes con variaciones del nombre siguen siendo una limitacion.

Se limitan las solicitudes por IP y la extraccion por empresa: por defecto, tres
por minuto y cincuenta por dia. Los contadores usan Redis cuando esta configurado;
sin Redis son locales al proceso y se reinician con el servicio. Son limites de
solicitudes, no un presupuesto monetario. La llamada no se reintenta automaticamente;
usa timeout de conexion de 5 s, lectura de 30 s y maximo de 10000 tokens de salida.
El proxy de Next permite 45 s para esta ruta y conserva los limites de otras rutas.

La auditoria existente registra modelo, empresa, tipo de entrada, latencia,
tokens de entrada/salida de respuestas completas y resultado. No registra fotos,
texto, listas de productos ni claves. Los tokens de solicitudes fallidas no siempre
estan disponibles: la facturacion del proveedor es la referencia para el gasto.

## Verificacion reproducible

Desde la raiz:

```bash
venv/bin/python -m pytest -q tests/test_menu_inteligente.py
venv/bin/python -m scripts.evaluar_menu_ia
```

La primera prueba usa un proveedor simulado y una base aislada. Verifica permisos,
aislamiento, ausencia de escrituras en vista previa, errores del proveedor,
rollback y confirmacion. La segunda orden solamente describe la evaluacion;
no llama a OpenAI ni consume saldo.

Para evaluar realmente los quince textos sinteticos, una vez configurada la clave:

```bash
TURNO_ENV=.env.pruebas venv/bin/python -m scripts.evaluar_menu_ia --en-vivo
```

Esta orden consume saldo, no guarda productos y devuelve un codigo distinto de
cero si hay discrepancias. Compara nombres y precios contra resultados esperados;
no es un benchmark completo y puede marcar nombres equivalentes para revision.
No mide OCR de fotos: hay que preparar un conjunto de menus etiquetados, con permiso
de uso, y medir por separado nombres, precios y omisiones antes de afirmar precision.

Desde `frontend`, las pruebas de navegador utilizan la compilacion de produccion:

```bash
npm run test:proxy
npm run build
npm run test:e2e
```

Solo el lector externo se simula en `tests/navegador/servidor.py`; la conciliacion y
el guardado usan la API y una base desechable reales. Las pruebas de concurrencia
en `tests/test_concurrencia_postgres.py` requieren `TEST_DATABASE_URL` apuntando a
un PostgreSQL local de pruebas terminado en `_pytest`. CI ya ejecuta ese recorrido.

Referencias: [Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create),
[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs),
[imagenes](https://developers.openai.com/api/docs/guides/images-vision).
