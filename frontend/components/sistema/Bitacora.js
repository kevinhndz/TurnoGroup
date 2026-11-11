'use client';
import { useState } from 'react';
import FiltrosListado, { useFiltrosListado } from './FiltrosListado';
import { usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { api, fechaLocal } from '../../lib/api';
import { Mensaje, Vacio } from './Controles';
export default function Bitacora() {
  const { sesion } = usarSesion();
  const [soloSucursal, setSoloSucursal] = useState(true);
  const [pagina, setPagina] = useState(1);
  const filtros = useFiltrosListado();
  const datos = useDatos(
    () =>
      api(
        `/bitacora/?pagina_actual=${pagina}&limite=20&solo_sucursal=${soloSucursal}&${filtros.parametros}`,
      ),
    [pagina, soloSucursal, filtros.parametros],
  );
  const lista = datos.datos;
  return (
    <>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">ACTIVIDAD REGISTRADA</span>
          <h1>Registros</h1>
          <p>
            Quién registró, actualizó, cobró o entregó cada pedido y quién abrió o cerró
            la caja.
          </p>
        </div>
        <button className="tg-button tg-secondary" onClick={datos.recargar}>
          Actualizar
        </button>
      </div>
      <Mensaje error={datos.error} />
      <FiltrosListado
        filtros={filtros}
        cambiar={() => setPagina(1)}
        nombre="Buscar registros por persona"
      />
      {sesion.rol_empresa === 'Gerente' && (
        <label className="tg-field">
          <span>Alcance de la actividad</span>
          <select
            value={String(soloSucursal)}
            onChange={(e) => {
              setSoloSucursal(e.target.value === 'true');
              setPagina(1);
            }}
          >
            <option value="true">Sucursal seleccionada</option>
            <option value="false">Toda mi empresa</option>
          </select>
        </label>
      )}
      <section className="tg-card tg-table-card">
        {datos.cargando ? (
          <p role="status">Consultando actividad…</p>
        ) : !lista?.data.length ? (
          <Vacio
            titulo="Todavía no hay actividad registrada"
            detalle="Las acciones nuevas se registran automáticamente."
          />
        ) : (
          <div className="tg-table-scroll">
            <table className="tg-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Persona</th>
                  <th>Sucursal</th>
                  <th>Acción</th>
                  <th>Cliente</th>
                  <th>Registro</th>
                </tr>
              </thead>
              <tbody>
                {lista.data.map((fila) => (
                  <tr key={fila.id}>
                    <td>{fechaLocal(fila.fecha)}</td>
                    <td>{fila.persona}</td>
                    <td>{fila.sucursal || 'Plataforma'}</td>
                    <td>{fila.accion}</td>
                    <td>{fila.cliente || '—'}</td>
                    <td>#{fila.id_registro}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="tg-pagination">
          <span>
            Página {pagina} · {lista?.total || 0} actividades
          </span>
          <div>
            <button
              className="tg-button tg-secondary"
              disabled={pagina === 1 || datos.actualizando}
              onClick={() => setPagina((n) => n - 1)}
            >
              Anterior
            </button>
            <button
              className="tg-button tg-secondary"
              disabled={!lista || pagina >= lista.total_paginas || datos.actualizando}
              onClick={() => setPagina((n) => n + 1)}
            >
              Siguiente
            </button>
          </div>
        </div>
      </section>
    </>
  );
}
