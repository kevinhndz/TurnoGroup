'use client';
import { useId } from 'react';
import { dinero } from '../../lib/api';

function puntos(valores, maximo) {
  const max = maximo || Math.max(1, ...valores);
  return valores.map((valor, i) => [
    valores.length === 1 ? 180 : 12 + (i / (valores.length - 1)) * 336,
    138 - (valor / max) * 126,
  ]);
}

export function CurvaVentas({ series, moneda }) {
  const id = useId().replace(/:/g, '');
  const coords = puntos(series.map((item) => Number(item.ventas)));
  const linea = coords.map((p) => p.join(',')).join(' ');
  return (
    <svg
      viewBox="0 0 360 170"
      className="tg-finance-line"
      role="img"
      aria-label="Evolución de los cobros del periodo"
    >
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#25a46b" stopOpacity=".22" />
          <stop offset="100%" stopColor="#25a46b" stopOpacity="0" />
        </linearGradient>
      </defs>
      {[35, 75, 115].map((y) => (
        <line key={y} x1="12" x2="348" y1={y} y2={y} stroke="#e9e5dd" />
      ))}
      {coords.length > 1 && (
        <polygon points={`12,150 ${linea} 348,150`} fill={`url(#${id})`} />
      )}
      <polyline
        points={linea}
        fill="none"
        stroke="#25a46b"
        strokeWidth="3"
        strokeLinejoin="round"
      />
      {coords.map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r={series.length > 45 ? 1.5 : 3} fill="#25a46b">
          <title>
            {series[i].periodo}: {dinero(series[i].ventas, moneda)}
          </title>
        </circle>
      ))}
      <text x="12" y="168" fontSize="10" fill="#82776a">
        {series[0]?.periodo}
      </text>
      <text x="348" y="168" textAnchor="end" fontSize="10" fill="#82776a">
        {series.at(-1)?.periodo}
      </text>
    </svg>
  );
}

export function HorasPedidos({ horas }) {
  const max = Math.max(1, ...horas.actual, ...horas.anterior);
  return (
    <svg
      viewBox="0 0 360 170"
      className="tg-finance-line"
      role="img"
      aria-label="Pedidos cobrados por hora: periodo actual y anterior"
    >
      {[35, 75, 115].map((y) => (
        <line key={y} x1="12" x2="348" y1={y} y2={y} stroke="#e9e5dd" />
      ))}
      {['anterior', 'actual'].map((clave, i) => (
        <g key={clave}>
          <polyline
            points={puntos(horas[clave], max)
              .map((p) => p.join(','))
              .join(' ')}
            stroke={i ? '#ff8a22' : '#8b3dff'}
            fill="none"
            strokeWidth="2.5"
            strokeLinejoin="round"
          />
          {puntos(horas[clave], max).map(([x, y], hora) => (
            <circle key={hora} cx={x} cy={y} r="3" fill={i ? '#ff8a22' : '#8b3dff'}>
              <title>
                {hora}:00 · {horas[clave][hora]} pedidos ·{' '}
                {clave === 'actual' ? 'Actual' : 'Anterior'}
              </title>
            </circle>
          ))}
        </g>
      ))}
      {[0, 6, 12, 18, 23].map((h) => (
        <text
          key={h}
          x={12 + (h / 23) * 336}
          y="168"
          textAnchor={h === 23 ? 'end' : 'start'}
          fontSize="10"
          fill="#82776a"
        >
          {h}:00
        </text>
      ))}
    </svg>
  );
}

function repartir(items, x, y, ancho, alto) {
  if (!items.length) return [];
  if (items.length === 1) return [{ ...items[0], x, y, ancho, alto }];
  const total = items.reduce((s, item) => s + Number(item.ventas), 0) || items.length;
  let indice = 1,
    parte = Number(items[0].ventas) || (total === items.length ? 1 : 0);
  while (indice < items.length - 1 && parte < total / 2) {
    parte += Number(items[indice].ventas) || (total === items.length ? 1 : 0);
    indice++;
  }
  const p = Math.max(0.08, Math.min(0.92, parte / total));
  return ancho >= alto
    ? [
        ...repartir(items.slice(0, indice), x, y, ancho * p, alto),
        ...repartir(items.slice(indice), x + ancho * p, y, ancho * (1 - p), alto),
      ]
    : [
        ...repartir(items.slice(0, indice), x, y, ancho, alto * p),
        ...repartir(items.slice(indice), x, y + alto * p, ancho, alto * (1 - p)),
      ];
}

export function MapaCategorias({ categorias, moneda }) {
  const id = useId().replace(/:/g, '');
  const colores = ['#ffb800', '#ff6b2b', '#8b3dff', '#8ae65b', '#b7b4ad'];
  const total = categorias.reduce((s, item) => s + Number(item.ventas), 0);
  const items = categorias.slice(0, 9);
  if (categorias.length > 9)
    items.push({
      nombre: 'Otras categorías',
      ventas: categorias.slice(9).reduce((s, item) => s + Number(item.ventas), 0),
    });
  const cuadros = repartir(
    items.map((item, i) => ({ ...item, color: colores[i % colores.length] })),
    0,
    0,
    600,
    300,
  );
  return (
    <svg
      viewBox="0 0 600 300"
      className="tg-finance-map"
      role="img"
      aria-label="Proporción de ventas cobradas por categoría"
    >
      {cuadros.map((item, i) => (
        <g key={item.nombre}>
          <defs>
            <clipPath id={`${id}-${i}`}>
              <rect
                x={item.x + 12}
                y={item.y + 5}
                width={Math.max(0, item.ancho - 24)}
                height={Math.max(0, item.alto - 10)}
              />
            </clipPath>
          </defs>
          <rect
            x={item.x + 3}
            y={item.y + 3}
            width={Math.max(0, item.ancho - 6)}
            height={Math.max(0, item.alto - 6)}
            rx="14"
            fill={item.color}
          >
            <title>
              {item.nombre}: {dinero(item.ventas, moneda)} ·{' '}
              {total ? ((Number(item.ventas) / total) * 100).toFixed(1) : 0}%
            </title>
          </rect>
          <g
            clipPath={`url(#${id}-${i})`}
            fill={item.color === '#8b3dff' ? 'white' : '#25221a'}
          >
            <text
              x={item.x + 16}
              y={item.y + (item.alto < 90 ? 22 : 28)}
              fontSize={item.alto < 90 ? '11' : '13'}
              fontWeight="700"
            >
              {item.nombre}
            </text>
            <text
              x={item.x + 16}
              y={item.y + item.alto - (item.alto < 90 ? 14 : 33)}
              fontSize={item.alto < 90 ? '16' : item.ancho > 180 ? '25' : '19'}
              fontWeight="600"
            >
              {dinero(item.ventas, moneda)}
            </text>
            {item.alto >= 90 && (
              <text x={item.x + 16} y={item.y + item.alto - 14} fontSize="11">
                {total ? ((Number(item.ventas) / total) * 100).toFixed(1) : 0}% del total
              </text>
            )}
          </g>
        </g>
      ))}
    </svg>
  );
}

export function RadarVentas({ valores, moneda }) {
  const meses = [
    'Ene',
    'Feb',
    'Mar',
    'Abr',
    'May',
    'Jun',
    'Jul',
    'Ago',
    'Sep',
    'Oct',
    'Nov',
    'Dic',
  ];
  const max = Math.max(1, ...valores.map(Number));
  const punto = (i, r) => [
    200 + Math.sin((i * Math.PI) / 6) * r,
    190 - Math.cos((i * Math.PI) / 6) * r,
  ];
  const coords = valores.map((v, i) => punto(i, (Number(v) / max) * 132));
  return (
    <svg
      viewBox="0 0 400 380"
      className="tg-finance-radar"
      role="img"
      aria-label="Ventas de enero a diciembre"
    >
      {[33, 66, 99, 132].map((r) => (
        <circle key={r} cx="200" cy="190" r={r} stroke="#e9e5dd" fill="none" />
      ))}
      {meses.map((mes, i) => {
        const p = punto(i, 132),
          t = punto(i, 157);
        return (
          <g key={mes}>
            <line x1="200" y1="190" x2={p[0]} y2={p[1]} stroke="#e9e5dd" />
            <text x={t[0]} y={t[1] + 4} textAnchor="middle" fill="#847968" fontSize="12">
              {mes}
            </text>
          </g>
        );
      })}
      <polygon
        points={coords.map((p) => p.join(',')).join(' ')}
        fill="#ffb80024"
        stroke="#e9a419"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />
      {coords.map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="4" fill="#e9a419">
          <title>
            {meses[i]}: {dinero(valores[i], moneda)}
          </title>
        </circle>
      ))}
      {valores.every((v) => Number(v) === 0) && (
        <text x="200" y="195" textAnchor="middle" fontSize="13" fill="#847968">
          Sin cobros en este año
        </text>
      )}
    </svg>
  );
}
