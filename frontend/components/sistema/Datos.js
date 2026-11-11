'use client';

import { useEffect, useState } from 'react';
import { usarSesion } from './Sesion';
import { limpiarCache } from '../../lib/api';

export function useDatos(cargar, dependencias = []) {
  const { version } = usarSesion();
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(true);
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError('');
    Promise.resolve()
      .then(cargar)
      .then((resultado) => {
        if (vigente) setDatos(resultado);
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
  }, [...dependencias, version, revision]);

  return {
    datos,
    setDatos,
    error,
    cargando: cargando && datos === null,
    actualizando: cargando,
    recargar: () => {
      limpiarCache();
      setRevision((valor) => valor + 1);
    },
  };
}
