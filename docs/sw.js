// 璧山好房 · Service Worker
// 离线缓存 + PWA 支持

const CACHE_NAME = 'bishanhaofang-v1';
const STATIC_ASSETS = [
  '/',
  '/web/index.html',
  '/web/results.html',
  '/web/map.html',
  '/web/detail.html',
  '/web/guides.html',
  '/web/guide-detail.html',
  '/web/css/base.css',
  '/web/css/mobile.css',
  '/web/css/desktop.css',
  '/web/js/app.js',
  '/web/js/voice-input.js',
  '/web/js/ai-match.js',
  '/web/js/map-view.js',
  '/web/js/lead-capture.js',
  '/web/js/deepseek-api.js',
  '/web/js/admin.js',
  '/web/manifest.json'
];

// 安装：预缓存静态资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] 缓存静态资源');
      return cache.addAll(STATIC_ASSETS);
    })
  );
});

// 激活：清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
});

// 请求拦截：缓存优先，网络兜底
self.addEventListener('fetch', (event) => {
  // JSON 数据文件走网络优先
  if (event.request.url.includes('/shared/')) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const cloned = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, cloned));
          return response;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // 静态资源走缓存优先
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request).then((response) => {
        const cloned = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, cloned));
        return response;
      });
    })
  );
});
