from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "home" / "templates" / "home.html"
text = TEMPLATE.read_text(encoding="utf-8")

slides = [
    ("🛍️ SHOPIVA KENYA", "SMART SHOPPING · LOCAL DISCOVERY", "Everything you need.", "One smarter marketplace.", "Discover trusted products, compare your options and order with a shopping experience built for Kenya.", "Shop Products" , "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=2200&q=88", "Customer shopping online"),
    ("✨ DISCOVER MORE", "PRODUCTS · CATEGORIES · SELLERS", "Find your next", "favourite.", "Browse products from Shopiva sellers in one clean digital marketplace.", "Browse Products", "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=2200&q=88", "Modern retail shopping"),
    ("👗 SHOP YOUR STYLE", "FASHION · BEAUTY · LIFESTYLE", "Style that moves", "with you.", "Explore fashion, lifestyle essentials and new finds for every day.", "Shop Fashion", "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=2200&q=88", "Fashion shopping"),
    ("👟 FRESH PICKS", "SHOES · ACCESSORIES · STREET STYLE", "Step into", "something better.", "Find footwear and accessories that match your pace and your budget.", "Shop Footwear", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=2200&q=88", "Sneakers and footwear"),
    ("📱 TECH PICKS", "PHONES · GADGETS · SMART DEVICES", "Power your", "everyday life.", "Discover practical electronics for work, entertainment and everyday life.", "Shop Electronics", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=2200&q=88", "Modern smartphone"),
    ("💻 WORK SMART", "LAPTOPS · COMPUTING · WORKSPACE", "Build your", "better setup.", "Upgrade your workspace with computers, accessories and tools that keep you productive.", "Explore Tech", "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=2200&q=88", "Laptop workspace"),
    ("💄 BEAUTY & CARE", "BEAUTY · SELF CARE · DAILY ESSENTIALS", "Feel good.", "Look your best.", "Shop beauty and self-care essentials for everyday routines and special moments.", "Shop Beauty", "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=2200&q=88", "Beauty products"),
    ("🏠 HOME & LIVING", "HOME · FURNITURE · COMFORT", "Make space for", "better living.", "Refresh your home with practical pieces, useful accessories and everyday comfort.", "Shop Home", "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=2200&q=88", "Modern home interior"),
    ("🥑 EVERYDAY ESSENTIALS", "GROCERIES · HOUSEHOLD · DAILY NEEDS", "Stock up", "with less stress.", "Discover everyday essentials and household products in one convenient marketplace.", "Shop Essentials", "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=2200&q=88", "Fresh groceries"),
    ("⌚ PREMIUM PICKS", "ACCESSORIES · GIFTS · PREMIUM FINDS", "Small details.", "Big difference.", "Find standout accessories and gift-worthy products for yourself or someone special.", "See Premium Picks", "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?auto=format&fit=crop&w=2200&q=88", "Luxury watch"),
    ("🏃 LIVE ACTIVE", "SPORTS · FITNESS · OUTDOORS", "Move more.", "Live stronger.", "Explore fitness, sports and outdoor essentials for active days and weekend adventures.", "Shop Sports", "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=2200&q=88", "Sports and fitness"),
    ("💳 EASY PAYMENTS", "M-PESA · CHECKOUT · ORDER CONFIRMATION", "Pay with", "confidence.", "Use Shopiva checkout to place your order and follow confirmed payment updates without guessing.", "Start Shopping", "https://images.unsplash.com/photo-1556740749-887f6717d7e4?auto=format&fit=crop&w=2200&q=88", "Digital payment and shopping"),
    ("🤝 CUSTOMER SUPPORT", "HELP · ORDERS · DELIVERY QUESTIONS", "Need help?", "Shopiva is here.", "Get support before, during and after your purchase with digital help for orders, delivery and shopping questions.", "Get Help", "https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&w=2200&q=88", "Customer support conversation"),
    ("🚚 DELIVERY UPDATES", "TRACKING · RIDERS · LAST-MILE DELIVERY", "Know where", "your order is.", "Follow your delivery journey and see rider details when live GPS is available.", "Track Orders", "https://images.unsplash.com/photo-1556157382-97eda2d62296?auto=format&fit=crop&w=2200&q=88", "Delivery and logistics"),
    ("↩️ RETURNS & RESOLUTION", "ORDER HELP · ISSUE REPORTING · CUSTOMER CARE", "We listen.", "We help resolve.", "Shopiva is designed to give customers a clear path for order issues and support requests.", "Shop with Confidence", "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=2200&q=88", "Customer service technology"),
    ("🤖 SHOPIVA AI", "AI SHOPPING · VOICE · PRODUCT DISCOVERY", "Ask Shopiva.", "Shop smarter.", "Use the Shopiva AI assistant to search products, compare options and get shopping help in natural language.", "Ask Shopiva AI", "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&w=2200&q=88", "Digital customer assistance"),
]

hero_parts = [
    '<!-- SHOPIVA-HERO-V4 -->',
    '<section class="hero hero-slideshow shopiva-hero-v4" aria-label="Shopiva shopping and customer service highlights">',
    '    <div class="hero-track">',
]
for index, (badge, kicker, heading, emphasis, paragraph, button, image, alt) in enumerate(slides):
    hero_parts.extend([
        f'        <article class="hero-slide{" is-active" if index == 0 else ""}" data-index="{index}">',
        '            <div class="hero-slide-image">',
        f'                <img src="{image}" alt="{alt}" loading="{"eager" if index == 0 else "lazy"}"{" fetchpriority=\"high\"" if index == 0 else ""}>',
        '            </div>',
        '            <div class="hero-overlay"></div>',
        '            <div class="hero-content">',
        f'                <span class="hero-badge">{badge}</span>',
        f'                <div class="hero-kicker">{kicker}</div>',
        f'                <h1>{heading}<br><em>{emphasis}</em></h1>',
        f'                <p>{paragraph}</p>',
        '                <div class="hero-buttons">',
        f'                    <a href="/products/" class="primary-btn">{button} <span>↗</span></a>',
        '                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>',
        '                </div>',
        '            </div>',
        '        </article>',
        '',
    ])
hero_parts.extend([
    '    </div>',
    '    <button class="hero-arrow hero-prev" type="button" aria-label="Previous slide">‹</button>',
    '    <button class="hero-arrow hero-next" type="button" aria-label="Next slide">›</button>',
    '    <div class="hero-dots" aria-label="Slideshow controls">',
])
for index in range(len(slides)):
    hero_parts.append(f'        <button class="hero-dot{" is-active" if index == 0 else ""}" type="button" data-slide="{index}" aria-label="Go to slide {index + 1}"></button>')
hero_parts.extend([
    '    </div>',
    '    <div class="hero-status"><span class="hero-live-dot"></span><strong>LIVE</strong><span class="hero-status-label">Shopiva services & discovery</span></div>',
    '    <div class="hero-progress"><span></span></div>',
    '</section>',
])
new_hero = "\n".join(hero_parts)

pattern = re.compile(r'<!-- SHOPIVA-HERO-V3 -->\s*<section class="hero hero-slideshow shopiva-hero-v2"[\s\S]*?</section>\s*\n\s*<section class="section" id="categories">', re.M)
if not pattern.search(text):
    pattern = re.compile(r'<!-- SHOPIVA-HERO-V4 -->\s*<section class="hero hero-slideshow shopiva-hero-v4"[\s\S]*?</section>\s*\n\s*<section class="section" id="categories">', re.M)
text = pattern.sub(new_hero + '\n<section class="section" id="categories">', text, count=1)

css = r'''
<style id="shopiva-hero-v4-css">
.hero.shopiva-hero-v4{height:540px;margin:24px auto 34px;border-radius:30px;background:#edf2f7;box-shadow:0 24px 70px rgba(16,24,40,.10);position:relative;overflow:hidden;isolation:isolate}
.shopiva-hero-v4 .hero-slide{transition:opacity .65s ease,transform 1.1s ease,visibility .65s;}
.shopiva-hero-v4 .hero-slide-image img{filter:saturate(1.08) contrast(1.01);object-position:center;}
.shopiva-hero-v4 .hero-overlay{background:linear-gradient(90deg,rgba(15,23,42,.20) 0%,rgba(15,23,42,.10) 34%,rgba(15,23,42,.025) 68%,rgba(15,23,42,0) 100%)}
.shopiva-hero-v4 .hero-content{max-width:760px;padding:48px 56px;}
.shopiva-hero-v4 .hero-content:before{content:"";position:absolute;left:36px;top:34px;bottom:34px;width:min(650px,62%);z-index:-1;border-radius:26px;background:rgba(255,255,255,.82);border:1px solid rgba(255,255,255,.72);box-shadow:0 18px 45px rgba(15,23,42,.08);backdrop-filter:blur(7px)}
.shopiva-hero-v4 .hero-badge{background:rgba(255,255,255,.86);color:#172033;border:1px solid rgba(15,23,42,.10);box-shadow:0 8px 20px rgba(15,23,42,.07)}
.shopiva-hero-v4 .hero-kicker{color:#4f46e5;opacity:1;letter-spacing:.16em;font-weight:900}
.shopiva-hero-v4 .hero h1{color:#111827!important;font-weight:900;text-shadow:none}
.shopiva-hero-v4 .hero h1 em{font-style:normal;color:#4f46e5!important;background:none!important;-webkit-text-fill-color:#4f46e5}
.shopiva-hero-v4 .hero p{color:#344054!important;text-shadow:none}
.shopiva-hero-v4 .primary-btn{background:#111827;color:#fff;border:1px solid #111827;box-shadow:0 10px 24px rgba(17,24,39,.13)}
.shopiva-hero-v4 .primary-btn span{color:#76e4ff}
.shopiva-hero-v4 .secondary-btn{background:rgba(255,255,255,.72);border:1px solid rgba(17,24,39,.14);color:#111827;box-shadow:0 8px 20px rgba(17,24,39,.06)}
.shopiva-hero-v4 .secondary-btn:hover{background:#fff}
.shopiva-hero-v4 .secondary-btn span{color:#4f46e5}
.shopiva-hero-v4 .hero-arrow{width:48px;height:48px;background:rgba(255,255,255,.86);border:1px solid rgba(17,24,39,.12);color:#111827;box-shadow:0 8px 24px rgba(17,24,39,.10)}
.shopiva-hero-v4 .hero-arrow:hover{background:#fff}
.shopiva-hero-v4 .hero-dot{background:rgba(17,24,39,.20);height:6px;width:20px}
.shopiva-hero-v4 .hero-dot.is-active{background:#4f46e5;width:46px}
.shopiva-hero-v4 .hero-progress{background:rgba(17,24,39,.08);height:3px}
.shopiva-hero-v4 .hero-progress span{background:linear-gradient(90deg,#4f46e5,#76e4ff);}
.shopiva-hero-v4 .hero-status{color:#475467}
.shopiva-hero-v4 .hero-status strong{color:#059669}
.shopiva-hero-v4 .hero-live-dot{background:#34d399;box-shadow:0 0 0 5px rgba(52,211,153,.12)}
@media(max-width:900px){.shopiva-hero-v4 .hero-content{padding:44px}.shopiva-hero-v4 .hero-content:before{left:28px;width:70%}.shopiva-hero-v4 .hero-status{display:none}}
@media(max-width:650px){.hero.shopiva-hero-v4{height:600px;margin:15px;border-radius:24px}.shopiva-hero-v4 .hero-overlay{background:linear-gradient(180deg,rgba(15,23,42,.12),rgba(15,23,42,.03))}.shopiva-hero-v4 .hero-content{padding:30px 26px;align-self:flex-end;margin-bottom:26px}.shopiva-hero-v4 .hero-content:before{left:14px;right:14px;top:18px;bottom:18px;width:auto;border-radius:22px;background:rgba(255,255,255,.88)}.shopiva-hero-v4 .hero h1{font-size:40px}.shopiva-hero-v4 .hero p{font-size:16px}.shopiva-hero-v4 .hero-dots{left:26px;bottom:22px;max-width:72%;overflow:hidden}.shopiva-hero-v4 .hero-arrow{width:42px;height:42px}.shopiva-hero-v4 .hero-prev{left:10px}.shopiva-hero-v4 .hero-next{right:10px}}
</style>
'''
text = text.replace('</head>', css + '\n</head>', 1)

js = r'''
<script id="shopiva-hero-v4-js">
(function(){
 const root=document.querySelector('.shopiva-hero-v4');
 if(!root)return;
 const slides=[...root.querySelectorAll('.hero-slide')];
 const dots=[...root.querySelectorAll('.hero-dot')];
 const prev=root.querySelector('.hero-prev');
 const next=root.querySelector('.hero-next');
 const progress=root.querySelector('.hero-progress span');
 if(!slides.length)return;
 let index=0,timer=null;
 const duration=3000;
 function render(i){
   index=(i+slides.length)%slides.length;
   slides.forEach((s,n)=>s.classList.toggle('is-active',n===index));
   dots.forEach((d,n)=>d.classList.toggle('is-active',n===index));
   if(progress){progress.style.animation='none';progress.offsetHeight;progress.style.animation='shopivaHeroProgress '+duration+'ms linear forwards';}
 }
 function schedule(){clearTimeout(timer);timer=setTimeout(()=>{render(index+1);schedule();},duration);}
 prev?.addEventListener('click',()=>{render(index-1);schedule();});
 next?.addEventListener('click',()=>{render(index+1);schedule();});
 dots.forEach((d,n)=>d.addEventListener('click',()=>{render(n);schedule();}));
 root.addEventListener('mouseenter',()=>clearTimeout(timer));
 root.addEventListener('mouseleave',()=>schedule());
 render(0);schedule();
})();
</script>
<style id="shopiva-hero-v4-progress">
@keyframes shopivaHeroProgress{from{width:0}to{width:100%}}
</style>
'''
text = text.replace('</body>', js + '\n</body>', 1)

TEMPLATE.write_text(text, encoding='utf-8')
print(f"Shopiva homepage hero V4 applied with {len(slides)} slides and {3000}ms rotation.")
