import { test, expect } from '@playwright/test';
import { execFileSync } from 'node:child_process';

const clave = 'Clave-navegador123!';
function datoPrueba(...argumentos) {
  return execFileSync(
    process.env.PYTHON_E2E || '../venv/bin/python',
    ['../tests/navegador/servidor.py', ...argumentos],
    { encoding: 'utf8' },
  ).trim();
}
async function api(contexto, ruta, method = 'GET', data) {
  return contexto.request.fetch(`/api/backend${ruta}`, {
    method,
    data,
    headers: { 'X-Solicitud': 'TurnoGroup', Origin: 'https://127.0.0.1:18443' },
  });
}
async function entrar(page, correo, contrasena = clave) {
  await page.goto('/login');
  await page.locator('input[name=correo]').fill(correo);
  await page.locator('input[name=clave]').fill(contrasena);
  await page.getByRole('button', { name: 'Entrar a mi negocio', exact: true }).click();
  await expect(page).toHaveURL(/\/panel/);
}

test('menu inteligente revisa precios y guarda productos y categorias al confirmar', async ({
  page,
  context,
}) => {
  await entrar(page, 'gerente1@example.com');
  await page.goto('/panel/productos');
  await page.getByRole('button', { name: 'Importar con IA', exact: true }).click();
  const modal = page.getByRole('dialog', { name: 'Importar catálogo con IA' });
  await modal
    .getByLabel('Lista de productos')
    .fill('Cafe E2E 1 a 50, pan sin precio y galleta a 8');
  await modal.getByRole('button', { name: 'Preparar catálogo', exact: true }).click();
  await expect(modal.getByLabel('Importar fila 1', { exact: true })).not.toBeChecked();
  await expect(modal.getByLabel('Precio fila 2', { exact: true })).toHaveValue('');
  const antes = await api(context, '/productos/?limite=100');
  expect((await antes.json()).data.some((p) => p.nombre === 'Pan inteligente')).toBe(
    false,
  );
  await modal.getByLabel('Precio fila 2', { exact: true }).fill('12.50');
  await expect(
    modal.getByRole('button', { name: 'Confirmar importación', exact: true }),
  ).toBeDisabled();
  await modal.getByRole('button', { name: 'Revisar cambios', exact: true }).click();
  await expect(
    modal.getByText('2 productos nuevos · 0 existentes seleccionados.'),
  ).toBeVisible();
  await modal
    .getByRole('checkbox', { name: 'Revisé los productos seleccionados y sus precios.' })
    .check();
  const confirmacion = page.waitForResponse((r) =>
    r.url().endsWith('/menu-inteligente/confirmar'),
  );
  await modal.getByRole('button', { name: 'Confirmar importación', exact: true }).click();
  expect((await confirmacion).status()).toBe(201);
  await expect(modal).not.toBeVisible();
  await expect(
    page.getByText(
      'Catálogo actualizado: 2 productos creados, 1 categorías nuevas y 0 productos existentes utilizados.',
    ),
  ).toBeVisible();
  const despues = await api(context, '/productos/?limite=100');
  const productos = (await despues.json()).data;
  expect(productos.find((p) => p.nombre === 'Pan inteligente').precio).toBe('12.50');
  expect(productos.find((p) => p.nombre === 'Cafe E2E 1').precio).toBe('50.00');
});

test('menu inteligente acepta foto y cancelar no crea productos', async ({
  page,
  context,
}) => {
  await entrar(page, 'gerente2@example.com');
  await page.goto('/panel/productos');
  await page.getByRole('button', { name: 'Importar con IA', exact: true }).click();
  const modal = page.getByRole('dialog', { name: 'Importar catálogo con IA' });
  await modal.getByLabel('Origen del catálogo').selectOption('foto');
  await modal.locator('input[type=file]').setInputFiles({
    name: 'menu.png',
    mimeType: 'image/png',
    buffer: Buffer.from(
      'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=',
      'base64',
    ),
  });
  await modal.getByRole('button', { name: 'Preparar catálogo', exact: true }).click();
  await expect(modal.getByLabel('Nombre fila 2', { exact: true })).toHaveValue(
    'Pan inteligente',
  );
  await modal.getByRole('button', { name: 'Cancelar', exact: true }).click();
  const productos = (await (await api(context, '/productos/?limite=100')).json()).data;
  expect(productos.some((p) => p.nombre === 'Pan inteligente')).toBe(false);
});

// Se recorre el formulario completo: confirmar correo no crea una cuenta ni sesion.
test('registro confirma correo y guarda el negocio solo al terminar los ocho pasos', async ({
  page,
  context,
}) => {
  await page.goto('/registro');
  await page.locator('input[name=nombre]').fill('Gerente nuevo');
  await page.locator('input[name=correo]').fill('registro-ui@example.com');
  await page.locator('input[name=clave]').fill(clave);
  await page.getByRole('button', { name: 'Continuar a la configuración' }).click();
  await expect(page.locator('input[name=codigo_verificacion]')).toBeVisible();
  await page
    .locator('input[name=codigo_verificacion]')
    .fill(datoPrueba('correo', 'registro-ui@example.com', 'verificacion'));
  await page.getByRole('button', { name: 'Continuar a la configuración' }).click();
  await expect(page).toHaveURL(/configuracion-inicial/);
  expect((await api(context, '/sesiones/actual')).status()).toBe(401);
  await page.locator('input[name=nombre]').fill('Cafeteria registrada desde navegador');
  await page.getByRole('button', { name: 'Guardar y continuar' }).click();
  await page.getByRole('button', { name: '+ Crear sucursal', exact: true }).click();
  const modal = page.getByRole('dialog');
  await modal.locator('input[name=direccion]').fill('Direccion de prueba del navegador');
  await modal.getByRole('button', { name: 'Guardar cambios' }).click();
  await expect(modal).not.toBeVisible();
  await page.getByRole('button', { name: 'Continuar →', exact: true }).click();
  await page.getByRole('checkbox', { name: 'Activar Para llevar' }).check();
  await page.getByRole('button', { name: 'Continuar →', exact: true }).click();
  await page.getByRole('checkbox', { name: 'Efectivo', exact: true }).check();
  // Descuentos, catalogo, revision y suscripcion.
  for (let paso = 0; paso < 4; paso += 1)
    await page.getByRole('button', { name: 'Continuar →', exact: true }).click();
  await page.getByLabel('Vencimiento', { exact: true }).fill('12/99');
  await page.getByLabel('CVV de prueba', { exact: true }).fill('123');
  const registro = page.waitForResponse(
    (r) =>
      r.url().endsWith('/usuarios/registro-negocio') && r.request().method() === 'POST',
  );
  await page
    .getByRole('button', { name: 'Crear cuenta e iniciar mes de prueba' })
    .click();
  expect((await registro).status()).toBe(201);
  await expect(page).toHaveURL(/\/panel/);
  const actual = await api(context, '/sesiones/actual');
  expect(actual.status()).toBe(200);
  expect((await actual.json()).rol_empresa).toBe('Gerente');
  const cookie = (await context.cookies()).find((c) => c.name === 'sesion_turnogroup');
  expect(cookie.httpOnly).toBe(true);
  expect(cookie.secure).toBe(true);
  expect(cookie.sameSite).toBe('Lax');
});

test('mesero registra un pedido pendiente y cobra una sola vez desde pedidos', async ({
  page,
  context,
}) => {
  await entrar(page, 'mesero1@example.com');
  await page.goto('/nuevo-pedido');
  const producto = page
    .getByRole('article')
    .filter({ has: page.getByRole('heading', { name: 'Cafe E2E 1', exact: true }) });
  await producto.getByRole('button', { name: 'Agregar', exact: true }).click();
  await page.getByRole('button', { name: 'Continuar →', exact: true }).click();
  await page
    .getByLabel('Nombre del cliente (requerido)', { exact: true })
    .fill('Cliente navegador');
  await page
    .getByLabel('Teléfono de contacto (requerido)', { exact: true })
    .fill('99991234');
  await page
    .getByRole('checkbox', { name: 'Registrar que ya se recibió el pago' })
    .uncheck();
  const respuesta = page.waitForResponse(
    (r) =>
      /\/pedidos\/?$/.test(r.url()) &&
      r.request().method() === 'POST' &&
      r.status() !== 308,
  );
  await page.getByRole('button', { name: 'Registrar pedido', exact: true }).click();
  const creado = await respuesta;
  expect(creado.status()).toBe(201);
  const pedido = await creado.json();
  expect(pedido.estado).toBe('Abierto');
  await page.goto(`/panel/pedidos?pedido=${pedido.id}`);
  await page.getByRole('button', { name: 'Registrar cobro', exact: true }).click();
  await page.getByRole('button', { name: 'Sí, registrar cobro', exact: true }).click();
  await expect(
    page.getByText('Cobro registrado', { exact: false }).first(),
  ).toBeVisible();
  const doble = await api(context, `/pedidos/${pedido.id}/cobrar`, 'POST', {
    id_metodo_pago: pedido.id_metodo_pago,
  });
  expect(doble.status()).toBe(409);
  expect((await (await api(context, `/pedidos/${pedido.id}`)).json()).estado).toBe(
    'Cerrado',
  );
});

test('invitacion crea acceso con su rol y no se puede volver a usar', async ({
  page,
  context,
  browser,
}) => {
  await entrar(page, 'gerente1@example.com');
  const sucursal = (await (await api(context, '/sesiones/actual')).json()).id_sucursal;
  const respuesta = await api(context, '/invitaciones-laborales/', 'POST', {
    correo: 'invitado-ui@example.com',
    rol: 'Mesero',
    sucursales: [sucursal],
  });
  expect(respuesta.status()).toBe(201);
  const codigo = datoPrueba('correo', 'invitado-ui@example.com', 'invitacion');
  const invitado = await browser.newContext({
    ignoreHTTPSErrors: true,
    baseURL: 'https://127.0.0.1:18443',
  });
  try {
    const ventana = await invitado.newPage();
    await ventana.goto(`/invitacion#codigo=${encodeURIComponent(codigo)}`);
    await ventana.locator('input[name=nombre]').fill('Mesero invitado');
    await ventana.locator('input[name=clave]').fill(clave);
    await ventana
      .getByRole('button', { name: 'Crear acceso y aceptar invitación' })
      .click();
    await expect(ventana).toHaveURL(/\/panel/);
    expect((await (await api(invitado, '/sesiones/actual')).json()).rol_empresa).toBe(
      'Mesero',
    );
    expect(
      (
        await api(invitado, '/invitaciones-laborales/registrar', 'POST', {
          codigo,
          nombre: 'Repetido',
          clave,
        })
      ).status(),
    ).toBe(400);
    expect((await api(invitado, '/finanzas/dashboard')).status()).toBe(403);
    expect((await api(invitado, '/invitaciones-laborales/')).status()).toBe(403);
  } finally {
    await invitado.close();
  }
});

test('recuperacion y cambio de correo revocan sesiones y codigos anteriores', async ({
  page,
  context,
}) => {
  await page.goto('/recuperar-clave');
  await page.locator('input[name=correo]').fill('administrador1@example.com');
  await page.getByRole('button', { name: 'Solicitar código', exact: true }).click();
  await expect(page.getByRole('status')).toBeVisible();
  const codigo = datoPrueba('correo', 'administrador1@example.com', 'recuperacion');
  await page.goto('/restablecer-clave');
  await page.locator('input[name=codigo]').fill(codigo);
  await page.locator('input[name=clave]').fill('Clave-nueva-navegador123!');
  await page.getByRole('button', { name: 'Guardar contraseña' }).click();
  await expect(page.getByRole('status')).toContainText('actualizada');
  await entrar(page, 'administrador1@example.com', 'Clave-nueva-navegador123!');
  // Emito otro codigo antes de cambiar el correo: luego debe dejar de funcionar.
  await api(context, '/recuperaciones-clave/solicitar', 'POST', {
    correo: 'administrador1@example.com',
  });
  const anterior = datoPrueba('correo', 'administrador1@example.com', 'recuperacion');
  await page.goto('/panel/cuenta');
  await page.getByLabel('Nuevo correo', { exact: true }).fill('admin-nuevo@example.com');
  await page
    .getByLabel('Contraseña actual', { exact: true })
    .fill('Clave-nueva-navegador123!');
  await page.getByRole('button', { name: 'Enviar código', exact: true }).click();
  await expect(page.getByLabel('Código recibido', { exact: true })).toBeVisible();
  await page
    .getByLabel('Código recibido', { exact: true })
    .fill(datoPrueba('correo', 'admin-nuevo@example.com', 'cambio_correo'));
  await page
    .getByLabel('Contraseña actual', { exact: true })
    .fill('Clave-nueva-navegador123!');
  await page.getByRole('button', { name: 'Confirmar correo', exact: true }).click();
  await expect(page).toHaveURL(/\/login/);
  expect((await api(context, '/sesiones/actual')).status()).toBe(401);
  expect(
    (
      await api(context, '/recuperaciones-clave/restablecer', 'POST', {
        codigo: anterior,
        nueva_clave: 'Clave-que-no-debe-guardar123!',
      })
    ).status(),
  ).toBe(400);
  await entrar(page, 'admin-nuevo@example.com', 'Clave-nueva-navegador123!');
  await api(context, '/sesiones/cerrar', 'POST');
  expect((await api(context, '/sesiones/actual')).status()).toBe(401);
});

for (const rol of ['Mesero', 'Gerente']) {
  test(`${rol} no puede consultar ni modificar productos de otra empresa`, async ({
    page,
    context,
  }) => {
    await entrar(page, `${rol.toLowerCase()}1@example.com`);
    const lista = await api(context, '/productos/');
    const productos = (await lista.json()).data;
    expect(productos.some((p) => p.nombre === 'Cafe E2E 2')).toBe(false);
    expect((await api(context, '/productos/2')).status()).toBe(404);
    const cambio = await api(context, '/productos/2', 'PATCH', {
      nombre: 'Cambio ajeno',
    });
    expect(cambio.status()).toBe(rol === 'Gerente' ? 404 : 403);
    if (rol === 'Mesero') {
      expect((await api(context, '/finanzas/dashboard')).status()).toBe(403);
      expect((await api(context, '/invitaciones-laborales/')).status()).toBe(403);
    }
  });
}

test('respaldo MFA permite entrar una vez y no acepta reutilizacion', async ({
  page,
  context,
}) => {
  const codigo = datoPrueba('respaldo');
  await page.goto('/login');
  await page.locator('input[name=correo]').fill('plataforma@example.com');
  await page.locator('input[name=clave]').fill(clave);
  await page.getByRole('button', { name: 'Entrar a mi negocio' }).click();
  await expect(page.locator('input[name=codigo_mfa]')).toBeVisible();
  await page.getByRole('button', { name: /Perdí mi autenticador/ }).click();
  await page.locator('input[name=codigo_recuperacion_mfa]').fill(codigo);
  await page.getByRole('button', { name: 'Entrar a mi negocio' }).click();
  await expect(page).toHaveURL(/\/panel/);
  await api(context, '/sesiones/cerrar', 'POST');
  const repetida = await api(context, '/sesiones/iniciar', 'POST', {
    correo: 'plataforma@example.com',
    clave,
    codigo_recuperacion_mfa: codigo,
  });
  expect(repetida.status()).toBe(401);
});

test('CSP bloquea scripts inyectados y conserva la hidratacion de la pagina', async ({
  page,
}) => {
  // Inserto contenido no autorizado en el HTML recibido, antes de que el navegador
  // lo interprete. page.evaluate usa el depurador y no demuestra una inyeccion real.
  await page.route('**/login', async (ruta) => {
    const respuesta = await ruta.fetch();
    const contenido = (await respuesta.text()).replace(
      /<body([^>]*)>/,
      `<body$1>
      <script>window.pruebaScriptNoAutorizado = true</script>
      <img src="/imagen-que-no-existe-e2e.png" onerror="window.pruebaEventoNoAutorizado = true" />`,
    );
    await ruta.fulfill({ response: respuesta, body: contenido });
  });
  const respuesta = await page.goto('/login');
  const politica = respuesta.headers()['content-security-policy'];
  expect(politica).toContain("'strict-dynamic'");
  expect(politica).not.toContain('unsafe-eval');
  await expect(page.locator('input[name=clave]')).toBeVisible();
  expect(await page.evaluate(() => !!window.pruebaScriptNoAutorizado)).toBe(false);
  expect(await page.evaluate(() => !!window.pruebaEventoNoAutorizado)).toBe(false);
  await page.getByRole('button', { name: 'Mostrar contraseña', exact: true }).click();
  await expect(page.locator('input[name=clave]')).toHaveAttribute('type', 'text');
  const segunda = await page.goto('/login');
  expect(segunda.headers()['content-security-policy']).not.toBe(politica);
});
