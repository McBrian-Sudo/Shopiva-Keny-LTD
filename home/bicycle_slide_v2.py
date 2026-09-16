from django.http import HttpResponse
from .views import home as base_home
from .bicycle_home_enhancement import BIKE_1, BIKE_2, BIKE_3


BIKE_SLIDE_V2 = f'''
<style>
.shopiva-bike-v2{{position:relative;isolation:isolate;overflow:hidden;background:#071a2d;color:#fff;border-radius:24px}}
.shopiva-bike-v2 .slide-photo{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0;filter:saturate(1.05) contrast(1.04)}}
.shopiva-bike-v2::after{{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(2,12,24,.88) 0%,rgba(2,15,29,.72) 42%,rgba(2,15,29,.36) 67%,rgba(2,15,29,.58) 100%);z-index:1}}
.shopiva-bike-v2 .v2-content{{position:relative;z-index:2;height:100%;display:grid;grid-template-columns:minmax(0,1fr) 520px;gap:30px;align-items:center;padding:46px 52px 70px}}
.shopiva-bike-v2 .v2-copy{{max-width:680px}}
.shopiva-bike-v2 .v2-eyebrow{{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border:1px solid rgba(255,255,255,.18);border-radius:999px;background:rgba(255,255,255,.08);font-size:10px;font-weight:1000;letter-spacing:.13em;text-transform:uppercase}}
.shopiva-bike-v2 .v2-dot{{width:8px;height:8px;border-radius:50%;background:#19d978;box-shadow:0 0 0 6px rgba(25,217,120,.12)}}
.shopiva-bike-v2 h1{{font-size:clamp(42px,5vw,72px);line-height:.92;letter-spacing:-.07em;margin:17px 0 14px}}
.shopiva-bike-v2 h1 span{{color:#19d978}}
.shopiva-bike-v2 .v2-copy p{{max-width:650px;color:rgba(255,255,255,.82);font-size:15px;line-height:1.65}}
.shopiva-bike-v2 .v2-actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}}
.shopiva-bike-v2 .v2-btn{{display:inline-flex;align-items:center;justify-content:center;padding:13px 17px;border-radius:11px;font-size:10px;font-weight:1000}}
.shopiva-bike-v2 .v2-white{{background:#fff;color:#061a2f}}
.shopiva-bike-v2 .v2-green{{background:#19d978;color:#052111}}
.shopiva-bike-v2 .v2-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.18);padding:12px;border-radius:22px;backdrop-filter:blur(12px);box-shadow:0 30px 80px rgba(0,0,0,.28)}}
.shopiva-bike-v2 .v2-card{{min-width:0;background:#13263a;border:1px solid rgba(255,255,255,.16);border-radius:16px;overflow:hidden;box-shadow:0 14px 30px rgba(0,0,0,.2)}}
.shopiva-bike-v2 .v2-card img{{display:block;width:100%;height:205px;object-fit:cover;background:#eef3f5}}
.shopiva-bike-v2 .v2-card-body{{padding:10px 10px 12px}}
.shopiva-bike-v2 .v2-card-body b{{display:block;font-size:11px}}
.shopiva-bike-v2 .v2-card-body small{{display:block;margin-top:3px;color:rgba(255,255,255,.62);font-size:8px;line-height:1.35}}
.shopiva-bike-v2 .v2-card:first-child img{{object-position:center}}
.shopiva-bike-v2 .v2-card:nth-child(2) img{{object-position:center}}
.shopiva-bike-v2 .v2-card:nth-child(3) img{{object-position:center}}
@media(max-width:1050px){{.shopiva-bike-v2 .v2-content{{grid-template-columns:1fr 430px;gap:20px;padding-left:34px;padding-right:34px}}.shopiva-bike-v2 .v2-card img{{height:175px}}}}
@media(max-width:780px){{.shopiva-bike-v2 .v2-content{{grid-template-columns:1fr;align-items:end;padding:28px 22px 72px}}.shopiva-bike-v2 .v2-copy{{max-width:100%}}.shopiva-bike-v2 h1{{font-size:44px}}.shopiva-bike-v2 .v2-grid{{max-width:100%}}.shopiva-bike-v2 .v2-card img{{height:145px}}}}
@media(max-width:520px){{.shopiva-bike-v2 .v2-grid{{grid-template-columns:1fr}}.shopiva-bike-v2 .v2-card{{display:grid;grid-template-columns:110px 1fr;align-items:stretch}}.shopiva-bike-v2 .v2-card img{{height:100%;min-height:105px}}}}
</style>
<div class="slide shopiva-bike-v2" data-v2-bike="1">
  <img class="slide-photo" src="{BIKE_2}" alt="Full bicycle hub product image" loading="eager">
  <div class="v2-content">
    <div class="v2-copy">
      <span class="v2-eyebrow"><i class="v2-dot"></i> BICYCLE SPARES · SHOPIVA</span>
      <h1>Ride Strong.<br><span>Build Better.</span></h1>
      <p>Quality bicycle spares for repairs, upgrades and custom builds — with the hub, cassette and cycling components you need in one place.</p>
      <div class="v2-actions"><a class="v2-btn v2-white" href="/products/?q=bicycle">Shop bicycle spares →</a><a class="v2-btn v2-green" href="/products/?q=bicycle+spares">Browse all parts</a></div>
    </div>
    <div class="v2-grid" aria-label="Bicycle spare parts">
      <article class="v2-card"><img src="{BIKE_1}" alt="Bicycle cassette and sprocket"><div class="v2-card-body"><b>Cassette</b><small>Multi-speed sprockets</small></div></article>
      <article class="v2-card"><img src="{BIKE_2}" alt="Bicycle freehub and hub"><div class="v2-card-body"><b>Freehub</b><small>Hub and drivetrain parts</small></div></article>
      <article class="v2-card"><img src="{BIKE_3}" alt="Bicycle hub component"><div class="v2-card-body"><b>Hub</b><small>Wheel-building essentials</small></div></article>
    </div>
  </div>
</div>
'''


def bicycle_home_v2(request):
    response = base_home(request)
    try:
        html = response.content.decode(response.charset or "utf-8")
    except Exception:
        return response

    cleanup = '''
<script>
(function(){
  const root=document.querySelector('.hero');
  if(!root) return;
  // Remove prior Bicycle Spares slides/cards so only the redesigned slide remains.
  root.querySelectorAll('.slide').forEach(function(slide){
    const text=(slide.textContent||'').toUpperCase();
    if(text.includes('BICYCLE SPARES') || text.includes('RIDE STRONG')) slide.remove();
  });
  root.insertAdjacentHTML('afterbegin', `__BIKE_SLIDE__`);
  const dots=root.querySelector('.dots');
  if(dots){
    dots.innerHTML='';
    const slides=root.querySelectorAll('.slide');
    slides.forEach(function(_,i){
      const d=document.createElement('button');
      d.className='dot'+(i===0?' active':'');
      d.type='button'; d.dataset.slide=String(i);
      d.setAttribute('aria-label','Go to slide '+(i+1));
      dots.appendChild(d);
    });
  }
})();
</script>
'''.replace('__BIKE_SLIDE__', BIKE_SLIDE_V2.replace('`','\\`'))
    html = html.replace('</body>', cleanup + '\n</body>', 1)
    return HttpResponse(html, status=response.status_code, content_type=response.get('Content-Type', 'text/html'))
