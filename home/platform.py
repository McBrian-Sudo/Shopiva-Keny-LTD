from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


def app_install(request):
    return render(request, "platform/install.html")


def app_manifest(request):
    manifest = {
        "name": "Shopiva Kenya",
        "short_name": "Shopiva",
        "start_url": "/?source=pwa",
        "scope": "/",
        "display": "standalone",
        "background_color": "#f5f7fb",
        "theme_color": "#2563eb",
        "description": "Shopiva Kenya — modern shopping for customers across Kenya.",
        "icons": [
            {"src": "/static/shopiva/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}
        ],
    }
    return JsonResponse(manifest)


def service_worker(request):
    script = """const CACHE = 'shopiva-shell-v1';\nconst SHELL = ['/', '/products/', '/categories/', '/install/'];\n\nself.addEventListener('install', event => {\n  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)));\n  self.skipWaiting();\n});\n\nself.addEventListener('activate', event => {\n  event.waitUntil(self.clients.claim());\n});\n\nself.addEventListener('fetch', event => {\n  if (event.request.method !== 'GET') return;\n  event.respondWith(\n    caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {\n      const clone = response.clone();\n      caches.open(CACHE).then(cache => cache.put(event.request, clone));\n      return response;\n    }).catch(() => caches.match('/')))\n  );\n});\n"""
    return HttpResponse(script, content_type="application/javascript")
