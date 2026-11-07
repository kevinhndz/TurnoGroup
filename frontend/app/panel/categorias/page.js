'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import '../../login/acceso.css';

export default function Categorias() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState('');
  const [guardando, setGuardando] = useState(false);
  useEffect(() => {
    api('/categorias')
      .then(setDatos)
      .catch((fallo) => setError(fallo.message));
  }, []);
  const categorias = datos?.data || [];
  async function crear(event) {
    event.preventDefault();
    setGuardando(true); setError('');
    try {
      await api('/categorias', { method: 'POST', body: { nombre: new FormData(event.currentTarget).get('nombre'), orden_presentacion: 1 } });
      event.currentTarget.reset();
      setDatos(await api('/categorias'));
    } catch (fallo) { setError(fallo.message); } finally { setGuardando(false); }
  }
  return (
    <main id="contenido" className="acceso-formulario catalogo">
      <Link href="/panel" className="brand">
        Turno Group
      </Link>
      <p>
        <Link href="/panel">← Volver al panel</Link>
      </p>
      <h1>Categorías</h1>
      <p>Organiza los productos de tu negocio.</p>
      <form className="catalogo-form" onSubmit={crear}>
        <label htmlFor="nombre-categoria">Nueva categoría</label>
        <input id="nombre-categoria" name="nombre" maxLength={60} required />
        <button className="button button-primary" disabled={guardando}>{guardando ? 'Guardando…' : 'Agregar categoría'}</button>
      </form>
      {error && <p role="alert">{error}</p>}
      {!datos && !error && <p role="status">Cargando categorías…</p>}
      {datos && (
        <ul className="catalogo-lista">
          {categorias.map((item) => (
            <li key={item.id}>
              <strong>{item.nombre}</strong>
              <span>{item.activo ? 'Activa' : 'Inactiva'}</span>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
