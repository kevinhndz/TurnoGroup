import Icon from './Icon';
import ActionButton from './ActionButton';

const included = [
  'Registro y consulta de pedidos',
  'Catálogo de productos, fotos y complementos',
  'Invitaciones a empleados y permisos por rol',
  'Gestión opcional de mesas y reservas',
  'Importación de productos con CSV o Excel',
];
export default function Pricing() {
  return (
    <section id="precios" className="section pricing" aria-labelledby="pricing-title">
      <div className="container">
        <div className="section-intro pricing-intro">
          <p className="eyebrow">Simple desde el primer día</p>
          <h2 id="pricing-title">
            Un precio claro.
            <br />
            Espacio para crecer.
          </h2>
          <p>
            Empieza con un mes gratis en todas tus sucursales. Después, paga por los
            locales que mantengas activos.
          </p>
        </div>
        <div className="pricing-grid">
          <article className="price-card base-plan">
            <div className="plan-heading">
              <span className="eyebrow">Plan base</span>
              <span className="status-pill">Primer mes gratis</span>
            </div>
            <p className="plan-description">Todo en orden, desde un solo lugar.</p>
            <div className="price">
              <span>$100</span>
              <div>
                <strong>USD</strong>
                <span>al mes por sucursal</span>
              </div>
            </div>
            <p className="price-note">
              Tu operación diaria, con las herramientas que necesitas.
            </p>
            <ul className="plan-list">
              {included.map((item) => (
                <li key={item}>
                  <Icon name="check" size={16} />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
            <ActionButton className="button button-primary plan-button" arrow>
              Iniciar prueba gratis
            </ActionButton>
            <p className="plan-footnote">
              El cobro mensual comienza después del mes de prueba.
            </p>
          </article>
          <article className="price-card finance-plan">
            <div className="plan-heading">
              <span className="eyebrow">Un paso más</span>
              <span className="optional-label">Opcional</span>
            </div>
            <div className="finance-title">
              <span className="feature-icon sage-icon">
                <Icon name="chart" size={23} />
              </span>
              <h3>Finanzas de tu empresa.</h3>
            </div>
            <p className="plan-description">La vista completa de tus números.</p>
            <div className="price finance-price">
              <span>+$30</span>
              <div>
                <strong>USD</strong>
                <span>al mes por empresa</span>
              </div>
            </div>
            <p className="price-note">Una tarifa fija, tengas una o varias sucursales.</p>
            <ul className="plan-list">
              <li>
                <Icon name="check" size={16} />
                <span>Consolidación financiera de tus sucursales</span>
              </li>
              <li>
                <Icon name="check" size={16} />
                <span>Control y reportes contables por empresa</span>
              </li>
            </ul>
            <div className="finance-note">
              <Icon name="store" size={18} />
              <p>
                Se añade una vez para toda tu empresa. No se multiplica por el número de
                locales.
              </p>
            </div>
            <a href="#calculadora" className="button button-secondary plan-button">
              Calcular mi plan <Icon name="arrow" size={16} />
            </a>
          </article>
        </div>
        <p className="pricing-transparency">
          Puedes añadir o pausar sucursales según las necesidades de tu negocio.
          <br />
          Conoce el total antes de confirmar cualquier cambio.
        </p>
      </div>
    </section>
  );
}
