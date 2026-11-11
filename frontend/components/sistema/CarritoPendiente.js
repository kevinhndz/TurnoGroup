'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { usarSesion } from './Sesion';
import Icon from '../Icon';
import { api, dinero } from '../../lib/api';
import { Mensaje, Modal } from './Controles';
import PedidoNuevo from './PedidoNuevo';

export default function CarritoPendiente() {
  const { sesion } = usarSesion();
  const [encontrado, setPendiente] = useState(null);
  const [respaldo, setRespaldo] = useState(null);
  const [checkout, setCheckout] = useState(false);
  const [bloqueado, setBloqueado] = useState(false);
  const [abierto, setAbierto] = useState(false);
  const [catalogo, setCatalogo] = useState(null);
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);
  const prefijo = `turno-pedido:${sesion.usuario.id}:${sesion.id_empresa}:${sesion.id_sucursal}:`;
  useEffect(() => {
    function revisar() {
      try {
        const encontrados = Object.keys(sessionStorage)
          .filter((clave) => clave.startsWith(prefijo))
          .flatMap((clave) => {
            try {
              const dato = JSON.parse(sessionStorage.getItem(clave));
              const lineas = Array.isArray(dato) ? dato : dato.lineas;
              const cantidad = (lineas || []).reduce(
                (n, item) => n + (Number(item.cantidad) || 0),
                0,
              );
              return cantidad > 0
                ? [
                    {
                      clave,
                      cantidad,
                      dato: Array.isArray(dato) ? { lineas: dato } : dato,
                      fecha: dato.actualizado || 0,
                    },
                  ]
                : [];
            } catch {
              return [];
            }
          })
          .sort((a, b) => b.fecha - a.fecha);
        setPendiente(encontrados[0] || null);
      } catch {
        setPendiente(null);
      }
    }
    revisar();
    window.addEventListener('turno-carrito', revisar);
    window.addEventListener('storage', revisar);
    return () => {
      window.removeEventListener('turno-carrito', revisar);
      window.removeEventListener('storage', revisar);
    };
  }, [prefijo]);
  useEffect(() => {
    if (!abierto) return;
    let vigente = true;
    setCargando(true);
    setError('');
    setCatalogo(null);
    api('/pedidos/catalogo')
      .then((datos) => {
        if (vigente) setCatalogo(datos);
      })
      .catch((fallo) => {
        if (vigente) setError(fallo.message);
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });
    return () => {
      vigente = false;
    };
  }, [abierto, prefijo]);
  const pendiente = encontrado || (abierto ? respaldo : null);
  if (!pendiente) return null;
  const editar = pendiente.clave.slice(prefijo.length);
  const lineas = pendiente.dato.lineas || [];
  const moneda = catalogo?.empresa?.codigo_moneda || 'HNL';
  const total = lineas.reduce(
    (suma, item) =>
      suma +
      Number(
        catalogo?.productos.find((p) => p.id === item.id_producto)?.precio_local || 0,
      ) *
        item.cantidad,
    0,
  );
  function cambiar(id, cantidad) {
    const nuevas = lineas
      .map((item) => (item.id_producto === id ? { ...item, cantidad } : item))
      .filter((item) => item.cantidad > 0);
    try {
      if (nuevas.length)
        sessionStorage.setItem(
          pendiente.clave,
          JSON.stringify({
            ...pendiente.dato,
            lineas: nuevas,
            paso: 'catalogo',
            actualizado: Date.now(),
          }),
        );
      else {
        sessionStorage.removeItem(pendiente.clave);
        setAbierto(false);
      }
      window.dispatchEvent(
        new CustomEvent('turno-carrito', {
          detail: { clave: pendiente.clave, lineas: nuevas },
        }),
      );
    } catch {
      setError('No se pudo actualizar el carrito en este navegador.');
    }
  }
  function cerrar() {
    if (bloqueado) return;
    setAbierto(false);
    setCheckout(false);
    setRespaldo(null);
  }
  function descartar() {
    if (
      !window.confirm(
        '¿Descartar este carrito? Un pedido ya registrado, si existe, se conserva.',
      )
    )
      return;
    sessionStorage.removeItem(pendiente.clave);
    setAbierto(false);
    setCheckout(false);
    setRespaldo(null);
    window.dispatchEvent(
      new CustomEvent('turno-carrito', {
        detail: { clave: pendiente.clave, lineas: [] },
      }),
    );
  }
  return (
    <div className="tg-resume-cart">
      <button
        className="tg-button tg-primary"
        onClick={() => {
          setRespaldo(pendiente);
          setAbierto(true);
        }}
        aria-haspopup="dialog"
      >
        <Icon name="cart" size={18} />
        Ver carrito <span className="tg-cart-count">{pendiente.cantidad}</span>
      </button>
      <button
        className="tg-icon-button"
        aria-label="Descartar carrito"
        onClick={descartar}
      >
        <Icon name="close" size={18} />
      </button>
      {abierto && (
        <Modal titulo={`Tu carrito · ${pendiente.cantidad} productos`} cerrar={cerrar}>
          <div className="tg-cart-peek">
            {checkout ? (
              <PedidoNuevo
                editar={editar === 'nuevo' ? null : Number(editar)}
                incrustado
                alOcupado={setBloqueado}
                alCerrar={() => (encontrado ? setCheckout(false) : cerrar())}
              />
            ) : (
              <>
                <p>Revisa tu pedido sin salir de esta página.</p>
                <Mensaje error={error} />
                {cargando ? (
                  <p role="status">Cargando productos…</p>
                ) : (
                  catalogo && (
                    <>
                      <div className="tg-cart-peek-lines">
                        {lineas.map((item) => {
                          const producto = catalogo.productos.find(
                            (p) => p.id === item.id_producto,
                          );
                          return (
                            <article key={item.id_producto}>
                              {producto?.ruta_imagen ? (
                                <img
                                  src={`/api/backend/productos/${producto.id}/imagen`}
                                  alt={producto.nombre}
                                  width="64"
                                  height="64"
                                />
                              ) : (
                                <span className="tg-tile-icon">
                                  <Icon name="coffee" />
                                </span>
                              )}
                              <div>
                                <strong>
                                  {producto?.nombre || 'Producto no disponible'}
                                </strong>
                                <small>
                                  {producto
                                    ? dinero(producto.precio_local, moneda)
                                    : 'Revisa el catálogo al continuar'}
                                </small>
                                <div className="tg-quantity">
                                  <button
                                    aria-label={`Quitar una unidad de ${producto?.nombre || 'producto'}`}
                                    disabled={!!pendiente.dato.claveOperacion}
                                    onClick={() =>
                                      cambiar(item.id_producto, item.cantidad - 1)
                                    }
                                  >
                                    −
                                  </button>
                                  <span>{item.cantidad}</span>
                                  <button
                                    aria-label={`Añadir una unidad de ${producto?.nombre || 'producto'}`}
                                    disabled={
                                      item.cantidad >= 99 ||
                                      !!pendiente.dato.claveOperacion ||
                                      !producto
                                    }
                                    onClick={() =>
                                      cambiar(item.id_producto, item.cantidad + 1)
                                    }
                                  >
                                    +
                                  </button>
                                </div>
                              </div>
                              <strong>
                                {producto
                                  ? dinero(
                                      Number(producto.precio_local) * item.cantidad,
                                      moneda,
                                    )
                                  : '—'}
                              </strong>
                            </article>
                          );
                        })}
                      </div>
                      <footer>
                        <div className="tg-subtotal">
                          <span>Subtotal estimado</span>
                          <strong>{dinero(total, moneda)}</strong>
                        </div>
                        <p>Los descuentos y el total final se revisan al continuar.</p>
                        <button
                          className="tg-button tg-primary"
                          onClick={() => {
                            setRespaldo(pendiente);
                            setCheckout(true);
                          }}
                        >
                          Completar pedido aquí
                        </button>
                        <Link
                          className="tg-button tg-secondary"
                          href={
                            editar === 'nuevo'
                              ? '/nuevo-pedido'
                              : `/nuevo-pedido?editar=${editar}`
                          }
                          onClick={() => setAbierto(false)}
                        >
                          Abrir página de checkout <Icon name="arrow" size={16} />
                        </Link>
                        <button className="tg-link-button tg-danger" onClick={descartar}>
                          Cancelar carrito
                        </button>
                      </footer>
                    </>
                  )
                )}
              </>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}
