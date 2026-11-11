export function etiquetaSucursal(sucursal) {
  if (!sucursal) return 'Sin sucursal asignada';
  const direccion = sucursal.direccion?.trim();
  return `${sucursal.nombre} · Sucursal${sucursal.id ? ` #${sucursal.id}` : ''}${direccion ? ` · ${direccion}` : ''}`;
}
