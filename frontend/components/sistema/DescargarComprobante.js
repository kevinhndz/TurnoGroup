'use client';

import { useEffect, useState } from 'react';
import { Mensaje, Modal } from './Controles';
import { dinero, fechaLocal } from '../../lib/api';

export default function DescargarComprobante({ comprobantes, individual = false }) {
  const [abierto, setAbierto] = useState(false);
  const [formato, setFormato] = useState('pdf');
  return (
    <>
      <button
        className="tg-button tg-secondary"
        onClick={() => setAbierto(true)}
        disabled={!comprobantes.length}
      >
        {individual ? 'Ver / descargar' : 'Descargar'}
      </button>
      {abierto && (
        <Modal
          titulo={
            individual
              ? 'Vista previa del comprobante'
              : 'Descargar historial de facturación'
          }
          cerrar={() => setAbierto(false)}
        >
          <label className="tg-field">
            <span>Formato de descarga</span>
            <select value={formato} onChange={(event) => setFormato(event.target.value)}>
              <option value="pdf">PDF</option>
              <option value="excel">Excel</option>
            </select>
          </label>
          <VistaPrevia
            key={formato}
            formato={formato}
            comprobantes={comprobantes}
            individual={individual}
          />
        </Modal>
      )}
    </>
  );
}

function VistaPrevia({ formato, comprobantes, individual }) {
  const [documento, setDocumento] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    let url;
    setDocumento(null);
    setError('');
    const worker = new Worker('/workers/comprobantes.js');
    worker.onmessage = ({ data }) => {
      if (data.error) {
        setError(data.error);
        return;
      }
      url = URL.createObjectURL(
        new Blob([data.archivo], {
          type:
            formato === 'pdf'
              ? 'application/pdf'
              : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }),
      );
      setDocumento({ url, filas: data.filas });
    };
    worker.onerror = () =>
      setError('No se pudo preparar la vista previa. Intenta de nuevo.');
    worker.postMessage({
      ruta: `/api/backend/suscripciones/comprobantes/${individual ? `${comprobantes[0].id}/${formato}` : formato}`,
      filas: comprobantes,
    });
    return () => {
      worker.terminate();
      if (url) URL.revokeObjectURL(url);
    };
  }, [formato, comprobantes, individual]);
  return (
    <>
      <Mensaje error={error} />
      {!documento && !error && (
        <p role="status">Preparando vista previa en segundo plano…</p>
      )}
      {documento && (
        <>
          <p className="tg-muted">Documento de prueba · Sin validez fiscal</p>
          {formato === 'pdf' ? (
            <div className="tg-document-preview" aria-label="Contenido del comprobante">
              {comprobantes.map((item) => (
                <article className="tg-receipt-preview" key={item.id}>
                  <header>
                    <h2>Turno Group</h2>
                    <strong>COMPROBANTE DE PRUEBA</strong>
                    <p>TG-PRUEBA-{String(item.id).padStart(6, '0')}</p>
                  </header>
                  <dl>
                    <div>
                      <dt>Fecha</dt>
                      <dd>{fechaLocal(item.fecha)}</dd>
                    </div>
                    <div>
                      <dt>Concepto</dt>
                      <dd>{item.concepto}</dd>
                    </div>
                    <div>
                      <dt>Periodo</dt>
                      <dd>
                        {fechaLocal(item.periodo_inicio)} al{' '}
                        {fechaLocal(item.periodo_fin)}
                      </dd>
                    </div>
                  </dl>
                  <p className="tg-receipt-detail">{item.detalle}</p>
                  <div className="tg-receipt-total">
                    <span>Total</span>
                    <strong>{dinero(item.importe, item.moneda || 'USD')}</strong>
                  </div>
                  <p className="tg-muted">
                    Sin validez fiscal. No acredita pagos reales.
                  </p>
                </article>
              ))}
              <p className="tg-muted">Descarga el PDF para guardarlo o imprimirlo.</p>
            </div>
          ) : (
            <div className="tg-table-scroll">
              <table className="tg-table">
                <thead>
                  <tr>
                    {['Número', 'Fecha', 'Concepto', 'Importe', 'Detalle'].map((item) => (
                      <th key={item}>{item}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {documento.filas.map((fila, indice) => (
                    <tr key={indice}>
                      {fila.map((valor, columna) => (
                        <td key={columna}>{valor}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <a
            className="tg-button tg-primary"
            href={documento.url}
            download={`${individual ? `comprobante-${comprobantes[0].id}` : 'historial-facturacion'}.${formato === 'pdf' ? 'pdf' : 'xlsx'}`}
          >
            Descargar {formato === 'pdf' ? 'PDF' : 'Excel'}
          </a>
        </>
      )}
    </>
  );
}
