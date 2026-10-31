'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { usarSesion } from './Sesion';
import { Campo, Mensaje, Modal, Vacio } from './Controles';
import Formulario from './Formulario';
import { camposEmpresa, modulos } from '../../lib/modulos';
import { dinero } from '../../lib/api';
import ImportarProductos from './ImportarProductos';

const pasos = [
  'Negocio',
  'Sucursales',
  'Servicios',
  'Pagos e impuestos',
  'Descuentos',
  'Productos',
  'Revisión',
];
const servicios = [
  ['comer_aqui', 'Comer aquí'],
  ['para_llevar', 'Para llevar'],
  ['domicilio', 'Domicilio'],
];
const pagos = [
  ['efectivo', 'Efectivo'],
  ['transferencia', 'Transferencia'],
  ['tarjeta', 'Tarjeta'],
];

export default function AltaInicial() {
  const { registro, setRegistro, finalizarRegistro } = usarSesion();
  const router = useRouter();
  const [paso, setPaso] = useState(1);
  const [importando, setImportando] = useState(false);
  const [local, setLocal] = useState(null);
  const [catalogo, setCatalogo] = useState('categorias');
  const [error, setError] = useState('');
  const [editarCuenta, setEditarCuenta] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const sucursal =
    registro.sucursales.find((item) => item.id_local === local) || registro.sucursales[0];
  const moneda = registro.negocio?.codigo_moneda || 'HNL';

  function actualizar(campo, valor) {
    setRegistro((anterior) => ({ ...anterior, [campo]: valor }));
  }
  function cambiarLocal(cambio) {
    actualizar(
      'sucursales',
      registro.sucursales.map((item) =>
        item.id_local === sucursal.id_local ? { ...item, ...cambio } : item,
      ),
    );
  }
  function cambiarServicio(clave, cambio) {
    const opciones = { ...sucursal.servicios };
    const servicio = {
      habilitado: false,
      mesas_habilitadas: false,
      reservas_habilitadas: false,
      ...opciones[clave],
      ...cambio,
    };
    if (!servicio.habilitado) {
      servicio.mesas_habilitadas = false;
      servicio.reservas_habilitadas = false;
    }
    if (!servicio.mesas_habilitadas) servicio.reservas_habilitadas = false;
    opciones[clave] = servicio;
    cambiarLocal({ servicios: opciones });
  }
  function validar(punto) {
    if (!registro.negocio) throw new Error('Guarda los datos del negocio en el paso 1.');
    if (punto >= 2) {
      if (!registro.sucursales.length) throw new Error('Agrega al menos una sucursal.');
      if (registro.sucursales.filter((item) => item.es_principal).length !== 1)
        throw new Error('Selecciona una única sucursal principal.');
    }
    if (punto >= 3) {
      const sinServicios = registro.sucursales.find(
        (item) => !Object.values(item.servicios).some((opcion) => opcion.habilitado),
      );
      if (sinServicios)
        throw new Error(`Activa al menos un servicio en ${sinServicios.nombre}.`);
    }
    if (punto >= 4) {
      const sinPagos = registro.sucursales.find((item) => !item.pagos.length);
      if (sinPagos)
        throw new Error(`Activa al menos un método de pago en ${sinPagos.nombre}.`);
      if (
        registro.impuesto &&
        (registro.impuesto.porcentaje === '' ||
          !Number.isFinite(Number(registro.impuesto.porcentaje)) ||
          Number(registro.impuesto.porcentaje) < 0 ||
          Number(registro.impuesto.porcentaje) > 100)
      )
        throw new Error('Escribe un porcentaje de impuesto entre 0 y 100.');
    }
  }
  function ir(nuevo) {
    setError('');
    try {
      if (nuevo > paso) validar(nuevo - 1);
      setPaso(nuevo);
      window.scrollTo({ top: 0, behavior: 'instant' });
    } catch (fallo) {
      setError(fallo.message);
    }
  }
  async function terminar() {
    setError('');
    try {
      validar(7);
      setEnviando(true);
      const { categorias, productos, descuentos, ...resto } = registro;
      await finalizarRegistro({
        ...resto,
        impuesto: resto.impuesto
          ? { ...resto.impuesto, nombre: resto.impuesto.nombre?.trim() || null }
          : null,
        categorias: categorias.map(({ id_local, nombre, orden_presentacion }) => ({
          id_local,
          nombre,
          orden_presentacion,
        })),
        productos: productos.map(({ id_local, ...producto }) => ({
          ...producto,
          sucursales: producto.sucursales.filter((id) =>
            registro.sucursales.some((item) => item.id_local === id),
          ),
          id_categoria: registro.categorias.some(
            (item) => item.id_local === producto.id_categoria,
          )
            ? producto.id_categoria
            : null,
        })),
        descuentos: descuentos.map(({ id_local, ...descuento }) => descuento),
      });
      router.replace('/panel');
    } catch (fallo) {
      const campos = fallo.errores
        ?.map((item) => item.campo.replace(/^body\./, ''))
        .join(', ');
      setError(campos ? `${fallo.message}: ${campos}` : fallo.message);
      setEnviando(false);
    }
  }

  return (
    <div className="tg-wizard">
      <header className="tg-wizard-header">
        <Link href="/" className="tg-brand">
          Turno Group
          <span />
        </Link>
        <span>{registro.cuenta.nombre}</span>
      </header>
      <main id="contenido" className="tg-wizard-main">
        <div className="tg-step-caption">
          <span>
            PASO {paso} DE 7 · {pasos[paso - 1].toUpperCase()}
          </span>
          <span>Configuración inicial</span>
        </div>
        <ol className="tg-stepper">
          {pasos.map((nombre, indice) => (
            <li className={paso >= indice + 1 ? 'is-done' : ''} key={nombre}>
              <button
                disabled={enviando}
                onClick={() => ir(indice + 1)}
                aria-current={paso === indice + 1 ? 'step' : undefined}
              >
                <span>{indice + 1}</span>
                {nombre}
              </button>
            </li>
          ))}
        </ol>
        <p className="tg-table-note">
          Tu cuenta y tu negocio se crearán al confirmar el paso 7. Mientras tanto, los
          cambios están solo en esta pantalla; si recargas, tendrás que empezar de nuevo.
        </p>
        <Mensaje error={error} />
        <fieldset className="tg-registration-fields" disabled={enviando}>
          {paso === 1 && (
            <section className="tg-card">
              <div className="tg-section-heading">
                <div>
                  <h1>Cuéntanos sobre tu negocio</h1>
                  <p>Usaremos esta información para preparar tu espacio.</p>
                </div>
              </div>
              <Formulario
                campos={camposEmpresa}
                inicial={registro.negocio || {}}
                guardar={async (datos) => {
                  actualizar('negocio', datos);
                  setPaso(2);
                }}
                texto="Guardar y continuar"
              />
            </section>
          )}
          {paso === 2 && (
            <ListaRegistro
              titulo="Configura tus sucursales"
              singular="sucursal"
              campos={modulos.sucursales.campos}
              filas={registro.sucursales}
              guardar={(filas) =>
                actualizar(
                  'sucursales',
                  filas.map((item) => ({
                    ...item,
                    servicios: item.servicios || {},
                    pagos: item.pagos || [],
                  })),
                )
              }
              inicial={{ es_principal: registro.sucursales.length === 0 }}
            />
          )}
          {(paso === 3 || paso === 4) && sucursal && (
            <div className="tg-wizard-context">
              <Campo label="Configurar sucursal">
                <select
                  value={sucursal.id_local}
                  onChange={(event) => setLocal(Number(event.target.value))}
                >
                  {registro.sucursales.map((item) => (
                    <option key={item.id_local} value={item.id_local}>
                      {item.nombre}
                    </option>
                  ))}
                </select>
              </Campo>
            </div>
          )}
          {paso === 3 && sucursal && (
            <>
              <div className="tg-section-heading">
                <div>
                  <h1>Elige cómo atiendes a tus clientes</h1>
                  <p>El personal solo verá las modalidades habilitadas en cada local.</p>
                </div>
              </div>
              <div className="tg-option-list">
                {servicios.map(([clave, nombre]) => (
                  <section key={clave} className="tg-card tg-option">
                    <div className="tg-option-main">
                      <div>
                        <h3>{nombre}</h3>
                      </div>
                      <label className="tg-switch">
                        <input
                          type="checkbox"
                          aria-label={`Activar ${nombre}`}
                          checked={!!sucursal.servicios[clave]?.habilitado}
                          onChange={(event) =>
                            cambiarServicio(clave, { habilitado: event.target.checked })
                          }
                        />
                        <span />
                      </label>
                    </div>
                    {clave === 'comer_aqui' && (
                      <div className="tg-option-children">
                        <label className="tg-check">
                          <input
                            type="checkbox"
                            disabled={!sucursal.servicios[clave]?.habilitado}
                            checked={!!sucursal.servicios[clave]?.mesas_habilitadas}
                            onChange={(event) =>
                              cambiarServicio(clave, {
                                mesas_habilitadas: event.target.checked,
                              })
                            }
                          />
                          Gestionar mesas en este local
                        </label>
                        <label className="tg-check">
                          <input
                            type="checkbox"
                            disabled={!sucursal.servicios[clave]?.mesas_habilitadas}
                            checked={!!sucursal.servicios[clave]?.reservas_habilitadas}
                            onChange={(event) =>
                              cambiarServicio(clave, {
                                reservas_habilitadas: event.target.checked,
                              })
                            }
                          />
                          Habilitar reservas para mesas
                        </label>
                        <p className="tg-muted">
                          Si desactivas mesas, no aparecerán en el panel de esta sucursal.
                        </p>
                      </div>
                    )}
                  </section>
                ))}
              </div>
            </>
          )}
          {paso === 4 && sucursal && (
            <div className="tg-step-stack">
              <section className="tg-card">
                <h1>Pagos e impuestos</h1>
                <h2>Métodos de pago del local</h2>
                <p className="tg-muted">El cobro se realiza fuera de Turno Group.</p>
                {pagos.map(([clave, nombre]) => (
                  <label key={clave} className="tg-check">
                    <input
                      type="checkbox"
                      checked={sucursal.pagos.includes(clave)}
                      onChange={(event) =>
                        cambiarLocal({
                          pagos: event.target.checked
                            ? [...sucursal.pagos, clave]
                            : sucursal.pagos.filter((item) => item !== clave),
                        })
                      }
                    />
                    {nombre}
                  </label>
                ))}
              </section>
              <ImpuestoRegistro
                impuesto={registro.impuesto}
                guardar={(valor) => actualizar('impuesto', valor)}
              />
            </div>
          )}
          {paso === 5 && (
            <ListaRegistro
              titulo="Descuentos"
              singular="descuento"
              campos={modulos.descuentos.campos}
              filas={registro.descuentos}
              guardar={(valor) => actualizar('descuentos', valor)}
            />
          )}
          {paso === 6 && (
            <>
              <div className="tg-section-heading">
                <div>
                  <h1>Catálogo inicial</h1>
                  <p>
                    Puedes continuar sin productos y agregarlos después desde el panel.
                  </p>
                </div>
              </div>
              <button
                className="tg-button tg-secondary"
                onClick={() => setImportando(true)}
              >
                Importar archivo CSV
              </button>
              {importando && (
                <Modal titulo="Revisar importación" cerrar={() => setImportando(false)}>
                  <ImportarProductos
                    local
                    categorias={registro.categorias.map((item) => ({
                      ...item,
                      id: item.id_local,
                      activo: true,
                    }))}
                    cancelar={() => setImportando(false)}
                    guardar={async (filas) => {
                      const nombres = [...registro.productos, ...filas].map((item) =>
                        item.nombre.toLocaleLowerCase('es'),
                      );
                      if (new Set(nombres).size !== nombres.length)
                        throw new Error('Hay nombres de producto repetidos.');
                      actualizar('productos', [
                        ...registro.productos,
                        ...filas.map((item, indice) => ({
                          ...item,
                          id_local: Date.now() + indice,
                          sucursales: registro.sucursales.map((local) => local.id_local),
                        })),
                      ]);
                      setImportando(false);
                    }}
                  />
                </Modal>
              )}
              <nav className="tg-tabs" aria-label="Catálogo inicial">
                <button
                  aria-current={catalogo === 'categorias' ? 'page' : undefined}
                  onClick={() => setCatalogo('categorias')}
                >
                  Categorías
                </button>
                <button
                  aria-current={catalogo === 'productos' ? 'page' : undefined}
                  onClick={() => setCatalogo('productos')}
                >
                  Productos
                </button>
              </nav>
              {catalogo === 'categorias' ? (
                <ListaRegistro
                  titulo="Tus categorías"
                  singular="categoría"
                  campos={modulos.categorias.campos}
                  filas={registro.categorias}
                  guardar={(valor) => actualizar('categorias', valor)}
                />
              ) : (
                <ListaRegistro
                  titulo="Tus productos"
                  singular="producto"
                  campos={modulos.productos.campos}
                  filas={registro.productos}
                  opciones={{
                    categorias: registro.categorias.map((item) => ({
                      ...item,
                      id: item.id_local,
                    })),
                  }}
                  sucursales={registro.sucursales}
                  guardar={(valor) => actualizar('productos', valor)}
                />
              )}
            </>
          )}
          {paso === 7 && (
            <>
              <div className="tg-section-heading">
                <div>
                  <h1>Revisa y activa tu negocio</h1>
                  <p>Confirma estos datos para crear tu cuenta y abrir el panel.</p>
                </div>
              </div>
              <div className="tg-summary-grid">
                <ResumenAlta titulo="Cuenta" editar={() => setEditarCuenta(true)}>
                  <p>{registro.cuenta.nombre}</p>
                  <p>{registro.cuenta.correo}</p>
                </ResumenAlta>
                <ResumenAlta titulo="Negocio" editar={() => ir(1)}>
                  <p>{registro.negocio.nombre}</p>
                  <p>
                    {registro.negocio.tipo_negocio} · {moneda}
                  </p>
                  <small>{registro.negocio.zona_horaria}</small>
                </ResumenAlta>
                <ResumenAlta titulo="Sucursales y servicios" editar={() => ir(2)}>
                  {registro.sucursales.map((item) => (
                    <div key={item.id_local}>
                      <h3>
                        {item.nombre}
                        {item.es_principal ? ' · Principal' : ''}
                      </h3>
                      <p>{item.direccion}</p>
                      <p>
                        {servicios
                          .filter(([clave]) => item.servicios[clave]?.habilitado)
                          .map(([, nombre]) => nombre)
                          .join(', ')}
                      </p>
                      <small>
                        Mesas:{' '}
                        {item.servicios.comer_aqui?.mesas_habilitadas
                          ? 'Habilitadas'
                          : 'Deshabilitadas'}
                      </small>
                    </div>
                  ))}
                </ResumenAlta>
                <ResumenAlta titulo="Pagos e impuestos" editar={() => ir(4)}>
                  {registro.sucursales.map((item) => (
                    <p key={item.id_local}>
                      {item.nombre}:{' '}
                      {pagos
                        .filter(([clave]) => item.pagos.includes(clave))
                        .map(([, nombre]) => nombre)
                        .join(', ')}
                    </p>
                  ))}
                  <p>
                    {registro.impuesto
                      ? `${registro.impuesto.nombre || 'Impuesto'}: ${registro.impuesto.porcentaje}%`
                      : 'Sin impuestos'}
                  </p>
                </ResumenAlta>
                <section className="tg-card">
                  <h3>Plan de la empresa</h3>
                  <p>{registro.sucursales.length} sucursales × 100 USD al mes.</p>
                  <label className="tg-check">
                    <input
                      type="checkbox"
                      checked={!!registro.finanzas_habilitadas}
                      onChange={(event) =>
                        actualizar('finanzas_habilitadas', event.target.checked)
                      }
                    />
                    Finanzas: 30 USD adicionales al mes para toda la empresa
                  </label>
                  <p>
                    Total mensual después del primer mes gratis:{' '}
                    {registro.sucursales.length * 100 +
                      (registro.finanzas_habilitadas ? 30 : 0)}{' '}
                    USD.
                  </p>
                  <small>
                    La integración de cobro con Paddle se completará antes del despliegue.
                  </small>
                </section>
                <ResumenAlta titulo="Descuentos" editar={() => ir(5)}>
                  <p>{registro.descuentos.length} descuentos</p>
                </ResumenAlta>
                <ResumenAlta titulo="Catálogo inicial" editar={() => ir(6)}>
                  <p>
                    {registro.categorias.length} categorías · {registro.productos.length}{' '}
                    productos
                  </p>
                  {registro.productos.map((item) => (
                    <p key={item.id_local}>
                      {item.nombre} · {dinero(item.precio, moneda)}
                    </p>
                  ))}
                </ResumenAlta>
              </div>
            </>
          )}
        </fieldset>
        {editarCuenta && (
          <Modal titulo="Datos de tu cuenta" cerrar={() => setEditarCuenta(false)}>
            <Formulario
              campos={[
                {
                  clave: 'nombre',
                  label: 'Nombre',
                  required: true,
                  minLength: 1,
                  maxLength: 100,
                },
                {
                  clave: 'correo',
                  label: 'Correo electrónico',
                  type: 'email',
                  required: true,
                },
                {
                  clave: 'clave',
                  label: 'Contraseña',
                  type: 'password',
                  required: true,
                  minLength: 12,
                  maxLength: 128,
                },
              ]}
              inicial={registro.cuenta}
              guardar={async (cuenta) => {
                actualizar('cuenta', cuenta);
                setEditarCuenta(false);
              }}
            />
          </Modal>
        )}
        <footer className="tg-wizard-actions">
          <button
            className="tg-button tg-secondary"
            disabled={paso === 1 || enviando}
            onClick={() => ir(paso - 1)}
          >
            ← Volver
          </button>
          <span className="tg-muted">
            {paso < 7
              ? 'Todavía no se ha creado la cuenta'
              : 'Todo se guardará al confirmar'}
          </span>
          {paso < 7 ? (
            <button
              className="tg-button tg-primary"
              disabled={enviando || (paso === 1 && !registro.negocio)}
              onClick={() => ir(paso + 1)}
            >
              Continuar →
            </button>
          ) : (
            <button
              className="tg-button tg-primary"
              disabled={enviando}
              onClick={terminar}
            >
              {enviando ? 'Creando tu negocio…' : 'Finalizar configuración y abrir panel'}
            </button>
          )}
        </footer>
      </main>
    </div>
  );
}

function ResumenAlta({ titulo, editar, children }) {
  return (
    <section className="tg-card">
      <header className="tg-summary-header">
        <h3>{titulo}</h3>
        <button className="tg-link-button" onClick={editar}>
          Editar
        </button>
      </header>
      {children}
    </section>
  );
}

function ImpuestoRegistro({ impuesto, guardar }) {
  const cambiar = (valor) => guardar({ ...impuesto, ...valor });
  return (
    <section className="tg-card">
      <h2>Configuración fiscal de la empresa</h2>
      <label className="tg-check">
        <input
          type="checkbox"
          checked={!!impuesto}
          onChange={(event) =>
            guardar(
              event.target.checked
                ? { nombre: null, porcentaje: '', precios_incluyen_impuesto: false }
                : null,
            )
          }
        />
        El negocio aplica impuestos
      </label>
      {impuesto && (
        <div className="tg-form">
          <div className="tg-form-grid">
            <Campo label="Nombre del impuesto (opcional)">
              <input
                maxLength={80}
                value={impuesto.nombre || ''}
                onChange={(event) => cambiar({ nombre: event.target.value || null })}
              />
            </Campo>
            <Campo label="Porcentaje (%)">
              <input
                type="number"
                min={0}
                max={100}
                step="0.001"
                required
                value={impuesto.porcentaje}
                onChange={(event) => cambiar({ porcentaje: event.target.value })}
              />
            </Campo>
          </div>
          <label className="tg-check">
            <input
              type="checkbox"
              checked={impuesto.precios_incluyen_impuesto}
              onChange={(event) =>
                cambiar({ precios_incluyen_impuesto: event.target.checked })
              }
            />
            Los precios incluyen el impuesto
          </label>
        </div>
      )}
    </section>
  );
}

function ListaRegistro({
  titulo,
  singular,
  campos,
  filas,
  guardar,
  opciones,
  sucursales,
  inicial = {},
}) {
  const [edicion, setEdicion] = useState(null);
  const [locales, setLocales] = useState([]);
  const abrir = (item) => {
    setEdicion(item);
    setLocales(item.sucursales || sucursales?.map((sucursal) => sucursal.id_local) || []);
  };
  return (
    <section>
      <div className="tg-section-heading">
        <div>
          <h1>{titulo}</h1>
        </div>
        <button className="tg-button tg-primary" onClick={() => abrir(inicial)}>
          + Crear {singular}
        </button>
      </div>
      <div className="tg-card">
        {!filas.length ? (
          <Vacio titulo={`Todavía no has agregado ${singular}`} />
        ) : (
          filas.map((item) => (
            <div key={item.id_local} className="tg-initial-row">
              <div>
                <strong>{item.nombre}</strong>
                {item.es_principal && <span className="tg-badge">Principal</span>}
              </div>
              <div className="tg-row-actions">
                <button onClick={() => abrir(item)}>Editar</button>
                <button
                  onClick={() =>
                    guardar(filas.filter((fila) => fila.id_local !== item.id_local))
                  }
                >
                  Quitar
                </button>
              </div>
            </div>
          ))
        )}
      </div>
      {edicion && (
        <Modal
          titulo={`${edicion.id_local ? 'Editar' : 'Crear'} ${singular}`}
          cerrar={() => setEdicion(null)}
        >
          <Formulario
            campos={campos}
            inicial={edicion}
            opciones={opciones}
            guardar={async (body) => {
              if (
                filas.some(
                  (item) =>
                    item.id_local !== edicion.id_local &&
                    item.nombre.toLocaleLowerCase('es') ===
                      body.nombre.toLocaleLowerCase('es'),
                )
              )
                throw new Error('Ya agregaste un registro con ese nombre.');
              const nuevo = {
                ...edicion,
                ...body,
                id_local:
                  edicion.id_local ||
                  Math.max(Date.now(), ...filas.map((item) => item.id_local + 1)),
                ...(sucursales ? { sucursales: locales } : {}),
              };
              guardar(
                edicion.id_local
                  ? filas.map((item) =>
                      item.id_local === edicion.id_local ? nuevo : item,
                    )
                  : [...filas, nuevo],
              );
              setEdicion(null);
            }}
          >
            {sucursales && (
              <fieldset>
                <legend>Disponible en estas sucursales</legend>
                {sucursales.map((item) => (
                  <label key={item.id_local} className="tg-check">
                    <input
                      type="checkbox"
                      checked={locales.includes(item.id_local)}
                      onChange={(event) =>
                        setLocales(
                          event.target.checked
                            ? [...locales, item.id_local]
                            : locales.filter((id) => id !== item.id_local),
                        )
                      }
                    />
                    {item.nombre}
                  </label>
                ))}
              </fieldset>
            )}
          </Formulario>
        </Modal>
      )}
    </section>
  );
}
