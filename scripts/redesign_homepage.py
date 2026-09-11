from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "home" / "templates" / "home.html"
text = TEMPLATE.read_text(encoding="utf-8")

MARKER = "<!-- SHOPIVA-HERO-V3 -->"
if MARKER in text:
    print("Homepage hero V3 already applied.")
    raise SystemExit(0)

new_hero = r'''<!-- SHOPIVA-HERO-V3 -->
<section class="hero hero-slideshow shopiva-hero-v2" aria-label="Shopiva featured shopping stories">
    <div class="hero-track">
        <article class="hero-slide is-active" data-index="0">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=2200&q=88" alt="Customer shopping online" loading="eager" fetchpriority="high">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">🇰🇪 SHOPIVA KENYA</span>
                <div class="hero-kicker">SMART SHOPPING · LOCAL DISCOVERY</div>
                <h1>Everything you need.<br><em>One smarter marketplace.</em></h1>
                <p>Discover trusted products, compare your options and order with a shopping experience built for Kenya.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">Shop Products <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>

        <article class="hero-slide" data-index="1">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=2200&q=88" alt="Modern retail store" loading="lazy">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">🛍️ DISCOVER MORE</span>
                <div class="hero-kicker">PRODUCTS · CATEGORIES · SELLERS</div>
                <h1>Find your next<br><em>favourite.</em></h1>
                <p>Browse the marketplace and discover useful products from Shopiva sellers in one clean digital experience.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">Browse Products <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>

        <article class="hero-slide" data-index="2">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=2200&q=88" alt="Fashion shopping" loading="lazy">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">✨ SHOP YOUR STYLE</span>
                <div class="hero-kicker">FASHION · BEAUTY · LIFESTYLE</div>
                <h1>Style that moves<br><em>with you.</em></h1>
                <p>Explore fashion, lifestyle essentials and new finds with simple product discovery and quick ordering.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">Shop Fashion <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>

        <article class="hero-slide" data-index="3">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=2200&q=88" alt="Sneakers and footwear" loading="lazy">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">👟 FRESH PICKS</span>
                <div class="hero-kicker">SHOES · ACCESSORIES · STREET STYLE</div>
                <h1>Step into<br><em>something better.</em></h1>
                <p>Find everyday footwear and accessories that match your pace, your look and your budget.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">Shop Footwear <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>

        <article class="hero-slide" data-index="4">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=2200&q=88" alt="Modern smartphone" loading="lazy">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">📱 TECH PICKS</span>
                <div class="hero-kicker">PHONES · GADGETS · SMART DEVICES</div>
                <h1>Power your<br><em>everyday life.</em></h1>
                <p>Discover practical tech, smart devices and electronics for work, entertainment and everyday life.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">Shop Electronics <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>

        <article class="hero-slide" data-index="5">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=2200&q=88" alt="Laptop workspace" loading="lazy">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">💻 WORK SMART</span>
                <div class="hero-kicker">LAPTOPS · COMPUTING · WORKSPACE</div>
                <h1>Build your<br><em>better setup.</em></h1>
                <p>Upgrade your workspace with computers, accessories and tools that keep you productive.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">Explore Tech <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>

        <article class="hero-slide" data-index="6">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=2200&q=88" alt="Beauty products" loading="lazy">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">💄 BEAUTY & CARE</span>
                <div class="hero-kicker">BEAUTY · SELF CARE · DAILY ESSENTIALS</div>
                <h1>Feel good.<br><em>Look your best.</em></h1>
                <p>Shop beauty and self-care essentials selected for everyday routines and special moments.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">Shop Beauty <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>

        <article class="hero-slide" data-index="7">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=2200&q=88" alt="Modern home interior" loading="lazy">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">🏠 HOME & LIVING</span>
                <div class="hero-kicker">HOME · FURNITURE · COMFORT</div>
                <h1>Make space for<br><em>better living.</em></h1>
                <p>Refresh your home with practical pieces, useful accessories and everyday comfort.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">Shop Home <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>

        <article class="hero-slide" data-index="8">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=2200&q=88" alt="Fresh groceries" loading="lazy">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">🥑 EVERYDAY ESSENTIALS</span>
                <div class="hero-kicker">GROCERIES · HOUSEHOLD · DAILY NEEDS</div>
                <h1>Stock up<br><em>with less stress.</em></h1>
                <p>Discover useful everyday essentials and household products in one convenient marketplace.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">Shop Essentials <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>

        <article class="hero-slide" data-index="9">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1523170335258-f5ed11844a49?auto=format&fit=crop&w=2200&q=88" alt="Luxury watch" loading="lazy">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">⌚ PREMIUM PICKS</span>
                <div class="hero-kicker">ACCESSORIES · GIFTS · PREMIUM FINDS</div>
                <h1>Small details.<br><em>Big difference.</em></h1>
                <p>Find standout accessories and gift-worthy products for yourself or someone special.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">See Premium Picks <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>

        <article class="hero-slide" data-index="10">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=2200&q=88" alt="Sports and fitness" loading="lazy">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">🏃 LIVE ACTIVE</span>
                <div class="hero-kicker">SPORTS · FITNESS · OUTDOORS</div>
                <h1>Move more.<br><em>Live stronger.</em></h1>
                <p>Explore fitness, sports and outdoor essentials for active days and weekend adventures.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">Shop Sports <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>
    </div>

    <button class="hero-arrow hero-prev" type="button" aria-label="Previous slide">‹</button>
    <button class="hero-arrow hero-next" type="button" aria-label="Next slide">›</button>

    <div class="hero-dots" aria-label="Slideshow controls">
        {% for n in "0123456789A" %}
        <button class="hero-dot{% if forloop.first %} is-active{% endif %}" type="button" aria-label="Go to slide {{ forloop.counter }}"></button>
        {% endfor %}
    </div>

    <div class="hero-status"><span class="hero-live-dot"></span><strong>LIVE</strong><span class="hero-status-label">Shopiva discovery</span></div>
    <div class="hero-progress"><span></span></div>
</section>
'''

pattern = re.compile(r'<!-- SHOPIVA-HERO-V2 -->\s*<section class="hero hero-slideshow shopiva-hero-v2"[\s\S]*?</section>\s*\n\s*<section class="section" id="categories">', re.M)
if not pattern.search(text):
    raise SystemExit("Could not locate the Shopiva hero V2 block.")
text = pattern.sub(new_hero + "\n<section class=\"section\" id=\"categories\">", text, count=1)

# Use a lighter, clearer version of the dark theme while keeping the premium midnight look.
css = r'''
/* SHOPIVA HERO V3 — clearer midnight theme */
.hero.shopiva-hero-v2{background:#111827}
.shopiva-hero-v2 .hero-slide-image img{filter:saturate(1.06) contrast(1.02)}
.shopiva-hero-v2 .hero-overlay{background:linear-gradient(90deg,rgba(8,13,28,.52) 0%,rgba(8,13,28,.30) 38%,rgba(8,13,28,.08) 70%,rgba(8,13,28,.01) 100%)}
.shopiva-hero-v2 .hero-content{max-width:760px;padding:58px 70px;text-shadow:0 2px 18px rgba(0,0,0,.28)}
.shopiva-hero-v2 .hero-content:after{content:"";position:absolute;inset:34px auto 34px 46px;width:min(670px,68%);z-index:-1;border-radius:28px;background:linear-gradient(90deg,rgba(8,13,28,.42),rgba(8,13,28,.12),transparent);border:1px solid rgba(255,255,255,.07);backdrop-filter:blur(1px)}
.shopiva-hero-v2 .hero h1{color:#fff!important;font-weight:850}
.shopiva-hero-v2 .hero h1 em{color:transparent!important}
.shopiva-hero-v2 .hero p{color:#f3f6fb!important}
.shopiva-hero-v2 .hero-kicker{color:#d7deff!important}
.shopiva-hero-v2 .hero-badge{background:rgba(17,24,39,.28);border-color:rgba(255,255,255,.30)}
.shopiva-hero-v2 .secondary-btn{background:rgba(255,255,255,.13);border-color:rgba(255,255,255,.34)}
.shopiva-hero-v2 .secondary-btn:hover{background:rgba(255,255,255,.21)}
.shopiva-hero-v2 .hero-arrow{background:rgba(17,24,39,.42)}
.shopiva-hero-v2 .hero-arrow:hover{background:rgba(17,24,39,.62)}
.shopiva-hero-v2 .hero-dot{background:rgba(255,255,255,.38)}
.shopiva-hero-v2 .hero-dot.is-active{background:#76e4ff}
.shopiva-hero-v2 .hero-progress{background:rgba(255,255,255,.13)}
.shopiva-hero-v2 .hero-progress span{background:linear-gradient(90deg,#76e4ff,#a99cff)}
@media (max-width:900px){.shopiva-hero-v2 .hero-content{padding:46px}.shopiva-hero-v2 .hero-content:after{left:28px;inset-top:28px;inset-bottom:28px;width:72%}}
@media (max-width:650px){.hero.shopiva-hero-v2{height:610px}.shopiva-hero-v2 .hero-overlay{background:linear-gradient(180deg,rgba(8,13,28,.48) 0%,rgba(8,13,28,.30) 55%,rgba(8,13,28,.12) 100%)}.shopiva-hero-v2 .hero-content{padding:36px 28px;margin-bottom:24px}.shopiva-hero-v2 .hero-content:after{left:16px;right:16px;width:auto;inset:22px 16px 18px;border-radius:22px;background:rgba(8,13,28,.28)}.shopiva-hero-v2 .hero-dots{left:28px;bottom:22px;max-width:72%;overflow:hidden}.shopiva-hero-v2 .hero-dot{width:12px}.shopiva-hero-v2 .hero-dot.is-active{width:30px}}
'''
text = text.replace("    </style>\n</head>", css + "\n    </style>\n</head>", 1)

# Replace the old hero controller with a robust 3-second controller and preload all hero images.
js = r'''<script>
(function(){
    const root=document.querySelector('.shopiva-hero-v2');
    if(!root) return;
    const slides=[...root.querySelectorAll('.hero-slide')];
    const dots=[...root.querySelectorAll('.hero-dot')];
    const next=root.querySelector('.hero-next');
    const prev=root.querySelector('.hero-prev');
    const progress=root.querySelector('.hero-progress span');
    const interval=3000;
    let index=0, timer=null;

    slides.forEach(slide=>{
        const img=slide.querySelector('img');
        if(img?.src){ const preload=new Image(); preload.src=img.src; }
    });

    function render(i){
        index=(i+slides.length)%slides.length;
        slides.forEach((slide,n)=>slide.classList.toggle('is-active',n===index));
        dots.forEach((dot,n)=>{
            dot.classList.toggle('is-active',n===index);
            dot.setAttribute('aria-current',n===index?'true':'false');
        });
        if(progress){
            progress.style.animation='none';
            progress.style.width='0%';
            void progress.offsetWidth;
            progress.style.animation='heroProgress 3s linear forwards';
        }
    }

    function start(){
        clearInterval(timer);
        if(slides.length>1) timer=setInterval(()=>render(index+1),interval);
    }

    next?.addEventListener('click',()=>{render(index+1);start();});
    prev?.addEventListener('click',()=>{render(index-1);start();});
    dots.forEach((dot,n)=>dot.addEventListener('click',()=>{render(n);start();}));
    root.addEventListener('mouseenter',()=>clearInterval(timer));
    root.addEventListener('mouseleave',start);
    document.addEventListener('visibilitychange',()=>document.hidden?clearInterval(timer):start());

    render(0);
    start();
})();
</script>'''
old_js = re.compile(r'<script>\s*\(function\(\)\{\s*const root=document\.querySelector\(\'\.shopiva-hero-v2\'\);[\s\S]*?</script>\s*\n\s*</body>', re.M)
if old_js.search(text):
    text = old_js.sub(js + "\n\n</body>", text, count=1)
else:
    # Remove the legacy controller at the bottom if present, then install the V3 controller.
    legacy = re.compile(r'<script>\s*const heroSlides = document\.querySelectorAll\("\.hero-slide"\);[\s\S]*?</script>\s*\n\s*</body>', re.M)
    text, count = legacy.subn(js + "\n\n</body>", text, count=1)
    if count != 1:
        raise SystemExit("Could not locate an existing hero slideshow controller.")

TEMPLATE.write_text(text, encoding="utf-8")
print("Homepage hero V3 applied successfully.")
