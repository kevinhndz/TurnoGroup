'use client';

import { useState } from 'react';
import { VistaTarjeta } from './TarjetaSuscripcion';

export default function SobreTarjetas({ tarjetas, seleccionar, ocupado }) {
  const [indice, setIndice] = useState(0);
  const [abierto, setAbierto] = useState(false);
  const [reverso, setReverso] = useState(false);
  const [teclado, setTeclado] = useState(false);
  const actual = tarjetas[Math.min(indice, tarjetas.length - 1)];
  if (!actual)
    return (
      <p>
        No tienes tarjetas guardadas. Agrega una para completar tu método de suscripción.
      </p>
    );
  function mover(direccion) {
    setIndice(
      (Math.min(indice, tarjetas.length - 1) + direccion + tarjetas.length) %
        tarjetas.length,
    );
    setReverso(false);
  }
  return (
    <div className="tg-wallet">
      <div
        className={`tg-card-folder ${abierto ? 'is-open' : ''} ${teclado ? 'is-keyboard' : ''}`}
      >
        <div className="tg-folder-back" aria-hidden="true" />
        <button
          type="button"
          className="tg-folder-trigger"
          aria-label={`${abierto ? 'Guardar' : 'Sacar'} tarjeta terminada en ${actual.ultimos_cuatro}`}
          aria-expanded={abierto}
          onClick={(event) => {
            setTeclado(event.detail === 0);
            setAbierto(!abierto);
          }}
        >
          <VistaTarjeta
            titular={actual.titular}
            marca={actual.marca}
            numero={`•••• •••• •••• ${actual.ultimos_cuatro}`}
            vencimiento={`${String(actual.mes).padStart(2, '0')}/${String(actual.anio).slice(-2)}`}
            reverso={reverso}
          />
        </button>
        <div className="tg-folder-front" aria-hidden="true">
          <svg viewBox="0 0 384 110" preserveAspectRatio="none">
            <path d="M0 17C15 7 31 4 49 4H87C110 4 126 17 144 32L158 44C176 59 206 59 225 43L240 30C257 16 271 4 295 4H335C354 4 370 8 384 18V94C384 103 377 110 368 110H16C7 110 0 103 0 94Z" />
            <path
              className="tg-folder-stitch"
              d="M10 21C22 13 35 11 51 11H85C105 11 120 23 137 37L153 50C175 68 208 68 231 49L246 36C262 23 275 11 297 11H333C350 11 363 14 374 22V89C374 97 369 101 360 101H24C15 101 10 96 10 89Z"
            />
          </svg>
          <span>{actual.titular}</span>
          <strong>•••• {actual.ultimos_cuatro}</strong>
        </div>
      </div>
      <div className="tg-wallet-navigation">
        <button
          type="button"
          className="tg-icon-button"
          aria-label="Tarjeta anterior"
          disabled={tarjetas.length < 2}
          onClick={() => mover(-1)}
        >
          ←
        </button>
        <span>
          {Math.min(indice, tarjetas.length - 1) + 1} / {tarjetas.length} ·{' '}
          {actual.prioridad}
        </span>
        <button
          type="button"
          className="tg-icon-button"
          aria-label="Tarjeta siguiente"
          disabled={tarjetas.length < 2}
          onClick={() => mover(1)}
        >
          →
        </button>
      </div>
      <p className="tg-muted">
        {abierto ? 'Tarjeta fuera del sobre' : 'Pulsa la tarjeta para sacarla del sobre'}
      </p>
      <div className="tg-form-actions">
        <button
          type="button"
          className="tg-button tg-secondary"
          aria-pressed={reverso}
          onClick={() => {
            setAbierto(true);
            setReverso(!reverso);
          }}
        >
          {reverso ? 'Ver frente' : 'Ver reverso'}
        </button>
        {actual.prioridad !== 'Principal' && (
          <button
            type="button"
            className="tg-button tg-secondary"
            disabled={ocupado}
            onClick={() => seleccionar(actual, 'principal')}
          >
            Usar como principal
          </button>
        )}
        {actual.prioridad === 'Adicional' && (
          <button
            type="button"
            className="tg-link-button"
            disabled={ocupado}
            onClick={() => seleccionar(actual, 'secundaria')}
          >
            Usar como secundaria
          </button>
        )}
        <button
          type="button"
          className="tg-link-button tg-danger"
          disabled={ocupado}
          onClick={() => seleccionar(actual, 'retirar')}
        >
          Retirar tarjeta
        </button>
      </div>
    </div>
  );
}
