import PedidoNuevo from '../../components/sistema/PedidoNuevo';
export const metadata = { title: 'Nuevo pedido | Turno Group' };
export default async function Page({ searchParams }) {
  const { editar } = await searchParams;
  return <PedidoNuevo editar={/^\d+$/.test(editar || '') ? Number(editar) : null} />;
}
