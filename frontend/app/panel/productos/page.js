'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api, dinero } from '../../../lib/api';
import '../../login/acceso.css';

export default function Productos() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    api('/productos').then(setDatos).catch((fallo) => setError(fallo.message));
  }, []);
  const productos = datos?.data || [];
  return <main id="contenido" className="acceso-formulario catalogo">
    <Link href="/panel" className="brand">Turno Group</Link>
    <p><Link href="/panel">← Volver al panel</Link></p>
    <h1>Productos</h1>
    <p>Consulta el catálogo disponible para tu negocio.</p>
    {error && <p role="alert">{error}</p>}
    {!datos && !error && <p role="status">Cargando productos…</p>}
    {datos && <ul className="catalogo-lista">{productos.map((item) => <li key={item.id}><strong>{item.nombre}</strong><span>{dinero(item.precio)} · {item.activo ? 'Activo' : 'Inactivo'}</span></li>)}</ul>}
  </main>;
}
