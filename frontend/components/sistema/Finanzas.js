'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { Campo, Mensaje, Vacio } from './Controles';
import { api, dinero } from '../../lib/api';
import { etiquetaSucursal } from '../../lib/sucursales';
import {
  CurvaVentas,
  HorasPedidos,
  MapaCategorias,
  RadarVentas,
} from './GraficosFinanzas';

const periodos = [
  ['dia', 'Diario'],
  ['semana', 'Semanal'],
  ['mes', 'Mensual'],
  ['anio', 'Anual'],
];

export default function Finanzas() {
  const { sesion } = usarSesion();
  const [periodo, setPeriodo] = useState('mes');
  const [soloSucursal, setSoloSucursal] = useState(true);
  const [anio, setAnio] = useState(null);
  const [rango, setRango] = useState(null);
  const parametros = new URLSearchParams({
    periodo,
    solo_sucursal: String(soloSucursal),
    ...(anio ? { anio } : {}),
    ...(rango || {}),
  }).toString();
  const datos = useDatos(
    () =>
      sesion.finanzas_habilitadas
        ? api(`/finanzas/dashboard?${parametros}`)
        : Promise.resolve(null),
    [parametros, sesion.finanzas_habilitadas],
  );
  useEffect(() => {
    if (!sesion.finanzas_habilitadas) return;
    const refrescar = () => {
      if (document.visibilityState === 'visible') datos.recargar();
    };
    const intervalo = setInterval(refrescar, 15000);
    window.addEventListener('focus', refrescar);
    window.addEventListener('turno-datos', refrescar);
    return () => {
      clearInterval(intervalo);
      window.removeEventListener('focus', refrescar);
      window.removeEventListener('turno-datos', refrescar);
    };
  }, [parametros, sesion.finanzas_habilitadas]);
  if (!sesion.finanzas_habilitadas)
    return (
      <Vacio
        titulo="Finanzas no está habilitado en tu plan"
        detalle="Este módulo está disponible para el gerente y reúne las ventas de todas sus sucursales."
      >
        <Link className="tg-button tg-primary" href="/panel/suscripcion">
          Ver mi plan
        </Link>
      </Vacio>
    );
  const d = datos.datos;
  const etiqueta = rango
    ? 'Periodo personalizado'
    : periodos.find(([clave]) => clave === periodo)?.[1];
  return (
    <div className="tg-finance">
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">EL PULSO DE TU NEGOCIO</span>
          <h1>Finanzas</h1>
          <p>Cobros registrados, categorías y resultados de tus sucursales.</p>
        </div>
        <button
          className="tg-button tg-secondary"
          onClick={datos.recargar}
          disabled={datos.actualizando}
        >
          {datos.actualizando ? 'Actualizando…' : 'Actualizar'}
        </button>
      </div>
      <div className="tg-finance-controls">
        <nav className="tg-finance-segment" aria-label="Periodo de ventas">
          {periodos.map(([clave, titulo]) => (
            <button
              key={clave}
              aria-pressed={!rango && periodo === clave}
              onClick={() => {
                setPeriodo(clave);
                setRango(null);
              }}
            >
              {titulo}
            </button>
          ))}
        </nav>
        <label className="tg-field">
          <span>Ver ventas de</span>
          <select
            value={String(soloSucursal)}
            onChange={(event) => setSoloSucursal(event.target.value === 'true')}
          >
            <option value="true">Sucursal seleccionada</option>
            <option value="false">Toda la empresa</option>
          </select>
        </label>
        <details className="tg-finance-dates">
          <summary>Elegir otras fechas</summary>
          <form
            key={`${d?.desde}:${d?.hasta}`}
            onSubmit={(event) => {
              event.preventDefault();
              const f = new FormData(event.currentTarget);
              setRango({ desde: f.get('desde'), hasta: f.get('hasta') });
            }}
          >
            <Campo label="Primera fecha">
              <input name="desde" type="date" required defaultValue={d?.desde} />
            </Campo>
            <Campo label="Última fecha">
              <input name="hasta" type="date" required defaultValue={d?.hasta} />
            </Campo>
            <button className="tg-button tg-primary">Ver cobros de estas fechas</button>
          </form>
        </details>
      </div>
      <Mensaje error={datos.error} />
      {datos.cargando ? (
        <div className="tg-finance-skeleton" role="status">
          Preparando tu dashboard de ventas…
        </div>
      ) : (
        d && (
          <>
            <div className="tg-finance-live">
              <span>
                <i />
                Actualización cada 15 segundos
              </span>
              <span>
                {etiqueta} · {d.desde} al {d.hasta}
              </span>
              <small>
                Última actualización:{' '}
                {new Date(d.actualizado).toLocaleTimeString('es-HN')} · {d.zona_horaria}
              </small>
            </div>
            <div className="tg-finance-grid">
              <section className="tg-finance-card tg-finance-top">
                <div>
                  <span className="tg-finance-caption">Ingresos cobrados</span>
                  <strong className="tg-finance-number">
                    {dinero(d.total_cobrado, d.moneda)}
                  </strong>
                  <span
                    className={`tg-finance-delta ${Number(d.variacion) < 0 ? 'is-negative' : ''}`}
                  >
                    {d.variacion === null
                      ? 'Sin cobros en el periodo anterior'
                      : `${Number(d.variacion) >= 0 ? '↑' : '↓'} ${Math.abs(Number(d.variacion))}% frente al periodo anterior`}
                  </span>
                  <p>
                    Promedio por pedido <b>{dinero(d.promedio_pedido, d.moneda)}</b>
                  </p>
                </div>
                <CurvaVentas series={d.series} moneda={d.moneda} />
              </section>
              <section className="tg-finance-card tg-finance-top">
                <div>
                  <span className="tg-finance-caption">Pedidos cobrados</span>
                  <strong className="tg-finance-number">
                    {d.pedidos.toLocaleString('es-HN')}
                  </strong>
                  <p>Distribución por hora de cobro</p>
                  <div className="tg-finance-legend">
                    <span>
                      <i style={{ background: '#ff8a22' }} />
                      Actual
                    </span>
                    <span>
                      <i style={{ background: '#8b3dff' }} />
                      Anterior
                    </span>
                  </div>
                </div>
                <HorasPedidos horas={d.horas} />
              </section>
              <section className="tg-finance-card tg-finance-categories">
                <header>
                  <h2>Ventas por categoría</h2>
                  <span className="tg-muted">
                    {soloSucursal ? 'Esta sucursal' : 'Toda la empresa'}
                  </span>
                </header>
                <div className="tg-finance-periods">
                  {periodos.map(([clave, titulo]) => (
                    <button
                      key={clave}
                      aria-pressed={!rango && periodo === clave}
                      onClick={() => {
                        setPeriodo(clave);
                        setRango(null);
                      }}
                    >
                      <span>{titulo}</span>
                      <strong>{dinero(d.periodos[clave], d.moneda)}</strong>
                      <small>
                        {clave === 'dia'
                          ? 'Hoy'
                          : clave === 'semana'
                            ? 'Esta semana'
                            : clave === 'mes'
                              ? 'Este mes'
                              : 'Este año'}
                      </small>
                    </button>
                  ))}
                </div>
                {d.categorias.length ? (
                  <>
                    <MapaCategorias categorias={d.categorias} moneda={d.moneda} />
                    <details className="tg-finance-category-table">
                      <summary>
                        Ver detalle de las {d.categorias.length} categorías
                      </summary>
                      <div className="tg-table-scroll">
                        <table className="tg-table">
                          <thead>
                            <tr>
                              <th>Categoría</th>
                              <th>Unidades</th>
                              <th>Total cobrado</th>
                            </tr>
                          </thead>
                          <tbody>
                            {d.categorias.map((item) => (
                              <tr key={item.nombre}>
                                <td>{item.nombre}</td>
                                <td>{item.unidades}</td>
                                <td>{dinero(item.ventas, d.moneda)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </details>
                  </>
                ) : (
                  <Vacio
                    titulo="Todavía no hay cobros en este periodo"
                    detalle="Al registrar el pago de un pedido, sus ventas aparecerán aquí."
                  />
                )}
                <h3>Resultados por sucursal</h3>
                <div className="tg-table-scroll">
                  <table className="tg-table">
                    <thead>
                      <tr>
                        <th>Sucursal</th>
                        <th>Pedidos cobrados</th>
                        <th>Ingresos</th>
                      </tr>
                    </thead>
                    <tbody>
                      {d.sucursales.map((item) => (
                        <tr key={item.id_sucursal}>
                          <td>{etiquetaSucursal({ ...item, id: item.id_sucursal })}</td>
                          <td>{item.pedidos}</td>
                          <td>{dinero(item.ventas, d.moneda)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
              <section className="tg-finance-card tg-finance-year">
                <header>
                  <h2>Comportamiento anual</h2>
                  <div className="tg-finance-segment" aria-label="Año del gráfico">
                    {[d.anio_actual, d.anio_actual - 1].map((valor) => (
                      <button
                        key={valor}
                        aria-pressed={d.anio === valor}
                        onClick={() => setAnio(valor)}
                      >
                        {valor}
                      </button>
                    ))}
                  </div>
                </header>
                <RadarVentas valores={d.anual} moneda={d.moneda} />
                <div className="tg-finance-year-stats">
                  <div>
                    <span>Promedio mensual</span>
                    <strong>{dinero(d.promedio_mensual, d.moneda)}</strong>
                  </div>
                  <div>
                    <span>Total del año {d.anio}</span>
                    <strong>{dinero(d.total_anual, d.moneda)}</strong>
                  </div>
                </div>
                <p className="tg-muted">
                  El gráfico reúne los cobros de enero a diciembre del año elegido.
                </p>
                <div className="tg-finance-discounts">
                  <h3>Descuentos del periodo</h3>
                  <p>
                    <span>Ventas con descuento</span>
                    <strong>
                      {dinero(
                        d.series.reduce(
                          (s, item) => s + Number(item.ventas_con_descuento),
                          0,
                        ),
                        d.moneda,
                      )}
                    </strong>
                  </p>
                  <p>
                    <span>Ventas sin descuento</span>
                    <strong>
                      {dinero(
                        d.series.reduce(
                          (s, item) => s + Number(item.ventas_sin_descuento),
                          0,
                        ),
                        d.moneda,
                      )}
                    </strong>
                  </p>
                  <p>
                    <span>Descuentos otorgados</span>
                    <strong>
                      {dinero(
                        d.series.reduce((s, item) => s + Number(item.descuentos), 0),
                        d.moneda,
                      )}
                    </strong>
                  </p>
                </div>
              </section>
            </div>
            <details className="tg-finance-card tg-finance-table">
              <summary>Ver desglose diario del periodo</summary>
              <div className="tg-table-scroll">
                <table className="tg-table">
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>Pedidos cobrados</th>
                      <th>Descuentos</th>
                      <th>Total cobrado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {d.series.map((item) => (
                      <tr key={item.periodo}>
                        <td>{item.periodo}</td>
                        <td>{item.pedidos}</td>
                        <td>{dinero(item.descuentos, d.moneda)}</td>
                        <td>{dinero(item.ventas, d.moneda)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </details>
            <p className="tg-finance-note">
              Se excluyen los pedidos cancelados y los pendientes de pago. Estos ingresos
              no equivalen a utilidad después de costos.
            </p>
          </>
        )
      )}
    </div>
  );
}
