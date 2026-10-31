'use client';

import { useState } from 'react';
import { usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { Mensaje } from './Controles';
import { api, fechaLocal } from '../../lib/api';

export default function Suscripcion() {
  const { actualizar } = usarSesion();
  const [error, setError] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const datos = useDatos(() => api('/suscripciones/actual'), []);
  const d = datos.datos;
  return (
    <>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">CUENTA DE LA EMPRESA</span>
          <h1>Plan y facturación</h1>
          <p>
            100 USD mensuales por sucursal y 30 USD adicionales por Finanzas para toda la
            empresa.
          </p>
        </div>
      </div>
      <Mensaje error={error || datos.error} />
      {datos.cargando ? (
        <p role="status">Consultando plan…</p>
      ) : (
        d && (
          <div className="tg-settings-grid">
            <section className="tg-card">
              <span className="tg-badge">{d.estado}</span>
              <h2>Tu plan actual</h2>
              <div className="tg-payment-breakdown">
                <div>
                  <span>{d.sucursales_activas} sucursales × 100 USD</span>
                  <strong>{d.sucursales_activas * 100} USD / mes</strong>
                </div>
                <div>
                  <span>Finanzas para todas las sucursales</span>
                  <strong>{d.complemento_finanzas_usd} USD / mes</strong>
                </div>
                <div>
                  <span>Total mensual</span>
                  <strong>{d.total_mensual_usd} USD</strong>
                </div>
              </div>
              <p>Fin del primer mes gratuito: {fechaLocal(d.fin_prueba)}</p>
              <p>Próximo ciclo: {fechaLocal(d.proximo_cobro || d.fin_prueba)}</p>
              <label className="tg-check">
                <input
                  type="checkbox"
                  checked={d.finanzas_habilitadas}
                  disabled={ocupado || d.estado !== 'Prueba'}
                  onChange={async (event) => {
                    const valor = event.target.checked;
                    setOcupado(true);
                    setError('');
                    try {
                      await api('/suscripciones/plan', {
                        method: 'PATCH',
                        body: { finanzas_habilitadas: valor },
                      });
                      datos.recargar();
                      await actualizar();
                    } catch (fallo) {
                      setError(fallo.message);
                    } finally {
                      setOcupado(false);
                    }
                  }}
                />
                Habilitar Finanzas · 30 USD adicionales por empresa
              </label>
            </section>
            <section className="tg-card">
              <h2>Métodos de pago de la suscripción</h2>
              <p>
                La integración con Paddle sandbox se realizará antes del despliegue, según
                lo acordado.
              </p>
              <p>
                No se han realizado cargos desde esta aplicación. Aquí se mostrarán las
                tarjetas y el historial cuando se conecte Paddle.
              </p>
              <button className="tg-button tg-secondary" disabled>
                Administrar tarjetas · Pendiente de Paddle
              </button>
            </section>
          </div>
        )
      )}
    </>
  );
}
