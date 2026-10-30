import ActionButton from './ActionButton';
import Icon from './Icon';

export default function CallToAction() {
  return (
    <section className="closing-section" id="registro" aria-labelledby="closing-title">
      <div className="container">
        <div className="closing-card">
          <div className="closing-copy">
            <p className="eyebrow">El próximo turno puede ser más sencillo</p>
            <h2 id="closing-title">Pon orden en tu restaurante o cafetería hoy mismo.</h2>
            <p>
              Tu equipo se encarga de los buenos momentos. Turno Group te ayuda a mantener
              el resto en su lugar.
            </p>
            <ActionButton arrow>Comenzar mi prueba gratis</ActionButton>
            <span className="closing-note">
              Primer mes gratis · Después, $100 USD al mes por sucursal.
            </span>
          </div>
          <div className="closing-illustration" aria-hidden="true">
            <div className="closing-circle">
              <Icon name="coffee" size={80} />
            </div>
            <span>Para servir mejor.</span>
            <div className="closing-small-note">
              <Icon name="check" size={13} /> Un pendiente menos.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
