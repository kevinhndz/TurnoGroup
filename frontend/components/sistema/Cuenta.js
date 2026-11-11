'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { api } from '../../lib/api';
import { usarSesion } from './Sesion';
import { Mensaje, Modal } from './Controles';
import Formulario from './Formulario';

export default function Cuenta() {
  const { sesion, actualizar, olvidar } = usarSesion();
  const router = useRouter();
  const [aviso, setAviso] = useState('');
  const [error, setError] = useState('');
  const [confirmar, setConfirmar] = useState(false);
  const [ocupado, setOcupado] = useState(false);
  return (
    <>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">TU PERFIL</span>
          <h1>Mi cuenta</h1>
          <p>Tus datos personales y el acceso a tu espacio de trabajo.</p>
        </div>
      </div>
      <Mensaje error={error} aviso={aviso} />
      <div className="tg-settings-grid">
        <section className="tg-card">
          <h2>Datos personales</h2>
          <Formulario
            inicial={sesion.usuario}
            campos={[
              {
                clave: 'nombre',
                label: 'Nombre',
                required: true,
                minLength: 1,
                maxLength: 100,
              },
              {
                clave: 'correo',
                label: 'Correo electrónico',
                type: 'email',
                required: true,
              },
            ]}
            guardar={async (body) => {
              await api(`/usuarios/${sesion.usuario.id}`, { method: 'PATCH', body });
              await actualizar();
              setAviso('Tu perfil quedó actualizado.');
            }}
          />
        </section>
        <section className="tg-card">
          <h2>Acceso y sesiones</h2>
          <p className="tg-muted">
            La sesión termina el{' '}
            {new Date(
              sesion.vencimiento +
                (/Z$|[+-]\d\d:\d\d$/.test(sesion.vencimiento) ? '' : 'Z'),
            ).toLocaleString('es-HN')}
            .
          </p>
          <Link href="/recuperar-clave" className="tg-button tg-secondary">
            Cambiar mi contraseña
          </Link>
          <hr />
          <button
            className="tg-button tg-secondary"
            disabled={ocupado}
            onClick={async () => {
              setOcupado(true);
              setError('');
              try {
                await api('/sesiones/renovar', { method: 'POST' });
                await actualizar();
                setAviso('La sesión quedó renovada. Se conserva su hora de vencimiento.');
              } catch (fallo) {
                setError(fallo.message);
              } finally {
                setOcupado(false);
              }
            }}
          >
            Renovar sesión actual
          </button>
          <button className="tg-link-button tg-danger" onClick={() => setConfirmar(true)}>
            Cerrar todas mis sesiones
          </button>
        </section>
      </div>
      {confirmar && (
        <Modal titulo="Cerrar todas las sesiones" cerrar={() => setConfirmar(false)}>
          <p>
            También se cerrará la sesión que estás usando ahora. Necesitarás tu correo y
            contraseña para volver a entrar.
          </p>
          <div className="tg-form-actions">
            <button
              className="tg-button tg-secondary"
              disabled={ocupado}
              onClick={() => setConfirmar(false)}
            >
              Cancelar
            </button>
            <button
              className="tg-button tg-primary"
              disabled={ocupado}
              onClick={async () => {
                setOcupado(true);
                setError('');
                try {
                  await api('/sesiones/revocar-todas', { method: 'POST' });
                  olvidar();
                  router.replace('/login');
                } catch (fallo) {
                  setError(fallo.message);
                } finally {
                  setOcupado(false);
                }
              }}
            >
              {ocupado ? 'Cerrando…' : 'Cerrar todas'}
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
