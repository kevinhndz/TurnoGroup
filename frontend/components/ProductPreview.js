import Image from 'next/image';

export default function ProductPreview() {
  return (
    <section className="product-preview" aria-labelledby="product-preview-title">
      <div className="container">
        <div className="section-intro">
          <span className="eyebrow">ASÍ SE VE POR DENTRO</span>
          <h2 id="product-preview-title">Tu operación, a la vista.</h2>
          <p>
            Consulta tu negocio, entra a los pedidos y cambia de sucursal desde un mismo
            panel.
          </p>
        </div>
        <figure className="product-preview-frame">
          <Image
            src="/images/panel-ejemplo.png"
            alt="Vista de ejemplo del panel de Turno Group con resumen de sucursales, productos y pedidos"
            width={1440}
            height={1000}
            sizes="(max-width: 800px) 100vw, 1100px"
          />
          <figcaption>Vista del panel con datos de demostración.</figcaption>
        </figure>
      </div>
    </section>
  );
}
