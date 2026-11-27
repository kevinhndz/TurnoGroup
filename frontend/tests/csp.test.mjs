import test from 'node:test';
import assert from 'node:assert/strict';
import { politicaContenido } from '../lib/politica-contenido.mjs';
import { proxy } from '../proxy.js';

test('produccion exige nonce y no permite eval ni manejadores inline', () => {
  const politica = politicaContenido('nonce-prueba');
  assert.match(politica, /script-src 'self' 'nonce-nonce-prueba' 'strict-dynamic'/);
  assert.match(politica, /script-src-attr 'none'/);
  assert.doesNotMatch(
    politica.split(';').find((parte) => parte.trim().startsWith('script-src ')),
    /unsafe-inline|unsafe-eval/,
  );
  assert.match(politicaContenido('nonce-prueba', true), /unsafe-eval/);
});

test('cada respuesta reemplaza cabeceras del cliente con un nonce distinto', () => {
  const request = new Request('http://localhost:3000/login', {
    headers: { 'x-nonce': 'controlado-por-cliente' },
  });
  const primera = proxy(request);
  const segunda = proxy(request);
  const politica = primera.headers.get('content-security-policy');
  assert.notEqual(politica, segunda.headers.get('content-security-policy'));
  assert.doesNotMatch(politica, /controlado-por-cliente/);
  assert.equal(
    primera.headers.get('x-middleware-request-content-security-policy'),
    politica,
  );
  assert.match(primera.headers.get('cache-control'), /no-store/);
});

test('el acceso limpia credenciales de una URL anterior', () => {
  const respuesta = proxy(
    new Request('http://localhost:3000/login?correo=prueba&clave=prueba'),
  );
  assert.equal(respuesta.headers.get('location'), 'http://localhost:3000/login');
});
