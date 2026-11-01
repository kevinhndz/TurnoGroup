'use client';

import { useState } from 'react';
import { api, dinero, listarTodo } from '../../lib/api';
import { modulos } from '../../lib/modulos';
import { usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { Mensaje, Modal, Vacio } from './Controles';
import Formulario from './Formulario';
import Icon from '../Icon';
import PrepararMesas from './PrepararMesas';
import ImportarProductos, { ImagenProducto } from './ImportarProductos';

export default function Crud({ modulo, compacto = false, alGuardar, configuracion }) {
  const config = configuracion || modulos[modulo];
  const { sesion } = usarSesion();
  const [importando, setImportando] = useState(false);
  const [pagina, setPagina] = useState(1);
  const [busqueda, setBusqueda] = useState('');
  const [edicion, setEdicion] = useState(null);
  const [confirmacion, setConfirmacion] = useState(null);
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const editable = config.plataforma
    ? sesion.usuario.rol_plataforma === 'Superadministrador'
    : sesion.rol_empresa === 'Gerente';
  const datos = useDatos(async () => {
    if (config.porSucursal && !sesion.id_sucursal)
      return { lista: { data: [], total: 0, total_paginas: 0 }, categorias: [] };
    const [lista, categorias, empresa] = await Promise.all([
      api(`${config.ruta}?pagina_actual=${pagina}&limite=10`),
      modulo === 'productos' ? listarTodo('/categorias/') : Promise.resolve([]),
      ['productos', 'descuentos'].includes(modulo)
        ? api(`/empresas/${sesion.id_empresa}`)
        : Promise.resolve(null),
    ]);
    return { lista, categorias, moneda: empresa?.codigo_moneda };
  }, [pagina, config.ruta, sesion.id_sucursal]);

  if (config.porSucursal && !sesion.id_sucursal)
    return (
      <Vacio
        titulo="Selecciona una sucursal"
        detalle="Elige un local en la parte superior para administrar sus mesas."
        icono="store"
      />
    );

  const lista = datos.datos?.lista;
  const filas = (lista?.data || []).filter(
    (item) =>
      !busqueda ||
      String(item.nombre || item.correo || '')
        .toLocaleLowerCase('es')
        .includes(busqueda.toLocaleLowerCase('es')),
  );

  async function editar(fila) {
    setOcupado(true);
    setError('');
    try {
      setEdicion(await api(`${config.ruta}${fila.id}`));
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setOcupado(false);
    }
  }

  async function guardar(body) {
    if (edicion.id) await api(`${config.ruta}${edicion.id}`, { method: 'PATCH', body });
    else await api(config.ruta, { method: 'POST', body });
    setEdicion(null);
    setAviso('Los cambios quedaron guardados.');
    datos.recargar();
    window.dispatchEvent(new Event('turno-datos'));
    if (alGuardar) {
      try {
        await alGuardar();
      } catch (fallo) {
        setError(`Registro guardado. ${fallo.message}`);
      }
    }
  }

  async function cambiarEstado() {
    setOcupado(true);
    setError('');
    try {
      if (confirmacion[config.estado])
        await api(`${config.ruta}${confirmacion.id}/desactivar`, { method: 'POST' });
      else
        await api(`${config.ruta}${confirmacion.id}`, {
          method: 'PATCH',
          body: { [config.estado]: true },
        });
      setConfirmacion(null);
      datos.recargar();
      setAviso('El estado quedó actualizado.');
      window.dispatchEvent(new Event('turno-datos'));
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setOcupado(false);
    }
  }

  function valor(fila, clave) {
    if (clave === 'categoria')
      return (
        datos.datos?.categorias.find((item) => item.id === fila.id_categoria)?.nombre ||
        (fila.id_categoria ? `Categoría #${fila.id_categoria}` : 'Sin categoría')
      );
    if (clave === 'precio') return dinero(fila[clave], datos.datos?.moneda || 'HNL');
    if (clave === 'tipo_descuento')
      return fila[clave] === 'Porcentaje' ? 'Porcentaje' : 'Cantidad fija';
    if (clave === 'valor')
      return fila.tipo_descuento === 'Porcentaje'
        ? `${fila.valor}%`
        : dinero(fila.valor, datos.datos?.moneda || 'HNL');
    if (typeof fila[clave] === 'boolean') return fila[clave] ? 'Sí' : 'No';
    return fila[clave] ?? '—';
  }

  return (
    <section className={compacto ? 'tg-crud tg-compact' : 'tg-crud'}>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">
            {config.porSucursal
              ? 'EN ESTA SUCURSAL'
              : config.plataforma
                ? 'PLATAFORMA'
                : 'TU EMPRESA'}
          </span>
          <h1>{config.titulo}</h1>
          <p>{config.detalle}</p>
          {datos.datos?.moneda && (
            <small className="tg-muted">Moneda del negocio: {datos.datos.moneda}</small>
          )}
        </div>
        {editable && (
          <button
            className="tg-button tg-primary"
            onClick={() => {
              setEdicion({});
              setAviso('');
            }}
          >
            <Icon name="plus" size={17} /> Crear {config.singular}
          </button>
        )}
      </div>
      <Mensaje error={error || datos.error} aviso={aviso} />
      {modulo === 'mesas' && editable && <PrepararMesas guardar={datos.recargar} />}
      {modulo === 'productos' && editable && (
        <div className="tg-form-actions">
          <button className="tg-button tg-secondary" onClick={() => setImportando(true)}>
            Importar productos
          </button>
        </div>
      )}
      {importando && (
        <Modal titulo="Importar productos" cerrar={() => setImportando(false)}>
          <ImportarProductos
            categorias={datos.datos?.categorias || []}
            cancelar={() => setImportando(false)}
            guardar={() => {
              setImportando(false);
              datos.recargar();
              setAviso('Productos importados.');
            }}
          />
        </Modal>
      )}

      <div className="tg-card tg-table-card">
        <div className="tg-toolbar">
          <label className="tg-search">
            <span>Buscar en esta página</span>
            <input
              type="search"
              value={busqueda}
              placeholder="Escribe un nombre…"
              onChange={(event) => setBusqueda(event.target.value)}
            />
          </label>
          <span className="tg-muted">{lista?.total ?? '—'} registros</span>
          <button className="tg-link-button" onClick={datos.recargar}>
            Actualizar
          </button>
        </div>
        {datos.cargando ? (
          <p className="tg-loading-inline" role="status">
            Cargando registros…
          </p>
        ) : !filas.length ? (
          <Vacio
            titulo={
              busqueda
                ? 'No hay coincidencias en esta página'
                : `Todavía no hay ${config.titulo.toLocaleLowerCase('es')}`
            }
            detalle={
              editable
                ? `Puedes crear tu primer registro con el botón de arriba.`
                : 'Los registros aparecerán cuando tu gerente los agregue.'
            }
            icono={config.icono}
          />
        ) : (
          <div className="tg-table-scroll">
            <table className="tg-table">
              <thead>
                <tr>
                  {config.columnas.map(([clave, label]) => (
                    <th key={clave}>{label}</th>
                  ))}
                  <th>Estado</th>
                  {editable && <th>Acciones</th>}
                </tr>
              </thead>
              <tbody>
                {filas.map((fila) => (
                  <tr key={fila.id}>
                    {config.columnas.map(([clave]) => (
                      <td key={clave}>{valor(fila, clave)}</td>
                    ))}
                    <td>
                      <span
                        className={`tg-status ${(config.estadoTexto ? fila[config.estado] !== 'Inactiva' : fila[config.estado]) ? 'is-active' : ''}`}
                      >
                        {config.estadoTexto
                          ? fila[config.estado]
                          : fila[config.estado]
                            ? 'Activo'
                            : 'Desactivado'}
                      </span>
                    </td>
                    {editable && (
                      <td>
                        <div className="tg-row-actions">
                          <button disabled={ocupado} onClick={() => editar(fila)}>
                            Editar
                          </button>
                          {(!config.estadoTexto ||
                            fila[config.estado] !== 'Inactiva') && (
                            <button
                              disabled={ocupado}
                              onClick={() => setConfirmacion(fila)}
                            >
                              {fila[config.estado] ? 'Desactivar' : 'Activar'}
                            </button>
                          )}
                          {modulo === 'productos' && (
                            <ImagenProducto producto={fila} guardar={datos.recargar} />
                          )}
                          {config.accion?.(fila)}
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="tg-pagination">
          <span>
            Página {pagina} de {Math.max(1, lista?.total_paginas || 1)}
          </span>
          <div>
            <button
              className="tg-button tg-secondary"
              disabled={pagina === 1 || datos.cargando}
              onClick={() => setPagina(pagina - 1)}
            >
              Anterior
            </button>
            <button
              className="tg-button tg-secondary"
              disabled={!lista || pagina >= lista.total_paginas || datos.cargando}
              onClick={() => setPagina(pagina + 1)}
            >
              Siguiente
            </button>
          </div>
        </div>
      </div>
      {edicion && (
        <Modal
          titulo={`${edicion.id ? 'Editar' : 'Crear'} ${config.singular}`}
          cerrar={() => setEdicion(null)}
        >
          <Formulario
            campos={
              !edicion.id && config.camposCrear ? config.camposCrear : config.campos
            }
            inicial={edicion}
            opciones={{
              categorias:
                datos.datos?.categorias.filter(
                  (item) => item.activo || item.id === edicion.id_categoria,
                ) || [],
            }}
            guardar={guardar}
            cancelar={() => setEdicion(null)}
          />
        </Modal>
      )}
      {confirmacion && (
        <Modal
          titulo={`${confirmacion[config.estado] ? 'Desactivar' : 'Activar'} ${config.singular}`}
          cerrar={() => setConfirmacion(null)}
        >
          <p>
            ¿Quieres {confirmacion[config.estado] ? 'desactivar' : 'activar'} «
            {confirmacion.nombre || confirmacion.correo}»?
          </p>
          <p className="tg-muted">El registro se conserva en la empresa.</p>
          <div className="tg-form-actions">
            <button
              className="tg-button tg-secondary"
              disabled={ocupado}
              onClick={() => setConfirmacion(null)}
            >
              Cancelar
            </button>
            <button
              className="tg-button tg-primary"
              disabled={ocupado}
              onClick={cambiarEstado}
            >
              {ocupado ? 'Guardando…' : 'Confirmar'}
            </button>
          </div>
        </Modal>
      )}
    </section>
  );
}
