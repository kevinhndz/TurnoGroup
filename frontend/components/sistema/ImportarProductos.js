'use client';

import { useState } from 'react';
import { api } from '../../lib/api';
import { Mensaje } from './Controles';

export default function ImportarProductos({
  categorias,
  guardar,
  cancelar,
  local = false,
}) {
  const [filas, setFilas] = useState([]);
  const [error, setError] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const [formato, setFormato] = useState('csv');
  const [leyendo, setLeyendo] = useState(false);
  return (
    <div className="tg-form">
      <p>
        Una fila por producto, hasta 1000 productos. Columnas: nombre, precio, categoria y
        descripcion. Las dos últimas son opcionales. Usa categorías que ya existan o deja
        esa columna vacía. Excel se lee desde la primera hoja, sin fórmulas. Los precios
        se toman en la moneda de tu negocio.
      </p>
      <label className="tg-field">
        <span>Formato del archivo</span>
        <select
          value={formato}
          disabled={ocupado || leyendo}
          onChange={(event) => {
            setFormato(event.target.value);
            setFilas([]);
            setError('');
          }}
        >
          <option value="csv">CSV (.csv)</option>
          <option value="excel">Excel (.xlsx)</option>
        </select>
      </label>
      {formato === 'csv' && (
        <a
          className="tg-link-button"
          download="productos.csv"
          href={
            'data:text/csv;charset=utf-8,' +
            encodeURIComponent(
              'nombre,precio,categoria,descripcion\nCafe americano,45.00,,Cafe negro\n',
            )
          }
        >
          Descargar ejemplo CSV
        </a>
      )}
      <label className="tg-field">
        <span>Archivo {formato === 'excel' ? 'Excel' : 'CSV'} · hasta 1 MB</span>
        <input
          key={formato}
          type="file"
          accept={
            formato === 'excel'
              ? '.xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
              : '.csv,text/csv'
          }
          disabled={ocupado || leyendo}
          onChange={async (event) => {
            setError('');
            setFilas([]);
            const archivo = event.target.files[0];
            if (!archivo) return;
            setLeyendo(true);
            try {
              if (archivo.size > 1000000) throw new Error('El archivo supera 1 MB.');
              const extension = formato === 'excel' ? '.xlsx' : '.csv';
              if (!archivo.name.toLowerCase().endsWith(extension))
                throw new Error(`Selecciona un archivo ${extension}.`);
              const contenido = await new Promise((resolve, reject) => {
                const lector = new FileReader();
                lector.onload = () => resolve(lector.result.split(',')[1]);
                lector.onerror = () => reject(new Error('No se pudo leer el archivo.'));
                lector.readAsDataURL(archivo);
              });
              const respuesta = await api('/productos/revisar-archivo', {
                method: 'POST',
                body: { formato, nombre_archivo: archivo.name, contenido },
              });
              const leidas = respuesta.productos;
              const productos = leidas.map((fila) => {
                const categoria = categorias.find(
                  (item) =>
                    item.activo &&
                    item.nombre.toLocaleLowerCase('es') ===
                      fila.categoria.toLocaleLowerCase('es'),
                );
                if (fila.categoria && !categoria)
                  throw new Error(
                    `No existe la categoría ${fila.categoria}. Créala antes de importar.`,
                  );
                return {
                  nombre: fila.nombre,
                  precio: fila.precio,
                  descripcion: fila.descripcion,
                  id_categoria: categoria?.id || null,
                };
              });
              setFilas(productos);
            } catch (fallo) {
              setError(fallo.message);
            } finally {
              setLeyendo(false);
            }
          }}
        />
      </label>
      {leyendo && <p role="status">Leyendo archivo y preparando vista previa…</p>}
      <Mensaje error={error} />
      {!!filas.length && (
        <>
          <p>
            {filas.length} productos listos.{' '}
            {local
              ? 'Se añadirán a la configuración y se guardarán al finalizar el registro.'
              : 'Se crearán en el catálogo y se asignarán a la sucursal seleccionada.'}
          </p>
          <div className="tg-table-scroll">
            <table className="tg-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Precio</th>
                </tr>
              </thead>
              <tbody>
                {filas.slice(0, 20).map((fila, i) => (
                  <tr key={i}>
                    <td>{fila.nombre}</td>
                    <td>{fila.precio}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filas.length > 20 && <small>Se muestran los primeros 20 productos.</small>}
        </>
      )}
      <div className="tg-form-actions">
        <button
          className="tg-button tg-secondary"
          disabled={ocupado || leyendo}
          onClick={cancelar}
        >
          Cancelar
        </button>
        <button
          className="tg-button tg-primary"
          disabled={!filas.length || ocupado || leyendo}
          onClick={async () => {
            setOcupado(true);
            setError('');
            try {
              if (local) {
                await guardar(filas);
                return;
              }
              await api('/productos/importar', {
                method: 'POST',
                body: { productos: filas, asignar_sucursal: true },
              });
              guardar();
            } catch (fallo) {
              setError(fallo.message);
            } finally {
              setOcupado(false);
            }
          }}
        >
          {ocupado ? 'Importando…' : 'Confirmar importación'}
        </button>
      </div>
    </div>
  );
}

export function ImagenProducto({ producto, guardar }) {
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const [imagen, setImagen] = useState(producto.ruta_imagen);
  const [ocupado, setOcupado] = useState(false);
  return (
    <div className="tg-photo-field">
      <label className="tg-field">
        <span>
          {ocupado ? 'Guardando imagen…' : 'Cambiar foto JPG / PNG · hasta 5 MB'}
        </span>
        <input
          type="file"
          accept="image/jpeg,image/png"
          disabled={ocupado}
          onChange={async (event) => {
            const archivo = event.target.files[0];
            if (!archivo) return;
            setError('');
            setAviso('');
            setOcupado(true);
            try {
              if (archivo.size > 5 * 1024 * 1024)
                throw new Error('La imagen supera 5 MB.');
              const contenido = await new Promise((resolve, reject) => {
                const lector = new FileReader();
                lector.onload = () => resolve(lector.result.split(',')[1]);
                lector.onerror = () => reject(new Error('No se pudo leer la imagen.'));
                lector.readAsDataURL(archivo);
              });
              const actualizado = await api(`/productos/${producto.id}/imagen`, {
                method: 'POST',
                body: { contenido },
              });
              setImagen(actualizado.ruta_imagen);
              setAviso(`Foto actualizada correctamente: ${archivo.name}`);
              guardar();
            } catch (fallo) {
              setError(fallo.message);
            } finally {
              setOcupado(false);
              event.target.value = '';
            }
          }}
        />
      </label>
      {imagen && (
        <img
          className="tg-photo-preview"
          src={`/api/backend/productos/${producto.id}/imagen?v=${encodeURIComponent(imagen)}`}
          alt={`Foto actual de ${producto.nombre}`}
          width={72}
          height={72}
        />
      )}
      <Mensaje error={error} aviso={aviso} />
    </div>
  );
}
