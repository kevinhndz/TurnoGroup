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
  const [editando, setEditando] = useState(null);
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
  async function actualizar(event, item) {
    event.preventDefault();
    setGuardando(true);
    setError('');
    const datosFormulario = new FormData(event.currentTarget);
    try {
      await api(`/productos/${item.id}`, {
        method: 'PATCH',
        body: {
          nombre: datosFormulario.get('nombre'),
          precio: Number(datosFormulario.get('precio')),
        },
      });
      setEditando(null);
      setDatos(await api('/productos'));
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setGuardando(false);
    }
  }
  async function desactivar(item) {
    if (!window.confirm(`¿Desactivar ${item.nombre}?`)) return;
    setGuardando(true);
    setError('');
    try {
      await api(`/productos/${item.id}/desactivar`, { method: 'POST' });
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
      {error && (
        <p role="alert" aria-live="polite">
          {error}
        </p>
      )}
      {!datos && !error && <p role="status">Cargando productos…</p>}
      {datos && (
        <ul className="catalogo-lista">
          {productos.map((item) => (
            <li key={item.id}>
              {editando === item.id ? (
                <form
                  className="fila-edicion"
                  onSubmit={(event) => actualizar(event, item)}
                >
                  <input name="nombre" defaultValue={item.nombre} required />
                  <input
                    name="precio"
                    type="number"
                    step="0.01"
                    min="0"
                    defaultValue={item.precio}
                    required
                  />
                  <button disabled={guardando}>Guardar</button>
                  <button type="button" onClick={() => setEditando(null)}>
                    Cancelar
                  </button>
                </form>
              ) : (
                <>
                  <strong>{item.nombre}</strong>
                  <span>
                    {dinero(item.precio)} · {item.activo ? 'Activo' : 'Inactivo'}{' '}
                    {item.activo && (
                      <>
                        <button type="button" onClick={() => setEditando(item.id)}>
                          Editar
                        </button>
                        <button type="button" onClick={() => desactivar(item)}>
                          Desactivar
                        </button>
                      </>
                    )}
                  </span>
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
