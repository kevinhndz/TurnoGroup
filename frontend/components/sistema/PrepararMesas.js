'use client';
import { useState } from 'react';
import { api } from '../../lib/api';
import { Campo, Mensaje } from './Controles';
export default function PrepararMesas({ guardar }) {
  const [cantidad, setCantidad] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  return (
    <section className="tg-card">
      <h2>Preparar las mesas del local</h2>
      <p>
        Indica cuántas mesas necesitas en total. Conservamos las existentes y creamos
        únicamente las que falten.
      </p>
      <form
        className="tg-inline-form"
        onSubmit={async (event) => {
          event.preventDefault();
          setOcupado(true);
          setError('');
          try {
            const resultado = await api('/mesas/preparar', {
              method: 'POST',
              body: { cantidad: Number(cantidad) },
            });
            setAviso(`${resultado.creadas} mesas nuevas preparadas.`);
            guardar();
          } catch (fallo) {
            setError(fallo.message);
          } finally {
            setOcupado(false);
          }
        }}
      >
        <Campo label="Cantidad total de mesas">
          <input
            type="number"
            min={1}
            max={200}
            required
            value={cantidad}
            onChange={(e) => setCantidad(e.target.value)}
          />
        </Campo>
        <button className="tg-button tg-primary" disabled={ocupado}>
          {ocupado ? 'Preparando…' : 'Preparar mesas'}
        </button>
      </form>
      <Mensaje error={error} aviso={aviso} />
    </section>
  );
}
