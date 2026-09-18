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


def favicon(request):
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
<rect width="256" height="256" rx="56" fill="#061b31"/>
<circle cx="128" cy="128" r="92" fill="#19d978"/>
<path d="M83 103c0-18 17-30 43-30 22 0 39 7 51 21l-18 16c-9-10-19-14-33-14-9 0-15 3-15 8 0 6 6 8 21 12 26 6 48 13 48 38 0 23-20 39-51 39-25 0-46-9-61-27l19-17c12 13 25 19 43 19 12 0 19-4 19-10 0-7-7-9-23-13-24-5-43-13-43-42z" fill="#fff"/>
<circle cx="96" cy="188" r="8" fill="#ffd34f"/><circle cx="160" cy="188" r="8" fill="#ffd34f"/>
</svg>"""
    return HttpResponse(svg, content_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})


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
