'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { usarSesion } from './Sesion';
import { api } from '../../lib/api';
import { Campo, Mensaje, Modal } from './Controles';
import { useDatos } from './Datos';
import { fechaLocal } from '../../lib/api';

export default function DesactivarCuenta() {
  const { olvidar } = usarSesion();
  const router = useRouter();
  const [abierto, setAbierto] = useState(false);
  const [error, setError] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const [cancelar, setCancelar] = useState(false);
  const [aviso, setAviso] = useState('');
  const datos = useDatos(() => api('/suscripciones/actual'), []);
  return (
    <section className="tg-card tg-account-deactivation">
      <h2>Renovación de la suscripción</h2>
      <p>
        Puedes cancelar durante el mes gratuito o después de pagar. Conservarás el acceso
        hasta finalizar el periodo actual.
      </p>
      <Mensaje error={datos.error} aviso={aviso} />
      {datos.datos && (
        <p>
          Acceso hasta: {fechaLocal(datos.datos.proximo_cobro || datos.datos.fin_prueba)}
        </p>
      )}
      {datos.datos?.renovacion_automatica ? (
        <button className="tg-button tg-secondary" onClick={() => setCancelar(true)}>
          Cancelar renovación automática
        </button>
      ) : (
        datos.datos && <span className="tg-badge">Renovación cancelada</span>
      )}
      <hr />
      <h2>Desactivar mi cuenta</h2>
      <p>
        Puedes desactivar tu cuenta después de haber pagado al menos una mensualidad y
        estar al día. Se conservará la configuración del negocio y se cancelará la
        renovación de tus suscripciones.
      </p>
      <button
        className="tg-button tg-secondary tg-danger"
        onClick={() => setAbierto(true)}
      >
        Desactivar mi cuenta
      </button>
      {cancelar && (
        <Modal
          titulo="¿Cancelar la renovación?"
          cerrar={() => {
            if (!ocupado) setCancelar(false);
          }}
        >
          <Mensaje error={error} />
          <p>
            No se renovará el siguiente ciclo. Podrás seguir usando el sistema hasta{' '}
            {fechaLocal(datos.datos.proximo_cobro || datos.datos.fin_prueba)}.
          </p>
          <div className="tg-form-actions">
            <button
              className="tg-button tg-secondary"
              disabled={ocupado}
              onClick={() => setCancelar(false)}
            >
              Volver
            </button>
            <button
              className="tg-button tg-primary"
              disabled={ocupado}
              onClick={async () => {
                setOcupado(true);
                setError('');
                try {
                  await api('/suscripciones/renovacion', {
                    method: 'PATCH',
                    body: { renovacion_automatica: false },
                  });
                  datos.recargar();
                  setCancelar(false);
                  setAviso(
                    'Renovación cancelada. Tu acceso continúa hasta la fecha indicada.',
                  );
                } catch (fallo) {
                  setError(fallo.message);
                } finally {
                  setOcupado(false);
                }
              }}
            >
              {ocupado ? 'Guardando…' : 'Confirmar cancelación'}
            </button>
          </div>
        </Modal>
      )}
      {abierto && (
        <Modal
          titulo="¿Desactivar tu cuenta?"
          cerrar={() => {
            if (!ocupado) setAbierto(false);
          }}
        >
          <p>
            Se cerrarán todas tus sesiones. Podrás recuperar el acceso al iniciar sesión y
            confirmar la reactivación.
          </p>
          <Mensaje error={error} />
          <form
            className="tg-form"
            onSubmit={async (event) => {
              event.preventDefault();
              setOcupado(true);
              setError('');
              const campos = new FormData(event.currentTarget);
              try {
                await api('/suscripciones/desactivar-cuenta', {
                  method: 'POST',
                  body: {
                    clave: campos.get('clave'),
                    confirmacion: campos.get('confirmacion'),
                  },
                });
                olvidar();
                router.replace('/login');
              } catch (fallo) {
                setError(fallo.message);
              } finally {
                setOcupado(false);
              }
            }}
          >
            <Campo label="Tu contraseña">
              <input
                name="clave"
                type="password"
                required
                autoComplete="current-password"
              />
            </Campo>
            <Campo label="Escribe DESACTIVAR para confirmar">
              <input
                name="confirmacion"
                pattern="DESACTIVAR"
                required
                autoComplete="off"
              />
            </Campo>
            <div className="tg-form-actions">
              <button
                type="button"
                className="tg-button tg-secondary"
                disabled={ocupado}
                onClick={() => setAbierto(false)}
              >
                Volver
              </button>
              <button className="tg-button tg-primary" disabled={ocupado}>
                {ocupado ? 'Desactivando…' : 'Confirmar desactivación'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </section>
  );
}
