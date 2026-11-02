'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import '../login/acceso.css';

export default function RestablecerClave() {
  const [codigo, setCodigo] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState('');
  const [terminado, setTerminado] = useState(false);

  useEffect(() => {
    const url = new URL(window.location.href);
    const recibido = url.searchParams.get('codigo');
    if (recibido) {
      setCodigo(recibido);
      url.searchParams.delete('codigo');
      window.history.replaceState(null, '', url.pathname + url.search + url.hash);
    }
  }, []);

  async function restablecer(event) {
    event.preventDefault();
    if (enviando) return;
    const formulario = event.currentTarget;
    const datos = new FormData(formulario);
    setError('');
    if (datos.get('clave') !== datos.get('confirmacion')) {
      setError('Las contraseñas no coinciden.');
      return;
    }
    setEnviando(true);
    try {
      await api('/recuperaciones-clave/restablecer', {
        method: 'POST', body: { codigo, nueva_clave: datos.get('clave') },
      });
      formulario.reset();
      setCodigo('');
      setTerminado(true);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main id="contenido" className="acceso-formulario">
      <Link className="brand" href="/">Turno Group</Link>
      <h1>Elige una nueva contraseña</h1>
      {error && <p role="alert">{error}</p>}
      {terminado ? (
        <p role="status">Tu contraseña quedó actualizada. Inicia sesión con tu nueva clave.</p>
      ) : (
        <form onSubmit={restablecer}>
          <label htmlFor="codigo">Código recibido por correo</label>
          <input id="codigo" name="codigo" autoComplete="off" minLength={40} maxLength={128} value={codigo} onChange={(event) => setCodigo(event.target.value)} required />
          <label htmlFor="clave">Nueva contraseña · mínimo 12 caracteres</label>
          <input id="clave" name="clave" type="password" autoComplete="new-password" minLength={12} maxLength={128} required />
          <label htmlFor="confirmacion">Repite la contraseña</label>
          <input id="confirmacion" name="confirmacion" type="password" autoComplete="new-password" minLength={12} maxLength={128} required />
          <button className="button button-primary" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Guardar contraseña'}
          </button>
        </form>
      )}
      <p><Link href="/recuperar-clave">Solicitar otro código</Link></p>
      <Link href="/login">Volver a iniciar sesión</Link>
    </main>
  );
}
