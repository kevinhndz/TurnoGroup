'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api, dinero } from '../../../lib/api';
import '../../login/acceso.css';

export default function Productos() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState('');
  const [categorias, setCategorias] = useState([]);
  const [guardando, setGuardando] = useState(false);
  useEffect(() => {
    api('/productos')
      .then(setDatos)
      .catch((fallo) => setError(fallo.message));
    api('/categorias')
      .then((respuesta) => setCategorias(respuesta.data || []))
      .catch(() => {});
  }, []);
  const productos = datos?.data || [];
  async function crear(event) {
    event.preventDefault();
    setGuardando(true);
    setError('');
    const datosFormulario = new FormData(event.currentTarget);
    try {
      await api('/productos', {
        method: 'POST',
        body: {
          nombre: datosFormulario.get('nombre'),
          precio: Number(datosFormulario.get('precio')),
          id_categoria: Number(datosFormulario.get('id_categoria')) || null,
        },
      });
      event.currentTarget.reset();
      setDatos(await api('/productos'));
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
      <h1>Productos</h1>
      <p>Consulta el catálogo disponible para tu negocio.</p>
      <form className="catalogo-form" onSubmit={crear}>
        <label htmlFor="nombre-producto">Nuevo producto</label>
        <input id="nombre-producto" name="nombre" required maxLength={100} />
        <label htmlFor="precio-producto">Precio</label>
        <input
          id="precio-producto"
          name="precio"
          type="number"
          min="0"
          step="0.01"
          required
        />
        <label htmlFor="categoria-producto">Categoría</label>
        <select id="categoria-producto" name="id_categoria">
          <option value="">Sin categoría</option>
          {categorias.map((item) => (
            <option key={item.id} value={item.id}>
              {item.nombre}
            </option>
          ))}
        </select>
        <button className="button button-primary" disabled={guardando}>
          {guardando ? 'Guardando…' : 'Agregar producto'}
        </button>
      </form>
      {error && <p role="alert" aria-live="polite">{error}</p>}
      {!datos && !error && <p role="status">Cargando productos…</p>}
      {datos && (
        <ul className="catalogo-lista">
          {productos.map((item) => (
            <li key={item.id}>
              <strong>{item.nombre}</strong>
              <span>
                {dinero(item.precio)} · {item.activo ? 'Activo' : 'Inactivo'}
              </span>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
