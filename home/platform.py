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
    script = r'''const CACHE = 'shopiva-shell-v2';
const SHELL = ['/', '/products/', '/categories/', '/install/'];
const BOOT_TIMEOUT_MS = 800;

function isSameOrigin(url) {
  return url.origin === self.location.origin;
}

function isPublicShell(url) {
  return url.origin === self.location.origin && SHELL.includes(url.pathname);
}

function bootPage(targetUrl) {
  const safeTarget = JSON.stringify(targetUrl);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Shopiva Kenya</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;width:100%;height:100%;overflow:hidden}
body{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:radial-gradient(circle at 50% 20%,#e8f1ff 0,#f7f9fc 42%,#eef3f8 100%);color:#111827;display:grid;place-items:center}
.shell{width:min(92vw,520px);text-align:center;padding:34px 24px}
.orb{width:74px;height:74px;margin:0 auto 20px;border-radius:24px;background:linear-gradient(135deg,#2563eb,#06b6d4);display:grid;place-items:center;color:#fff;font-size:34px;font-weight:950;box-shadow:0 16px 42px rgba(37,99,235,.23);animation:float 1.4s ease-in-out infinite}
h1{margin:0;font-size:30px;letter-spacing:-.05em}
p{margin:9px 0 0;color:#64748b;font-size:13px;line-height:1.55}
.bar{height:5px;width:min(330px,80vw);margin:22px auto 0;border-radius:999px;background:#dbe5f1;overflow:hidden}
.bar i{display:block;width:38%;height:100%;border-radius:999px;background:linear-gradient(90deg,#2563eb,#06b6d4);animation:load 1.15s ease-in-out infinite}
.badge{display:inline-flex;align-items:center;gap:7px;margin-top:14px;padding:7px 10px;border-radius:999px;background:#fff;border:1px solid #dfe7f0;color:#475569;font-size:10px;font-weight:800;box-shadow:0 7px 20px rgba(15,23,42,.06)}
.dot{width:7px;height:7px;border-radius:50%;background:#22c55e;box-shadow:0 0 0 4px rgba(34,197,94,.12)}
small{display:block;margin-top:16px;color:#94a3b8;font-size:10px}
@keyframes load{0%{transform:translateX(-120%)}50%{transform:translateX(90%)}100%{transform:translateX(280%)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
</style>
</head>
<body>
<main class="shell" aria-live="polite">
  <div class="orb">S</div>
  <h1>Shopiva Kenya</h1>
  <p>Waking the Shopiva service and preparing your workspace…</p>
  <div class="bar"><i></i></div>
  <div class="badge"><span class="dot"></span>Secure connection</div>
  <small id="status">Connecting…</small>
</main>
<script>
(function(){
  const target=${safeTarget};
  const status=document.getElementById('status');
  let attempts=0;
  async function load(){
    attempts+=1;
    status.textContent=attempts>1?'Shopiva is taking a little longer. Retrying automatically…':'Connecting…';
    try{
      const join=target.includes('?')?'&':'?';
      const url=target+join+'_shopiva_boot=1';
      const response=await fetch(url,{credentials:'same-origin',cache:'no-store',redirect:'follow'});
      if(!response.ok) throw new Error('HTTP '+response.status);
      const html=await response.text();
      document.open();
      document.write(html);
      document.close();
    }catch(err){
      setTimeout(load,2000);
    }
  }
  load();
})();
</script>
</body>
</html>`;
}

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (!isSameOrigin(url)) return;

  if (request.mode === 'navigate') {
    if (url.searchParams.has('_shopiva_boot')) {
      event.respondWith(fetch(request));
      return;
    }

    event.respondWith((async () => {
      const network = fetch(request).then(response => {
        if (response.ok && isPublicShell(url)) {
          const clone = response.clone();
          caches.open(CACHE).then(cache => cache.put(url.pathname + url.search, clone)).catch(() => {});
        }
        return response;
      });

      const timeout = new Promise(resolve => setTimeout(() => resolve(null), BOOT_TIMEOUT_MS));
      const first = await Promise.race([network, timeout]);
      if (first) return first;

      return new Response(bootPage(url.href), {
        status: 200,
        headers: {'Content-Type': 'text/html; charset=UTF-8', 'Cache-Control': 'no-store'}
      });
    })());
    return;
  }

  if (isPublicShell(url)) {
    event.respondWith(
      caches.match(request).then(cached => {
        const fresh = fetch(request).then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE).then(cache => cache.put(request, clone)).catch(() => {});
          }
          return response;
        }).catch(() => cached || Response.error());
        return cached || fresh;
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
