'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { api, limpiarCache } from '../../lib/api';

const Contexto = createContext(null);

export function ProveedorSesion({ children }) {
  const [sesion, setSesion] = useState(null);
  const [registro, setRegistro] = useState(null);
  const [mesasHabilitadas, setMesasHabilitadas] = useState(false);
  const [reservasHabilitadas, setReservasHabilitadas] = useState(false);
  const [cargando, setCargando] = useState(true);
  const [fallo, setFallo] = useState('');
  const [version, setVersion] = useState(0);
  const solicitud = useRef(0);

  const olvidar = useCallback(() => {
    solicitud.current += 1;
    limpiarCache();
    setSesion(null);
    setRegistro(null);
    setFallo('');
    setCargando(false);
    try {
      for (const clave of Object.keys(sessionStorage)) {
        if (clave.startsWith('turno-carrito:') || clave.startsWith('turno-pedido:'))
          sessionStorage.removeItem(clave);
      }
    } catch {}
  }, []);

  const actualizar = useCallback(async () => {
    const numero = ++solicitud.current;
    try {
      const datos = await api('/sesiones/actual', { avisarSesion: false });
      if (solicitud.current === numero) {
        setSesion(datos);
        setFallo('');
      }
      return datos;
    } catch (error) {
      if (solicitud.current === numero) {
        setSesion(null);
        setFallo(error.estado === 401 ? '' : error.message);
      }
      return null;
    } finally {
      if (solicitud.current === numero) setCargando(false);
    }
  }, []);

  useEffect(() => {
    actualizar();
    window.addEventListener('sesion-vencida', olvidar);
    return () => {
      window.removeEventListener('sesion-vencida', olvidar);
      solicitud.current += 1;
    };
  }, [actualizar, olvidar]);

  useEffect(() => {
    setMesasHabilitadas(!!sesion?.mesas_habilitadas);
    setReservasHabilitadas(!!sesion?.reservas_habilitadas);
    const cambiar = (evento) => {
      if (evento.detail.id_sucursal === sesion?.id_sucursal) {
        setMesasHabilitadas(evento.detail.habilitado);
        setReservasHabilitadas(!!evento.detail.reservas);
      }
    };
    window.addEventListener('turno-mesas', cambiar);
    return () => window.removeEventListener('turno-mesas', cambiar);
  }, [
    sesion?.id_empresa,
    sesion?.id_sucursal,
    sesion?.mesas_habilitadas,
    sesion?.reservas_habilitadas,
    version,
  ]);

  const iniciar = async (datos) => {
    solicitud.current += 1;
    try {
      const respuesta = await api('/sesiones/iniciar', { method: 'POST', body: datos });
      setSesion(respuesta);
      setRegistro(null);
      setFallo('');
      return respuesta;
    } finally {
      setCargando(false);
    }
  };

  const cambiarContexto = async (idVinculo, idSucursal) => {
    solicitud.current += 1;
    const respuesta = await api('/sesiones/contexto', {
      method: 'PATCH',
      body: {
        id_vinculo_laboral: Number(idVinculo),
        id_sucursal: idSucursal ? Number(idSucursal) : null,
      },
    });
    setSesion(respuesta);
    setVersion((valor) => valor + 1);
    return respuesta;
  };

  const finalizarRegistro = async (datos) => {
    const respuesta = await api('/usuarios/registro-negocio', {
      method: 'POST',
      body: datos,
    });
    solicitud.current += 1;
    setSesion(respuesta);
    setRegistro(null);
    setFallo('');
    setCargando(false);
    setVersion((valor) => valor + 1);
    return respuesta;
  };

  const cerrar = async () => {
    await api('/sesiones/cerrar', { method: 'POST' });
    olvidar();
  };

  return (
    <Contexto.Provider
      value={{
        sesion,
        registro,
        mesasHabilitadas,
        reservasHabilitadas,
        setRegistro,
        finalizarRegistro,
        cargando,
        fallo,
        iniciar,
        actualizar,
        cerrar,
        olvidar,
        cambiarContexto,
        version,
      }}
    >
      {children}
    </Contexto.Provider>
  );
}

export function usarSesion() {
  return useContext(Contexto);
}

export function AccesoPrivado({ children }) {
  const { sesion, registro, cargando, fallo, actualizar, cerrar } = usarSesion();
  const router = useRouter();
  const pathname = usePathname();
  const [errorSalida, setErrorSalida] = useState('');

  useEffect(() => {
    if (registro) {
      router.replace('/configuracion-inicial');
      return;
    }
    if (!cargando && !sesion && !fallo)
      router.replace(`/login?volver=${encodeURIComponent(pathname)}`);
  }, [cargando, sesion, registro, fallo, pathname, router]);

  if (registro)
    return <div className="tg-loading">Continúa con la configuración inicial…</div>;
  if (cargando)
    return (
      <div className="tg-loading" role="status">
        Preparando tu espacio…
      </div>
    );
  if (!sesion && fallo)
    return (
      <main id="contenido" className="tg-loading">
        <h2>No pudimos abrir tu espacio</h2>
        <p>{fallo}</p>
        <button className="button button-primary" onClick={actualizar}>
          Volver a intentar
        </button>
        <button
          className="button button-secondary"
          onClick={async () => {
            try {
              await cerrar();
              router.replace('/login');
            } catch (error) {
              setErrorSalida(error.message);
            }
          }}
        >
          Cerrar sesión e ingresar de nuevo
        </button>
        {errorSalida && <p role="alert">{errorSalida}</p>}
        <Link href="/login">Ir a la página de acceso</Link>
      </main>
    );
  if (!sesion)
    return (
      <div className="tg-loading" role="status">
        Abriendo acceso…
      </div>
    );
  return children;
}
