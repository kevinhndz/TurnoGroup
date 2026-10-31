'use client';

import Link from 'next/link';
import { useState } from 'react';
import { api, listarTodo } from '../../lib/api';
import { camposEmpresa } from '../../lib/modulos';
import { usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { Mensaje, Vacio } from './Controles';
import Formulario from './Formulario';
import Crud from './Crud';
import Icon from '../Icon';

export function Negocio({ crear = false, despues }) {
  const { sesion, actualizar } = usarSesion();
  const [aviso, setAviso] = useState('');
  const datos = useDatos(
    () =>
      crear || !sesion.id_empresa
        ? Promise.resolve({})
        : api(`/empresas/${sesion.id_empresa}`),
    [crear, sesion.id_empresa],
  );
  if (datos.cargando) return <p role="status">Cargando negocio…</p>;
  if (datos.error) return <Mensaje error={datos.error} />;
  return (
    <section className="tg-card">
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">TU NEGOCIO</span>
          <h2>{crear ? 'Cuéntanos sobre tu negocio' : 'Información del negocio'}</h2>
          <p>Estos datos se utilizan en todo el espacio de tu empresa.</p>
        </div>
      </div>
      <Mensaje aviso={aviso} />
      <Formulario
        key={sesion.id_empresa || 'nueva'}
        campos={camposEmpresa}
        inicial={datos.datos}
        texto={crear ? 'Crear mi negocio' : 'Guardar negocio'}
        guardar={async (body) => {
          const empresa = await api(
            crear ? '/empresas/' : `/empresas/${sesion.id_empresa}`,
            { method: crear ? 'POST' : 'PATCH', body },
          );
          await actualizar();
          window.dispatchEvent(new Event('turno-datos'));
          setAviso('Tu negocio quedó guardado.');
          if (despues) despues(empresa);
        }}
      />
    </section>
  );
}

export function OpcionesSucursal({ pagos = false, lectura = false }) {
  const { sesion } = usarSesion();
  const [ocupado, setOcupado] = useState(() => new Set());
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const ruta = pagos ? '/pagos-sucursales/' : '/servicios-sucursales/';
  const clave = pagos ? 'id_metodo_pago' : 'id_tipo_servicio';
  const datos = useDatos(async () => {
    if (!sesion.id_sucursal) return null;
    const [opciones, asignaciones] = await Promise.all([
      listarTodo(pagos ? '/metodos-pago/' : '/tipos-servicio/'),
      listarTodo(`${ruta}?solo_habilitados=false`),
    ]);
    return { opciones, asignaciones };
  }, [pagos, sesion.id_sucursal]);

  async function cambiar(opcion, asignacion, cambio) {
    setOcupado((anteriores) => new Set([...anteriores, opcion.id]));
    setError('');
    setAviso('');
    const flags = pagos
      ? { habilitado: asignacion?.habilitado || false }
      : {
          habilitado: asignacion?.habilitado || false,
          mesas_habilitadas: asignacion?.mesas_habilitadas || false,
          reservas_habilitadas: asignacion?.reservas_habilitadas || false,
        };
    const body = { ...flags, ...cambio };
    if (!pagos && !body.habilitado) {
      body.mesas_habilitadas = false;
      body.reservas_habilitadas = false;
    }
    if (!pagos && !body.mesas_habilitadas) body.reservas_habilitadas = false;
    const reemplazar = (valor) =>
      datos.setDatos((anterior) => ({
        ...anterior,
        asignaciones: [
          ...anterior.asignaciones.filter((item) => item[clave] !== opcion.id),
          ...(valor ? [valor] : []),
        ],
      }));
    const avisarMesas = (valor) => {
      if (!pagos && opcion.clave_concepto === 'comer_aqui')
        window.dispatchEvent(
          new CustomEvent('turno-mesas', {
            detail: {
              id_sucursal: sesion.id_sucursal,
              habilitado: !!valor?.habilitado && !!valor?.mesas_habilitadas,
              reservas: !!valor?.habilitado && !!valor?.reservas_habilitadas,
            },
          }),
        );
    };
    const provisional = { [clave]: opcion.id, id_sucursal: sesion.id_sucursal, ...body };
    reemplazar(provisional);
    avisarMesas(provisional);
    try {
      const guardado = await api(
        asignacion ? `${ruta}${sesion.id_sucursal}/${opcion.id}` : ruta,
        {
          method: asignacion ? 'PATCH' : 'POST',
          body: asignacion ? body : { [clave]: opcion.id, ...body },
        },
      );
      reemplazar(guardado);
      avisarMesas(guardado);
      setAviso('Configuración guardada para esta sucursal.');
    } catch (fallo) {
      reemplazar(asignacion);
      avisarMesas(asignacion);
      setError(fallo.message);
    } finally {
      setOcupado(
        (anteriores) => new Set([...anteriores].filter((id) => id !== opcion.id)),
      );
    }
  }

  if (!sesion.id_sucursal)
    return (
      <Vacio
        titulo="Primero selecciona una sucursal"
        detalle="Las modalidades de atención y los métodos de pago se configuran por local."
        icono="store"
      />
    );
  return (
    <section>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">POR SUCURSAL</span>
          <h2>
            {pagos
              ? 'Define cómo cobran en tu negocio'
              : 'Elige cómo atiendes a tus clientes'}
          </h2>
          <p>
            {pagos
              ? 'El sistema registra el método elegido. El cobro se realiza fuera de Turno Group.'
              : 'Cada local puede ofrecer modalidades distintas.'}
          </p>
        </div>
      </div>
      <Mensaje error={error || datos.error} aviso={aviso} />
      {datos.cargando ? (
        <p role="status">Cargando opciones…</p>
      ) : (
        <div className="tg-option-list">
          {datos.datos?.opciones.map((opcion) => {
            const asignacion = datos.datos.asignaciones.find(
              (item) => item[clave] === opcion.id,
            );
            return (
              <article key={opcion.id} className="tg-card tg-option">
                <div className="tg-option-main">
                  <span className="tg-tile-icon">
                    <Icon
                      name={
                        pagos
                          ? 'money'
                          : opcion.clave_concepto === 'comer_aqui'
                            ? 'table'
                            : 'store'
                      }
                    />
                  </span>
                  <div>
                    <h3>{opcion.nombre_visible}</h3>
                    <p>
                      {opcion.descripcion ||
                        (pagos
                          ? 'Método registrado al atender un pedido.'
                          : 'Modalidad de atención del local.')}
                    </p>
                  </div>
                  <label className="tg-switch">
                    <input
                      type="checkbox"
                      checked={!!asignacion?.habilitado}
                      disabled={ocupado.has(opcion.id) || lectura}
                      onChange={(event) =>
                        cambiar(opcion, asignacion, { habilitado: event.target.checked })
                      }
                      aria-label={`${opcion.nombre_visible}: habilitado`}
                    />
                    <span />
                  </label>
                </div>
                {!pagos && opcion.clave_concepto === 'comer_aqui' && (
                  <div className="tg-option-children">
                    <label className="tg-check">
                      <input
                        type="checkbox"
                        checked={!!asignacion?.mesas_habilitadas}
                        disabled={
                          ocupado.has(opcion.id) || lectura || !asignacion?.habilitado
                        }
                        onChange={(event) =>
                          cambiar(opcion, asignacion, {
                            mesas_habilitadas: event.target.checked,
                          })
                        }
                      />{' '}
                      Gestionar mesas en este local
                    </label>
                    <label className="tg-check">
                      <input
                        type="checkbox"
                        checked={!!asignacion?.reservas_habilitadas}
                        disabled={
                          ocupado.has(opcion.id) ||
                          lectura ||
                          !asignacion?.mesas_habilitadas
                        }
                        onChange={(event) =>
                          cambiar(opcion, asignacion, {
                            reservas_habilitadas: event.target.checked,
                          })
                        }
                      />
                      Habilitar reservas para mesas
                    </label>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

export function Impuestos() {
  const [aviso, setAviso] = useState('');
  const [error, setError] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const datos = useDatos(() => listarTodo('/configuracion-impuestos/'), []);
  const impuesto = datos.datos?.[0];
  const campos = [
    { clave: 'nombre', label: 'Nombre del impuesto', nullable: true, maxLength: 80 },
    {
      clave: 'porcentaje',
      label: 'Porcentaje (%)',
      type: 'number',
      min: 0,
      max: 100,
      step: '0.001',
      required: true,
    },
    {
      clave: 'precios_incluyen_impuesto',
      label: 'Los precios ya incluyen el impuesto',
      type: 'checkbox',
      valor: false,
    },
  ];
  return (
    <section className="tg-card">
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">CONFIGURACIÓN FISCAL</span>
          <h2>Impuestos</h2>
          <p>Una configuración por empresa. Se aplica al calcular los nuevos pedidos.</p>
        </div>
      </div>
      <Mensaje error={error || datos.error} aviso={aviso} />
      {datos.cargando ? (
        <p role="status">Cargando configuración…</p>
      ) : (
        <>
          <p>
            <span className={`tg-status ${impuesto?.activo ? 'is-active' : ''}`}>
              {impuesto?.activo ? 'Impuesto activo' : 'Sin impuesto activo'}
            </span>
          </p>
          <Formulario
            key={JSON.stringify(impuesto)}
            campos={campos}
            inicial={impuesto || {}}
            texto={impuesto ? 'Guardar y activar impuesto' : 'Crear impuesto'}
            guardar={async (body) => {
              await api(
                impuesto
                  ? `/configuracion-impuestos/${impuesto.id}`
                  : '/configuracion-impuestos/',
                {
                  method: impuesto ? 'PATCH' : 'POST',
                  body: impuesto ? { ...body, activo: true } : body,
                },
              );
              setAviso('El impuesto quedó guardado.');
              datos.recargar();
            }}
          />
          {impuesto?.activo && (
            <button
              className="tg-link-button tg-danger"
              disabled={ocupado}
              onClick={async () => {
                setOcupado(true);
                setError('');
                try {
                  await api(`/configuracion-impuestos/${impuesto.id}/desactivar`, {
                    method: 'POST',
                  });
                  datos.recargar();
                  setAviso('La empresa quedó sin impuesto activo.');
                } catch (fallo) {
                  setError(fallo.message);
                } finally {
                  setOcupado(false);
                }
              }}
            >
              Desactivar impuesto
            </button>
          )}
        </>
      )}
    </section>
  );
}

export default function Configuracion({ pestañaInicial = 'negocio' }) {
  const [pestaña, setPestaña] = useState(pestañaInicial);
  const pestañas = [
    ['negocio', 'Negocio'],
    ['servicios', 'Servicios'],
    ['pagos', 'Métodos de pago'],
    ['impuestos', 'Impuestos'],
    ['descuentos', 'Descuentos'],
  ];
  return (
    <>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">A TU MANERA</span>
          <h1>Configuración</h1>
          <p>Prepara la forma de trabajar de tu empresa y de cada sucursal.</p>
        </div>
        <Link className="tg-button tg-secondary" href="/configuracion-inicial">
          Abrir asistente
        </Link>
      </div>
      <nav className="tg-tabs" aria-label="Configuración">
        {pestañas.map(([id, titulo]) => (
          <button
            key={id}
            onClick={() => setPestaña(id)}
            aria-current={pestaña === id ? 'page' : undefined}
          >
            {titulo}
          </button>
        ))}
      </nav>
      <div key={pestaña}>
        {pestaña === 'negocio' ? (
          <Negocio />
        ) : pestaña === 'servicios' ? (
          <OpcionesSucursal />
        ) : pestaña === 'pagos' ? (
          <OpcionesSucursal pagos />
        ) : pestaña === 'impuestos' ? (
          <Impuestos />
        ) : (
          <Crud modulo="descuentos" />
        )}
      </div>
    </>
  );
}
