'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '../../lib/api';
import './acceso.css';

export default function Login() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [enviando, setEnviando] = useState(false);

  async function entrar(event) {
    event.preventDefault();
    if (enviando) return;
    const datos = new FormData(event.currentTarget);
    setError('');
    setEnviando(true);
    try {
      await api('/sesiones/iniciar', {
        method: 'POST',
        body: { correo: datos.get('correo'), clave: datos.get('clave') },
      });
      router.replace('/panel');
    } catch (fallo) {
      setError(fallo.message);
      setEnviando(false);
    }
  }

  return (
    <main id="contenido" className="acceso">
      <aside className="acceso-historia">
        <Link href="/" className="brand">Turno Group</Link>
        <h2>Más tiempo para quienes se sientan a tu mesa.</h2>
        <p>El orden detrás de un buen servicio.</p>
      </aside>
      <section className="acceso-formulario">
        <Link href="/">← Volver al inicio</Link>
        <h1>Inicia sesión en tu negocio</h1>
        <p>Bienvenido de vuelta.</p>
        {error && <p role="alert">{error}</p>}
        <form onSubmit={entrar}>
          <label htmlFor="correo">Correo electrónico</label>
          <input id="correo" name="correo" type="email" autoComplete="email" maxLength={254} required />
          <label htmlFor="clave">Contraseña</label>
          <input id="clave" name="clave" type="password" autoComplete="current-password" maxLength={128} required />
          <button className="button button-primary" disabled={enviando}>
            {enviando ? 'Entrando…' : 'Entrar a mi negocio'}
          </button>
        </form>
      </section>
    </main>
  );
}
