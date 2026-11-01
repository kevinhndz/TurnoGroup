'use client';

import { useState } from 'react';
import FiltrosListado, { useFiltrosListado } from './FiltrosListado';
import { api, listarTodo } from '../../lib/api';
import { useDatos } from './Datos';
import { Campo, Mensaje, Modal, Vacio } from './Controles';
import Formulario from './Formulario';

const roles = ['Gerente', 'Administrador', 'Mesero'];

export default function Equipo() {
  const [pagina, setPagina] = useState(1);
  const filtros = useFiltrosListado();
  const [invitacion, setInvitacion] = useState(false);
  const [seleccionado, setSeleccionado] = useState(null);
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const datos = useDatos(async () => {
    const [vinculos, invitaciones, sucursales] = await Promise.all([
      api(`/vinculos-laborales/?pagina_actual=${pagina}&limite=10&${filtros.parametros}`),
      api(
        `/invitaciones-laborales/?pagina_actual=${pagina}&limite=10&${filtros.parametros}`,
      ),
      listarTodo('/sucursales/'),
    ]);
    return { vinculos, invitaciones, sucursales };
  }, [pagina, filtros.parametros]);

  async function abrir(vinculo) {
    setError('');
    setOcupado(true);
    try {
      setSeleccionado(await api(`/vinculos-laborales/${vinculo.id}`));
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setOcupado(false);
    }
  }

  async function asignar(sucursal, tiene) {
    setOcupado(true);
    setError('');
    try {
      await api(
        tiene
          ? `/vinculos-laborales/${seleccionado.id}/sucursales/${sucursal.id}`
          : `/vinculos-laborales/${seleccionado.id}/sucursales`,
        {
          method: tiene ? 'DELETE' : 'POST',
          ...(tiene ? {} : { body: { id_sucursal: sucursal.id } }),
        },
      );
      setSeleccionado(await api(`/vinculos-laborales/${seleccionado.id}`));
      window.dispatchEvent(new Event('turno-datos'));
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setOcupado(false);
    }
  }

  const paginas = Math.max(
    1,
    datos.datos?.vinculos.total_paginas || 1,
    datos.datos?.invitaciones.total_paginas || 1,
  );
  return (
    <section>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">PERSONAS Y LOCALES</span>
          <h1>Tu equipo</h1>
          <p>
            Administra roles y asignaciones. Invita a cada persona con el correo de su
            cuenta.
          </p>
        </div>
        <button className="tg-button tg-primary" onClick={() => setInvitacion(true)}>
          + Invitar persona
        </button>
      </div>
      <Mensaje error={error || datos.error} aviso={aviso} />
      <FiltrosListado
        filtros={filtros}
        cambiar={() => setPagina(1)}
        nombre="Buscar empleado por nombre o correo"
      />
      <div className="tg-card tg-table-card">
        <div className="tg-toolbar">
          <h2>Vínculos laborales</h2>
          <button className="tg-link-button" onClick={datos.recargar}>
            Actualizar
          </button>
        </div>
        {datos.cargando ? (
          <p className="tg-loading-inline" role="status">
            Cargando equipo…
          </p>
        ) : !datos.datos?.vinculos.data.length ? (
          <Vacio titulo="Todavía no hay vínculos" />
        ) : (
          <div className="tg-table-scroll">
            <table className="tg-table">
              <thead>
                <tr>
                  <th>Persona</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {datos.datos.vinculos.data.map((item) => (
                  <tr key={item.id}>
                    <td>{item.nombre_usuario || 'Persona del equipo'}</td>
                    <td>{item.rol}</td>
                    <td>
                      <span className={`tg-status ${item.activo ? 'is-active' : ''}`}>
                        {item.activo ? 'Activo' : 'Desactivado'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="tg-link-button"
                        disabled={ocupado}
                        onClick={() => abrir(item)}
                      >
                        Administrar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      <section className="tg-card tg-table-card">
        <div className="tg-toolbar">
          <h2>Invitaciones</h2>
        </div>
        {!datos.datos?.invitaciones.data.length ? (
          <Vacio titulo="Sin invitaciones en esta página" />
        ) : (
          <div className="tg-table-scroll">
            <table className="tg-table">
              <thead>
                <tr>
                  <th>Correo</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th>Vence</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {datos.datos.invitaciones.data.map((item) => {
                  const pendiente =
                    !item.fecha_revocacion &&
                    !item.fecha_aceptacion &&
                    new Date(
                      `${item.vencimiento}${/Z$|[+-]\d\d:\d\d$/.test(item.vencimiento) ? '' : 'Z'}`,
                    ) > new Date();
                  return (
                    <tr key={item.id}>
                      <td>{item.correo}</td>
                      <td>{item.rol}</td>
                      <td>
                        {item.fecha_aceptacion
                          ? 'Aceptada'
                          : item.fecha_revocacion
                            ? 'Revocada'
                            : pendiente
                              ? 'Pendiente'
                              : 'Vencida'}
                      </td>
                      <td>{new Date(item.vencimiento).toLocaleDateString('es-HN')}</td>
                      <td>
                        {pendiente && (
                          <button
                            className="tg-link-button"
                            disabled={ocupado}
                            onClick={async () => {
                              setOcupado(true);
                              setError('');
                              try {
                                await api(`/invitaciones-laborales/${item.id}/revocar`, {
                                  method: 'POST',
                                });
                                datos.recargar();
                                setAviso('Invitación revocada.');
                              } catch (fallo) {
                                setError(fallo.message);
                              } finally {
                                setOcupado(false);
                              }
                            }}
                          >
                            Revocar
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <div className="tg-pagination">
        <span>
          Página {pagina} de {paginas}
        </span>
        <div>
          <button
            className="tg-button tg-secondary"
            disabled={pagina === 1 || datos.cargando}
            onClick={() => setPagina(pagina - 1)}
          >
            Anterior
          </button>
          <button
            className="tg-button tg-secondary"
            disabled={pagina >= paginas || datos.cargando}
            onClick={() => setPagina(pagina + 1)}
          >
            Siguiente
          </button>
        </div>
      </div>
      {invitacion && (
        <Modal titulo="Invitar al equipo" cerrar={() => setInvitacion(false)}>
          <Invitar
            sucursales={datos.datos?.sucursales.filter((item) => item.activo) || []}
            terminar={() => {
              setInvitacion(false);
              datos.recargar();
              setAviso(
                'La invitación quedó creada. Revisa el correo de la persona invitada.',
              );
            }}
          />
        </Modal>
      )}
      {seleccionado && (
        <Modal
          titulo={`Usuario #${seleccionado.id_usuario}`}
          cerrar={() => setSeleccionado(null)}
        >
          <Mensaje error={error} />
          <Formulario
            campos={[
              {
                clave: 'rol',
                label: 'Rol en la empresa',
                type: 'select',
                opciones: roles.map((rol) => [rol, rol]),
              },
              { clave: 'activo', label: 'Vínculo activo', type: 'checkbox' },
            ]}
            inicial={seleccionado}
            guardar={async (body) => {
              await api(`/vinculos-laborales/${seleccionado.id}`, {
                method: 'PATCH',
                body,
              });
              setSeleccionado(null);
              datos.recargar();
              setAviso('Vínculo actualizado.');
              window.dispatchEvent(new Event('turno-datos'));
            }}
          />
          <hr />
          <h3>Sucursales asignadas</h3>
          <p className="tg-muted">
            Administrador y mesero tienen una sola sucursal. Para trasladarlos, retira la
            anterior y asigna la nueva.
          </p>
          <div className="tg-check-list">
            {datos.datos?.sucursales.map((sucursal) => {
              const tiene = seleccionado.asignaciones_sucursales.some(
                (item) => item.id_sucursal === sucursal.id,
              );
              return (
                <label key={sucursal.id} className="tg-check">
                  <input
                    type="checkbox"
                    checked={tiene}
                    disabled={
                      ocupado ||
                      !sucursal.activo ||
                      (seleccionado.rol !== 'Gerente' &&
                        !tiene &&
                        seleccionado.asignaciones_sucursales.length > 0)
                    }
                    onChange={() => asignar(sucursal, tiene)}
                  />
                  {sucursal.nombre}
                  {!sucursal.activo && ' (desactivada)'}
                </label>
              );
            })}
          </div>
        </Modal>
      )}
    </section>
  );
}

function Invitar({ sucursales, terminar }) {
  const [rol, setRol] = useState('Mesero');
  const [seleccion, setSeleccion] = useState([]);
  const [error, setError] = useState('');
  const [ocupado, setOcupado] = useState(false);
  return (
    <form
      className="tg-form"
      onSubmit={async (event) => {
        event.preventDefault();
        const correo = new FormData(event.currentTarget).get('correo');
        if (rol !== 'Gerente' && seleccion.length !== 1) {
          setError('Selecciona una sola sucursal para este rol.');
          return;
        }
        setOcupado(true);
        setError('');
        try {
          await api('/invitaciones-laborales/', {
            method: 'POST',
            body: { correo, rol, sucursales: seleccion },
          });
          terminar();
        } catch (fallo) {
          setError(fallo.message);
        } finally {
          setOcupado(false);
        }
      }}
    >
      <Mensaje error={error} />
      <Campo label="Correo de la persona">
        <input type="email" name="correo" autoComplete="email" required />
      </Campo>
      <Campo label="Rol">
        <select
          value={rol}
          onChange={(event) => {
            setRol(event.target.value);
            setSeleccion([]);
          }}
        >
          {roles.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
      </Campo>
      <fieldset>
        <legend>Sucursales</legend>
        {!sucursales.length && <p className="tg-muted">Primero crea una sucursal.</p>}
        <div className="tg-check-list">
          {sucursales.map((item) => (
            <label className="tg-check" key={item.id}>
              <input
                type={rol === 'Gerente' ? 'checkbox' : 'radio'}
                name="sucursal-invitada"
                checked={seleccion.includes(item.id)}
                onChange={(event) =>
                  setSeleccion(
                    event.target.checked
                      ? rol === 'Gerente'
                        ? [...seleccion, item.id]
                        : [item.id]
                      : seleccion.filter((id) => id !== item.id),
                  )
                }
              />
              {item.nombre}
            </label>
          ))}
        </div>
      </fieldset>
      <button className="tg-button tg-primary" disabled={ocupado}>
        {ocupado ? 'Enviando…' : 'Enviar invitación'}
      </button>
    </form>
  );
}
