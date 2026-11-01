self.onmessage = async ({ data }) => {
  try {
    if (
      !/^\/api\/backend\/suscripciones\/comprobantes\/(excel|pdf|\d+\/(pdf|excel))$/.test(
        data.ruta,
      )
    )
      throw new Error('Documento no permitido');
    const respuesta = await fetch(data.ruta, {
      credentials: 'same-origin',
      cache: 'no-store',
    });
    if (!respuesta.ok)
      throw new Error(
        'No se pudo preparar el documento. Revisa tu sesión e intenta de nuevo.',
      );
    const archivo = await respuesta.arrayBuffer();
    const filas = data.filas.map((item) => [
      `TG-PRUEBA-${String(item.id).padStart(6, '0')}`,
      new Intl.DateTimeFormat('es-HN').format(new Date(item.fecha)),
      item.concepto,
      `${Number(item.importe).toFixed(2)} ${item.moneda || 'USD'}`,
      item.detalle,
    ]);
    self.postMessage({ archivo, filas }, [archivo]);
  } catch (error) {
    self.postMessage({ error: error.message });
  }
};
