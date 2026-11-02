'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '../../lib/api';
import '../login/acceso.css';

export default function Panel() {
  const router = useRouter();
  const [sesion, setSesion] = useState(null);
  const [error, setError] = useState('');
  const [cerrando, setCerrando] = useState(false);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    const controlador = new AbortController();
    setError('');
    api('/sesiones/actual', { signal: controlador.signal })
      .then(setSesion)
      .catch((fallo) => {
        if (fallo.name === 'AbortError') return;
        if (fallo.estado === 401) router.replace('/login');
        else setError(fallo.message);
      });
    return () => controlador.abort();
  }, [router, intento]);

  async function salir() {
    setCerrando(true);
    setError('');
    try {
      await api('/sesiones/cerrar', { method: 'POST' });
      router.replace('/login');
    } catch (fallo) {
      setError(fallo.message);
      setCerrando(false);
    }
  }

  return (
    <main id="contenido" className="acceso-formulario">
      <Link href="/panel" className="brand">
        Turno Group
      </Link>
      <h1>Mi espacio</h1>
      {error && (
        <div role="alert">
          <p>{error}</p>
          <button onClick={() => setIntento(intento + 1)}>Volver a intentar</button>
        </div>
      )}
      {!sesion && !error && <p role="status">Consultando tu sesión…</p>}
      {sesion && (
        <>
          <h2>Hola, {sesion.usuario.nombre}</h2>
          <p>Tu sesión está activa.</p>
          <dl>
            <dt>Correo</dt>
            <dd>{sesion.usuario.correo}</dd>
            <dt>Rol</dt>
            <dd>
              {sesion.rol_empresa || sesion.usuario.rol_plataforma || 'Sin asignación'}
            </dd>
          </dl>
          <button className="button button-primary" disabled={cerrando} onClick={salir}>
            {cerrando ? 'Cerrando sesión…' : 'Cerrar sesión'}
          </button>
        </>
      )}
    </main>
  );
}
