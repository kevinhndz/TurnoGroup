'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { AccesoPrivado, usarSesion } from './Sesion';
import { SelectorContexto } from './Espacio';
import { Negocio, OpcionesSucursal, Impuestos } from './Configuracion';
import Crud from './Crud';
import Disponibilidad from './Disponibilidad';
import { Mensaje, Vacio } from './Controles';
import { useDatos } from './Datos';
import { api, listarTodo } from '../../lib/api';
import Icon from '../Icon';
import AltaInicial from './AltaInicial';
import { useRouter } from 'next/navigation';

const pasos = [
  'Negocio',
  'Sucursales',
  'Servicios',
  'Pagos e impuestos',
  'Descuentos',
  'Productos',
  'Revisión',
];

export default function Asistente() {
  const { registro, cargando } = usarSesion();
  const router = useRouter();
  useEffect(() => {
    if (!cargando && !registro) router.replace('/panel/configuracion');
  }, [cargando, registro, router]);
  if (registro) return <AltaInicial />;
  return <p role="status">Abriendo configuración…</p>;
}

function Interior() {
  const { sesion, cambiarContexto } = usarSesion();
  const [paso, setPaso] = useState(1);
  const [catalogo, setCatalogo] = useState('categorias');
  const [error, setError] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const clave = `turno-asistente:${sesion.usuario.id}:${sesion.id_empresa || 'nuevo'}`;
  useEffect(() => {
    if (!sesion.id_empresa) {
      setPaso(1);
      return;
    }
    try {
      const guardado = Number(localStorage.getItem(clave) || 1);
      setPaso(Number.isInteger(guardado) ? Math.min(7, Math.max(1, guardado)) : 1);
    } catch {
      setPaso(1);
    }
  }, [clave, sesion.id_empresa]);

  function ir(nuevo) {
    setError('');
    setPaso(nuevo);
    try {
      localStorage.setItem(clave, String(nuevo));
    } catch {}
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  async function seleccionarPrimeraSucursal() {
    if (sesion.id_sucursal) return;
    const vinculos = await api('/sesiones/vinculos');
    const vinculo = vinculos.find((item) => item.id_empresa === sesion.id_empresa);
    if (vinculo?.sucursales.length)
      await cambiarContexto(vinculo.id, vinculo.sucursales[0].id);
  }

  async function siguiente() {
    setOcupado(true);
    setError('');
    try {
      if (!sesion.id_empresa) throw new Error('Guarda primero los datos de tu negocio.');
      if (paso === 2) {
        const sucursales = await listarTodo('/sucursales/');
        if (!sucursales.some((item) => item.activo))
          throw new Error('Crea al menos una sucursal activa para continuar.');
        await seleccionarPrimeraSucursal();
      }
      if ((paso === 3 || paso === 4) && !sesion.id_sucursal)
        throw new Error('Selecciona una sucursal en la parte superior.');
      if (paso === 3 || paso === 4) {
        const registros = await listarTodo(
          paso === 3 ? '/servicios-sucursales/' : '/pagos-sucursales/',
        );
        if (!registros.some((item) => item.habilitado))
          throw new Error(
            paso === 3
              ? 'Activa al menos un servicio en el local seleccionado.'
              : 'Activa al menos un método de pago en el local seleccionado.',
          );
      }
      ir(paso + 1);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setOcupado(false);
    }
  }

  if (
    sesion.usuario.rol_plataforma === 'Superadministrador' ||
    (sesion.id_empresa && sesion.rol_empresa !== 'Gerente')
  )
    return (
      <main id="contenido" className="tg-loading">
        <h1>La configuración pertenece al gerente</h1>
        <Link href="/panel" className="tg-button tg-primary">
          Ir al panel
        </Link>
      </main>
    );

  return (
    <div className="tg-wizard">
      <header className="tg-wizard-header">
        <Link href="/panel" className="tg-brand">
          Turno Group
          <span />
        </Link>
        <Link href="/panel/cuenta" className="tg-user">
          <span className="tg-avatar">{sesion.usuario.nombre.slice(0, 1)}</span>
          <span>
            {sesion.usuario.nombre}
            <small>{sesion.rol_empresa || 'Nueva cuenta'}</small>
          </span>
        </Link>
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
                disabled={!sesion.id_empresa && indice > 0}
                onClick={() => ir(indice + 1)}
                aria-current={paso === indice + 1 ? 'step' : undefined}
              >
                <span>{paso > indice + 1 ? '✓' : indice + 1}</span>
                {nombre}
              </button>
            </li>
          ))}
        </ol>
        {sesion.id_empresa && (
          <div className="tg-wizard-context">
            <SelectorContexto />
            <Link href="/panel">Ir al panel →</Link>
          </div>
        )}
        <Mensaje error={error} />
        <div
          className="tg-step-body"
          key={`${paso}:${sesion.id_empresa}:${sesion.id_sucursal}`}
        >
          {paso === 1 && (
            <Negocio
              crear={!sesion.id_empresa}
              despues={(empresa) => {
                try {
                  localStorage.setItem(
                    `turno-asistente:${sesion.usuario.id}:${empresa.id}`,
                    '2',
                  );
                } catch {}
                ir(2);
              }}
            />
          )}
          {paso === 2 && (
            <Crud modulo="sucursales" compacto alGuardar={seleccionarPrimeraSucursal} />
          )}
          {paso === 3 && <OpcionesSucursal />}
          {paso === 4 && (
            <div className="tg-step-stack">
              <OpcionesSucursal pagos />
              <Impuestos />
            </div>
          )}
          {paso === 5 && <Crud modulo="descuentos" compacto />}
          {paso === 6 && (
            <>
              <div className="tg-section-heading">
                <div>
                  <span className="tg-eyebrow">CATÁLOGO INICIAL</span>
                  <h1>Prepara tus productos</h1>
                  <p>
                    Este paso es opcional. Primero crea categorías, luego productos y por
                    último asígnalos al local.
                  </p>
                </div>
              </div>
              <nav className="tg-tabs" aria-label="Catálogo inicial">
                {[
                  ['categorias', '1. Categorías'],
                  ['productos', '2. Productos'],
                  ['disponibilidad', '3. Disponibilidad del local'],
                ].map(([id, label]) => (
                  <button
                    key={id}
                    aria-current={catalogo === id ? 'page' : undefined}
                    onClick={() => setCatalogo(id)}
                  >
                    {label}
                  </button>
                ))}
              </nav>
              {catalogo === 'disponibilidad' ? (
                <Disponibilidad />
              ) : (
                <Crud key={catalogo} modulo={catalogo} compacto />
              )}
            </>
          )}
          {paso === 7 && <Resumen editar={ir} />}
        </div>
        {(paso === 5 || paso === 6) && (
          <p className="tg-table-note">
            Puedes continuar sin agregar registros y completarlos después desde el panel.
          </p>
        )}
        <footer className="tg-wizard-actions">
          <button
            className="tg-button tg-secondary"
            disabled={paso === 1 || ocupado}
            onClick={() => ir(paso - 1)}
          >
            ← Volver
          </button>
          <Link href="/panel" className="tg-muted">
            Salir y continuar más tarde
          </Link>
          {paso < 7 ? (
            <button
              className="tg-button tg-primary"
              disabled={ocupado}
              onClick={siguiente}
            >
              {ocupado ? 'Revisando…' : 'Continuar'}
              <Icon name="arrow" size={17} />
            </button>
          ) : (
            <Link
              href="/panel"
              className="tg-button tg-primary"
              onClick={() => {
                try {
                  localStorage.setItem(clave, '7');
                } catch {}
              }}
            >
              Finalizar y abrir panel
              <Icon name="check" size={17} />
            </Link>
          )}
        </footer>
      </main>
    </div>
  );
}

function Resumen({ editar }) {
  const { sesion } = usarSesion();
  const datos = useDatos(async () => {
    if (!sesion.id_empresa) return null;
    const [
      empresa,
      sucursales,
      impuestos,
      descuentos,
      productos,
      categorias,
      servicios,
      pagos,
      tipos,
      metodos,
    ] = await Promise.all([
      api(`/empresas/${sesion.id_empresa}`),
      listarTodo('/sucursales/'),
      listarTodo('/configuracion-impuestos/'),
      listarTodo('/descuentos/'),
      api('/productos/?limite=1'),
      api('/categorias/?limite=1'),
      sesion.id_sucursal ? listarTodo('/servicios-sucursales/') : [],
      sesion.id_sucursal ? listarTodo('/pagos-sucursales/') : [],
      listarTodo('/tipos-servicio/'),
      listarTodo('/metodos-pago/'),
    ]);
    return {
      empresa,
      sucursales,
      impuestos,
      descuentos,
      productos,
      categorias,
      servicios,
      pagos,
      tipos,
      metodos,
    };
  }, [sesion.id_empresa, sesion.id_sucursal]);
  if (!sesion.id_empresa) return <Vacio titulo="Crea primero tu negocio" />;
  if (datos.cargando) return <p role="status">Preparando resumen…</p>;
  if (datos.error) return <Mensaje error={datos.error} />;
  const d = datos.datos;
  return (
    <>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">REVISIÓN FINAL</span>
          <h1>Revisa tu negocio</h1>
          <p>
            Los cambios ya están guardados. Puedes volver a cada sección para ajustarlos.
          </p>
        </div>
      </div>
      <div className="tg-summary-grid">
        <article className="tg-card">
          <Cabecera titulo="Negocio" paso={1} editar={editar} />
          <h3>{d.empresa.nombre}</h3>
          <p>
            {d.empresa.tipo_negocio} · {d.empresa.codigo_pais} · {d.empresa.codigo_moneda}
          </p>
          <small>{d.empresa.zona_horaria}</small>
        </article>
        <article className="tg-card">
          <Cabecera titulo="Sucursales" paso={2} editar={editar} />
          {d.sucursales.map((item) => (
            <p key={item.id}>
              <strong>{item.nombre}</strong> · {item.activo ? 'Activa' : 'Desactivada'}
              <small className="tg-muted">{item.direccion}</small>
            </p>
          ))}
          {!d.sucursales.length && <p>Sin sucursales registradas.</p>}
        </article>
        <article className="tg-card">
          <Cabecera titulo="Servicios del local seleccionado" paso={3} editar={editar} />
          <p>
            {d.servicios
              .map(
                (item) =>
                  d.tipos.find((tipo) => tipo.id === item.id_tipo_servicio)
                    ?.nombre_visible,
              )
              .filter(Boolean)
              .join(', ') || 'Sin servicios habilitados.'}
          </p>
          <small>
            Este resumen corresponde únicamente a la sucursal seleccionada arriba.
          </small>
        </article>
        <article className="tg-card">
          <Cabecera titulo="Pagos e impuestos" paso={4} editar={editar} />
          <p>
            {d.pagos
              .map(
                (item) =>
                  d.metodos.find((metodo) => metodo.id === item.id_metodo_pago)
                    ?.nombre_visible,
              )
              .filter(Boolean)
              .join(', ') || 'Sin métodos habilitados en este local.'}
          </p>
          <p>
            {d.impuestos[0]?.activo
              ? `${d.impuestos[0].nombre || 'Impuesto'}: ${d.impuestos[0].porcentaje}% · ${d.impuestos[0].precios_incluyen_impuesto ? 'Incluido en precios' : 'Se agrega al total'}`
              : 'Sin impuesto activo en la empresa.'}
          </p>
        </article>
        <article className="tg-card">
          <Cabecera titulo="Descuentos" paso={5} editar={editar} />
          <p>{d.descuentos.filter((item) => item.activo).length} descuentos activos.</p>
        </article>
        <article className="tg-card">
          <Cabecera titulo="Catálogo inicial" paso={6} editar={editar} />
          <p>
            {d.categorias.total} categorías · {d.productos.total} productos.
          </p>
          <Link href="/panel/disponibilidad">Revisar disponibilidad por local →</Link>
        </article>
      </div>
    </>
  );
}

function Cabecera({ titulo, paso, editar }) {
  return (
    <header className="tg-summary-header">
      <h3>{titulo}</h3>
      <button className="tg-link-button" onClick={() => editar(paso)}>
        Editar
      </button>
    </header>
  );
}
