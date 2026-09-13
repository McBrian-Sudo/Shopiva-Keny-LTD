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
            {"src": "/static/shopiva/shopiva-shopping-logo.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}
        ],
    }
    return JsonResponse(manifest)


def service_worker(request):
    script = r'''const CACHE = 'shopiva-shell-v3';
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
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#052e1b"><title>Shopiva Kenya LTD</title><style>*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden}body{font-family:Inter,system-ui,sans-serif;background:radial-gradient(circle at 70% 10%,#1b9b5a 0,#07351f 35%,#02120a 100%);color:#fff;display:grid;place-items:center}.shell{width:min(92vw,520px);text-align:center;padding:34px 24px}.logo{width:92px;height:92px;margin:0 auto 18px;border-radius:26px;box-shadow:0 18px 48px rgba(0,0,0,.32)}h1{margin:0;font-size:31px;letter-spacing:-.05em}p{margin:9px 0 0;color:#c7e8d5;font-size:13px;line-height:1.55}.bar{height:5px;width:min(330px,80vw);margin:22px auto 0;border-radius:999px;background:rgba(255,255,255,.14);overflow:hidden}.bar i{display:block;width:40%;height:100%;border-radius:999px;background:linear-gradient(90deg,#13c66a,#f5c84c);animation:load 1.15s ease-in-out infinite}.badge{display:inline-flex;align-items:center;gap:7px;margin-top:14px;padding:7px 10px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);color:#d7eee0;font-size:10px;font-weight:800}.dot{width:7px;height:7px;border-radius:50%;background:#51ee8f;box-shadow:0 0 0 4px rgba(81,238,143,.12)}small{display:block;margin-top:16px;color:#8fb7a1;font-size:10px}@keyframes load{0%{transform:translateX(-120%)}50%{transform:translateX(90%)}100%{transform:translateX(280%)}}</style></head><body><main class="shell" aria-live="polite"><img class="logo" src="/static/shopiva/shopiva-shopping-logo.svg" alt="Shopiva Kenya LTD"><h1>Shopiva Kenya LTD</h1><p>Opening your smart shopping experience…</p><div class="bar"><i></i></div><div class="badge"><span class="dot"></span>Secure connection</div><small id="status">Connecting…</small></main><script>(function(){const target=${safeTarget},status=document.getElementById('status');let attempts=0;async function load(){attempts+=1;status.textContent=attempts>1?'Shopiva is taking a little longer. Retrying automatically…':'Connecting…';try{const join=target.includes('?')?'&':'?';const response=await fetch(target+join+'_shopiva_boot=1',{credentials:'same-origin',cache:'no-store',redirect:'follow'});if(!response.ok)throw new Error('HTTP '+response.status);const html=await response.text();document.open();document.write(html);document.close()}catch(err){setTimeout(load,2000)}}load()})();</script></body></html>`;
}

self.addEventListener('install', event => { event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)).catch(() => {})); self.skipWaiting(); });
self.addEventListener('activate', event => { event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))); self.clients.claim(); });
self.addEventListener('fetch', event => { const request=event.request; if(request.method!=='GET')return; const url=new URL(request.url); if(!isSameOrigin(url))return; if(request.mode==='navigate'){ if(url.searchParams.has('_shopiva_boot')){event.respondWith(fetch(request));return} event.respondWith((async()=>{const network=fetch(request).then(response=>{if(response.ok&&isPublicShell(url)){const clone=response.clone();caches.open(CACHE).then(cache=>cache.put(url.pathname+url.search,clone)).catch(()=>{})}return response});const timeout=new Promise(resolve=>setTimeout(()=>resolve(null),BOOT_TIMEOUT_MS));const first=await Promise.race([network,timeout]);if(first)return first;return new Response(bootPage(url.href),{status:200,headers:{'Content-Type':'text/html; charset=UTF-8','Cache-Control':'no-store'}})})());return} if(isPublicShell(url)){event.respondWith(caches.match(request).then(cached=>{const fresh=fetch(request).then(response=>{if(response.ok){const clone=response.clone();caches.open(CACHE).then(cache=>cache.put(request,clone)).catch(()=>{})}return response}).catch(()=>cached||Response.error());return cached||fresh}))}});
'''
    return HttpResponse(script, content_type="application/javascript", headers={"Cache-Control": "no-store, max-age=0"})