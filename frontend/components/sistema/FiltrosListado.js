'use client';

import { useEffect, useState } from 'react';

export function useFiltrosListado() {
  const [busqueda, setBusqueda] = useState('');
  const [orden, setOrden] = useState('recientes');
  const [consulta, setConsulta] = useState('');
  useEffect(() => {
    const espera = setTimeout(() => setConsulta(busqueda.trim()), 250);
    return () => clearTimeout(espera);
  }, [busqueda]);
  return {
    busqueda,
    setBusqueda,
    orden,
    setOrden,
    parametros: new URLSearchParams({ busqueda: consulta, orden }).toString(),
  };
}

export default function FiltrosListado({
  filtros,
  cambiar,
  nombre = 'Buscar por nombre',
  soloOrden = false,
}) {
  return (
    <div className="tg-list-filters">
      {!soloOrden && (
        <label className="tg-field">
          <span>{nombre}</span>
          <input
            type="search"
            value={filtros.busqueda}
            placeholder="Escribe para buscar…"
            onChange={(event) => {
              filtros.setBusqueda(event.target.value);
              cambiar?.();
            }}
          />
        </label>
      )}
      <label className="tg-field">
        <span>Ordenar registros</span>
        <select
          value={filtros.orden}
          onChange={(event) => {
            filtros.setOrden(event.target.value);
            cambiar?.();
          }}
        >
          <option value="recientes">Más recientes primero</option>
          <option value="antiguos">Más antiguos primero</option>
          <option value="nombre_asc">Nombre: A a Z</option>
          <option value="nombre_desc">Nombre: Z a A</option>
        </select>
      </label>
    </div>
  );
}
