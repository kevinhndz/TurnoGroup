import './globals.css';
import './sistema.css';
import { ProveedorSesion } from '../components/sistema/Sesion';

export const metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
  title: 'Turno Group | Pedidos y sucursales en orden',
  description:
    'Organiza los pedidos, el catálogo y las sucursales de tu restaurante o cafetería con Turno Group. Empieza con un mes de prueba gratis.',
  applicationName: 'Turno Group',
  openGraph: {
    title: 'Turno Group | Más tiempo para tus clientes',
    description:
      'Pedidos, sucursales y equipo en un solo lugar. Gestión presencial para restaurantes y cafeterías.',
    siteName: 'Turno Group',
    locale: 'es_HN',
    type: 'website',
    images: [
      {
        url: '/images/cafe-turno.webp',
        width: 1024,
        height: 576,
        alt: 'Turno Group en una cafetería',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Turno Group | Pedidos y sucursales en orden',
    description: 'Un espacio para organizar tu restaurante o cafetería.',
    images: ['/images/cafe-turno.webp'],
  },
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#fcf9f4',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es" data-scroll-behavior="smooth">
      <body>
        <a className="skip-link" href="#contenido">
          Saltar al contenido
        </a>
        <ProveedorSesion>{children}</ProveedorSesion>
      </body>
    </html>
  );
}
