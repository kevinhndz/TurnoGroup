'use client';

import Link from 'next/link';
import { useState } from 'react';
import { usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { Campo, Mensaje, Vacio } from './Controles';
import { api, dinero } from '../../lib/api';

const hoy = () => {
  const fecha = new Date();
  return new Date(fecha.getTime() - fecha.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);
};
export default function Finanzas() {
  const { sesion } = usarSesion();
  const [filtro, setFiltro] = useState({
    desde: hoy().slice(0, 8) + '01',
    hasta: hoy(),
    periodo: 'dia',
    solo_sucursal: 'true',
  });
  const datos = useDatos(
    () =>
      sesion.finanzas_habilitadas
        ? api(`/finanzas/ventas?${new URLSearchParams(filtro)}`)
        : Promise.resolve(null),
    [JSON.stringify(filtro), sesion.finanzas_habilitadas],
  );
  if (!sesion.finanzas_habilitadas)
    return (
      <Vacio
        titulo="Finanzas no está habilitado en tu plan"
        detalle="El gerente puede habilitar este módulo para todas las sucursales desde el plan de la empresa."
      >
        <Link className="tg-button tg-primary" href="/panel/suscripcion">
          Ver mi plan
        </Link>
      </Vacio>
    );
  const d = datos.datos;
  const maximo = Math.max(1, ...(d?.series || []).map((item) => Number(item.ventas)));
  return (
    <>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">VENTAS COBRADAS</span>
          <h1>Finanzas</h1>
          <p>
            Resumen de cobros registrados. Los pedidos cancelados se excluyen; estas
            cifras no representan utilidad después de costos.
          </p>
        </div>
        <button className="tg-button tg-secondary" onClick={datos.recargar}>
          Actualizar
        </button>
      </div>
      <form
        className="tg-card tg-report-filters"
        onSubmit={(event) => {
          event.preventDefault();
          const formulario = new FormData(event.currentTarget);
          setFiltro(Object.fromEntries(formulario));
        }}
      >
        <Campo label="Desde">
          <input name="desde" type="date" required defaultValue={filtro.desde} />
        </Campo>
        <Campo label="Hasta">
          <input name="hasta" type="date" required defaultValue={filtro.hasta} />
        </Campo>
        <Campo label="Agrupar por">
          <select name="periodo" defaultValue={filtro.periodo}>
            <option value="dia">Día</option>
            <option value="semana">Semana</option>
            <option value="mes">Mes</option>
            <option value="anio">Año</option>
          </select>
        </Campo>
        <Campo label="Alcance">
          <select name="solo_sucursal" defaultValue={filtro.solo_sucursal}>
            <option value="true">Esta sucursal</option>
            <option value="false">Toda la empresa</option>
          </select>
        </Campo>
        <button className="tg-button tg-primary">Consultar</button>
      </form>
      <Mensaje error={datos.error} />
      {datos.cargando ? (
        <p role="status">Preparando resumen…</p>
      ) : (
        d && (
          <>
            <div className="tg-stats">
              <article className="tg-card tg-stat">
                <span className="tg-stat-label">Total cobrado</span>
                <strong className="tg-money-stat">
                  {dinero(d.total_cobrado, d.moneda)}
                </strong>
              </article>
              <article className="tg-card tg-stat">
                <span className="tg-stat-label">Pedidos con cobro</span>
                <strong>{d.pedidos}</strong>
              </article>
            </div>
            <section className="tg-card">
              <h2>
                Ventas por{' '}
                {d.periodo === 'anio' ? 'año' : d.periodo === 'dia' ? 'día' : d.periodo}
              </h2>
              {!d.series.length ? (
                <Vacio titulo="No hay ventas en este periodo" />
              ) : (
                <div className="tg-chart" aria-label="Ventas por periodo">
                  {d.series.map((item) => (
                    <div key={item.periodo}>
                      <span>{item.periodo}</span>
                      <div
                        className="tg-chart-bar"
                        style={{
                          height: `${Math.max(1, (Number(item.ventas) / maximo) * 160)}px`,
                        }}
                      />
                      <strong>{dinero(item.ventas, d.moneda)}</strong>
                    </div>
                  ))}
                </div>
              )}
            </section>
            <section className="tg-card tg-table-card">
              <div className="tg-table-scroll">
                <table className="tg-table">
                  <thead>
                    <tr>
                      <th>Periodo</th>
                      <th>Pedidos</th>
                      <th>Ventas con descuento</th>
                      <th>Ventas sin descuento</th>
                      <th>Descuentos otorgados</th>
                      <th>Total cobrado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {d.series.map((item) => (
                      <tr key={item.periodo}>
                        <td>{item.periodo}</td>
                        <td>{item.pedidos}</td>
                        <td>{dinero(item.ventas_con_descuento, d.moneda)}</td>
                        <td>{dinero(item.ventas_sin_descuento, d.moneda)}</td>
                        <td>{dinero(item.descuentos, d.moneda)}</td>
                        <td>{dinero(item.ventas, d.moneda)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
            <section className="tg-card">
              <h2>Resumen por sucursal</h2>
              <div className="tg-payment-breakdown">
                {d.sucursales.map((item) => (
                  <div key={item.id_sucursal}>
                    <span>
                      Sucursal #{item.id_sucursal} · {item.pedidos} pedidos
                    </span>
                    <strong>{dinero(item.ventas, d.moneda)}</strong>
                  </div>
                ))}
              </div>
            </section>
          </>
        )
      )}
    </>
  );
}
