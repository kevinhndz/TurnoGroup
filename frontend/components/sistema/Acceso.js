'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { usarSesion } from './Sesion';
import { Campo, Mensaje } from './Controles';
import { api } from '../../lib/api';
import Icon from '../Icon';

const textos = {
  login: [
    'Bienvenido de vuelta',
    'Inicia sesión en tu negocio',
    'Tu equipo, tu catálogo y tus sucursales en un mismo espacio.',
    'Entrar a mi negocio',
  ],
  registro: [
    'Tu siguiente turno empieza aquí',
    'Crea tu cuenta',
    'Completa tus datos y los siete pasos. Tu cuenta se creará al confirmar la revisión final.',
    'Continuar a la configuración',
  ],
  recuperar: [
    'Recupera el acceso',
    '¿Olvidaste tu contraseña?',
    'Escribe tu correo y solicita un código para crear una nueva contraseña.',
    'Solicitar código',
  ],
  restablecer: [
    'Volvamos a empezar',
    'Elige una nueva contraseña',
    'Usa el código de tu correo. Cada código se puede utilizar una sola vez.',
    'Guardar contraseña',
  ],
};

export default function Acceso({ modo = 'login' }) {
  const router = useRouter();
  const { iniciar, setRegistro } = usarSesion();
  const [visible, setVisible] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const [terminado, setTerminado] = useState(false);
  const [codigo, setCodigo] = useState('');
  useEffect(() => {
    setCodigo(new URLSearchParams(window.location.search).get('codigo') || '');
  }, []);
  const [ceja, titulo, detalle, boton] = textos[modo];

  async function enviar(event) {
    event.preventDefault();
    const datos = new FormData(event.currentTarget);
    setError('');
    setAviso('');
    setEnviando(true);
    try {
      if (modo === 'recuperar') {
        await api('/recuperaciones-clave/solicitar', {
          method: 'POST',
          body: { correo: datos.get('correo') },
        });
        setAviso(
          'Si el correo está registrado, recibirás las instrucciones para recuperar el acceso.',
        );
        setTerminado(true);
      } else if (modo === 'restablecer') {
        const codigo =
          datos.get('codigo') ||
          new URLSearchParams(window.location.search).get('codigo');
        await api('/recuperaciones-clave/restablecer', {
          method: 'POST',
          body: { codigo, nueva_clave: datos.get('clave') },
        });
        setAviso('Tu contraseña quedó actualizada. Ya puedes iniciar sesión.');
        setTerminado(true);
      } else {
        if (modo === 'registro') {
          setRegistro({
            cuenta: {
              nombre: datos.get('nombre'),
              correo: datos.get('correo'),
              clave: datos.get('clave'),
            },
            negocio: null,
            sucursales: [],
            categorias: [],
            productos: [],
            descuentos: [],
            impuesto: null,
          });
          router.push('/configuracion-inicial');
          return;
        }
        const sesion = await iniciar({
          correo: datos.get('correo'),
          clave: datos.get('clave'),
        });
        const volver = new URLSearchParams(window.location.search).get('volver');
        const destino =
          volver &&
          /^\/(panel|configuracion-inicial|nuevo-pedido|invitacion)(\/|\?|$)/.test(volver)
            ? volver
            : null;
        router.replace(
          destino ||
            (sesion.id_empresa || sesion.usuario.rol_plataforma === 'Superadministrador'
              ? '/panel'
              : '/configuracion-inicial'),
        );
      }
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main id="contenido" className="tg-auth">
      <aside className="tg-auth-story">
        <Link href="/" className="tg-brand">
          Turno Group
          <span />
        </Link>
        <span className="tg-auth-eyebrow">
          GESTIÓN PRESENCIAL · RESTAURANTES Y CAFETERÍAS
        </span>
        <div className="tg-auth-quote">
          <span className="tg-tag">CADA DETALLE CUENTA</span>
          <h2>
            Más tiempo para
            <br />
            quienes se sientan
            <br />a tu mesa.
          </h2>
          <p>
            Un espacio para preparar tu negocio y acompañar la operación de cada local.
          </p>
        </div>
        <small>El orden detrás de un buen servicio.</small>
      </aside>
      <section className="tg-auth-form">
        <Link href="/" className="tg-back">
          ← Volver al inicio
        </Link>
        <div className="tg-auth-inner">
          <span className="tg-badge">{ceja}</span>
          <h1>{titulo}</h1>
          <p className="tg-muted">{detalle}</p>
          <Mensaje error={error} aviso={aviso} />
          {!terminado && (
            <form onSubmit={enviar} className="tg-form">
              {modo === 'registro' && (
                <Campo label="Tu nombre">
                  <input
                    name="nombre"
                    autoComplete="name"
                    maxLength={100}
                    required
                    placeholder="¿Cómo te llamas?"
                  />
                </Campo>
              )}
              {modo !== 'restablecer' && (
                <Campo label="Correo electrónico">
                  <input
                    name="correo"
                    type="email"
                    autoComplete="email"
                    maxLength={254}
                    required
                    placeholder="tu@negocio.com"
                  />
                </Campo>
              )}
              {modo === 'restablecer' && (
                <Campo
                  label="Código de recuperación"
                  ayuda="Copia el código que recibiste en tu correo."
                >
                  <input
                    name="codigo"
                    required
                    minLength={40}
                    maxLength={128}
                    autoComplete="off"
                    value={codigo}
                    onChange={(event) => setCodigo(event.target.value)}
                  />
                </Campo>
              )}
              {modo !== 'recuperar' && (
                <Campo
                  label={modo === 'restablecer' ? 'Nueva contraseña' : 'Contraseña'}
                  ayuda={modo !== 'login' ? 'Mínimo 12 caracteres.' : undefined}
                >
                  <span className="tg-password">
                    <input
                      name="clave"
                      type={visible ? 'text' : 'password'}
                      autoComplete={
                        modo === 'login' ? 'current-password' : 'new-password'
                      }
                      minLength={modo === 'login' ? 1 : 12}
                      maxLength={128}
                      required
                      placeholder="Escribe tu contraseña"
                    />
                    <button
                      type="button"
                      onClick={() => setVisible(!visible)}
                      aria-label={visible ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                    >
                      {visible ? 'Ocultar' : 'Mostrar'}
                    </button>
                  </span>
                </Campo>
              )}
              {modo === 'login' && (
                <Link href="/recuperar-clave" className="tg-forgot">
                  Olvidé mi contraseña
                </Link>
              )}
              <button className="tg-button tg-primary tg-wide" disabled={enviando}>
                {enviando ? 'Un momento…' : boton}
                <Icon name="arrow" size={18} />
              </button>
            </form>
          )}
          {modo === 'recuperar' && (
            <Link href="/restablecer-clave" className="tg-forgot">
              Ya tengo un código de recuperación
            </Link>
          )}
          <div className="tg-auth-switch">
            {modo === 'login' ? (
              <>
                ¿Aún no tienes cuenta? <Link href="/registro">Crear una cuenta</Link>
              </>
            ) : (
              <Link href="/login">Volver a iniciar sesión</Link>
            )}
          </div>
        </div>
        <footer>Turno Group · Tu negocio, en orden.</footer>
      </section>
    </main>
  );
}
