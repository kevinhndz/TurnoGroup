'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import '../../login/acceso.css';

export default function Sucursales() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api('/sucursales')
      .then(setDatos)
      .catch((fallo) => setError(fallo.message));
  }, []);

  const sucursales = datos?.data || [];

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
