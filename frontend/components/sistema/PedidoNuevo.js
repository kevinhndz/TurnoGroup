'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import { AccesoPrivado, usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { Campo, Mensaje, Modal, Vacio } from './Controles';
import { api, dinero } from '../../lib/api';
import Icon from '../Icon';

export default function PedidoNuevo({ editar = null }) {
  const { sesion } = usarSesion();
  return (
    <AccesoPrivado>
      {sesion && (
        <Contenido
          key={`${sesion.id_empresa}:${sesion.id_sucursal}:${editar}`}
          editar={editar}
        />
      )}
    </AccesoPrivado>
  );
}

function Contenido({ editar }) {
  const { sesion, mesasHabilitadas } = usarSesion();
  const [paso, setPaso] = useState('catalogo');
  const [categoria, setCategoria] = useState('todas');
  const [busqueda, setBusqueda] = useState('');
  const [carrito, setCarrito] = useState([]);
  const [listo, setListo] = useState(false);
  const [nota, setNota] = useState(null);
  const [error, setError] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [cotizacion, setCotizacion] = useState(null);
  const [calculando, setCalculando] = useState(false);
  const [creado, setCreado] = useState(null);
  const [seleccion, setSeleccion] = useState({
    id_tipo_servicio: '',
    id_metodo_pago: '',
    id_mesa: '',
    id_descuento: '',
    cliente: '',
    telefono: '',
    direccion: '',
    nota: '',
    cobrado: false,
  });
  const claveOperacion = useRef(null);
  const claveCarrito = `turno-pedido:${sesion.usuario.id}:${sesion.id_empresa}:${sesion.id_sucursal}:${editar || 'nuevo'}`;
  const datos = useDatos(async () => {
    if (!sesion.id_sucursal || sesion.usuario.rol_plataforma === 'Superadministrador')
      return null;
    const catalogo = await api('/pedidos/catalogo');
    return {
      ...catalogo,
      productos: catalogo.productos.map((producto) => ({
        ...producto,
        precioLocal: Math.round(Number(producto.precio_local) * 100),
      })),
    };
  }, [sesion.id_sucursal, mesasHabilitadas]);

  useEffect(() => {
    try {
      const guardado = JSON.parse(sessionStorage.getItem(claveCarrito) || '[]');
      if (Array.isArray(guardado))
        setCarrito(
          guardado
            .filter(
              (item) =>
                Number.isInteger(item.id_producto) &&
                Number.isInteger(item.cantidad) &&
                item.cantidad > 0 &&
                item.cantidad <= 99,
            )
            .map((item) => ({
              id_producto: item.id_producto,
              cantidad: item.cantidad,
              nota: typeof item.nota === 'string' ? item.nota.slice(0, 300) : null,
            })),
        );
    } catch {}
    setListo(true);
  }, [claveCarrito]);
  useEffect(() => {
    if (listo)
      try {
        sessionStorage.setItem(claveCarrito, JSON.stringify(carrito));
      } catch {}
  }, [carrito, listo, claveCarrito]);
  useEffect(() => {
    if (datos.datos)
      setSeleccion((anterior) => ({
        ...anterior,
        id_tipo_servicio:
          anterior.id_tipo_servicio || datos.datos.servicios[0]?.id_tipo_servicio || '',
        id_metodo_pago:
          anterior.id_metodo_pago || datos.datos.pagos[0]?.id_metodo_pago || '',
      }));
  }, [datos.datos]);

  useEffect(() => {
    if (!editar) return;
    let vigente = true;
    api(`/pedidos/${editar}`)
      .then((pedido) => {
        if (!vigente) return;
        if (pedido.estado !== 'Abierto' || pedido.fecha_pago || pedido.fecha_entrega) {
          setError('Este pedido ya no se puede editar.');
          return;
        }
        setCarrito(
          pedido.detalles.map(({ id_producto, cantidad, nota }) => ({
            id_producto,
            cantidad,
            nota,
          })),
        );
        setSeleccion({
          id_tipo_servicio: pedido.id_tipo_servicio,
          id_metodo_pago: pedido.id_metodo_pago,
          id_mesa: pedido.id_mesa || '',
          id_descuento: pedido.id_descuento || '',
          cliente: pedido.cliente || '',
          telefono: pedido.telefono || '',
          direccion: pedido.direccion || '',
          nota: pedido.nota || '',
          cobrado: false,
        });
      })
      .catch((fallo) => setError(fallo.message));
    return () => {
      vigente = false;
    };
  }, [editar]);

  const cuerpo = {
    id_tipo_servicio: Number(seleccion.id_tipo_servicio),
    id_metodo_pago: Number(seleccion.id_metodo_pago),
    id_mesa: seleccion.id_mesa ? Number(seleccion.id_mesa) : null,
    id_descuento: seleccion.id_descuento ? Number(seleccion.id_descuento) : null,
    cliente: seleccion.cliente || null,
    telefono: seleccion.telefono || null,
    direccion: seleccion.direccion || null,
    nota: seleccion.nota || null,
    detalles: carrito,
  };
  const firma = JSON.stringify(cuerpo);
  useEffect(() => {
    if (paso !== 'revision' || !carrito.length) return;
    const cancelar = new AbortController();
    setCotizacion(null);
    setCalculando(true);
    const temporizador = setTimeout(() => {
      api(`/pedidos/cotizar${editar ? `?id_pedido=${editar}` : ''}`, {
        method: 'POST',
        body: JSON.parse(firma),
        signal: cancelar.signal,
      })
        .then((resultado) => {
          setCotizacion(resultado);
          setError('');
        })
        .catch((fallo) => {
          if (fallo.name !== 'AbortError') setError(fallo.message);
        })
        .finally(() => {
          if (!cancelar.signal.aborted) setCalculando(false);
        });
    }, 250);
    return () => {
      clearTimeout(temporizador);
      cancelar.abort();
    };
  }, [firma, paso, carrito.length]);

  if (sesion.usuario.rol_plataforma === 'Superadministrador')
    return (
      <Vacio titulo="La plataforma no opera pedidos de clientes">
        <Link href="/panel">Volver al panel</Link>
      </Vacio>
    );
  if (!sesion.id_sucursal)
    return (
      <Vacio titulo="Selecciona una sucursal en el panel">
        <Link href="/panel">Volver al panel</Link>
      </Vacio>
    );
  if (datos.cargando)
    return (
      <div className="tg-loading" role="status">
        Abriendo catálogo…
      </div>
    );
  if (datos.error)
    return (
      <main className="tg-loading">
        <Mensaje error={datos.error} />
        <button className="tg-button tg-secondary" onClick={datos.recargar}>
          Volver a intentar
        </button>
      </main>
    );
  const d = datos.datos;
  const moneda = d.empresa.codigo_moneda;
  const lineas = carrito.map((item) => ({
    ...item,
    producto: d.productos.find((producto) => producto.id === item.id_producto),
  }));
  const subtotal = lineas.reduce(
    (total, item) => total + (item.producto?.precioLocal || 0) * item.cantidad,
    0,
  );
  const visibles = d.productos.filter(
    (item) =>
      (categoria === 'todas' || item.id_categoria === Number(categoria)) &&
      item.nombre.toLocaleLowerCase('es').includes(busqueda.toLocaleLowerCase('es')),
  );
  const servicio = d.servicios.find(
    (item) => item.id_tipo_servicio === Number(seleccion.id_tipo_servicio),
  );

  function agregar(producto) {
    setCarrito((anterior) => {
      const existe = anterior.find((item) => item.id_producto === producto.id);
      return existe
        ? anterior.map((item) =>
            item.id_producto === producto.id
              ? { ...item, cantidad: Math.min(99, item.cantidad + 1) }
              : item,
          )
        : [...anterior, { id_producto: producto.id, cantidad: 1, nota: null }];
    });
  }
  function cantidad(id, numero) {
    setCarrito((anterior) =>
      numero <= 0
        ? anterior.filter((item) => item.id_producto !== id)
        : anterior.map((item) =>
            item.id_producto === id ? { ...item, cantidad: Math.min(99, numero) } : item,
          ),
    );
  }
  function cambiar(campo, valor) {
    setSeleccion((anterior) => ({
      ...anterior,
      [campo]: valor,
      ...(campo === 'id_tipo_servicio' ? { id_mesa: '' } : {}),
    }));
  }
  async function registrar(event) {
    event.preventDefault();
    if (!cotizacion || calculando || enviando) return;
    setEnviando(true);
    setError('');
    try {
      claveOperacion.current ||= crypto.randomUUID();
      const pedido = await api(editar ? `/pedidos/${editar}` : '/pedidos/', {
        method: editar ? 'PATCH' : 'POST',
        body: editar
          ? cuerpo
          : {
              ...cuerpo,
              clave_operacion: claveOperacion.current,
              cobrado: seleccion.cobrado,
              total_esperado: Number(cotizacion.total).toFixed(2),
            },
      });
      setCreado(pedido);
      setCarrito([]);
      setPaso('confirmado');
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="tg-wizard tg-orders">
      <header className="tg-order-header">
        <Link href="/panel">← Volver al panel</Link>
        <h2>
          {paso === 'revision'
            ? 'Revisar pedido'
            : paso === 'confirmado'
              ? 'Pedido registrado'
              : editar
                ? 'Editar pedido'
                : 'Nuevo pedido'}
        </h2>
        <span className="tg-badge">{d.sucursal.nombre}</span>
        <span className="tg-order-attendant">Atendido por: {sesion.usuario.nombre}</span>
      </header>
      <main id="contenido" className="tg-order-main">
        <Mensaje error={error} />
        {paso === 'catalogo' && (
          <>
            <label className="tg-search tg-order-search">
              <span>Buscar producto</span>
              <input
                type="search"
                placeholder="Buscar producto por nombre…"
                value={busqueda}
                onChange={(event) => setBusqueda(event.target.value)}
              />
            </label>
            <div className="tg-order-layout">
              <nav className="tg-order-categories" aria-label="Categorías">
                <button
                  aria-pressed={categoria === 'todas'}
                  onClick={() => setCategoria('todas')}
                >
                  Todas las categorías
                </button>
                {d.categorias
                  .filter((item) => item.activo)
                  .map((item) => (
                    <button
                      key={item.id}
                      aria-pressed={categoria === String(item.id)}
                      onClick={() => setCategoria(String(item.id))}
                    >
                      {item.nombre}
                    </button>
                  ))}
              </nav>
              <section className="tg-catalog-main">
                <div className="tg-section-heading">
                  <h2>Catálogo de productos</h2>
                  <small>{visibles.length} productos</small>
                </div>
                {!visibles.length ? (
                  <Vacio
                    titulo="No hay productos disponibles"
                    detalle="El gerente debe asignar productos activos a esta sucursal."
                  />
                ) : (
                  <div className="tg-product-grid">
                    {visibles.map((producto) => (
                      <article className="tg-product" key={producto.id}>
                        <div className="tg-product-visual">
                          {producto.ruta_imagen ? (
                            <img
                              src={`/api/backend/productos/${producto.id}/imagen?v=${encodeURIComponent(producto.ruta_imagen)}`}
                              alt={producto.nombre}
                              width={400}
                              height={260}
                              loading="lazy"
                            />
                          ) : (
                            <Icon name="coffee" size={46} />
                          )}
                        </div>
                        <div className="tg-product-body">
                          <h3>{producto.nombre}</h3>
                          <p>{producto.descripcion || 'Sin descripción.'}</p>
                          <footer>
                            <strong>{dinero(producto.precioLocal / 100, moneda)}</strong>
                            <button
                              className="tg-button tg-secondary"
                              onClick={() => agregar(producto)}
                            >
                              <Icon name="plus" size={15} />
                              Agregar
                            </button>
                          </footer>
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </section>
              <aside className="tg-cart">
                <header>
                  <Icon name="receipt" />
                  <div>
                    <h2>Pedido</h2>
                    <small>
                      {carrito.reduce((n, item) => n + item.cantidad, 0)} productos
                    </small>
                  </div>
                </header>
                <div className="tg-cart-lines">
                  {!lineas.length ? (
                    <Vacio
                      titulo="Comanda vacía"
                      detalle="Selecciona productos del catálogo para armar el pedido."
                    />
                  ) : (
                    lineas.map((item) => (
                      <article className="tg-cart-line" key={item.id_producto}>
                        <div>
                          <h3>{item.producto?.nombre || 'Producto no disponible'}</h3>
                          <strong>
                            {dinero(
                              ((item.producto?.precioLocal || 0) * item.cantidad) / 100,
                              moneda,
                            )}
                          </strong>
                        </div>
                        <small>
                          {dinero((item.producto?.precioLocal || 0) / 100, moneda)} ×{' '}
                          {item.cantidad}
                        </small>
                        <div className="tg-cart-line-actions">
                          <button
                            className="tg-link-button"
                            onClick={() => setNota(item)}
                          >
                            {item.nota ? `Nota: ${item.nota}` : '+ Añadir nota libre'}
                          </button>
                          <button
                            className="tg-link-button"
                            onClick={() => cantidad(item.id_producto, 0)}
                          >
                            Quitar
                          </button>
                        </div>
                        <div className="tg-quantity">
                          <button
                            aria-label="Restar una unidad"
                            onClick={() => cantidad(item.id_producto, item.cantidad - 1)}
                          >
                            −
                          </button>
                          <span>{item.cantidad}</span>
                          <button
                            disabled={item.cantidad === 99}
                            aria-label="Agregar una unidad"
                            onClick={() => cantidad(item.id_producto, item.cantidad + 1)}
                          >
                            +
                          </button>
                        </div>
                      </article>
                    ))
                  )}
                </div>
                <footer>
                  <div className="tg-subtotal">
                    <span>Subtotal de productos</span>
                    <strong>{dinero(subtotal / 100, moneda)}</strong>
                  </div>
                  <button
                    className="tg-button tg-primary tg-wide"
                    disabled={!carrito.length || lineas.some((item) => !item.producto)}
                    onClick={() => {
                      setError('');
                      setPaso('revision');
                    }}
                  >
                    Continuar →
                  </button>
                  <button
                    className="tg-link-button"
                    onClick={() => {
                      if (window.confirm('¿Quitar los productos de esta comanda?'))
                        setCarrito([]);
                    }}
                  >
                    Cancelar pedido
                  </button>
                </footer>
              </aside>
            </div>
          </>
        )}
        {paso === 'revision' && (
          <form onSubmit={registrar} className="tg-checkout">
            <div className="tg-step-stack">
              <section className="tg-card">
                <h2>1. Tipo de servicio</h2>
                <div className="tg-choice-grid">
                  {d.servicios.map((item) => (
                    <button
                      type="button"
                      className={
                        Number(seleccion.id_tipo_servicio) === item.id_tipo_servicio
                          ? 'is-selected'
                          : ''
                      }
                      key={item.id_tipo_servicio}
                      onClick={() => cambiar('id_tipo_servicio', item.id_tipo_servicio)}
                    >
                      {item.nombre_visible}
                    </button>
                  ))}
                </div>
                {!d.servicios.length && (
                  <p>El gerente debe habilitar un servicio en esta sucursal.</p>
                )}
                {servicio?.clave_concepto === 'comer_aqui' &&
                  servicio.mesas_habilitadas && (
                    <Campo label="Mesa asignada">
                      <select
                        value={seleccion.id_mesa}
                        onChange={(event) => cambiar('id_mesa', event.target.value)}
                      >
                        <option value="">Sin mesa / mostrador</option>
                        {d.mesas.map((item) => (
                          <option key={item.id} value={item.id}>
                            {item.nombre}
                          </option>
                        ))}
                      </select>
                    </Campo>
                  )}
                <div className="tg-form-grid">
                  <Campo
                    label={`Nombre del cliente${servicio?.clave_concepto === 'domicilio' ? ' (requerido)' : ' (opcional)'}`}
                  >
                    <input
                      maxLength={100}
                      value={seleccion.cliente}
                      required={servicio?.clave_concepto === 'domicilio'}
                      onChange={(event) => cambiar('cliente', event.target.value)}
                    />
                  </Campo>
                  <Campo label="Teléfono de contacto">
                    <input
                      maxLength={30}
                      type="tel"
                      value={seleccion.telefono}
                      onChange={(event) => cambiar('telefono', event.target.value)}
                    />
                  </Campo>
                </div>
                {servicio?.clave_concepto === 'domicilio' && (
                  <Campo label="Dirección o referencia">
                    <textarea
                      maxLength={500}
                      required
                      value={seleccion.direccion}
                      onChange={(event) => cambiar('direccion', event.target.value)}
                    />
                  </Campo>
                )}
              </section>
              <section className="tg-card">
                <h2>2. ¿Cómo pagará el cliente?</h2>
                <div className="tg-choice-grid">
                  {d.pagos.map((item) => (
                    <button
                      type="button"
                      className={
                        Number(seleccion.id_metodo_pago) === item.id_metodo_pago
                          ? 'is-selected'
                          : ''
                      }
                      key={item.id_metodo_pago}
                      onClick={() => cambiar('id_metodo_pago', item.id_metodo_pago)}
                    >
                      {item.nombre_visible}
                    </button>
                  ))}
                </div>
                <label className="tg-check">
                  <input
                    type="checkbox"
                    checked={seleccion.cobrado}
                    onChange={(event) => cambiar('cobrado', event.target.checked)}
                  />
                  Registrar que ya se recibió el pago
                </label>
                <p className="tg-muted">
                  El dinero se cobra fuera de Turno Group. Para registrar un cobro debe
                  haber una caja abierta.
                </p>
                <Campo label="Descuento">
                  <select
                    value={seleccion.id_descuento}
                    onChange={(event) => cambiar('id_descuento', event.target.value)}
                  >
                    <option value="">Sin descuento</option>
                    {d.descuentos.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.nombre} ·{' '}
                        {item.tipo_descuento === 'Porcentaje'
                          ? `${item.valor}%`
                          : dinero(item.valor, moneda)}
                      </option>
                    ))}
                  </select>
                </Campo>
                <Campo label="Nota general del pedido">
                  <textarea
                    maxLength={1000}
                    value={seleccion.nota}
                    onChange={(event) => cambiar('nota', event.target.value)}
                  />
                </Campo>
              </section>
            </div>
            <aside className="tg-card tg-checkout-summary">
              <h2>Resumen del pedido</h2>
              <button
                type="button"
                className="tg-link-button"
                disabled={enviando}
                onClick={() => setPaso('catalogo')}
              >
                ← Volver al catálogo
              </button>
              <div className="tg-review-lines">
                {lineas.map((item) => (
                  <div key={item.id_producto}>
                    <span>
                      {item.cantidad} × {item.producto?.nombre}
                      <small>{item.nota}</small>
                    </span>
                    <strong>
                      {dinero(
                        ((item.producto?.precioLocal || 0) * item.cantidad) / 100,
                        moneda,
                      )}
                    </strong>
                  </div>
                ))}
              </div>
              {calculando ? (
                <p role="status">Calculando total…</p>
              ) : (
                cotizacion && (
                  <>
                    <div className="tg-subtotal">
                      <span>Subtotal</span>
                      <strong>{dinero(cotizacion.subtotal, moneda)}</strong>
                    </div>
                    <div className="tg-subtotal">
                      <span>Descuento</span>
                      <span>− {dinero(cotizacion.descuento, moneda)}</span>
                    </div>
                    <div className="tg-subtotal">
                      <span>
                        Impuesto {cotizacion.impuesto_incluido ? 'incluido' : ''}
                      </span>
                      <span>{dinero(cotizacion.impuesto, moneda)}</span>
                    </div>
                    <div className="tg-subtotal">
                      <span>Total · {moneda}</span>
                      <strong>{dinero(cotizacion.total, moneda)}</strong>
                    </div>
                  </>
                )
              )}
              <Mensaje error={error} />
              <button
                className="tg-button tg-primary tg-wide"
                disabled={enviando || calculando || !cotizacion}
              >
                {enviando
                  ? 'Guardando…'
                  : editar
                    ? 'Guardar cambios'
                    : 'Registrar pedido'}
              </button>
            </aside>
          </form>
        )}
        {paso === 'confirmado' && creado && (
          <section className="tg-card tg-confirmation">
            <span className="tg-empty-icon">
              <Icon name="check" size={32} />
            </span>
            <span className="tg-badge">Pedido registrado</span>
            <h1>Todo listo, pedido #TG-{creado.id}</h1>
            <p>El pedido quedó guardado en {d.sucursal.nombre}.</p>
            <div className="tg-confirmation-total">
              {dinero(creado.total, creado.moneda)}
            </div>
            <p>
              {creado.fecha_pago ? 'Cobro registrado' : 'Pendiente de cobro'} ·{' '}
              {creado.estado}
            </p>
            <div className="tg-form-actions">
              <Link
                className="tg-button tg-primary"
                href={`/panel/pedidos?pedido=${creado.id}`}
              >
                Ver pedido
              </Link>
              <Link
                className="tg-button tg-secondary"
                href="/nuevo-pedido"
                onClick={() => {
                  claveOperacion.current = null;
                  setPaso('catalogo');
                  setCreado(null);
                  setCotizacion(null);
                }}
              >
                Nuevo pedido
              </Link>
              <Link className="tg-button tg-secondary" href="/panel">
                Volver al panel
              </Link>
            </div>
          </section>
        )}
        {nota && (
          <Modal titulo="Nota de producto" cerrar={() => setNota(null)}>
            <form
              className="tg-form"
              onSubmit={(event) => {
                event.preventDefault();
                setCarrito(
                  carrito.map((item) =>
                    item.id_producto === nota.id_producto
                      ? { ...item, nota: nota.nota || null }
                      : item,
                  ),
                );
                setNota(null);
              }}
            >
              <Campo label="Nota libre para el producto">
                <textarea
                  maxLength={300}
                  rows={4}
                  value={nota.nota || ''}
                  onChange={(event) => setNota({ ...nota, nota: event.target.value })}
                />
              </Campo>
              <button className="tg-button tg-primary">Guardar nota</button>
            </form>
          </Modal>
        )}
      </main>
    </div>
  );
}
