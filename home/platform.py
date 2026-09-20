from django.http import HttpResponse, JsonResponse
from django.shortcuts import render



def shopiva_app_icon(request):
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-labelledby="title desc">
<title id="title">Shopiva Kenya LTD</title><desc id="desc">Shopiva Kenya LTD shopping app icon.</desc>
<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#073d2b"/><stop offset=".55" stop-color="#011711"/><stop offset="1" stop-color="#0a4a2b"/></linearGradient><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e1ff69"/><stop offset=".45" stop-color="#35ea6c"/><stop offset="1" stop-color="#00a35d"/></linearGradient><linearGradient id="y" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff7b0"/><stop offset=".45" stop-color="#ffd34f"/><stop offset="1" stop-color="#d88c0b"/></linearGradient></defs>
<rect x="10" y="10" width="492" height="492" rx="112" fill="url(#b)" stroke="#35ea6c" stroke-width="8"/>
<path d="M256 46l18 42 42-28-10 46 46 7-40 26 30 35-47-12-10 48-29-37-29 37-10-48-47 12 30-35-40-26 46-7-10-46 42 28z" fill="url(#y)"/>
<path d="M330 150c-22-29-54-43-93-43-55 0-91 25-91 65 0 48 34 61 92 74 35 8 44 14 44 28 0 13-15 22-38 22-34 0-57-13-79-37l-37 32c29 38 69 56 118 56 59 0 101-28 101-74 0-49-34-65-91-78-36-8-46-14-46-27 0-12 13-20 36-20 29 0 50 9 71 30z" fill="#fff"/>
<path d="M111 187h48l-18 22h-43l-10-22h23zm-17 34h54l-17 22H84l-11-22h21zm23 34h45l-18 22H107l-9-22h19z" fill="url(#g)"/>
<path d="M144 331c31 24 68 35 112 35 48 0 84-13 108-37-13 46-54 77-110 77-57 0-102-26-127-68z" fill="url(#g)"/>
<circle cx="205" cy="358" r="14" fill="url(#y)"/><circle cx="325" cy="358" r="14" fill="url(#y)"/>
<text x="256" y="424" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="68" font-weight="900" fill="#fff">Shop<tspan fill="url(#g)">iva</tspan></text>
<text x="256" y="463" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" letter-spacing="6" fill="#ffe58a">KENYA LTD</text>
</svg>"""
    return HttpResponse(svg, content_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})

def app_install(request):
    return render(request, "platform/install.html")


def app_manifest(request):
    manifest = {
        "name": "Shopiva Kenya LTD",
        "short_name": "Shopiva",
        "id": "/",
        "start_url": "/?source=pwa",
        "scope": "/",
        "display": "standalone",
        "background_color": "#052e1b",
        "theme_color": "#13c66a",
        "description": "Shopiva Kenya LTD — smart shopping, secure checkout and delivery tracking.",
        "icons": [
            {
                "src": "/static/shopiva/shopiva-customer-icon.webp",
                "sizes": "256x256",
                "type": "image/webp",
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
    script = r'''const CACHE = 'shopiva-static-v7';
const STATIC_PREFIX = '/static/';

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => Promise.all([
    cache.add('/static/shopiva/shopiva-shopping-logo.svg').catch(() => {}),
    cache.add('/static/shopiva/shopiva-customer-icon.webp').catch(() => {})
  ])).then(() => self.skipWaiting()));
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
