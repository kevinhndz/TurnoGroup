'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { usarSesion } from './Sesion';
import Icon from '../Icon';

export default function CarritoPendiente() {
  const { sesion } = usarSesion();
  const [pendiente, setPendiente] = useState(null);
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
                ? [{ clave, cantidad, fecha: dato.actualizado || 0 }]
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
  if (!pendiente) return null;
  const editar = pendiente.clave.slice(prefijo.length);
  return (
    <div className="tg-resume-cart">
      <Link
        className="tg-button tg-primary"
        href={editar === 'nuevo' ? '/nuevo-pedido' : `/nuevo-pedido?editar=${editar}`}
      >
        <Icon name="cart" size={18} />
        Volver al carrito <span className="tg-cart-count">{pendiente.cantidad}</span>
      </Link>
      <button
        className="tg-icon-button"
        aria-label="Descartar carrito"
        onClick={() => {
          if (
            window.confirm(
              '¿Descartar este carrito? El pedido guardado, si existe, no se modifica.',
            )
          ) {
            sessionStorage.removeItem(pendiente.clave);
            window.dispatchEvent(new Event('turno-carrito'));
          }
        }}
      >
        <Icon name="close" size={18} />
      </button>
    </div>
  );
}
