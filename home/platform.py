from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


def app_install(request):
    return render(request, "platform/install.html")


def app_manifest(request):
    manifest = {
        "name": "Shopiva Kenya LTD",
        "short_name": "Shopiva",
        "start_url": "/?source=pwa",
        "scope": "/",
        "display": "standalone",
        "background_color": "#052e1b",
        "theme_color": "#13c66a",
        "description": "Shopiva Kenya LTD — smart shopping, secure checkout and delivery tracking.",
        "icons": [
            {
                "src": "/static/shopiva/shopiva-shopping-logo.svg",
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any maskable",
            }
        ],
    }
    return JsonResponse(manifest)


def service_worker(request):
    """Return a safe service worker that never hijacks page navigation."""
    script = r'''const CACHE = 'shopiva-static-v6';
const STATIC_PREFIX = '/static/';

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.add('/static/shopiva/shopiva-shopping-logo.svg').catch(() => {})).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(key => key !== CACHE).map(key => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // Never intercept navigations or HTML documents. Django/Render must answer
  // directly so the customer cannot get trapped on a synthetic boot screen.
  if (request.mode === 'navigate' || request.destination === 'document') return;

  // Static assets can be cached safely without affecting application routes.
  if (url.pathname.startsWith(STATIC_PREFIX)) {
    event.respondWith(
      caches.match(request).then(cached => {
        const network = fetch(request).then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE).then(cache => cache.put(request, clone)).catch(() => {});
          }
          return response;
        }).catch(() => cached || Response.error());

        return cached || network;
      })
    );
  }
});
'''
    return HttpResponse(
        script,
        content_type="application/javascript",
        headers={"Cache-Control": "no-store, max-age=0"},
    )
