'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '../../lib/api';
import { usarSesion } from './Sesion';
import Espacio from './Espacio';
import { Campo, Mensaje } from './Controles';

export default function Invitacion() {
  const { sesion, cargando } = usarSesion();
  if (cargando) return <p className="tg-loading">Preparando invitación…</p>;
  if (!sesion) return <RegistroInvitado />;
  return (
    <Espacio>
      <FormularioInvitacion />
    </Espacio>
  );
}

function FormularioInvitacion() {
  const { sesion, actualizar, cambiarContexto } = usarSesion();
  const router = useRouter();
  const [error, setError] = useState('');
  const [ocupado, setOcupado] = useState(false);
  if (sesion.usuario.rol_plataforma === 'Superadministrador')
    return <p>Las invitaciones laborales se aceptan con una cuenta de usuario.</p>;
  return (
    <section className="tg-card tg-narrow">
      <span className="tg-eyebrow">BIENVENIDO AL EQUIPO</span>
      <h1>Aceptar invitación</h1>
      <p>
        Estás usando la cuenta <strong>{sesion.usuario.correo}</strong>. Debe coincidir
        con el correo que recibió la invitación.
      </p>
      <Mensaje error={error} />
      <form
        className="tg-form"
        onSubmit={async (event) => {
          event.preventDefault();
          const codigo = new FormData(event.currentTarget).get('codigo');
          setOcupado(true);
          setError('');
          try {
            const vinculo = await api('/invitaciones-laborales/aceptar', {
              method: 'POST',
              body: { codigo },
            });
            const vinculos = await api('/sesiones/vinculos');
            const autorizado = vinculos.find((item) => item.id === vinculo.id);
            if (autorizado)
              await cambiarContexto(autorizado.id, autorizado.sucursales[0]?.id || null);
            await actualizar();
            router.replace('/panel');
          } catch (fallo) {
            setError(fallo.message);
          } finally {
            setOcupado(false);
          }
        }}
      >
        <Campo label="Código de invitación">
          <input
            name="codigo"
            autoComplete="off"
            required
            minLength={40}
            maxLength={128}
          />
        </Campo>
        <button className="tg-button tg-primary" disabled={ocupado}>
          {ocupado ? 'Revisando invitación…' : 'Unirme a la empresa'}
        </button>
      </form>
      <Link href="/panel">Volver al panel</Link>
    </section>
  );
}

function RegistroInvitado() {
  const { actualizar } = usarSesion();
  const router = useRouter();
  const [error, setError] = useState('');
  const [ocupado, setOcupado] = useState(false);
  return (
    <main id="contenido" className="tg-loading">
      <section className="tg-card tg-narrow">
        <Link href="/" className="tg-brand">
          Turno Group
        </Link>
        <h1>Únete al equipo</h1>
        <p>
          Crea tu acceso con el código que te envió el gerente. No necesitas registrar un
          negocio.
        </p>
        <Mensaje error={error} />
        <form
          className="tg-form"
          onSubmit={async (event) => {
            event.preventDefault();
            setOcupado(true);
            setError('');
            const datos = new FormData(event.currentTarget);
            try {
              await api('/invitaciones-laborales/registrar', {
                method: 'POST',
                body: Object.fromEntries(datos),
              });
              await actualizar();
              router.replace('/panel');
            } catch (fallo) {
              setError(fallo.message);
            } finally {
              setOcupado(false);
            }
          }}
        >
          <Campo label="Código de invitación">
            <input
              name="codigo"
              required
              minLength={40}
              maxLength={128}
              autoComplete="off"
            />
          </Campo>
          <Campo label="Tu nombre">
            <input name="nombre" required maxLength={100} autoComplete="name" />
          </Campo>
          <Campo label="Contraseña">
            <input
              name="clave"
              required
              type="password"
              minLength={12}
              maxLength={128}
              autoComplete="new-password"
            />
          </Campo>
          <button disabled={ocupado} className="tg-button tg-primary">
            {ocupado ? 'Creando acceso…' : 'Crear acceso y aceptar invitación'}
          </button>
        </form>
        <p>
          ¿Ya tienes cuenta?{' '}
          <Link href="/login?volver=/invitacion">Inicia sesión para aceptar</Link>
        </p>
      </section>
    </main>
  );
}
