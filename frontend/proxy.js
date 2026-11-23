import { NextResponse } from 'next/server.js';
import { randomBytes } from 'node:crypto';
import { politicaContenido } from './lib/politica-contenido.mjs';

export function proxy(request) {
  const nonce = randomBytes(32).toString('base64');
  const politica = politicaContenido(nonce, process.env.NODE_ENV === 'development');
  const headers = new Headers(request.headers);
  // Sustituyo valores recibidos: el navegador no elige su propio nonce.
  headers.set('x-nonce', nonce);
  headers.set('content-security-policy', politica);
  const response = NextResponse.next({ request: { headers } });
  response.headers.set('content-security-policy', politica);
  // Un documento con nonce no se reutiliza entre solicitudes ni cuentas.
  response.headers.set('Cache-Control', 'private, no-store');
  return response;
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|images/|fonts/|workers/).*)'],
};
