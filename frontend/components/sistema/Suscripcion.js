'use client';

import { useState } from 'react';
import { usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { Mensaje, Modal } from './Controles';
import { api, fechaLocal, dinero } from '../../lib/api';
import TarjetaSuscripcion from './TarjetaSuscripcion';
import SobreTarjetas from './SobreTarjetas';
import DescargarComprobante from './DescargarComprobante';

export default function Suscripcion() {
  const { actualizar, sesion } = usarSesion();
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const [verTarjetas, setVerTarjetas] = useState(false);
  const [agregar, setAgregar] = useState(false);
  const [confirmacion, setConfirmacion] = useState(null);
  const datos = useDatos(() => api('/suscripciones/actual'), []);
  const d = datos.datos;

  async function ejecutar(ruta, opciones, mensaje) {
    setOcupado(true);
    setError('');
    setAviso('');
    try {
      await api(ruta, opciones);
      datos.recargar();
      setAviso(mensaje);
      setConfirmacion(null);
      return true;
    } catch (fallo) {
      setError(fallo.message);
      return false;
    } finally {
      setOcupado(false);
    }
  }
  async function seleccionar(tarjeta, accion) {
    if (accion === 'retirar') {
      setConfirmacion({ tarjeta });
      return;
    }
    await ejecutar(
      `/suscripciones/tarjetas/${tarjeta.id}/${accion}`,
      { method: 'POST' },
      'La prioridad de la tarjeta quedó actualizada.',
    );
  }
  return (
    <>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">CUENTA DE LA EMPRESA</span>
          <h1>Plan y facturación</h1>
          <p>Tu suscripción, tus tarjetas y tus comprobantes en un solo lugar.</p>
        </div>
      </div>
      <Mensaje error={error || datos.error} aviso={aviso} />
      {datos.cargando ? (
        <p role="status">Consultando plan…</p>
      ) : (
        d && (
          <>
            <div className="tg-settings-grid">
              <section className="tg-card">
                <span className="tg-badge">{d.estado}</span>
                <h2>Tu plan actual</h2>
                <div className="tg-payment-breakdown">
                  <div>
                    <span>
                      {d.sucursales_activas}{' '}
                      {d.sucursales_activas === 1 ? 'sucursal' : 'sucursales'} × 100 USD
                    </span>
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
                <p>
                  {d.renovacion_automatica ? 'Próximo ciclo' : 'Acceso hasta'}:{' '}
                  {fechaLocal(d.proximo_cobro || d.fin_prueba)}
                </p>
                <span className="tg-badge">Prueba de interfaz · Sin cargos reales</span>
                <label className="tg-check">
                  <input
                    type="checkbox"
                    checked={d.finanzas_habilitadas}
                    disabled={ocupado || d.estado !== 'Prueba'}
                    onChange={async (event) => {
                      if (
                        await ejecutar(
                          '/suscripciones/plan',
                          {
                            method: 'PATCH',
                            body: { finanzas_habilitadas: event.target.checked },
                          },
                          'Plan actualizado.',
                        )
                      )
                        await actualizar();
                    }}
                  />
                  Habilitar Finanzas · 30 USD adicionales por empresa
                </label>
                <button
                  className="tg-link-button"
                  disabled={ocupado}
                  onClick={() =>
                    setConfirmacion({ renovacion: !d.renovacion_automatica })
                  }
                >
                  {d.renovacion_automatica
                    ? 'Cancelar renovación automática'
                    : 'Activar renovación automática'}
                </button>
              </section>
              <section className="tg-card">
                <h2>Método de pago de la suscripción</h2>
                <p>
                  {d.tarjetas?.length
                    ? `${d.tarjetas.length} ${d.tarjetas.length === 1 ? 'tarjeta guardada' : 'tarjetas guardadas'}`
                    : 'Agrega tu tarjeta de prueba para completar la suscripción.'}
                </p>
                <div className="tg-form-actions">
                  <button
                    className="tg-button tg-primary"
                    onClick={() => setVerTarjetas(!verTarjetas)}
                    aria-expanded={verTarjetas}
                  >
                    {verTarjetas ? 'Ocultar tarjetas' : 'Ver tarjetas'}
                  </button>
                  <button
                    className="tg-button tg-secondary"
                    onClick={() => setAgregar(true)}
                  >
                    Añadir tarjeta
                  </button>
                </div>
                {verTarjetas && (
                  <SobreTarjetas
                    tarjetas={d.tarjetas || []}
                    seleccionar={seleccionar}
                    ocupado={ocupado}
                  />
                )}
              </section>
            </div>
            <section className="tg-card tg-billing-history">
              <div className="tg-section-heading">
                <div>
                  <h2>Historial de facturación</h2>
                  <p>Los documentos de esta versión son comprobantes de prueba.</p>
                </div>
                <DescargarComprobante comprobantes={d.comprobantes || []} />
              </div>
              {!d.comprobantes?.length ? (
                <>
                  <p>No hay comprobantes todavía.</p>
                  <button
                    className="tg-button tg-secondary"
                    disabled={ocupado}
                    onClick={() =>
                      ejecutar(
                        '/suscripciones/comprobantes/registro',
                        { method: 'POST' },
                        'Comprobante de registro preparado.',
                      )
                    }
                  >
                    Preparar comprobante de registro
                  </button>
                </>
              ) : (
                <div className="tg-table-scroll">
                  <table className="tg-table">
                    <thead>
                      <tr>
                        <th>Fecha</th>
                        <th>Concepto</th>
                        <th>Importe</th>
                        <th>Documento</th>
                      </tr>
                    </thead>
                    <tbody>
                      {d.comprobantes.map((item) => (
                        <tr key={item.id}>
                          <td>{fechaLocal(item.fecha)}</td>
                          <td>
                            {item.concepto}
                            <small>Prueba · Sin validez fiscal</small>
                          </td>
                          <td>{dinero(item.importe, 'USD')}</td>
                          <td>
                            <DescargarComprobante comprobantes={[item]} individual />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        )
      )}
      {agregar && (
        <Modal
          titulo="Añadir tarjeta de prueba"
          cerrar={() => {
            if (!ocupado) setAgregar(false);
          }}
        >
          <TarjetaSuscripcion
            titularInicial={sesion.usuario.nombre}
            ocupado={ocupado}
            guardar={async (tarjeta) => {
              const correcto = await ejecutar(
                '/suscripciones/tarjetas',
                { method: 'POST', body: tarjeta },
                'Tarjeta guardada.',
              );
              if (correcto) {
                setAgregar(false);
                setVerTarjetas(true);
              }
            }}
          />
        </Modal>
      )}
      {confirmacion && (
        <Modal
          titulo={
            confirmacion.tarjeta
              ? '¿Retirar esta tarjeta?'
              : confirmacion.renovacion
                ? '¿Activar la renovación?'
                : '¿Cancelar la renovación?'
          }
          cerrar={() => {
            if (!ocupado) setConfirmacion(null);
          }}
        >
          <Mensaje error={error} />
          <p>
            {confirmacion.tarjeta
              ? `Se retirará la tarjeta terminada en ${confirmacion.tarjeta.ultimos_cuatro}. Si era principal, se elegirá otra tarjeta vigente.`
              : confirmacion.renovacion
                ? 'Se necesita una tarjeta principal vigente. Esta versión no realiza cargos.'
                : 'Conservarás el acceso hasta terminar el periodo actual. No se renovará después.'}
          </p>
          <div className="tg-form-actions">
            <button
              className="tg-button tg-secondary"
              disabled={ocupado}
              onClick={() => setConfirmacion(null)}
            >
              Volver
            </button>
            <button
              className="tg-button tg-primary"
              disabled={ocupado}
              onClick={() =>
                confirmacion.tarjeta
                  ? ejecutar(
                      `/suscripciones/tarjetas/${confirmacion.tarjeta.id}`,
                      { method: 'DELETE' },
                      'Tarjeta retirada.',
                    )
                  : ejecutar(
                      '/suscripciones/renovacion',
                      {
                        method: 'PATCH',
                        body: { renovacion_automatica: confirmacion.renovacion },
                      },
                      'Renovación actualizada.',
                    )
              }
            >
              {ocupado ? 'Guardando…' : 'Confirmar'}
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
