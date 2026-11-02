'use client';

import Link from 'next/link';
import { useState } from 'react';
import { api } from '../../lib/api';
import '../login/acceso.css';

export default function RecuperarClave() {
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState('');
  const [terminado, setTerminado] = useState(false);

  async function solicitar(event) {
    event.preventDefault();
    if (enviando) return;
    const datos = new FormData(event.currentTarget);
    setEnviando(true);
    setError('');
    try {
      await api('/recuperaciones-clave/solicitar', {
        method: 'POST', body: { correo: datos.get('correo') },
      });
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
      <h1>Recupera tu acceso</h1>
      <p>Escribe el correo de tu cuenta para solicitar un código.</p>
      {error && <p role="alert">{error}</p>}
      {terminado ? (
        <p role="status">Si el correo está registrado, recibirás las instrucciones para recuperar el acceso. Revisa también la carpeta de spam.</p>
      ) : (
        <form onSubmit={solicitar}>
          <label htmlFor="correo">Correo electrónico</label>
          <input id="correo" name="correo" type="email" autoComplete="email" maxLength={254} required />
          <button className="button button-primary" disabled={enviando}>
            {enviando ? 'Solicitando…' : 'Solicitar código'}
          </button>
        </form>
      )}
      <p><Link href="/restablecer-clave">Ya tengo un código</Link></p>
      <Link href="/login">Volver a iniciar sesión</Link>
    </main>
  );
}
