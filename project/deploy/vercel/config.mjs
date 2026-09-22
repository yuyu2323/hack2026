export function deploymentConfig(value) {
  let url;
  try { url = new URL(value); } catch { /* 아래에서 동일한 안내로 처리 */ }
  if (!url || url.protocol !== 'https:' || url.username || url.password ||
      url.pathname !== '/' || url.search || url.hash ||
      url.hostname === 'localhost' || url.hostname.endsWith('.localhost') ||
      url.hostname === '127.0.0.1' || url.hostname === '[::1]') {
    throw new Error('BACKEND_ORIGIN에 공개 HTTPS origin을 설정하세요. 경로·인증정보·쿼리·localhost는 사용할 수 없습니다.');
  }
  return {
    version: 3,
    routes: [
      {
        src: '^(/api(?:/.*)?)$',
        dest: `${url.origin}$1`,
        headers: {
          'Cache-Control': 'no-store',
          'CDN-Cache-Control': 'no-store',
          'Vercel-CDN-Cache-Control': 'no-store',
        },
      },
      { handle: 'filesystem' },
      { src: '^/assets/.*$', status: 404 },
      { src: '^/.*$', dest: '/index.html', methods: ['GET', 'HEAD'] },
    ],
  };
}
