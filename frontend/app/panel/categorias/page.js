'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import '../../login/acceso.css';

export default function Categorias() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    api('/categorias').then(setDatos).catch((fallo) => setError(fallo.message));
  }, []);
  const categorias = datos?.data || [];
  return <main id="contenido" className="acceso-formulario catalogo">
    <Link href="/panel" className="brand">Turno Group</Link>
    <p><Link href="/panel">← Volver al panel</Link></p>
    <h1>Categorías</h1>
    <p>Organiza los productos de tu negocio.</p>
    {error && <p role="alert">{error}</p>}
    {!datos && !error && <p role="status">Cargando categorías…</p>}
    {datos && <ul className="catalogo-lista">{categorias.map((item) => <li key={item.id}><strong>{item.nombre}</strong><span>{item.activo ? 'Activa' : 'Inactiva'}</span></li>)}</ul>}
  </main>;
}
