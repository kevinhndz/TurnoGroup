export function leerCSV(texto) {
  const filas = [];
  let fila = [],
    campo = '',
    comillas = false;
  const fuente = texto.replace(/^\uFEFF/, '');
  for (let indice = 0; indice < fuente.length; indice += 1) {
    const letra = fuente[indice];
    if (letra === '"') {
      if (comillas && fuente[indice + 1] === '"') {
        campo += '"';
        indice += 1;
      } else comillas = !comillas;
    } else if (letra === ',' && !comillas) {
      fila.push(campo.trim());
      campo = '';
    } else if ((letra === '\n' || letra === '\r') && !comillas) {
      if (letra === '\r' && fuente[indice + 1] === '\n') indice += 1;
      fila.push(campo.trim());
      if (fila.some(Boolean)) filas.push(fila);
      fila = [];
      campo = '';
    } else campo += letra;
  }
  if (comillas) throw new Error('Hay una celda con comillas sin cerrar.');
  fila.push(campo.trim());
  if (fila.some(Boolean)) filas.push(fila);
  if (filas.length < 2 || filas.length > 1001)
    throw new Error('El archivo debe tener entre 1 y 1000 productos.');
  const titulos = filas.shift().map((valor) => valor.toLocaleLowerCase('es'));
  if (!titulos.includes('nombre') || !titulos.includes('precio'))
    throw new Error('El archivo necesita las columnas nombre y precio.');
  if (new Set(titulos).size !== titulos.length)
    throw new Error('Hay columnas repetidas.');
  return filas.map((valores, indice) => {
    if (valores.length !== titulos.length)
      throw new Error(`Revisa las columnas de la fila ${indice + 2}.`);
    const fila = Object.fromEntries(
      titulos.map((titulo, columna) => [titulo, valores[columna]]),
    );
    if (
      !fila.nombre ||
      fila.nombre.length > 100 ||
      !/^\d+(\.\d{1,2})?$/.test(fila.precio) ||
      Number(fila.precio) > 99999999.99
    )
      throw new Error(
        `Revisa el nombre y precio de la fila ${indice + 2}. Usa punto decimal.`,
      );
    return {
      nombre: fila.nombre,
      precio: fila.precio,
      categoria: fila.categoria || '',
      descripcion: fila.descripcion || null,
    };
  });
}
