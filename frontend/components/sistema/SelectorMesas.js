'use client';
import { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { Mensaje } from './Controles';

export default function SelectorMesas({ valor, cambiar, editar }) {
  const [mesas, setMesas] = useState([]);
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(true);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    let vigente = true;
    let solicitud;
    const cargar = async () => {
      solicitud?.abort();
      solicitud = new AbortController();
      try {
        const filas = await api(`/pedidos/mesas${editar ? `?id_pedido=${editar}` : ''}`, {
          signal: solicitud.signal,
        });
        if (vigente) {
          setMesas(filas);
          setError('');
        }
      } catch (fallo) {
        if (vigente && fallo.name !== 'AbortError') setError(fallo.message);
      } finally {
        if (vigente) setCargando(false);
      }
    };
    cargar();
    const reloj = setInterval(() => {
      if (document.visibilityState === 'visible') cargar();
    }, 20000);
    window.addEventListener('focus', cargar);
    return () => {
      vigente = false;
      solicitud?.abort();
      clearInterval(reloj);
      window.removeEventListener('focus', cargar);
    };
  }, [editar, revision]);
  const seleccionada = mesas.find((mesa) => String(mesa.id) === String(valor));
  return (
    <fieldset className="tg-table-picker">
      <legend>Plano del salón · Seleccionar mesa</legend>
      <div className="tg-table-legend">
        <span>🟢 Disponible</span>
        <span>🔴 Ocupada</span>
        <span>🟠 Reservada</span>
        <button
          type="button"
          className="tg-link-button"
          onClick={() => setRevision((n) => n + 1)}
        >
          Actualizar mesas
        </button>
      </div>
      <Mensaje error={error} />
      {seleccionada && seleccionada.estado !== 'Disponible' && (
        <Mensaje error="Esta mesa ya no está disponible. Selecciona otra antes de registrar." />
      )}
      {cargando ? (
        <p role="status">Consultando mesas…</p>
      ) : (
        <>
          <div className="tg-table-grid">
            {mesas.map((mesa) => (
              <button
                type="button"
                key={mesa.id}
                className={`tg-table-tile ${mesa.estado === 'Disponible' ? 'is-free' : mesa.estado === 'Ocupada' ? 'is-busy' : 'is-reserved'} ${String(valor) === String(mesa.id) ? 'is-selected' : ''}`}
                disabled={mesa.estado !== 'Disponible' || !!error}
                aria-pressed={String(valor) === String(mesa.id)}
                aria-label={`${mesa.nombre}, ${mesa.estado}`}
                onClick={() => cambiar(String(mesa.id))}
              >
                <span
                  className={`tg-floor-table ${(mesa.capacidad || 4) > 4 ? 'is-long' : ''}`}
                  aria-hidden="true"
                >
                  <i className="tg-chair tg-chair-top" />
                  <i className="tg-chair tg-chair-bottom" />
                  {(mesa.capacidad || 4) > 2 && (
                    <>
                      <i className="tg-chair tg-chair-left" />
                      <i className="tg-chair tg-chair-right" />
                    </>
                  )}
                  <span className="tg-table-surface">
                    {mesa.nombre.replace(/^Mesa\s*/i, '')}
                  </span>
                </span>
                <strong>{mesa.nombre}</strong>
                <small>
                  {mesa.capacidad
                    ? `${mesa.capacidad} personas`
                    : 'Capacidad sin definir'}
                </small>
                <span>
                  {String(valor) === String(mesa.id) ? 'Seleccionada' : mesa.estado}
                </span>
              </button>
            ))}
          </div>
          {!mesas.length && (
            <p>
              Este local todavía no tiene mesas. El gerente puede prepararlas desde Mesas.
            </p>
          )}
          <button
            type="button"
            className={`tg-button tg-secondary ${valor === 'mostrador' ? 'is-selected' : ''}`}
            aria-pressed={valor === 'mostrador'}
            onClick={() => cambiar('mostrador')}
          >
            Atención en mostrador · sin mesa
          </button>
        </>
      )}
    </fieldset>
  );
}
