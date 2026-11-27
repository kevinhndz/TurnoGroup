'use client';

import { useEffect, useId, useRef, useState } from 'react';
import { api, dinero } from '../../lib/api';
import { Campo, Mensaje } from './Controles';

const ruta = '/productos/menu-inteligente';

function datosExtraidos(fila) {
  return {
    nombre: fila.nombre.trim(),
    precio: fila.precio === '' ? null : fila.precio,
    categoria: fila.categoria?.trim() || null,
    descripcion: fila.descripcion || null,
    evidencia: fila.evidencia,
    advertencia: fila.advertencia,
  };
}

export default function MenuInteligente({
  categorias,
  sucursal,
  guardar,
  cancelar,
  alOcupar,
}) {
  const [modo, setModo] = useState('texto');
  const [texto, setTexto] = useState('');
  const [foto, setFoto] = useState(null);
  const [filas, setFilas] = useState([]);
  const [advertencias, setAdvertencias] = useState([]);
  const [moneda, setMoneda] = useState('HNL');
  const [error, setError] = useState('');
  const [ocupado, setOcupado] = useState('');
  const [pendiente, setPendiente] = useState(false);
  const [confirmado, setConfirmado] = useState(false);
  const solicitud = useRef(null);
  const listaCategorias = useId();
  useEffect(() => () => solicitud.current?.abort(), []);

  function ocupar(valor) {
    setOcupado(valor);
    alOcupar(!!valor);
  }

  function cambiar(indice, cambios, revisar = true) {
    setFilas((actuales) =>
      actuales.map((fila, i) => (i === indice ? { ...fila, ...cambios } : fila)),
    );
    setConfirmado(false);
    if (revisar) setPendiente(true);
  }

  async function preparar() {
    ocupar('leyendo');
    setError('');
    setFilas([]);
    setAdvertencias([]);
    setConfirmado(false);
    solicitud.current = new AbortController();
    try {
      const propuesta = await api(`${ruta}/preparar`, {
        method: 'POST',
        body: modo === 'texto' ? { texto } : { imagen: foto.contenido },
        signal: solicitud.current.signal,
      });
      setMoneda(propuesta.moneda);
      setAdvertencias(propuesta.advertencias);
      setFilas(
        propuesta.productos.map((fila) => ({
          ...fila,
          precio: fila.precio ?? '',
          categoria: fila.categoria || '',
          seleccionado: !fila.existente && !fila.repetido,
          accion: fila.existente ? 'usar_existente' : 'crear',
          id_existente: fila.existente?.id || null,
        })),
      );
      setPendiente(false);
    } catch (fallo) {
      if (fallo.name !== 'AbortError') setError(fallo.message);
    } finally {
      ocupar('');
    }
  }

  async function revisar() {
    ocupar('revisando');
    setError('');
    try {
      const propuesta = await api(`${ruta}/revisar`, {
        method: 'POST',
        body: { productos: filas.map(datosExtraidos) },
      });
      setFilas((actuales) =>
        actuales.map((fila, i) => ({
          ...fila,
          ...propuesta.productos[i],
          precio: propuesta.productos[i].precio ?? '',
          categoria: propuesta.productos[i].categoria || '',
        })),
      );
      setPendiente(false);
      setConfirmado(false);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      ocupar('');
    }
  }

  const seleccionados = filas.filter((fila) => fila.seleccionado);
  const nuevos = seleccionados.filter((fila) => fila.accion === 'crear');
  const categoriasNuevas = [
    ...new Set(
      nuevos
        .filter((fila) => fila.categoria && !fila.categoria_existente)
        .map((fila) => fila.categoria),
    ),
  ];
  const incompleto = seleccionados.some((fila) =>
    fila.accion === 'crear'
      ? !fila.nombre.trim() ||
        fila.precio === '' ||
        Number(fila.precio) < 0 ||
        !Number.isFinite(Number(fila.precio)) ||
        fila.existente ||
        fila.categoria_inactiva
      : !fila.id_existente,
  );

  return (
    <div className="tg-form tg-menu-ia" aria-busy={!!ocupado}>
      <p>
        Pega tus productos o sube una foto del menú. Prepararemos una propuesta editable.
        Los productos se guardan únicamente cuando confirmas.
      </p>
      {!filas.length && (
        <>
          <Campo label="Origen del catálogo">
            <select
              value={modo}
              disabled={!!ocupado}
              onChange={(event) => {
                setModo(event.target.value);
                setError('');
              }}
            >
              <option value="texto">Pegar una lista</option>
              <option value="foto">Subir foto del menú</option>
            </select>
          </Campo>
          {modo === 'texto' ? (
            <Campo
              label="Lista de productos"
              ayuda="Hasta 100 productos. Si falta un precio, podrás completarlo después."
            >
              <textarea
                value={texto}
                maxLength={12000}
                rows={5}
                disabled={!!ocupado}
                onChange={(event) => setTexto(event.target.value)}
                placeholder="Vendo café a 15 lempiras, pan dulce a 10 y agua pequeña sin precio todavía."
              />
            </Campo>
          ) : (
            <Campo
              label="Foto del menú · JPG o PNG, hasta 3 MB"
              ayuda="Una foto nítida, hasta 12 megapíxeles. Puedes recortarla antes de subirla."
            >
              <input
                type="file"
                accept="image/jpeg,image/png"
                disabled={!!ocupado}
                onChange={async (event) => {
                  setFoto(null);
                  setError('');
                  const archivo = event.target.files[0];
                  if (!archivo) return;
                  ocupar('archivo');
                  try {
                    if (archivo.size > 3_000_000) throw new Error('La foto supera 3 MB.');
                    if (!['image/jpeg', 'image/png'].includes(archivo.type))
                      throw new Error('Selecciona una foto JPG o PNG.');
                    const contenido = await new Promise((resolve, reject) => {
                      const lector = new FileReader();
                      lector.onload = () => resolve(lector.result.split(',')[1]);
                      lector.onerror = () =>
                        reject(new Error('No se pudo leer la foto.'));
                      lector.readAsDataURL(archivo);
                    });
                    setFoto({ contenido, nombre: archivo.name });
                  } catch (fallo) {
                    setError(fallo.message);
                  } finally {
                    ocupar('');
                  }
                }}
              />
            </Campo>
          )}
          {modo === 'foto' && foto && <small>Foto seleccionada: {foto.nombre}</small>}
          <small className="tg-muted">
            Al preparar, el texto o la foto se envía a OpenAI para su lectura. Revisa los
            nombres y precios antes de guardar.
          </small>
          <button
            type="button"
            className="tg-button tg-primary"
            disabled={!!ocupado || (modo === 'texto' ? !texto.trim() : !foto)}
            onClick={preparar}
          >
            Preparar catálogo
          </button>
        </>
      )}
      {!!ocupado && (
        <p role="status">
          {ocupado === 'leyendo'
            ? 'Leyendo el menú y buscando coincidencias…'
            : ocupado === 'guardando'
              ? 'Guardando catálogo…'
              : ocupado === 'archivo'
                ? 'Preparando foto…'
                : 'Revisando cambios…'}
        </p>
      )}
      <Mensaje error={error} />
      {!!filas.length && (
        <>
          <p className="tg-menu-summary">
            {filas.length} productos encontrados · Moneda: {moneda}. Los precios faltantes
            se dejan vacíos.
          </p>
          {!!advertencias.length && (
            <ul>
              {advertencias.map((aviso, i) => (
                <li key={i}>{aviso}</li>
              ))}
            </ul>
          )}
          <datalist id={listaCategorias}>
            {categorias
              .filter((c) => c.activo)
              .map((c) => (
                <option key={c.id} value={c.nombre} />
              ))}
          </datalist>
          <div className="tg-table-scroll">
            <table className="tg-table tg-menu-table">
              <caption>
                Revisa qué productos importar y corrige los datos necesarios
              </caption>
              <thead>
                <tr>
                  <th>Importar</th>
                  <th>Producto y origen</th>
                  <th>Categoría</th>
                  <th>Precio ({moneda})</th>
                  <th>Acción y coincidencias</th>
                </tr>
              </thead>
              <tbody>
                {filas.map((fila, i) => {
                  const coincidencias = fila.existente
                    ? [fila.existente]
                    : fila.similares;
                  return (
                    <tr key={i}>
                      <td>
                        <input
                          type="checkbox"
                          aria-label={`Importar fila ${i + 1}`}
                          checked={fila.seleccionado}
                          disabled={!!ocupado}
                          onChange={(e) =>
                            cambiar(i, { seleccionado: e.target.checked }, false)
                          }
                        />
                      </td>
                      <td>
                        <input
                          aria-label={`Nombre fila ${i + 1}`}
                          value={fila.nombre}
                          maxLength={100}
                          disabled={!!ocupado || fila.accion !== 'crear'}
                          onChange={(e) => cambiar(i, { nombre: e.target.value })}
                        />
                        <small>
                          Leído: {fila.evidencia || 'Sin fragmento de referencia'}
                        </small>
                        {fila.advertencia && (
                          <small className="tg-menu-warning">
                            Revisar: {fila.advertencia}
                          </small>
                        )}
                        {fila.repetido && (
                          <small className="tg-menu-warning">
                            Nombre repetido en la propuesta.
                          </small>
                        )}
                      </td>
                      <td>
                        <input
                          list={listaCategorias}
                          aria-label={`Categoría fila ${i + 1}`}
                          value={fila.categoria}
                          maxLength={60}
                          disabled={!!ocupado || fila.accion !== 'crear'}
                          onChange={(e) => cambiar(i, { categoria: e.target.value })}
                        />
                        <small>
                          {fila.categoria_inactiva
                            ? 'Categoría desactivada: elige otra.'
                            : fila.categoria_existente
                              ? 'Categoría existente'
                              : fila.categoria
                                ? 'Se creará esta categoría'
                                : 'Sin categoría'}
                        </small>
                      </td>
                      <td>
                        <input
                          type="number"
                          aria-label={`Precio fila ${i + 1}`}
                          min="0"
                          max="99999999.99"
                          step="0.01"
                          value={fila.precio}
                          placeholder="Completar"
                          disabled={!!ocupado || fila.accion !== 'crear'}
                          onChange={(e) => cambiar(i, { precio: e.target.value })}
                        />
                        {fila.precio === '' && (
                          <small className="tg-menu-warning">Falta el precio.</small>
                        )}
                      </td>
                      <td>
                        <select
                          aria-label={`Acción fila ${i + 1}`}
                          value={
                            fila.accion === 'crear' ? 'crear' : String(fila.id_existente)
                          }
                          disabled={!!ocupado}
                          onChange={(e) =>
                            cambiar(
                              i,
                              {
                                accion:
                                  e.target.value === 'crear' ? 'crear' : 'usar_existente',
                                id_existente:
                                  e.target.value === 'crear'
                                    ? null
                                    : Number(e.target.value),
                              },
                              false,
                            )
                          }
                        >
                          <option value="crear" disabled={!!fila.existente}>
                            Crear producto
                          </option>
                          {coincidencias.map((c) => (
                            <option key={c.id} value={c.id} disabled={!c.disponible}>
                              Usar: {c.nombre} · {dinero(c.precio, moneda)}
                              {!c.disponible ? ' · desactivado' : ''}
                            </option>
                          ))}
                        </select>
                        <small>
                          {fila.existente
                            ? 'Ya existe en tu catálogo.'
                            : coincidencias.length
                              ? 'Posibles coincidencias. Compara la presentación.'
                              : 'Sin coincidencias cercanas.'}
                        </small>
                        {fila.accion === 'usar_existente' && (
                          <small>
                            Se conserva su nombre, categoría y precio actuales.
                          </small>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p>
            {nuevos.length} productos nuevos · {seleccionados.length - nuevos.length}{' '}
            existentes seleccionados.
          </p>
          {!!categoriasNuevas.length && (
            <p>Categorías por crear: {categoriasNuevas.join(', ')}.</p>
          )}
          <p>
            Se asignarán a la sucursal seleccionada. Los productos desmarcados no se
            importan.
          </p>
          {!sucursal && (
            <Mensaje error="Selecciona una sucursal en el panel antes de guardar el catálogo." />
          )}
          {pendiente && (
            <p role="status">
              Cambiaste datos. Revisa las coincidencias antes de confirmar.
            </p>
          )}
          <div className="tg-form-actions">
            <button
              type="button"
              className="tg-button tg-secondary"
              disabled={!!ocupado}
              onClick={() => {
                setFilas([]);
                setError('');
                setConfirmado(false);
              }}
            >
              Cambiar origen
            </button>
            <button
              type="button"
              className="tg-button tg-secondary"
              disabled={!!ocupado || !pendiente}
              onClick={revisar}
            >
              Revisar cambios
            </button>
          </div>
          <label className="tg-check">
            <input
              type="checkbox"
              checked={confirmado}
              disabled={!!ocupado || pendiente}
              onChange={(e) => setConfirmado(e.target.checked)}
            />{' '}
            Revisé los productos seleccionados y sus precios.
          </label>
          <button
            type="button"
            className="tg-button tg-primary"
            disabled={
              !!ocupado ||
              pendiente ||
              !confirmado ||
              !seleccionados.length ||
              incompleto ||
              !sucursal
            }
            onClick={async () => {
              ocupar('guardando');
              setError('');
              try {
                const resultado = await api(`${ruta}/confirmar`, {
                  method: 'POST',
                  body: {
                    productos: seleccionados.map((fila) => ({
                      nombre: fila.nombre.trim(),
                      precio: fila.precio === '' ? null : fila.precio,
                      categoria: fila.categoria?.trim() || null,
                      descripcion: fila.descripcion,
                      accion: fila.accion,
                      id_existente: fila.id_existente,
                    })),
                    asignar_sucursal: true,
                  },
                });
                guardar(resultado);
              } catch (fallo) {
                setError(fallo.message);
                setConfirmado(false);
                if (fallo.estado === 409) setPendiente(true);
              } finally {
                ocupar('');
              }
            }}
          >
            Confirmar importación
          </button>
        </>
      )}
      <button
        type="button"
        className="tg-button tg-secondary"
        disabled={!!ocupado}
        onClick={cancelar}
      >
        Cancelar
      </button>
    </div>
  );
}
