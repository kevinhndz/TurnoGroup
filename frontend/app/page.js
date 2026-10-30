import Header from '../components/Header';
import Hero from '../components/Hero';
import Features from '../components/Features';
import Pricing from '../components/Pricing';
import CallToAction from '../components/CallToAction';
import Footer from '../components/Footer';
export default function Home() {
  return (
    <>
      <Header />
      <div id="inicio" />
      <main id="contenido" tabIndex={-1}>
        <Hero />
        <Features />
        <Pricing />
        <CallToAction />
      </main>
      <Footer />
    </>
  );
}
