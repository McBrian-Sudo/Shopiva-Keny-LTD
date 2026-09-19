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
        "icons": [
            {
                "src": "/static/shopiva/delivery-icon.svg",
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any maskable",
            }
        ],
    })


def delivery_service_worker(request):
    return HttpResponse(
        """self.addEventListener('install',event=>{self.skipWaiting()});
self.addEventListener('activate',event=>{event.waitUntil(self.clients.claim())});
self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET') return;
  const url=new URL(event.request.url);
  if(url.origin!==location.origin || !url.pathname.startsWith('/delivery/')) return;
  event.respondWith(fetch(event.request).catch(()=>new Response(
    '<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><title>Shopiva Delivery offline</title><body style="font-family:system-ui;padding:24px"><h1>Shopiva Delivery</h1><p>Network connection is unavailable. Reconnect to continue.</p></body>',
    {headers:{'Content-Type':'text/html;charset=UTF-8'}}
  )));
});""",
        content_type="application/javascript",
        headers={"Cache-Control": "no-store"},
    )
