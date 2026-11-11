'use client';
import FiltrosListado, { useFiltrosListado } from './FiltrosListado';

import { useState } from 'react';
import { usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { Campo, Mensaje, Modal, Vacio } from './Controles';
import { api, listarTodo, fechaLocal } from '../../lib/api';

const horaInput = (valor) => {
  if (!valor) return '';
  const fecha = new Date(valor + (/Z$|[+-]\d\d:\d\d$/.test(valor) ? '' : 'Z'));
  return new Date(fecha.getTime() - fecha.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
};

export default function Reservas() {
  const { sesion, reservasHabilitadas } = usarSesion();
  const [pagina, setPagina] = useState(1);
  const filtros = useFiltrosListado();
  const [estado, setEstado] = useState('Confirmada');
  const [edicion, setEdicion] = useState(null);
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const datos = useDatos(async () => {
    if (!reservasHabilitadas || !sesion.id_sucursal) return null;
    const [lista, mesas] = await Promise.all([
      api(
        `/reservas/?pagina_actual=${pagina}&limite=10&${filtros.parametros}${estado ? `&estado=${estado}` : ''}`,
      ),
      listarTodo('/mesas/'),
    ]);
    return { lista, mesas: mesas.filter((item) => item.activo) };
  }, [pagina, estado, sesion.id_sucursal, reservasHabilitadas, filtros.parametros]);
  if (!reservasHabilitadas)
    return (
      <Vacio
        titulo="Las reservas están deshabilitadas en este local"
        detalle="El gerente puede habilitarlas en Configuración → Servicios."
      />
    );
  const d = datos.datos;
  async function accion(item, tipo) {
    if (
      !window.confirm(
        tipo === 'cancelar'
          ? '¿Cancelar esta reserva?'
          : '¿Marcar que el cliente ya fue atendido?',
      )
    )
      return;
    setOcupado(true);
    setError('');
    try {
      await api(`/reservas/${item.id}/${tipo}`, { method: 'POST' });
      datos.recargar();
      setAviso('Reserva actualizada.');
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setOcupado(false);
    }
  }
  return (
    <>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">AGENDA DEL LOCAL</span>
          <h1>Reservas</h1>
          <p>
            Asignación de mesas por fecha, horario y cantidad de personas. Las horas se
            muestran según este dispositivo.
          </p>
        </div>
        <button className="tg-button tg-primary" onClick={() => setEdicion({})}>
          + Crear reserva
        </button>
      </div>
      <Mensaje error={error || datos.error} aviso={aviso} />
      <div className="tg-card tg-table-card">
        <div className="tg-toolbar">
          <FiltrosListado
            filtros={filtros}
            cambiar={() => setPagina(1)}
            nombre="Buscar reserva por cliente o teléfono"
          />
        </div>
        <nav className="tg-tabs tg-orders-tabs" aria-label="Estado de reservas">
          {[
            ['Confirmada', 'Confirmadas'],
            ['Atendida', 'Atendidas'],
            ['Cancelada', 'Canceladas'],
            ['', 'Todas'],
          ].map(([valor, label]) => (
            <button
              key={valor}
              aria-current={estado === valor ? 'page' : undefined}
              onClick={() => {
                setEstado(valor);
                setPagina(1);
              }}
            >
              {label}
            </button>
          ))}
        </nav>
        {datos.cargando ? (
          <p className="tg-loading-inline" role="status">
            Cargando reservas…
          </p>
        ) : !d?.lista.data.length ? (
          <Vacio titulo="Sin reservas en esta página" />
        ) : (
          <div className="tg-table-scroll">
            <table className="tg-table">
              <thead>
                <tr>
                  <th>Cliente</th>
                  <th>Mesa</th>
                  <th>Personas</th>
                  <th>Inicio</th>
                  <th>Fin</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {d.lista.data.map((item) => (
                  <tr key={item.id}>
                    <td>
                      {item.cliente}
                      <small>{item.telefono}</small>
                    </td>
                    <td>
                      {d.mesas.find((mesa) => mesa.id === item.id_mesa)?.nombre ||
                        `Mesa #${item.id_mesa}`}
                    </td>
                    <td>{item.personas}</td>
                    <td>{fechaLocal(item.inicio)}</td>
                    <td>{fechaLocal(item.fin)}</td>
                    <td>{item.estado}</td>
                    <td>
                      {item.estado === 'Confirmada' && (
                        <div className="tg-row-actions">
                          <button disabled={ocupado} onClick={() => setEdicion(item)}>
                            Editar
                          </button>
                          <button
                            disabled={ocupado}
                            onClick={() => accion(item, 'atender')}
                          >
                            Atendida
                          </button>
                          <button
                            disabled={ocupado}
                            onClick={() => accion(item, 'cancelar')}
                          >
                            Cancelar
                          </button>
                        </div>
                      )}
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
      </div>
      {edicion && (
        <Modal
          titulo={edicion.id ? 'Editar reserva' : 'Crear reserva'}
          cerrar={() => setEdicion(null)}
        >
          <FormularioReserva
            reserva={edicion}
            mesas={d?.mesas || []}
            guardar={async (body) => {
              await api(edicion.id ? `/reservas/${edicion.id}` : '/reservas/', {
                method: edicion.id ? 'PATCH' : 'POST',
                body,
              });
              setEdicion(null);
              datos.recargar();
              setAviso('Reserva guardada.');
            }}
          />
        </Modal>
      )}
    </>
  );
}

function FormularioReserva({ reserva, mesas, guardar }) {
  const [error, setError] = useState('');
  const [ocupado, setOcupado] = useState(false);
  return (
    <form
      className="tg-form"
      onSubmit={async (event) => {
        event.preventDefault();
        const datos = new FormData(event.currentTarget);
        setOcupado(true);
        setError('');
        try {
          await guardar({
            cliente: datos.get('cliente'),
            telefono: datos.get('telefono') || null,
            id_mesa: Number(datos.get('mesa')),
            personas: Number(datos.get('personas')),
            inicio: new Date(datos.get('inicio')).toISOString(),
            fin: new Date(datos.get('fin')).toISOString(),
            nota: datos.get('nota') || null,
          });
        } catch (fallo) {
          setError(fallo.message);
        } finally {
          setOcupado(false);
        }
      }}
    >
      <Mensaje error={error} />
      <div className="tg-form-grid">
        <Campo label="Nombre del cliente">
          <input
            name="cliente"
            required
            minLength={1}
            maxLength={100}
            defaultValue={reserva.cliente || ''}
          />
        </Campo>
        <Campo label="Teléfono">
          <input
            name="telefono"
            type="tel"
            maxLength={30}
            defaultValue={reserva.telefono || ''}
          />
        </Campo>
        <Campo label="Mesa">
          <select name="mesa" required defaultValue={reserva.id_mesa || ''}>
            <option value="" disabled>
              Selecciona una mesa
            </option>
            {mesas.map((mesa) => (
              <option key={mesa.id} value={mesa.id}>
                {mesa.nombre}
                {mesa.capacidad ? ` · ${mesa.capacidad} personas` : ''}
              </option>
            ))}
          </select>
        </Campo>
        <Campo label="Personas">
          <input
            name="personas"
            type="number"
            required
            min={1}
            max={1000}
            defaultValue={reserva.personas || 2}
          />
        </Campo>
        <Campo label="Inicio">
          <input
            name="inicio"
            type="datetime-local"
            required
            defaultValue={horaInput(reserva.inicio)}
          />
        </Campo>
        <Campo label="Fin">
          <input
            name="fin"
            type="datetime-local"
            required
            defaultValue={horaInput(reserva.fin)}
          />
        </Campo>
      </div>
      <Campo label="Nota">
        <textarea name="nota" maxLength={500} defaultValue={reserva.nota || ''} />
      </Campo>
      <button className="tg-button tg-primary" disabled={ocupado || !mesas.length}>
        {ocupado ? 'Guardando…' : 'Guardar reserva'}
      </button>
    </form>
  );
}
