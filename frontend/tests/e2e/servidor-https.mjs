// Puerta HTTPS exclusiva de las pruebas, con certificado local desechable.
import https from 'node:https';
import http from 'node:http';
import { readFileSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { spawn, execFileSync } from 'node:child_process';

const carpeta = resolve('../.archivos/e2e');
mkdirSync(carpeta, { recursive: true });
execFileSync(
  'openssl',
  [
    'req',
    '-x509',
    '-newkey',
    'rsa:2048',
    '-nodes',
    '-keyout',
    `${carpeta}/clave.pem`,
    '-out',
    `${carpeta}/cert.pem`,
    '-days',
    '1',
    '-subj',
    '/CN=127.0.0.1',
    '-addext',
    'subjectAltName=IP:127.0.0.1',
  ],
  { stdio: 'ignore' },
);
const next = spawn(
  process.execPath,
  [
    'node_modules/next/dist/bin/next',
    'start',
    '--hostname',
    '127.0.0.1',
    '--port',
    '18081',
  ],
  {
    stdio: 'inherit',
    env: {
      ...process.env,
      PUBLIC_ORIGIN: 'https://127.0.0.1:18443',
      BACKEND_URL: 'http://127.0.0.1:18080',
      BACKEND_PROXY_SECRET: 'proxy-aislado-para-pruebas-de-navegador',
      TRUST_REVERSE_PROXY: 'true',
    },
  },
);
const servidor = https.createServer(
  {
    key: readFileSync(`${carpeta}/clave.pem`),
    cert: readFileSync(`${carpeta}/cert.pem`),
  },
  (entrada, salida) => {
    const destino = http.request(
      {
        hostname: '127.0.0.1',
        port: 18081,
        path: entrada.url,
        method: entrada.method,
        headers: { ...entrada.headers, 'x-real-ip': '127.0.0.1' },
      },
      (respuesta) => {
        salida.writeHead(respuesta.statusCode, respuesta.headers);
        respuesta.pipe(salida);
      },
    );
    destino.on('error', () => {
      salida.writeHead(503);
      salida.end('Preparando pruebas');
    });
    entrada.pipe(destino);
  },
);
servidor.listen(18443, '127.0.0.1');
function cerrar() {
  next.kill('SIGTERM');
  servidor.closeAllConnections();
  servidor.close();
}
process.on('SIGTERM', cerrar);
process.on('SIGINT', cerrar);
next.on('exit', (codigo) => {
  servidor.close();
  process.exitCode = codigo || 0;
});
