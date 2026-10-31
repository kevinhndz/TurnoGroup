const nombre = (max = 100, min = 1) => ({
  clave: 'nombre',
  label: 'Nombre',
  required: true,
  minLength: min,
  maxLength: max,
});

export const modulos = {
  categorias: {
    titulo: 'Categorías de productos',
    singular: 'categoría',
    ruta: '/categorias/',
    icono: 'book',
    detalle:
      'Organiza el catálogo de tu empresa. Los productos se agrupan en estas categorías.',
    estado: 'activo',
    campos: [
      nombre(60),
      {
        clave: 'orden_presentacion',
        label: 'Orden de presentación',
        type: 'number',
        min: 0,
        valor: 1,
      },
    ],
    columnas: [
      ['nombre', 'Categoría'],
      ['orden_presentacion', 'Orden'],
    ],
  },
  productos: {
    titulo: 'Productos',
    singular: 'producto',
    ruta: '/productos/',
    icono: 'coffee',
    detalle:
      'Tu catálogo maestro. La disponibilidad y el precio de cada local se administran por separado.',
    estado: 'disponible',
    campos: [
      nombre(),
      {
        clave: 'id_categoria',
        label: 'Categoría',
        type: 'select',
        fuente: 'categorias',
        nullable: true,
      },
      {
        clave: 'descripcion',
        label: 'Descripción',
        type: 'textarea',
        nullable: true,
        maxLength: 2000,
      },
      {
        clave: 'precio',
        label: 'Precio de venta',
        type: 'number',
        min: 0,
        step: '0.01',
        required: true,
      },
    ],
    columnas: [
      ['nombre', 'Producto'],
      ['categoria', 'Categoría'],
      ['precio', 'Precio'],
    ],
  },
  sucursales: {
    titulo: 'Sucursales',
    singular: 'sucursal',
    ruta: '/sucursales/',
    icono: 'store',
    detalle:
      'Los locales de tu empresa. Cada uno conserva su propia configuración de atención y cobro.',
    estado: 'activo',
    campos: [
      nombre(100, 2),
      {
        clave: 'direccion',
        label: 'Dirección',
        required: true,
        minLength: 5,
        maxLength: 255,
      },
      {
        clave: 'telefono',
        label: 'Teléfono de contacto',
        minLength: 8,
        maxLength: 20,
        nullable: true,
        type: 'tel',
      },
      {
        clave: 'es_principal',
        label: 'Sucursal principal',
        type: 'checkbox',
        valor: false,
      },
    ],
    columnas: [
      ['nombre', 'Sucursal'],
      ['direccion', 'Dirección'],
      ['telefono', 'Contacto'],
      ['es_principal', 'Principal'],
    ],
  },
  mesas: {
    titulo: 'Mesas',
    singular: 'mesa',
    ruta: '/mesas/',
    icono: 'table',
    porSucursal: true,
    detalle: 'Administra las mesas físicas y la capacidad del local seleccionado.',
    estado: 'activo',
    campos: [
      nombre(60),
      {
        clave: 'capacidad',
        label: 'Capacidad de personas',
        type: 'number',
        min: 1,
        step: 1,
        nullable: true,
      },
    ],
    columnas: [
      ['nombre', 'Mesa'],
      ['capacidad', 'Capacidad'],
    ],
  },
  descuentos: {
    titulo: 'Descuentos',
    singular: 'descuento',
    ruta: '/descuentos/',
    icono: 'money',
    detalle:
      'Configura los descuentos que el personal puede aplicar al registrar pedidos.',
    estado: 'activo',
    campos: [
      nombre(),
      {
        clave: 'tipo_descuento',
        label: 'Tipo de descuento',
        type: 'select',
        required: true,
        opciones: [
          ['Porcentaje', 'Porcentaje (%)'],
          ['CantidadFija', 'Cantidad fija'],
        ],
        valor: 'Porcentaje',
      },
      {
        clave: 'valor',
        label: 'Valor',
        type: 'number',
        min: 0,
        step: '0.01',
        required: true,
      },
    ],
    columnas: [
      ['nombre', 'Descuento'],
      ['tipo_descuento', 'Tipo'],
      ['valor', 'Valor'],
    ],
  },
  'categorias-gastos': {
    titulo: 'Categorías de gastos',
    singular: 'categoría de gasto',
    ruta: '/categorias-gastos/',
    icono: 'chart',
    detalle:
      'Deja preparadas las clasificaciones. El registro de gastos y los reportes financieros están pendientes.',
    estado: 'activo',
    campos: [nombre()],
    columnas: [['nombre', 'Categoría']],
  },
};

export const camposEmpresa = [
  nombre(45, 4),
  {
    clave: 'tipo_negocio',
    label: 'Tipo de negocio',
    type: 'select',
    opciones: [
      ['Restaurante', 'Restaurante'],
      ['Cafeteria', 'Cafetería'],
      ['Mercadito', 'Mercadito'],
      ['Otro', 'Otro'],
    ],
    required: true,
    valor: 'Restaurante',
  },
  {
    clave: 'codigo_pais',
    label: 'Código del país',
    minLength: 2,
    maxLength: 5,
    required: true,
    valor: 'HN',
  },
  {
    clave: 'zona_horaria',
    label: 'Zona horaria',
    minLength: 4,
    maxLength: 45,
    required: true,
    valor: 'America/Tegucigalpa',
  },
  {
    clave: 'codigo_moneda',
    label: 'Código de moneda',
    minLength: 2,
    maxLength: 5,
    required: true,
    valor: 'HNL',
  },
];
