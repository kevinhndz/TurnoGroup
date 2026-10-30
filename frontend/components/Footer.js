import ActionButton from './ActionButton';

export default function Footer() {
  return (
    <footer className="site-footer" id="contacto">
      <div className="container">
        <div className="footer-top">
          <div className="footer-brand">
            <a className="brand" href="#inicio">
              Turno Group
              <span className="brand-dot" />
            </a>
            <p>
              Gestión presencial para restaurantes, cafeterías y los equipos que les dan
              vida.
            </p>
          </div>
          <div className="footer-links">
            <div>
              <p className="eyebrow">Conoce Turno Group</p>
              <a href="#funciones">Funciones</a>
              <a href="#precios">Precios</a>
              <ActionButton intent="contacto" className="footer-link">
                Contacto
              </ActionButton>
            </div>
            <div>
              <p className="eyebrow">Lo que debes saber</p>
              <ActionButton intent="terminos" className="footer-link">
                Términos de servicio
              </ActionButton>
              <ActionButton intent="privacidad" className="footer-link">
                Política de privacidad
              </ActionButton>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} Turno Group</span>
          <span>
            Diseñado para el servicio real.
            <span className="dot" />
          </span>
        </div>
      </div>
    </footer>
  );
}
