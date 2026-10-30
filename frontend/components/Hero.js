import Image from 'next/image';
import ActionButton from './ActionButton';
import Icon from './Icon';

export default function Hero() {
  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="container hero-grid">
        <div className="hero-copy">
          <span className="pill">
            <span className="dot" /> Operación presencial · Primer mes gratis
          </span>
          <h1 id="hero-title">
            Organiza tus pedidos y sucursales en un solo sistema,{' '}
            <span>sin papeles ni complicaciones.</span>
          </h1>
          <p>
            Turno Group centraliza la operación de tu restaurante o cafetería. Configura
            tus sucursales, empleados y menú a tu medida, y dedica más tiempo a tus
            clientes.
          </p>
          <div className="hero-actions">
            <ActionButton arrow />
            <a href="#funciones" className="button button-secondary">
              <Icon name="book" size={17} />
              Conocer funciones
            </a>
          </div>
          <div className="hero-note">
            <span className="note-check">
              <Icon name="check" size={12} />
            </span>
            Un mes para conocerlo. A tu ritmo.
          </div>
        </div>
        <div className="hero-visual">
          <div className="hero-photo">
            <Image
              src="/images/cafe-turno.webp"
              alt="Tablet sobre una mesa de madera junto a una taza de café en un restaurante"
              width={1024}
              height={576}
              priority
              sizes="(max-width: 800px) 90vw, 45vw"
            />
            <div className="photo-caption">
              <span>
                <i /> Servicio de sala activo
              </span>
              <span>Turno almuerzo</span>
            </div>
          </div>
          <div className="ticket" aria-label="Ejemplo de pedido de la mesa 4">
            <div className="ticket-header">
              <span>
                <Icon name="receipt" size={17} />
                Mesa 04
              </span>
              <span className="status-pill">Abierto</span>
            </div>
            <div className="ticket-item">
              <span>
                <b>2×</b> Café latte
              </span>
              <span>L 150.00</span>
            </div>
            <div className="ticket-item">
              <span>
                <b>2×</b> Medialuna de manteca
              </span>
              <span>L 90.00</span>
            </div>
            <div className="ticket-total">
              <span>Total del pedido</span>
              <strong>L 240.00</strong>
            </div>
            <div className="ticket-foot">
              <span className="dot" />
              Todo en orden, listo para servir.
            </div>
          </div>
          <div className="hero-annotation">
            <span className="annotation-line" /> Menos pendientes. Más sobremesas.
          </div>
        </div>
      </div>
      <div className="container hero-bottom">
        <span>Hecho para el ritmo de tu negocio</span>
        <div>
          <Icon name="coffee" size={16} /> Cafeterías
          <span className="separator-dot">·</span>
          <Icon name="table" size={16} /> Restaurantes
          <span className="separator-dot">·</span>
          <Icon name="store" size={16} /> Varias sucursales
        </div>
      </div>
    </section>
  );
}
