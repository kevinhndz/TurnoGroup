import Icon from './Icon';

const features = [
  { icon: 'receipt', title: 'Cada pedido, en su lugar.', text: 'Registra pedidos en sala o mostrador y consulta su estado e historial sin perder el hilo del servicio.', tag: 'Pedidos', className: 'feature-main' },
  { icon: 'book', title: 'Una carta a tu medida.', text: 'Organiza productos, categorías, fotos y complementos para que tu equipo encuentre todo a la primera.', tag: 'Tu catálogo' },
  { icon: 'store', title: 'Un negocio. Varias sucursales.', text: 'Mantén cada local organizado y consulta tus sucursales desde una misma cuenta empresarial.', tag: 'Sucursales' },
  { icon: 'team', title: 'El equipo conectado.', text: 'Invita a tus empleados y asigna a cada persona las sucursales y los permisos que necesita.', tag: 'Personas y roles' },
  { icon: 'table', title: 'Un sitio para cada cliente.', text: 'Activa mesas y reservas si las utilizas, o trabaja solo con pedidos para llevar. Tú eliges.', tag: 'Mesas y reservas' },
  { icon: 'money', title: 'Tus reglas, tus cuentas.', text: 'Configura la moneda, los impuestos y los descuentos que aplica tu empresa al registrar pedidos.', tag: 'Pagos y ajustes' },
  { icon: 'upload', title: 'Tu menú, listo para empezar.', text: 'Importa tus productos desde un archivo CSV o Excel y ahorra tiempo al preparar tu catálogo inicial.', tag: 'Importación', className: 'feature-import' },
];

export default function Features() {
  return <section id="funciones" className="section features" aria-labelledby="features-title"><div className="container">
    <div className="section-intro"><p className="eyebrow">Herramientas para el día a día</p><h2 id="features-title">Todo lo que tu equipo necesita.<br />Justo donde lo necesita.</h2><p>Del primer café al último pedido. Un espacio para coordinar tu salón, tu carta y a las personas que hacen que todo funcione.</p></div>
    <div className="features-grid">{features.map((feature, index) => <article className={`feature-card ${feature.className || ''}`} key={feature.tag}>
      <div className="feature-content"><div className={`feature-icon ${index % 3 === 1 ? 'sage-icon' : ''}`}><Icon name={feature.icon} size={22} /></div><p className="feature-tag">{feature.tag}</p><h3>{feature.title}</h3><p className="feature-description">{feature.text}</p></div>
      {index === 0 && <div className="mini-orders" aria-label="Ejemplo de seguimiento de pedidos"><div className="mini-order-title"><span>Pedidos del turno</span><span className="mini-count">03</span></div><div><span><i className="order-dot" />Mesa 04</span><span className="status-pill">Abierto</span></div><div><span><i className="order-dot" />Para llevar</span><span className="status-pill">Abierto</span></div><div><span><i className="order-dot closed" />Mesa 02</span><span className="closed-label">Cerrado <Icon name="check" size={11} /></span></div><p>El servicio sigue. Todo queda registrado.</p></div>}
      {index === 6 && <div className="import-file"><Icon name="upload" size={22} /><div><strong>mi-menu.xlsx</strong><span>Tu carta comienza aquí</span></div><span className="file-extension">XLSX</span></div>}
    </article>)}</div>
    <p className="features-note"><span className="dot" /> Activa solo las opciones que tu negocio utiliza.</p>
  </div></section>;
}
