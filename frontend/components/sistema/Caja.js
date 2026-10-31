'use client';

import { useState } from 'react';
import { usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { Mensaje, Modal, Vacio } from './Controles';
import Formulario from './Formulario';
import { api, dinero, fechaLocal } from '../../lib/api';

export default function Caja() {
  const { sesion } = usarSesion();
  const [pagina, setPagina] = useState(1);
  const [cierre, setCierre] = useState(false);
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const cajero = sesion.rol_empresa === 'Cajero';
  const datos = useDatos(async () => {
    if (!sesion.id_sucursal) return null;
    const [actual, lista, empresa] = await Promise.all([
      api('/cajas/actual'),
      api(`/cajas/?pagina_actual=${pagina}&limite=10`),
      api(`/empresas/${sesion.id_empresa}`),
    ]);
    return { actual, lista, moneda: empresa.codigo_moneda };
  }, [pagina, sesion.id_sucursal]);
  if (!sesion.id_sucursal)
    return <Vacio titulo="Selecciona una sucursal para consultar la caja" />;
  const d = datos.datos;
  const actual = d?.actual;
  return (
    <>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">CONTROL DIARIO DEL CAJERO</span>
          <h1>Caja diaria</h1>
          <p>
            Registra el efectivo inicial y cuenta el dinero al cerrar. Los meseros no
            necesitan abrir una caja propia.
          </p>
        </div>
        <button className="tg-button tg-secondary" onClick={datos.recargar}>
          Actualizar
        </button>
      </div>
      <Mensaje error={error || datos.error} aviso={aviso} />
      {datos.cargando ? (
        <p role="status">Consultando caja…</p>
      ) : actual ? (
        <>
          <div className="tg-stats">
            {[
              ['Efectivo inicial', actual.monto_inicial],
              ['Efectivo esperado', actual.efectivo_esperado],
              ['Ventas cobradas', actual.total_cobrado],
            ].map(([titulo, valor]) => (
              <article className="tg-card tg-stat" key={titulo}>
                <span className="tg-stat-label">{titulo}</span>
                <strong className="tg-money-stat">{dinero(valor, d.moneda)}</strong>
              </article>
            ))}
          </div>
          <section className="tg-card">
            <div className="tg-section-heading">
              <div>
                <h2>Caja #{actual.id} · Abierta</h2>
                <p>
                  {fechaLocal(actual.fecha_apertura)} · Cajero #{actual.id_usuario}
                </p>
              </div>
              {cajero && actual.id_usuario === sesion.usuario.id && (
                <button className="tg-button tg-primary" onClick={() => setCierre(true)}>
                  Cerrar caja
                </button>
              )}
            </div>
            <div className="tg-payment-breakdown">
              {Object.entries(actual.pagos_por_metodo).map(([metodo, valor]) => (
                <div key={metodo}>
                  <span>{metodo}</span>
                  <strong>{dinero(valor, d.moneda)}</strong>
                </div>
              ))}
            </div>
            <p>
              {actual.cobros} cobros registrados. El efectivo esperado incluye el monto
              inicial.
            </p>
          </section>
        </>
      ) : (
        <section className="tg-card">
          <h2>No hay una caja abierta</h2>
          {cajero ? (
            <Formulario
              campos={[
                {
                  clave: 'monto_inicial',
                  label: 'Efectivo inicial',
                  type: 'number',
                  min: 0,
                  step: '0.01',
                  required: true,
                  valor: 0,
                },
              ]}
              texto="Abrir caja"
              guardar={async (body) => {
                await api('/cajas/', { method: 'POST', body });
                datos.recargar();
                setAviso('Caja abierta. Ya se pueden registrar cobros en esta sucursal.');
              }}
            />
          ) : (
            <p>Un cajero debe abrirla para comenzar a registrar cobros.</p>
          )}
        </section>
      )}
      <section className="tg-card tg-table-card">
        <div className="tg-toolbar">
          <h2>Historial de cajas</h2>
        </div>
        {!d?.lista.data.length ? (
          <Vacio titulo="Sin aperturas registradas" />
        ) : (
          <div className="tg-table-scroll">
            <table className="tg-table">
              <thead>
                <tr>
                  <th>Caja</th>
                  <th>Apertura</th>
                  <th>Cierre</th>
                  <th>Cobrado</th>
                  <th>Efectivo contado</th>
                  <th>Diferencia</th>
                </tr>
              </thead>
              <tbody>
                {d.lista.data.map((item) => (
                  <tr key={item.id}>
                    <td>#{item.id}</td>
                    <td>{fechaLocal(item.fecha_apertura)}</td>
                    <td>
                      {item.fecha_cierre ? fechaLocal(item.fecha_cierre) : 'Abierta'}
                    </td>
                    <td>{dinero(item.total_cobrado, d.moneda)}</td>
                    <td>
                      {item.efectivo_contado === null
                        ? '—'
                        : dinero(item.efectivo_contado, d.moneda)}
                    </td>
                    <td>
                      {item.diferencia === null ? '—' : dinero(item.diferencia, d.moneda)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="tg-pagination">
          <span>Página {pagina}</span>
          <div>
            <button
              className="tg-button tg-secondary"
              disabled={pagina === 1 || datos.actualizando}
              onClick={() => setPagina(pagina - 1)}
            >
              Anterior
            </button>
            <button
              className="tg-button tg-secondary"
              disabled={!d || pagina >= d.lista.total_paginas || datos.actualizando}
              onClick={() => setPagina(pagina + 1)}
            >
              Siguiente
            </button>
          </div>
        </div>
      </section>
      {cierre && actual && (
        <Modal titulo={`Cerrar caja #${actual.id}`} cerrar={() => setCierre(false)}>
          <p>
            Cuenta el efectivo que hay en caja. El sistema volverá a calcular el esperado
            al confirmar.
          </p>
          <p>
            Esperado ahora: <strong>{dinero(actual.efectivo_esperado, d.moneda)}</strong>
          </p>
          <Formulario
            campos={[
              {
                clave: 'efectivo_contado',
                label: 'Efectivo contado',
                type: 'number',
                min: 0,
                step: '0.01',
                required: true,
              },
              {
                clave: 'nota',
                label: 'Observación del cierre',
                type: 'textarea',
                nullable: true,
                maxLength: 500,
              },
            ]}
            texto="Confirmar cierre"
            guardar={async (body) => {
              await api(`/cajas/${actual.id}/cerrar`, { method: 'POST', body });
              setCierre(false);
              datos.recargar();
              setAviso('La caja quedó cerrada y el conteo se conservó en el historial.');
            }}
          />
        </Modal>
      )}
    </>
  );
}
