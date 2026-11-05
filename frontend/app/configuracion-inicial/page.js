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
      <div className="acceso-resumen" aria-label="Pasos pendientes">
        <p><strong>Cuenta creada</strong><br />Tu acceso de gerente ya está registrado.</p>
        <p><strong>Sucursal principal</strong><br />La dirección inicial quedó guardada.</p>
        <p><strong>Siguiente paso</strong><br />Inicia sesión para continuar con tu negocio.</p>
      </div>
      <Link className="button button-primary" href="/login">
        Ir a iniciar sesión
      </Link>
    </main>
  );
}
