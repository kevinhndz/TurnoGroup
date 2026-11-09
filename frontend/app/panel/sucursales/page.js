'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import '../../login/acceso.css';

export default function Sucursales() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState('');
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    api('/sucursales')
      .then(setDatos)
      .catch((fallo) => setError(fallo.message));
  }, []);

  const sucursales = datos?.data || [];

  async function crear(event) {
    event.preventDefault();
    setGuardando(true);
    setError('');
    const formulario = new FormData(event.currentTarget);
    try {
      await api('/sucursales', {
        method: 'POST',
        body: {
          nombre: formulario.get('nombre'),
          direccion: formulario.get('direccion'),
          telefono: formulario.get('telefono') || null,
          es_principal: formulario.get('es_principal') === 'on',
        },
      });
      event.currentTarget.reset();
      setDatos(await api('/sucursales'));
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setGuardando(false);
    }
  }

  return (
    <main id="contenido" className="acceso-formulario catalogo">
      <Link href="/panel" className="brand">
        Turno Group
      </Link>
      <p>
        <Link href="/panel">← Volver al panel</Link>
      </p>
      <h1>Sucursales</h1>
      <p>Consulta los locales asociados a tu empresa.</p>
      <form className="catalogo-form" onSubmit={crear}>
        <label htmlFor="nombre-sucursal">Nueva sucursal</label>
        <input id="nombre-sucursal" name="nombre" placeholder="Nombre" required />
        <input name="direccion" placeholder="Direccion" required />
        <input name="telefono" placeholder="Telefono (opcional)" />
        <label>
          <input name="es_principal" type="checkbox" /> Es la sucursal principal
        </label>
        <button className="button button-primary" disabled={guardando}>
          {guardando ? 'Guardando…' : 'Agregar sucursal'}
        </button>
      </form>
      {error && <p role="alert">{error}</p>}
      {!datos && !error && <p role="status">Cargando sucursales…</p>}
      {datos && (
        <ul className="catalogo-lista">
          {sucursales.map((item) => (
            <li key={item.id}>
              <span>
                <strong>{item.nombre}</strong>
                <small>{item.direccion}</small>
              </span>
              <span>{item.activo ? 'Activa' : 'Inactiva'}</span>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
