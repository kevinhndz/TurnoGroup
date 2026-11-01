'use client';

import { useState } from 'react';
import { usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { Campo, Mensaje, Modal, Vacio } from './Controles';
import Formulario from './Formulario';
import { api, dinero, listarTodo } from '../../lib/api';

export default function Disponibilidad() {
  const { sesion } = usarSesion();
  const [edicion, setEdicion] = useState(null);
  const [retiro, setRetiro] = useState(null);
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const [busqueda, setBusqueda] = useState('');
  const [pagina, setPagina] = useState(1);
  const gerente = sesion.rol_empresa === 'Gerente';
  const editable = gerente || sesion.rol_empresa === 'Administrador';
  const datos = useDatos(async () => {
    if (!sesion.id_sucursal) return null;
    const [productos, asignaciones, empresa] = await Promise.all([
      listarTodo('/productos/'),
      listarTodo('/disponibilidad-productos/'),
      api(`/empresas/${sesion.id_empresa}`),
    ]);
    return { productos, asignaciones, moneda: empresa.codigo_moneda };
  }, [sesion.id_sucursal]);
  if (!sesion.id_sucursal)
    return (
      <Vacio
        titulo="Selecciona una sucursal"
        detalle="La disponibilidad se guarda para el local seleccionado arriba."
        icono="store"
      />
    );
  const resultados =
    datos.datos?.productos.filter((item) =>
      item.nombre.toLocaleLowerCase('es').includes(busqueda.toLocaleLowerCase('es')),
    ) || [];
  const filas = resultados.slice((pagina - 1) * 12, pagina * 12);
  const paginas = Math.max(1, Math.ceil(resultados.length / 12));

  async function guardar(body) {
    const asignado = datos.datos.asignaciones.some(
      (item) => item.id_producto === edicion.id,
    );
    await api(
      asignado
        ? `/disponibilidad-productos/${edicion.id}/${sesion.id_sucursal}`
        : '/disponibilidad-productos/',
      {
        method: asignado ? 'PATCH' : 'POST',
        body: asignado ? body : { id_producto: edicion.id, ...body },
      },
    );
    setEdicion(null);
    datos.recargar();
    setAviso('Disponibilidad guardada para este local.');
  }

  return (
    <section>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">CATÁLOGO POR LOCAL</span>
          <h1>Disponibilidad de productos</h1>
          <p>
            Asigna productos del catálogo maestro y define si el local usa un precio
            diferente.
          </p>
        </div>
      </div>
      <Mensaje error={error || datos.error} aviso={aviso} />
      <section className="tg-card tg-table-card">
        <div className="tg-toolbar">
          <Campo label="Buscar producto">
            <input
              type="search"
              value={busqueda}
              onChange={(event) => {
                setBusqueda(event.target.value);
                setPagina(1);
              }}
              placeholder="Nombre del producto…"
            />
          </Campo>
          <span>{resultados.length} productos</span>
          <button className="tg-link-button" onClick={datos.recargar}>
            Actualizar
          </button>
        </div>
        {datos.cargando ? (
          <p className="tg-loading-inline" role="status">
            Cargando catálogo…
          </p>
        ) : !filas.length ? (
          <Vacio
            titulo="No hay productos para mostrar"
            detalle="El gerente puede preparar el catálogo en Productos."
          />
        ) : (
          <div className="tg-table-scroll">
            <table className="tg-table">
              <thead>
                <tr>
                  <th>Producto</th>
                  <th>Precio</th>
                  <th>Estado en el local</th>
                  {editable && <th>Acciones</th>}
                </tr>
              </thead>
              <tbody>
                {filas.map((producto) => {
                  const asignacion = datos.datos.asignaciones.find(
                    (item) => item.id_producto === producto.id,
                  );
                  return (
                    <tr key={producto.id}>
                      <td>
                        <strong>{producto.nombre}</strong>
                        {!producto.disponible && (
                          <small className="tg-muted">
                            Desactivado en catálogo maestro
                          </small>
                        )}
                      </td>
                      <td>{dinero(producto.precio, datos.datos.moneda)}</td>
                      <td>
                        <span
                          className={`tg-status ${asignacion?.disponible && producto.disponible ? 'is-active' : ''}`}
                        >
                          {!asignacion
                            ? 'Sin asignar'
                            : asignacion.disponible && producto.disponible
                              ? 'Disponible'
                              : 'No disponible'}
                        </span>
                      </td>
                      {editable && (
                        <td>
                          <div className="tg-row-actions">
                            {(gerente || asignacion) && (
                              <button
                                onClick={() => setEdicion({ ...producto, asignacion })}
                              >
                                {asignacion ? 'Editar' : 'Asignar'}
                              </button>
                            )}
                            {gerente && asignacion && (
                              <button onClick={() => setRetiro(producto)}>Retirar</button>
                            )}
                          </div>
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        <div className="tg-pagination">
          <span>
            Página {pagina} de {paginas}
          </span>
          <div>
            <button
              className="tg-button tg-secondary"
              disabled={pagina <= 1}
              onClick={() => setPagina(pagina - 1)}
            >
              Anterior
            </button>
            <button
              className="tg-button tg-secondary"
              disabled={pagina >= paginas}
              onClick={() => setPagina(pagina + 1)}
            >
              Siguiente
            </button>
          </div>
        </div>
      </section>
      {edicion && (
        <Modal titulo={edicion.nombre} cerrar={() => setEdicion(null)}>
          <p className="tg-muted">
            El precio del producto es el mismo en todas las sucursales. El gerente puede
            cambiarlo desde Productos.
          </p>
          <Formulario
            campos={[
              {
                clave: 'disponible',
                label: 'Disponible en esta sucursal',
                type: 'checkbox',
                valor: true,
              },
            ]}
            inicial={edicion.asignacion || {}}
            guardar={guardar}
            cancelar={() => setEdicion(null)}
          />
        </Modal>
      )}
      {retiro && (
        <Modal titulo="Retirar del local" cerrar={() => setRetiro(null)}>
          <p>
            Se quitará la asignación de «{retiro.nombre}» de este local. El producto
            maestro se conserva.
          </p>
          <Mensaje error={error} />
          <div className="tg-form-actions">
            <button
              className="tg-button tg-secondary"
              disabled={ocupado}
              onClick={() => setRetiro(null)}
            >
              Cancelar
            </button>
            <button
              className="tg-button tg-primary"
              disabled={ocupado}
              onClick={async () => {
                setOcupado(true);
                setError('');
                try {
                  await api(
                    `/disponibilidad-productos/${retiro.id}/${sesion.id_sucursal}`,
                    { method: 'DELETE' },
                  );
                  setRetiro(null);
                  datos.recargar();
                  setAviso('Producto retirado de esta sucursal.');
                } catch (fallo) {
                  setError(fallo.message);
                } finally {
                  setOcupado(false);
                }
              }}
            >
              {ocupado ? 'Retirando…' : 'Retirar producto'}
            </button>
          </div>
        </Modal>
      )}
    </section>
  );
}
