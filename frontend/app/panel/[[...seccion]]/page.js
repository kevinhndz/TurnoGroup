import { notFound } from 'next/navigation';
import Panel from '../../../components/sistema/Panel';

const secciones = new Set([
  '',
  'cuenta',
  'empresas',
  'usuarios',
  'asignar-gerente',
  'productos',
  'categorias',
  'sucursales',
  'mesas',
  'descuentos',
  'configuracion',
  'equipo',
  'disponibilidad',
  'pedidos',
  'bitacora',
  'finanzas',
  'reservas',
  'suscripcion',
]);
export const metadata = { title: 'Mi espacio | Turno Group' };

export default async function Page({ params }) {
  const { seccion = [] } = await params;
  const nombre = seccion.join('/');
  if (!secciones.has(nombre)) notFound();
  return <Panel seccion={nombre} />;
}
