'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
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
  const [codigo] = usarCodigoInvitacion();
  if (sesion.usuario.rol_plataforma === 'Superadministrador')
    return <p>Las invitaciones laborales se aceptan con una cuenta de usuario.</p>;
  if (sesion.id_empresa)
    return (
      <section className="tg-card tg-narrow">
        <h1>Tu acceso ya está listo</h1>
        <p>
          La cuenta <strong>{sesion.usuario.correo}</strong> ya pertenece a una empresa.
          Puedes entrar directamente a tu panel.
        </p>
        <p>
          Si esta invitación llegó a otro correo, cierra sesión y abre el enlace con esa
          cuenta.
        </p>
        <Link href="/panel" className="tg-button tg-primary">
          Ir a mi panel
        </Link>
      </section>
    );
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
            sessionStorage.removeItem('turno-invitacion');
            router.replace('/panel');
          } catch (fallo) {
            setError(fallo.message);
          } finally {
            setOcupado(false);
          }
        }}
      >
        {!codigo && (
          <Mensaje error="Abre el enlace de la invitación que recibiste por correo para continuar." />
        )}
        <button className="tg-button tg-primary" disabled={ocupado || !codigo}>
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
  const [codigo] = usarCodigoInvitacion();
  return (
    <main id="contenido" className="tg-loading">
      <section className="tg-card tg-narrow">
        <Link href="/" className="tg-brand">
          Turno Group
        </Link>
        <h1>Únete al equipo</h1>
        <p>
          Escribe tu nombre y crea una contraseña. El enlace del correo ya incluye tu
          invitación y el rol que te asignó el gerente.
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
              sessionStorage.removeItem('turno-invitacion');
              router.replace('/panel');
            } catch (fallo) {
              setError(fallo.message);
            } finally {
              setOcupado(false);
            }
          }}
        >
          <input type="hidden" name="codigo" value={codigo} />
          {!codigo && (
            <Mensaje error="Abre el enlace de la invitación que recibiste por correo para crear tu acceso." />
          )}
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
          <button disabled={ocupado || !codigo} className="tg-button tg-primary">
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

function usarCodigoInvitacion() {
  const [codigo, setCodigo] = useState('');
  useEffect(() => {
    try {
      const nuevo = new URLSearchParams(window.location.hash.slice(1)).get('codigo');
      if (nuevo && nuevo.length >= 40 && nuevo.length <= 128) {
        setCodigo(nuevo);
        sessionStorage.setItem('turno-invitacion', nuevo);
        history.replaceState(null, '', window.location.pathname + window.location.search);
      } else setCodigo(sessionStorage.getItem('turno-invitacion') || '');
    } catch {}
  }, []);
  return [codigo, setCodigo];
}
