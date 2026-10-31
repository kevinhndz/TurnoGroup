'use client';

import { useState } from 'react';
import { Campo, Mensaje } from './Controles';

export default function Formulario({
  campos,
  inicial = {},
  opciones = {},
  guardar,
  cancelar,
  texto = 'Guardar cambios',
  children,
}) {
  const [valores, setValores] = useState(() =>
    Object.fromEntries(
      campos.map((campo) => [
        campo.clave,
        inicial[campo.clave] ??
          campo.valor ??
          (campo.type === 'checkbox'
            ? false
            : campo.type === 'select' && !campo.nullable
              ? String(
                  (campo.opciones ||
                    (opciones[campo.fuente] || []).map((item) => [item.id]))[0]?.[0] ??
                    '',
                )
              : ''),
      ]),
    ),
  );
  const [error, setError] = useState('');
  const [enviando, setEnviando] = useState(false);

  async function enviar(event) {
    event.preventDefault();
    setError('');
    const datos = {};
    for (const campo of campos) {
      const valor = valores[campo.clave];
      if (campo.nullable && valor === '') datos[campo.clave] = null;
      else if (campo.type === 'number' || campo.fuente)
        datos[campo.clave] = valor === '' ? (campo.valor ?? 0) : Number(valor);
      else
        datos[campo.clave] =
          typeof valor === 'string' && campo.type !== 'password' ? valor.trim() : valor;
    }
    if (datos.tipo_descuento === 'Porcentaje' && datos.valor > 100) {
      setError('El porcentaje no puede ser mayor que 100.');
      return;
    }
    setEnviando(true);
    try {
      await guardar(datos);
    } catch (fallo) {
      const camposInvalidos = fallo.errores
        ?.map((item) => item.campo.replace(/^body\./, ''))
        .join(', ');
      setError(camposInvalidos ? `${fallo.message}: ${camposInvalidos}.` : fallo.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form className="tg-form" onSubmit={enviar}>
      <Mensaje error={error} />
      <div className="tg-form-grid">
        {campos.map((campo) => {
          const cambiar = (event) =>
            setValores({
              ...valores,
              [campo.clave]:
                campo.type === 'checkbox' ? event.target.checked : event.target.value,
            });
          const props = {
            name: campo.clave,
            value: valores[campo.clave],
            onChange: cambiar,
            required: campo.required,
            minLength: campo.minLength,
            maxLength: campo.maxLength,
            min: campo.min,
            max: campo.max,
            step: campo.step,
            disabled: enviando,
          };
          if (campo.type === 'checkbox')
            return (
              <label className="tg-check" key={campo.clave}>
                <input
                  name={campo.clave}
                  type="checkbox"
                  checked={!!valores[campo.clave]}
                  onChange={cambiar}
                  disabled={enviando}
                />
                <span>{campo.label}</span>
              </label>
            );
          return (
            <Campo key={campo.clave} label={campo.label} ayuda={campo.ayuda}>
              {campo.type === 'select' ? (
                <select {...props}>
                  {campo.nullable && <option value="">Sin categoría</option>}
                  {(
                    campo.opciones ||
                    (opciones[campo.fuente] || []).map((item) => [item.id, item.nombre])
                  ).map(([valor, label]) => (
                    <option key={valor} value={valor}>
                      {label}
                    </option>
                  ))}
                  {!campo.fuente &&
                    campo.opciones &&
                    valores[campo.clave] &&
                    !campo.opciones.some(
                      ([valor]) => String(valor) === String(valores[campo.clave]),
                    ) && (
                      <option value={valores[campo.clave]}>{valores[campo.clave]}</option>
                    )}
                  {campo.fuente &&
                    valores[campo.clave] &&
                    !(opciones[campo.fuente] || []).some(
                      (item) => String(item.id) === String(valores[campo.clave]),
                    ) && (
                      <option value={valores[campo.clave]}>
                        Registro #{valores[campo.clave]}
                      </option>
                    )}
                </select>
              ) : campo.type === 'textarea' ? (
                <textarea {...props} rows={3} />
              ) : (
                <input {...props} type={campo.type || 'text'} />
              )}
            </Campo>
          );
        })}
      </div>
      {children}
      <div className="tg-form-actions">
        {cancelar && (
          <button
            type="button"
            className="tg-button tg-secondary"
            onClick={cancelar}
            disabled={enviando}
          >
            Cancelar
          </button>
        )}
        <button className="tg-button tg-primary" disabled={enviando}>
          {enviando ? 'Guardando…' : texto}
        </button>
      </div>
    </form>
  );
}
