'use client';

import { useState } from 'react';
import { Campo, Mensaje } from './Controles';

const ejemplos = {
  visa: { numero: '4242 4242 4242 4242', marca: 'Visa' },
  mastercard: { numero: '5555 5555 5555 4444', marca: 'Mastercard' },
  amex: { numero: '3782 822463 10005', marca: 'American Express' },
};

export function VistaTarjeta({
  titular,
  marca = 'Visa',
  numero = '•••• •••• •••• 4242',
  vencimiento = 'MM/AA',
  reverso = false,
}) {
  return (
    <div className={`tg-credit-preview ${reverso ? 'is-flipped' : ''}`}>
      <div className="tg-credit-rotor">
        <div className="tg-credit-face tg-credit-front">
          <div className="tg-credit-top">
            <span className="tg-credit-chip" />
            <strong>{marca}</strong>
          </div>
          <span className="tg-credit-number">{numero}</span>
          <div className="tg-credit-bottom">
            <div>
              <small>TITULAR</small>
              <strong>{titular || 'TU NOMBRE'}</strong>
            </div>
            <div>
              <small>VENCE</small>
              <span>{vencimiento}</span>
            </div>
          </div>
        </div>
        <div className="tg-credit-face tg-credit-back">
          <div className="tg-credit-stripe" />
          <div className="tg-credit-signature">•••</div>
          <small>TARJETA DE PRUEBA · SIN CARGOS</small>
        </div>
      </div>
    </div>
  );
}

export default function TarjetaSuscripcion({
  titularInicial = '',
  guardar,
  ocupado = false,
  boton = 'Guardar tarjeta de prueba',
}) {
  const [tipo, setTipo] = useState('visa');
  const [titular, setTitular] = useState(titularInicial);
  const [numero, setNumero] = useState(ejemplos.visa.numero);
  const [vencimiento, setVencimiento] = useState('12/29');
  const [codigo, setCodigo] = useState('');
  const [reverso, setReverso] = useState(false);
  const [error, setError] = useState('');
  async function enviar(event) {
    event.preventDefault();
    setError('');
    const ejemplo = Object.entries(ejemplos).find(
      ([, valor]) => valor.numero.replace(/\D/g, '') === numero.replace(/\D/g, ''),
    );
    if (!ejemplo) {
      setError('Usa uno de los números ficticios indicados.');
      return;
    }
    const [mes, anio] = vencimiento.split('/').map(Number);
    if (!titular.trim() || !mes || !anio) {
      setError('Completa el titular y el vencimiento.');
      return;
    }
    try {
      await guardar({
        tarjeta_prueba: ejemplo[0],
        titular: titular.trim(),
        mes,
        anio: 2000 + anio,
      });
      setCodigo('');
      setReverso(false);
    } catch (fallo) {
      setError(fallo.message);
    }
  }
  return (
    <div className="tg-card-entry">
      <div className="tg-card-entry-visual">
        <VistaTarjeta
          titular={titular}
          marca={ejemplos[tipo].marca}
          numero={numero}
          vencimiento={vencimiento}
          reverso={reverso}
        />
        <span className="tg-badge">Simulación · Solo tarjetas ficticias</span>
        <p>Elige un ejemplo para probar la experiencia. No se realizará ningún cargo.</p>
        <div className="tg-demo-cards" aria-label="Tarjetas de ejemplo">
          {Object.entries(ejemplos).map(([clave, valor]) => (
            <button
              type="button"
              key={clave}
              aria-pressed={tipo === clave}
              onClick={() => {
                setTipo(clave);
                setNumero(valor.numero);
              }}
            >
              {valor.marca}
            </button>
          ))}
        </div>
      </div>
      <form className="tg-form tg-card-entry-form" onSubmit={enviar}>
        <h2>Datos de la tarjeta</h2>
        <Mensaje error={error} />
        <Campo
          label="Número de tarjeta de prueba"
          ayuda="Usa los números de los ejemplos de la izquierda."
        >
          <input
            value={numero}
            onChange={(event) =>
              setNumero(event.target.value.replace(/[^\d ]/g, '').slice(0, 23))
            }
            inputMode="numeric"
            autoComplete="off"
            required
          />
        </Campo>
        <Campo label="Nombre del titular">
          <input
            value={titular}
            onChange={(event) => setTitular(event.target.value.toUpperCase())}
            required
            maxLength={100}
            autoComplete="off"
          />
        </Campo>
        <div className="tg-form-grid">
          <Campo label="Vencimiento">
            <input
              value={vencimiento}
              onChange={(event) => {
                const digitos = event.target.value.replace(/\D/g, '').slice(0, 4);
                setVencimiento(
                  digitos.length > 2
                    ? `${digitos.slice(0, 2)}/${digitos.slice(2)}`
                    : digitos,
                );
              }}
              placeholder="MM/AA"
              pattern="(0[1-9]|1[0-2])/[0-9]{2}"
              required
              inputMode="numeric"
              autoComplete="off"
            />
          </Campo>
          <Campo label="CVV de prueba">
            <input
              type="password"
              value={codigo}
              onChange={(event) =>
                setCodigo(event.target.value.replace(/\D/g, '').slice(0, 4))
              }
              onFocus={() => setReverso(true)}
              onBlur={() => setReverso(false)}
              pattern="[0-9]{3,4}"
              placeholder="123"
              required
              inputMode="numeric"
              autoComplete="off"
            />
          </Campo>
        </div>
        <button className="tg-button tg-primary" disabled={ocupado}>
          {ocupado ? 'Guardando…' : boton}
        </button>
      </form>
    </div>
  );
}
