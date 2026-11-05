'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '../../lib/api';
import '../login/acceso.css';

export default function Registro() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [enviando, setEnviando] = useState(false);

  async function registrar(event) {
    event.preventDefault();
    setEnviando(true);
    setError('');
    const datos = new FormData(event.currentTarget);
    if (datos.get('clave') !== datos.get('confirmacion')) {
      setError('Las contraseñas no coinciden.');
      setEnviando(false);
      return;
    }
    try {
      await api('/usuarios/registro-negocio', {
        method: 'POST',
        body: {
          nombre_usuario: datos.get('nombre_usuario'),
          correo: datos.get('correo'),
          clave: datos.get('clave'),
          nombre_empresa: datos.get('nombre_empresa'),
          direccion: datos.get('direccion'),
        },
      });
      router.replace('/configuracion-inicial');
    } catch (fallo) {
      setError(fallo.message);
      setEnviando(false);
    }
  }

  return (
    <main id="contenido" className="acceso-formulario">
      <Link className="brand" href="/">
        Turno Group
      </Link>
      <h1>Crea tu cuenta</h1>
      <p>Registra tu negocio para comenzar la configuración inicial.</p>
      {error && <p role="alert">{error}</p>}
      <form onSubmit={registrar}>
        <label htmlFor="nombre_usuario">Tu nombre</label>
        <input id="nombre_usuario" name="nombre_usuario" autoComplete="name" required maxLength={100} />
        <label htmlFor="correo">Correo electrónico</label>
        <input id="correo" name="correo" type="email" autoComplete="email" required maxLength={254} />
        <label htmlFor="clave">Contraseña</label>
        <input
          id="clave"
          name="clave"
          type="password"
          autoComplete="new-password"
          minLength={12}
          maxLength={128}
          required
        />
        <label htmlFor="confirmacion">Repite la contraseña</label>
        <input
          id="confirmacion"
          name="confirmacion"
          type="password"
          autoComplete="new-password"
          minLength={12}
          maxLength={128}
          required
        />
        <label htmlFor="nombre_empresa">Nombre del negocio</label>
        <input
          id="nombre_empresa"
          name="nombre_empresa"
          autoComplete="organization"
          minLength={4}
          maxLength={45}
          required
        />
        <label htmlFor="direccion">Dirección de la sucursal principal</label>
        <input id="direccion" name="direccion" autoComplete="street-address" minLength={5} maxLength={255} required />
        <button className="button button-primary" disabled={enviando}>
          {enviando ? 'Creando…' : 'Crear cuenta'}
        </button>
      </form>
      <p>
        ¿Ya tienes cuenta? <Link href="/login">Inicia sesión</Link>
      </p>
    </main>
  );
}
