'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { Campo, Mensaje, Modal, Vacio } from './Controles';
import { api, dinero, listarTodo, fechaLocal } from '../../lib/api';

export default function Pedidos() {
  const { sesion } = usarSesion();
  const [estado, setEstado] = useState('');
  const [pagina, setPagina] = useState(1);
  const [busqueda, setBusqueda] = useState('');
  const [detalle, setDetalle] = useState(null);
  const [accion, setAccion] = useState(null);
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const datos = useDatos(async () => {
    if (!sesion.id_sucursal) return null;
    const [lista, tipos, metodos] = await Promise.all([
      api(
        `/pedidos/?pagina_actual=${pagina}&limite=10${estado ? `&estado=${estado}` : ''}`,
      ),
      listarTodo('/tipos-servicio/'),
      listarTodo('/metodos-pago/'),
    ]);
    return { lista, tipos, metodos };
  }, [pagina, estado, sesion.id_sucursal]);
  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get('pedido');
    if (id && /^\d+$/.test(id))
      api(`/pedidos/${id}`)
        .then(setDetalle)
        .catch((fallo) => setError(fallo.message));
  }, []);
  if (!sesion.id_sucursal)
    return <Vacio titulo="Selecciona una sucursal para consultar sus pedidos" />;
  const d = datos.datos;
  async function abrir(id) {
    setOcupado(true);
    setError('');
    try {
      setDetalle(await api(`/pedidos/${id}`));
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setOcupado(false);
    }
  }
  async function ejecutar(event) {
    event.preventDefault();
    const formulario = new FormData(event.currentTarget);
    setOcupado(true);
    setError('');
    try {
      const body =
        accion.tipo === 'cancelar'
          ? { motivo: formulario.get('motivo') }
          : accion.tipo === 'cobrar'
            ? { id_metodo_pago: accion.pedido.id_metodo_pago }
            : undefined;
      const resultado = await api(`/pedidos/${accion.pedido.id}/${accion.tipo}`, {
        method: 'POST',
        body,
      });
      setDetalle(resultado);
      setAccion(null);
      setAviso('El pedido quedó actualizado.');
      datos.recargar();
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setOcupado(false);
    }
  }
  const filas = (d?.lista.data || []).filter(
    (item) =>
      !busqueda ||
      `TG-${item.id} ${item.cliente || ''}`
        .toLocaleLowerCase('es')
        .includes(busqueda.toLocaleLowerCase('es')),
  );
  const tipo = (id) => d?.tipos.find((item) => item.id === id)?.nombre_visible || '—';
  const metodo = (id) => d?.metodos.find((item) => item.id === id)?.nombre_visible || '—';
  return (
    <>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">PEDIDOS DE LA SUCURSAL</span>
          <h1>Pedidos</h1>
          <p>Los pedidos cerrados y cancelados se conservan en el historial.</p>
        </div>
        <Link className="tg-button tg-primary" href="/nuevo-pedido">
          + Nuevo pedido
        </Link>
      </div>
      <Mensaje error={error || datos.error} aviso={aviso} />
      <div className="tg-card tg-table-card">
        <nav className="tg-tabs tg-orders-tabs" aria-label="Estado de pedidos">
          {[
            ['', 'Todos'],
            ['Abierto', 'Abiertos'],
            ['Cerrado', 'Cerrados'],
            ['Cancelado', 'Cancelados'],
          ].map(([valor, label]) => (
            <button
              key={valor}
              aria-current={estado === valor ? 'page' : undefined}
              onClick={() => {
                setEstado(valor);
                setPagina(1);
              }}
            >
              {label} {d?.lista.conteos?.[valor || 'Todos'] ?? ''}
            </button>
          ))}
        </nav>
        <div className="tg-toolbar">
          <Campo label="Buscar número o cliente en esta página">
            <input
              type="search"
              value={busqueda}
              onChange={(event) => setBusqueda(event.target.value)}
              placeholder="Ej. TG-12…"
            />
          </Campo>
          <button className="tg-link-button" onClick={datos.recargar}>
            Actualizar
          </button>
        </div>
        {datos.cargando ? (
          <p className="tg-loading-inline" role="status">
            Cargando pedidos…
          </p>
        ) : !filas.length ? (
          <Vacio
            titulo="No hay pedidos para mostrar"
            detalle="Registra un pedido para comenzar la operación de esta sucursal."
          />
        ) : (
          <div className="tg-table-scroll">
            <table className="tg-table">
              <thead>
                <tr>
                  <th>Pedido</th>
                  <th>Hora / fecha</th>
                  <th>Tipo de servicio</th>
                  <th>Método de pago</th>
                  <th>Total</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filas.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <strong>#TG-{item.id}</strong>
                      <small>{item.cliente}</small>
                    </td>
                    <td>{fechaLocal(item.fecha_registro)}</td>
                    <td>
                      {tipo(item.id_tipo_servicio)}
                      {item.id_mesa && <small>Mesa #{item.id_mesa}</small>}
                    </td>
                    <td>
                      {metodo(item.id_metodo_pago)}
                      <small>{item.fecha_pago ? 'Cobrado' : 'Pendiente de cobro'}</small>
                    </td>
                    <td>{dinero(item.total, item.moneda)}</td>
                    <td>
                      <span
                        className={`tg-status ${item.estado === 'Cerrado' ? 'is-active' : ''}`}
                      >
                        {item.estado}
                      </span>
                    </td>
                    <td>
                      <button
                        className="tg-link-button"
                        disabled={ocupado}
                        onClick={() => abrir(item.id)}
                      >
                        Ver detalle
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="tg-pagination">
          <span>
            Página {pagina} de {Math.max(1, d?.lista.total_paginas || 1)}
          </span>
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
      {detalle && !accion && (
        <Modal
          titulo={`Detalle del pedido #TG-${detalle.id}`}
          cerrar={() => setDetalle(null)}
        >
          <span
            className={`tg-status ${detalle.estado === 'Cerrado' ? 'is-active' : ''}`}
          >
            {detalle.estado}
          </span>
          <dl className="tg-order-info">
            <div>
              <dt>Registrado por</dt>
              <dd>{detalle.registrado_por || 'Persona no disponible'}</dd>
            </div>
            <div>
              <dt>Fecha y hora</dt>
              <dd>{fechaLocal(detalle.fecha_registro)}</dd>
            </div>
            <div>
              <dt>Nombre del cliente</dt>
              <dd>{detalle.cliente || 'Sin nombre registrado'}</dd>
            </div>
            <div>
              <dt>Teléfono del cliente</dt>
              <dd>{detalle.telefono || 'Sin teléfono registrado'}</dd>
            </div>
            <div>
              <dt>Modalidad de atención</dt>
              <dd>
                {tipo(detalle.id_tipo_servicio)}
                {detalle.id_mesa
                  ? ` · ${detalle.nombre_mesa || `Mesa #${detalle.id_mesa}`}`
                  : ''}
              </dd>
            </div>
            <div>
              <dt>Método de pago</dt>
              <dd>
                {metodo(detalle.id_metodo_pago)} ·{' '}
                {detalle.fecha_pago ? 'Cobro registrado' : 'Pendiente de cobro'}
              </dd>
            </div>
            <div>
              <dt>Entrega</dt>
              <dd>{detalle.fecha_entrega ? 'Entregado' : 'Pendiente de entrega'}</dd>
            </div>
            {detalle.direccion && (
              <div>
                <dt>Dirección de entrega</dt>
                <dd>{detalle.direccion}</dd>
              </div>
            )}
          </dl>
          <h3>Detalle de productos</h3>
          <div className="tg-review-lines">
            {detalle.detalles.map((item, indice) => (
              <div key={indice}>
                <span>
                  {item.cantidad} × {item.nombre}
                  <small>
                    Precio unitario: {dinero(item.precio_unitario, detalle.moneda)}
                  </small>
                  <small>{item.nota}</small>
                </span>
                <strong>
                  {dinero(Number(item.precio_unitario) * item.cantidad, detalle.moneda)}
                </strong>
              </div>
            ))}
          </div>
          <div className="tg-order-totals">
            <p>
              <span>Subtotal</span>
              <strong>{dinero(detalle.subtotal, detalle.moneda)}</strong>
            </p>
            <p>
              <span>Descuento</span>
              <strong>{dinero(detalle.descuento, detalle.moneda)}</strong>
            </p>
            <p>
              <span>Impuesto {detalle.impuesto_incluido ? 'incluido' : ''}: </span>
              <strong>{dinero(detalle.impuesto, detalle.moneda)}</strong>
            </p>
          </div>
          <div className="tg-subtotal">
            <span>Total</span>
            <strong>{dinero(detalle.total, detalle.moneda)}</strong>
          </div>
          {detalle.nota && <p>{detalle.nota}</p>}
          {detalle.motivo_cancelacion && (
            <Mensaje aviso={`Cancelado: ${detalle.motivo_cancelacion}`} />
          )}
          <div className="tg-form-actions">
            {detalle.estado === 'Abierto' && (
              <>
                {!detalle.fecha_entrega && (
                  <button
                    className="tg-button tg-secondary"
                    onClick={() => setAccion({ tipo: 'entregar', pedido: detalle })}
                  >
                    Marcar entregado
                  </button>
                )}
                {!detalle.fecha_pago && (
                  <button
                    className="tg-button tg-primary"
                    onClick={() => setAccion({ tipo: 'cobrar', pedido: detalle })}
                  >
                    Registrar cobro
                  </button>
                )}
                {!detalle.fecha_pago && !detalle.fecha_entrega && (
                  <Link
                    href={`/nuevo-pedido?editar=${detalle.id}`}
                    className="tg-button tg-secondary"
                  >
                    Editar pedido
                  </Link>
                )}
              </>
            )}
            {detalle.estado !== 'Cancelado' && (
              <button
                className="tg-link-button tg-danger"
                onClick={() => setAccion({ tipo: 'cancelar', pedido: detalle })}
              >
                Cancelar pedido
              </button>
            )}
          </div>
        </Modal>
      )}
      {accion && (
        <Modal
          titulo={
            accion.tipo === 'cancelar'
              ? '¿Confirmar cancelación?'
              : accion.tipo === 'cobrar'
                ? '¿Confirmas que recibiste el pago?'
                : 'Confirmar entrega'
          }
          cerrar={() => {
            if (!ocupado) setAccion(null);
          }}
        >
          <Mensaje error={error} />
          <form className="tg-form" onSubmit={ejecutar}>
            {accion.tipo === 'cancelar' ? (
              <>
                <p>
                  El pedido permanecerá en el historial. Si ya fue cobrado, la devolución
                  del dinero se realiza fuera de Turno Group.
                </p>
                <Campo label="Motivo de la cancelación">
                  <textarea name="motivo" minLength={3} maxLength={500} required />
                </Campo>
              </>
            ) : accion.tipo === 'cobrar' ? (
              <>
                <p>
                  Se registrará el pago con {metodo(accion.pedido.id_metodo_pago)} y el
                  pedido quedará cerrado.
                </p>
              </>
            ) : (
              <p>Se marcará la entrega. El estado cerrado depende del pago.</p>
            )}
            <div className="tg-form-actions">
              <button
                type="button"
                className="tg-button tg-secondary"
                disabled={ocupado}
                onClick={() => setAccion(null)}
              >
                Volver
              </button>
              <button className="tg-button tg-primary" disabled={ocupado}>
                {ocupado
                  ? 'Guardando…'
                  : accion.tipo === 'cobrar'
                    ? 'Sí, registrar cobro'
                    : 'Confirmar'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
}
