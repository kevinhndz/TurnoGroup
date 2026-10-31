'use client';

import { useState } from 'react';
import { api, listarTodo } from '../../lib/api';
import { camposEmpresa } from '../../lib/modulos';
import { useDatos } from './Datos';
import Crud from './Crud';
import { Mensaje, Modal } from './Controles';
import Formulario from './Formulario';

const camposUsuario = [
  { clave: 'nombre', label: 'Nombre', required: true, maxLength: 100 },
  { clave: 'correo', label: 'Correo', type: 'email', required: true },
];

export function EmpresasPlataforma() {
  return (
    <Crud
      configuracion={{
        titulo: 'Empresas',
        singular: 'empresa',
        ruta: '/empresas/',
        icono: 'store',
        detalle:
          'Negocios registrados en la plataforma. La operación de cada local pertenece a su equipo.',
        plataforma: true,
        estado: 'estado',
        estadoTexto: true,
        campos: camposEmpresa,
        columnas: [
          ['id', 'Número'],
          ['nombre', 'Empresa'],
          ['tipo_negocio', 'Tipo'],
          ['codigo_moneda', 'Moneda'],
        ],
      }}
    />
  );
}

export function UsuariosPlataforma() {
  const [seleccion, setSeleccion] = useState(null);
  const [version, setVersion] = useState(0);
  return (
    <>
      <Crud
        key={version}
        configuracion={{
          titulo: 'Usuarios',
          singular: 'usuario',
          ruta: '/usuarios/',
          icono: 'team',
          detalle:
            'Perfiles y acceso a la plataforma. El rol laboral se administra dentro de cada empresa.',
          plataforma: true,
          estado: 'estado',
          campos: camposUsuario,
          camposCrear: [
            ...camposUsuario,
            {
              clave: 'clave',
              label: 'Contraseña inicial',
              type: 'password',
              required: true,
              minLength: 12,
              maxLength: 128,
            },
          ],
          columnas: [
            ['id', 'Número'],
            ['nombre', 'Persona'],
            ['correo', 'Correo'],
            ['rol_plataforma', 'Rol de plataforma'],
          ],
          accion: (fila) => (
            <button onClick={() => setSeleccion(fila)}>Rol de plataforma</button>
          ),
        }}
      />
      {seleccion && (
        <Modal
          titulo={`Permisos de ${seleccion.nombre}`}
          cerrar={() => setSeleccion(null)}
        >
          <p className="tg-muted">
            Cambiar este rol cerrará las sesiones de la persona. El superadministrador
            administra la plataforma y no opera ventas de clientes.
          </p>
          <Formulario
            campos={[
              {
                clave: 'rol_plataforma',
                label: 'Rol de plataforma',
                type: 'select',
                opciones: [
                  ['Usuario', 'Usuario'],
                  ['Superadministrador', 'Superadministrador'],
                ],
              },
            ]}
            inicial={seleccion}
            guardar={async (body) => {
              await api(`/usuarios/${seleccion.id}/rol-plataforma`, {
                method: 'PATCH',
                body,
              });
              setSeleccion(null);
              setVersion(version + 1);
            }}
          />
        </Modal>
      )}
    </>
  );
}

export function AsignarGerente() {
  const [aviso, setAviso] = useState('');
  const datos = useDatos(async () => {
    const [usuarios, empresas] = await Promise.all([
      listarTodo('/usuarios/'),
      listarTodo('/empresas/'),
    ]);
    return {
      usuarios: usuarios.filter(
        (item) => item.estado && item.rol_plataforma !== 'Superadministrador',
      ),
      empresas: empresas.filter((item) => item.estado !== 'Inactiva'),
    };
  }, []);
  return (
    <>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">PLATAFORMA</span>
          <h1>Asignar primer gerente</h1>
          <p>
            Utiliza esta opción para una empresa que todavía no tiene gerente. Los demás
            integrantes se agregan por invitación.
          </p>
        </div>
      </div>
      <Mensaje error={datos.error} aviso={aviso} />
      <section className="tg-card">
        {datos.cargando ? (
          <p role="status">Cargando empresas y usuarios…</p>
        ) : (
          <Formulario
            campos={[
              {
                clave: 'id_empresa',
                label: 'Empresa',
                type: 'select',
                fuente: 'empresas',
                required: true,
              },
              {
                clave: 'id_usuario',
                label: 'Persona',
                type: 'select',
                fuente: 'usuarios',
                required: true,
              },
            ]}
            opciones={datos.datos || {}}
            guardar={async (body) => {
              await api('/vinculos-laborales/', {
                method: 'POST',
                body: { ...body, rol: 'Gerente' },
              });
              setAviso('El gerente quedó vinculado a la empresa.');
            }}
            texto="Asignar gerente"
          />
        )}
      </section>
    </>
  );
}
