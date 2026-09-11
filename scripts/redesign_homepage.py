from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "home" / "templates" / "home.html"
text = TEMPLATE.read_text(encoding="utf-8")

MARKER = "<!-- SHOPIVA-HERO-V2 -->"
if MARKER in text:
    print("Homepage hero redesign already applied.")
    raise SystemExit(0)

new_hero = r'''<!-- SHOPIVA-HERO-V2 -->
<section class="hero hero-slideshow shopiva-hero-v2" aria-label="Shopiva featured shopping stories">
    <div class="hero-track">
        <article class="hero-slide is-active" data-index="0">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=2200&q=88" alt="Customer shopping online with a smartphone and bags" loading="eager">
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
                <img src="https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=2200&q=88" alt="Modern retail shopping experience" loading="lazy">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">🛍️ DISCOVER MORE</span>
                <div class="hero-kicker">PRODUCTS · CATEGORIES · SELLERS</div>
                <h1>Find your next<br><em>favourite.</em></h1>
                <p>Search the marketplace, browse categories and discover products from Shopiva sellers in one clean digital experience.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">Browse Products <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>

        <article class="hero-slide" data-index="2">
            <div class="hero-slide-image">
                <img src="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=2200&q=88" alt="Fashion shopping inspiration" loading="lazy">
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
                <img src="https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=2200&q=88" alt="Premium product discovery" loading="lazy">
            </div>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <span class="hero-badge">⚡ SHOPIVA PICKS</span>
                <div class="hero-kicker">QUALITY · VALUE · CONVENIENCE</div>
                <h1>Better finds.<br><em>Better value.</em></h1>
                <p>See featured products, live deals and useful everyday picks without the clutter.</p>
                <div class="hero-buttons">
                    <a href="/products/" class="primary-btn">See What's New <span>↗</span></a>
                    <a href="#categories" class="secondary-btn"><span>✦</span> Explore Categories <b>↓</b></a>
                </div>
            </div>
        </article>
    </div>

    <button class="hero-arrow hero-prev" type="button" aria-label="Previous slide">‹</button>
    <button class="hero-arrow hero-next" type="button" aria-label="Next slide">›</button>

    <div class="hero-dots" aria-label="Slideshow controls">
        <button class="hero-dot is-active" type="button" aria-label="Go to slide 1"></button>
        <button class="hero-dot" type="button" aria-label="Go to slide 2"></button>
        <button class="hero-dot" type="button" aria-label="Go to slide 3"></button>
        <button class="hero-dot" type="button" aria-label="Go to slide 4"></button>
    </div>

    <div class="hero-status"><span class="hero-live-dot"></span><strong>LIVE</strong><span class="hero-status-label">Discovering Shopiva</span></div>
    <div class="hero-progress"><span></span></div>
</section>
'''

pattern = re.compile(r'<section class="hero hero-slideshow"[\s\S]*?</section>\n\n<section class="section" id="categories">', re.M)
if not pattern.search(text):
    raise SystemExit("Could not locate the homepage hero section.")
text = pattern.sub(new_hero + "\n<section class=\"section\" id=\"categories\">", text, count=1)

# Add a premium digital theme as an override so older inline styles do not fight the redesign.
css = r'''
/* SHOPIVA HERO V2 — premium digital theme */
body{background:#f6f8fc;color:#101828}
.navbar{background:rgba(255,255,255,.96);backdrop-filter:blur(14px);border-bottom:1px solid #e7ebf3}
.logo{color:#101828}.logo span{color:#5b67f1}
.search-form button,.signup-btn,.cart-btn{background:#101828}
.nav-links a:hover{color:#5b67f1}
.login-btn{background:#eef0ff;color:#4f46e5!important}
.hero.shopiva-hero-v2{height:540px;margin:24px auto 34px;border-radius:30px;background:#0b1020;box-shadow:0 24px 70px rgba(16,24,40,.16)}
.shopiva-hero-v2 .hero-slide-image img{object-position:center}
.shopiva-hero-v2 .hero-overlay{background:linear-gradient(90deg,rgba(8,13,28,.96) 0%,rgba(8,13,28,.80) 38%,rgba(8,13,28,.16) 72%,rgba(8,13,28,.04) 100%)}
.shopiva-hero-v2 .hero-content{max-width:760px;padding:58px 70px}
.shopiva-hero-v2 .hero-badge{background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.20);color:#fff;box-shadow:0 8px 25px rgba(0,0,0,.12)}
.shopiva-hero-v2 .hero-kicker{color:#b8c4ff;letter-spacing:.20em}
.shopiva-hero-v2 .hero h1{color:#fff;font-weight:850;letter-spacing:-.055em;font-size:clamp(42px,5.5vw,72px)}
.shopiva-hero-v2 .hero h1 em{font-style:normal;background:linear-gradient(90deg,#76e4ff,#a99cff 80%);-webkit-background-clip:text;background-clip:text;color:transparent}
.shopiva-hero-v2 .hero p{color:#e3e8f2;max-width:620px}
.shopiva-hero-v2 .hero-buttons{gap:12px}
.shopiva-hero-v2 .primary-btn{background:linear-gradient(135deg,#ffffff,#eef1ff);color:#101828;border:1px solid rgba(255,255,255,.7);box-shadow:0 10px 26px rgba(0,0,0,.14)}
.shopiva-hero-v2 .primary-btn span{color:#5b67f1}
.shopiva-hero-v2 .secondary-btn{display:inline-flex;align-items:center;gap:9px;border:1px solid rgba(255,255,255,.26);background:rgba(255,255,255,.08);color:#fff;box-shadow:inset 0 1px rgba(255,255,255,.08);transition:.25s}
.shopiva-hero-v2 .secondary-btn:hover{background:rgba(255,255,255,.16);transform:translateY(-2px)}
.shopiva-hero-v2 .secondary-btn span{color:#76e4ff}.shopiva-hero-v2 .secondary-btn b{font-size:16px;opacity:.9}
.shopiva-hero-v2 .hero-arrow{width:48px;height:48px;background:rgba(7,12,28,.56);border:1px solid rgba(255,255,255,.20);color:#fff;box-shadow:0 8px 24px rgba(0,0,0,.18)}
.shopiva-hero-v2 .hero-arrow:hover{background:rgba(255,255,255,.16);border-color:rgba(255,255,255,.34)}
.shopiva-hero-v2 .hero-prev{left:22px}.shopiva-hero-v2 .hero-next{right:22px}
.shopiva-hero-v2 .hero-dots{left:70px;bottom:27px}
.shopiva-hero-v2 .hero-dot{height:6px;width:22px;background:rgba(255,255,255,.24)}
.shopiva-hero-v2 .hero-dot.is-active{width:52px;background:#76e4ff}
.shopiva-hero-v2 .hero-status{position:absolute;right:30px;bottom:24px;z-index:7;display:flex;align-items:center;gap:7px;font-size:11px;letter-spacing:.12em;color:rgba(255,255,255,.75)}
.shopiva-hero-v2 .hero-live-dot{width:7px;height:7px;border-radius:50%;background:#62f1a7;box-shadow:0 0 0 5px rgba(98,241,167,.12);animation:shopivaPulse 1.4s infinite}
.shopiva-hero-v2 .hero-status strong{color:#62f1a7}.shopiva-hero-v2 .hero-status-label{letter-spacing:.03em;color:rgba(255,255,255,.52)}
.shopiva-hero-v2 .hero-progress{height:3px;background:rgba(255,255,255,.10)}
.shopiva-hero-v2 .hero-progress span{background:linear-gradient(90deg,#76e4ff,#a99cff);animation:none}
@keyframes shopivaPulse{0%,100%{transform:scale(1);opacity:.8}50%{transform:scale(1.35);opacity:1}}
.category{background:#fff;border:1px solid #e8ebf2;border-radius:20px;box-shadow:0 10px 28px rgba(16,24,40,.04)}
.category:hover{box-shadow:0 16px 36px rgba(16,24,40,.10);border-color:#d9dded}
.view-btn{background:#f0f2ff;color:#4f46e5}
.price{color:#101828}
.ai-form button{background:#101828}
@media (max-width:900px){.shopiva-hero-v2 .hero-content{padding:44px}.shopiva-hero-v2 .hero-status{display:none}}
@media (max-width:650px){.hero.shopiva-hero-v2{height:610px;margin:15px;border-radius:24px}.shopiva-hero-v2 .hero-overlay{background:linear-gradient(180deg,rgba(8,13,28,.88) 0%,rgba(8,13,28,.74) 56%,rgba(8,13,28,.38) 100%)}.shopiva-hero-v2 .hero-content{padding:36px 28px;align-self:flex-end;margin-bottom:28px}.shopiva-hero-v2 .hero h1{font-size:42px}.shopiva-hero-v2 .hero p{font-size:16px}.shopiva-hero-v2 .hero-dots{left:28px;bottom:22px}.shopiva-hero-v2 .hero-prev{left:12px}.shopiva-hero-v2 .hero-next{right:12px}}
'''
text = text.replace("    </style>\n</head>", "" + css + "\n    </style>\n</head>", 1)

# Replace the old hero JS with a robust browser-side controller.
js = r'''<script>
(function(){
    const root=document.querySelector('.shopiva-hero-v2');
    if(!root) return;
    const slides=[...root.querySelectorAll('.hero-slide')];
    const dots=[...root.querySelectorAll('.hero-dot')];
    const next=root.querySelector('.hero-next');
    const prev=root.querySelector('.hero-prev');
    const progress=root.querySelector('.hero-progress span');
    const interval=1000;
    let index=0, timer=null, progressTimer=null;

    function render(i){
        index=(i+slides.length)%slides.length;
        slides.forEach((s,n)=>s.classList.toggle('is-active',n===index));
        dots.forEach((d,n)=>{d.classList.toggle('is-active',n===index);d.setAttribute('aria-current',n===index?'true':'false');});
        if(progress){
            progress.style.transition='none';progress.style.width='0%';
            void progress.offsetWidth;
            progress.style.transition=`width ${interval}ms linear`;
            progress.style.width='100%';
        }
    }
    function start(){
        clearInterval(timer);clearTimeout(progressTimer);
        if(slides.length<2) return;
        timer=setInterval(()=>render(index+1),interval);
    }
    function restart(){render(index);start();}
    next?.addEventListener('click',()=>{render(index+1);start();});
    prev?.addEventListener('click',()=>{render(index-1);start();});
    dots.forEach((dot,n)=>dot.addEventListener('click',()=>{render(n);start();}));
    root.addEventListener('mouseenter',()=>clearInterval(timer));
    root.addEventListener('mouseleave',start);
    document.addEventListener('visibilitychange',()=>{if(document.hidden) clearInterval(timer); else start();});
    render(0);start();
})();
</script>'''

# Locate only the old hero controller at the end of the file.
old_js = re.compile(r'<script>\s*const heroSlides = document\.querySelectorAll\("\.hero-slide"\);[\s\S]*?</script>\s*\n\s*</body>', re.M)
text, count = old_js.subn(js + "\n\n</body>", text, count=1)
if count != 1:
    raise SystemExit("Could not locate the old hero slideshow controller.")

TEMPLATE.write_text(text, encoding="utf-8")
print("Homepage hero redesigned successfully.")
