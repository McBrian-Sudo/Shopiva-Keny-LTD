from django.http import JsonResponse, HttpResponse

def delivery_manifest(request):
    return JsonResponse({
        "name": "Shopiva Delivery",
        "short_name": "Shopiva Delivery",
        "start_url": "/delivery/",
        "scope": "/delivery/",
        "display": "standalone",
        "background_color": "#03170e",
        "theme_color": "#0b5b35",
        "description": "Shopiva Kenya secure delivery partner app.",
        "icons": [{"src": "/static/shopiva/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}],
    })

def delivery_service_worker(request):
    return HttpResponse(
        """const CACHE='shopiva-delivery-v1';const SHELL=['/delivery/login/','/delivery/'];self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).catch(()=>{}));self.skipWaiting()});self.addEventListener('activate',e=>{e.waitUntil(self.clients.claim())});self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);if(u.origin!==location.origin||!u.pathname.startsWith('/delivery/'))return;e.respondWith(fetch(e.request).catch(()=>caches.match(e.request).then(r=>r||Response.error())))});""",
        content_type="application/javascript",
        headers={"Cache-Control":"no-store"},
    )
