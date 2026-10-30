import "./globals.css";

export const metadata = { title: "Turno Group", description: "Gestion de restaurantes y cafeterias." };

export default function RootLayout({ children }) {
  return <html lang="es"><body>{children}</body></html>;
}
