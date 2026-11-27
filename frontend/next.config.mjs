const config = {
  poweredByHeader: false,
  async redirects() {
    if (process.env.NODE_ENV !== 'development') return [];
    const origen = new URL(process.env.PUBLIC_ORIGIN || 'http://localhost:3000');
    // La API local acepta solamente el origen configurado.
    return [
      {
        source: '/:path*',
        missing: [{ type: 'host', value: origen.hostname.replaceAll('.', '\\.') }],
        destination: `${origen.origin}/:path*`,
        permanent: false,
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },
};

export default config;
