'use client';

import { useId, useState } from 'react';
import Icon from './Icon';

export default function PlanCalculator() {
  const [branches, setBranches] = useState(1);
  const [finance, setFinance] = useState(false);
  const inputId = useId();
  const number = Number(branches);
  const valid = Number.isInteger(number) && number >= 1 && number <= 99;
  const total = valid ? number * 100 + (finance ? 30 : 0) : null;

  function changeBranches(amount) {
    setBranches(Math.min(99, Math.max(1, (valid ? number : 1) + amount)));
  }

  return (
    <div className="plan-calculator" id="calculadora">
      <div className="calculator-heading">
        <p className="eyebrow">Sin hacer cuentas de más</p>
        <h3>¿Cuánto sería para tu negocio?</h3>
        <p>Costo mensual después del mes de prueba.</p>
      </div>
      <div className="calculator-controls">
        <div className="branch-control">
          <label htmlFor={inputId}>Sucursales activas</label>
          <div className="number-stepper">
            <button
              type="button"
              aria-label="Quitar una sucursal"
              disabled={valid && number === 1}
              onClick={() => changeBranches(-1)}
            >
              <Icon name="minus" size={15} />
            </button>
            <input
              id={inputId}
              type="number"
              inputMode="numeric"
              min="1"
              max="99"
              step="1"
              value={branches}
              onChange={(event) => setBranches(event.target.value)}
              aria-invalid={!valid}
              aria-describedby={!valid ? `${inputId}-error` : undefined}
            />
            <button
              type="button"
              aria-label="Agregar una sucursal"
              disabled={valid && number === 99}
              onClick={() => changeBranches(1)}
            >
              <Icon name="plus" size={15} />
            </button>
          </div>
          {!valid && (
            <span className="calculator-error" id={`${inputId}-error`}>
              Escribe un número entero de 1 a 99.
            </span>
          )}
        </div>
        <label className="finance-control">
          <input
            type="checkbox"
            checked={finance}
            onChange={(event) => setFinance(event.target.checked)}
          />
          <span>
            Incluir finanzas<small>+$30 USD por empresa</small>
          </span>
        </label>
      </div>
      <div className="calculator-total" aria-live="polite" aria-atomic="true">
        <span>Total mensual</span>
        <strong>{total === null ? '—' : `$${total.toLocaleString('en-US')}`}</strong>
        <span>USD / mes</span>
      </div>
    </div>
  );
}
