import Link from 'next/link';
import '../login/acceso.css';

export default function ConfiguracionInicial() {
  return (
    <main id="contenido" className="acceso-formulario">
      <Link className="brand" href="/">
        Turno Group
      </Link>
      <h1>Configuración inicial</h1>
      <p>
        Tu cuenta y la sucursal principal ya fueron creadas. En los siguientes avances
        podrás completar categorías, productos, servicios y métodos de pago.
      </p>
      <Link className="button button-primary" href="/login">
        Ir a iniciar sesión
      </Link>
    </main>
  );
}
