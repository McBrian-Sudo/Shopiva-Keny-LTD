from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "home" / "templates" / "home.html"
text = TEMPLATE.read_text(encoding="utf-8")

slides = [
    ("🛍️ SHOPIVA KENYA", "SMART SHOPPING · LOCAL DISCOVERY", "Everything you need.", "One smarter marketplace.", "Discover products, compare options and order with a shopping experience built for Kenya.", "Shop Products", "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=2200&q=88", "Customer shopping online"),
    ("✨ DISCOVER MORE", "PRODUCTS · CATEGORIES · SELLERS", "Find your next", "favourite.", "Browse products from Shopiva sellers in one clean digital marketplace.", "Browse Products", "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=2200&q=88", "Modern retail shopping"),
    ("👗 SHOP YOUR STYLE", "FASHION · BEAUTY · LIFESTYLE", "Style that moves", "with you.", "Explore fashion, lifestyle essentials and new finds for every day.", "Shop Fashion", "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=2200&q=88", "Fashion shopping"),
    ("👟 FRESH PICKS", "SHOES · ACCESSORIES · STREET STYLE", "Step into", "something better.", "Find footwear and accessories that match your pace and your budget.", "Shop Footwear", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=2200&q=88", "Sneakers and footwear"),
    ("📱 TECH PICKS", "PHONES · GADGETS · SMART DEVICES", "Power your", "everyday life.", "Discover practical electronics for work, entertainment and everyday life.", "Shop Electronics", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=2200&q=88", "Modern smartphone"),
    ("💻 WORK SMART", "LAPTOPS · COMPUTING · WORKSPACE", "Build your", "better setup.", "Upgrade your workspace with computers, accessories and tools that keep you productive.", "Explore Tech", "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=2200&q=88", "Laptop workspace"),
    ("💄 BEAUTY & CARE", "BEAUTY · SELF CARE · DAILY ESSENTIALS", "Feel good.", "Look your best.", "Shop beauty and self-care essentials for everyday routines and special moments.", "Shop Beauty", "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=2200&q=88", "Beauty products"),
    ("🏠 HOME & LIVING", "HOME · FURNITURE · COMFORT", "Make space for", "better living.", "Refresh your home with practical pieces, useful accessories and everyday comfort.", "Shop Home", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=2200&q=88", "Modern sofa and living room"),
    ("🥑 EVERYDAY ESSENTIALS", "GROCERIES · HOUSEHOLD · DAILY NEEDS", "Stock up", "with less stress.", "Discover everyday essentials and household products in one convenient marketplace.", "Shop Essentials", "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=2200&q=88", "Fresh groceries"),
    ("⌚ PREMIUM PICKS", "ACCESSORIES · GIFTS · PREMIUM FINDS", "Small details.", "Big difference.", "Find standout accessories and gift-worthy products for yourself or someone special.", "See Premium Picks", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=2200&q=88", "Wrist watch"),
    ("🏃 LIVE ACTIVE", "SPORTS · FITNESS · OUTDOORS", "Move more.", "Live stronger.", "Explore fitness, sports and outdoor essentials for active days and weekend adventures.", "Shop Sports", "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=2200&q=88", "Sports and fitness"),
    ("💳 EASY PAYMENTS", "M-PESA · CHECKOUT · ORDER CONFIRMATION", "Pay with", "confidence.", "Use Shopiva checkout and follow confirmed payment updates without guessing.", "Start Shopping", "https://images.unsplash.com/photo-1556740749-887f6717d7e4?auto=format&fit=crop&w=2200&q=88", "Digital payment and shopping"),
    ("🤝 CUSTOMER SUPPORT", "HELP · ORDERS · DELIVERY QUESTIONS", "Need help?", "Shopiva is here.", "Get support before, during and after your purchase for shopping, orders and delivery questions.", "Get Help", "https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&w=2200&q=88", "Customer support conversation"),
    ("🚚 DELIVERY UPDATES", "TRACKING · RIDERS · LAST-MILE DELIVERY", "Know where", "your order is.", "Follow your delivery journey and see rider details when live GPS is available.", "Track Orders", "https://images.unsplash.com/photo-1586864387967-d02ef85d93e8?auto=format&fit=crop&w=2200&q=88", "Delivery boxes and logistics"),
    ("↩️ RETURNS & RESOLUTION", "ORDER HELP · ISSUE REPORTING · CUSTOMER CARE", "We listen.", "We help resolve.", "Shopiva is designed to give customers a clear path for order issues and support requests.", "Shop with Confidence", "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=2200&q=88", "Customer service technology"),
    ("🤖 SHOPIVA AI", "AI SHOPPING · VOICE · PRODUCT DISCOVERY", "Ask Shopiva.", "Shop smarter.", "Use the Shopiva AI assistant to search products, compare options and get shopping help in natural language.", "Ask Shopiva AI", "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&w=2200&q=88", "Digital customer assistance"),
    ("🎧 AUDIO PICKS", "HEADPHONES · SPEAKERS · AUDIO", "Hear more.", "Carry the vibe.", "Shop headphones and audio accessories for music, work and entertainment.", "Shop Audio", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=2200&q=88", "Wireless headphones"),
    ("📷 CREATOR GEAR", "CAMERAS · CONTENT · CREATIVE TOOLS", "Create it.", "Share it.", "Find cameras and creator accessories for photos, videos and social content.", "Shop Creator Gear", "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=2200&q=88", "Digital camera"),
    ("🎒 READY TO GO", "BAGS · TRAVEL · EVERYDAY CARRY", "Pack smarter.", "Go further.", "Discover practical bags and travel accessories for school, work and weekends.", "Shop Bags", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=2200&q=88", "Travel backpack"),
    ("🕶️ STYLE ACCESSORIES", "SUNGLASSES · JEWELRY · ACCESSORIES", "Finish the look.", "Your way.", "Complete your everyday style with accessories selected for modern Kenyan shoppers.", "Shop Accessories", "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=2200&q=88", "Sunglasses"),
    ("🍳 KITCHEN LIFE", "KITCHEN · COOKING · HOME APPLIANCES", "Cook better.", "Live easier.", "Upgrade the kitchen with useful tools and appliances for everyday meals.", "Shop Kitchen", "https://images.unsplash.com/photo-1556911220-e15b29be8f7d?auto=format&fit=crop&w=2200&q=88", "Modern kitchen"),
    ("☕ COFFEE & MOMENTS", "FOOD · DRINKWARE · HOME COMFORT", "Slow down.", "Enjoy the moment.", "Discover drinkware and small comforts that make everyday routines better.", "Shop Lifestyle", "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=2200&q=88", "Coffee and lifestyle"),
    ("🎮 GAMING TIME", "GAMING · CONSOLES · ACCESSORIES", "Play more.", "Have fun.", "Find gaming gear and accessories for players, streamers and entertainment nights.", "Shop Gaming", "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=2200&q=88", "Gaming setup"),
    ("📺 HOME ENTERTAINMENT", "TV · STREAMING · SMART HOME", "Bring the cinema", "home.", "Explore entertainment devices and smart-home upgrades for your space.", "Shop Entertainment", "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=2200&q=88", "Modern television"),
    ("🇰🇪 NAIROBI CUSTOMER CARE", "KENYAN PEOPLE · SUPPORT · DIGITAL HELP", "Real people.", "Real support.", "Shopiva is built to make digital shopping feel human, with support for customers across Kenya.", "Get Customer Support", "https://images.unsplash.com/photo-1639472628910-ef02c5404b9c?auto=format&fit=crop&w=2200&q=88", "Kenyan customer support professional in Nairobi"),
    ("🇰🇪 KENYAN DELIVERY TEAM", "LAST-MILE · RIDERS · PARCEL HANDOFF", "From our team", "to your doorstep.", "Follow delivery progress and get clear updates from Shopiva's delivery network.", "Track Delivery", "https://images.unsplash.com/photo-1745895401130-7a44ac38ce01?auto=format&fit=crop&w=2200&q=88", "Kenyan people in Nairobi"),
    ("🇰🇪 LOCAL SHOPPING HELP", "KENYAN SHOPPERS · PRODUCT GUIDANCE", "Need a recommendation?", "Talk to Shopiva.", "Get shopping guidance for products, budgets and everyday needs from a Kenya-focused marketplace.", "Ask Shopiva", "https://images.unsplash.com/photo-1756197257616-e4af9690ccdd?auto=format&fit=crop&w=2200&q=88", "Kenyan woman in Nairobi"),
    ("🇰🇪 SELLER SUCCESS", "KENYAN BUSINESSES · MARKETPLACE · SELLERS", "Local sellers.", "More customers.", "Shopiva helps Kenyan businesses list products, manage orders and grow their digital storefront.", "Sell on Shopiva", "https://images.unsplash.com/photo-1746022637918-cf23f9c58016?auto=format&fit=crop&w=2200&q=88", "Kenyan man in Nairobi"),
    ("📦 ORDER PREPARATION", "PACKING · FULFILMENT · QUALITY CHECKS", "Packed with care.", "Ready to move.", "See the journey from seller preparation through fulfilment and delivery.", "View Orders", "https://images.unsplash.com/photo-1605733160314-4fc7dac4bb16?auto=format&fit=crop&w=2200&q=88", "Packages ready for delivery"),
    ("🔍 SMART SEARCH", "DISCOVER · FILTER · COMPARE", "Search less.", "Find faster.", "Use Shopiva search and categories to discover the right product without the clutter.", "Search Products", "https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?auto=format&fit=crop&w=2200&q=88", "Shopping products on shelves"),
    ("❤️ WISHLIST", "SAVE · COMPARE · BUY LATER", "See it today.", "Save it for later.", "Keep favourite products close and return when you're ready to buy.", "Open Wishlist", "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=2200&q=88", "Happy shopper"),
    ("⭐ VERIFIED REVIEWS", "RATINGS · CUSTOMER FEEDBACK · TRUST", "Real experiences.", "Better decisions.", "See customer feedback and verified reviews to shop with more confidence.", "See Reviews", "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=2200&q=88", "People discussing products"),
    ("🔐 ACCOUNT SECURITY", "CUSTOMER ACCOUNTS · PRIVACY · LOGIN", "Your account.", "Your control.", "Manage your profile, addresses, orders and saved products in one secure account.", "My Account", "https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&w=2200&q=88", "Secure customer support technology"),
    ("🎁 SPECIAL DEALS", "DISCOUNTS · PROMOS · VALUE", "More value.", "More to love.", "Discover live discounts, promotions and special offers from Shopiva sellers.", "See Deals", "https://images.unsplash.com/photo-1607082349566-187342175e2f?auto=format&fit=crop&w=2200&q=88", "Shopping bags and gifts"),
    ("🧡 SHOPIVA FOR FAMILIES", "EVERYDAY SHOPPING · HOME · ESSENTIALS", "For the whole", "household.", "Find products for home, family and everyday routines in one marketplace.", "Shop Family", "https://images.unsplash.com/photo-1511895426328-dc8714efa4d2?auto=format&fit=crop&w=2200&q=88", "Family shopping"),
    ("🌍 KENYA FIRST", "COUNTIES · CITIES · NATIONWIDE DELIVERY", "From Nairobi", "to every county.", "Shopiva is designed for Kenyan customers with a growing nationwide delivery vision.", "Explore Shopiva", "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?auto=format&fit=crop&w=2200&q=88", "Kenya landscape"),
]

hero_parts = [
    '<!-- SHOPIVA-HERO-V5 -->',
    '<section class="hero hero-slideshow shopiva-hero-v5" aria-label="Shopiva shopping, product and customer service highlights">',
    '    <div class="hero-track">',
]
for index, (badge, kicker, heading, emphasis, paragraph, button, image, alt) in enumerate(slides):
    hero_parts.extend([
        f'        <article class="hero-slide{" is-active" if index == 0 else ""}" data-index="{index}">',
        '            <div class="hero-slide-image">',
        f'                <img src="{image}" alt="{alt}" loading="{"eager" if index == 0 else "lazy"}"{" fetchpriority=\"high\"" if index == 0 else ""} onerror="this.onerror=null;this.src=\'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=2200&q=88\';">',
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

# Replace any previous Shopiva hero version while keeping the rest of the homepage intact.
pattern = re.compile(r'<!-- SHOPIVA-HERO-(?:V2|V3|V4|V5) -->\s*<section class="hero hero-slideshow shopiva-hero-[a-z0-9-]+"[\s\S]*?</section>\s*\n\s*<section class="section" id="categories">', re.M)
if not pattern.search(text):
    raise SystemExit("Could not locate the current Shopiva hero block.")
text = pattern.sub(new_hero + '\n<section class="section" id="categories">', text, count=1)

css = '''\n<style id="shopiva-hero-v5-css">\n.hero.shopiva-hero-v5{height:540px;margin:24px auto 34px;border-radius:30px;background:#edf2f7;box-shadow:0 24px 70px rgba(16,24,40,.10);position:relative;overflow:hidden;isolation:isolate}\n.shopiva-hero-v5 .hero-slide{transition:opacity .65s ease,transform 1.05s ease,visibility .65s}\n.shopiva-hero-v5 .hero-slide-image img{filter:saturate(1.08) contrast(1.01);object-position:center}\n.shopiva-hero-v5 .hero-overlay{background:linear-gradient(90deg,rgba(15,23,42,.16) 0%,rgba(15,23,42,.08) 34%,rgba(15,23,42,.02) 68%,rgba(15,23,42,0) 100%)}\n.shopiva-hero-v5 .hero-content{max-width:760px;padding:48px 56px}\n.shopiva-hero-v5 .hero-content:before{content:"";position:absolute;left:36px;top:34px;bottom:34px;width:min(650px,62%);z-index:-1;border-radius:26px;background:rgba(255,255,255,.86);border:1px solid rgba(255,255,255,.76);box-shadow:0 18px 45px rgba(15,23,42,.08);backdrop-filter:blur(8px)}\n.shopiva-hero-v5 .hero-badge{background:rgba(255,255,255,.90);color:#172033;border:1px solid rgba(15,23,42,.10);box-shadow:0 8px 20px rgba(15,23,42,.07)}\n.shopiva-hero-v5 .hero-kicker{color:#4f46e5;opacity:1;letter-spacing:.16em;font-weight:900}\n.shopiva-hero-v5 .hero h1{color:#111827!important;font-weight:900;text-shadow:none}\n.shopiva-hero-v5 .hero h1 em{font-style:normal;color:#4f46e5!important;background:none!important;-webkit-text-fill-color:#4f46e5}\n.shopiva-hero-v5 .hero p{color:#344054!important;text-shadow:none}\n.shopiva-hero-v5 .primary-btn{background:#111827;color:#fff;border:1px solid #111827;box-shadow:0 10px 24px rgba(17,24,39,.13)}\n.shopiva-hero-v5 .primary-btn span{color:#76e4ff}\n.shopiva-hero-v5 .secondary-btn{background:rgba(255,255,255,.78);border:1px solid rgba(17,24,39,.14);color:#111827;box-shadow:0 8px 20px rgba(17,24,39,.06)}\n.shopiva-hero-v5 .secondary-btn:hover{background:#fff}\n.shopiva-hero-v5 .secondary-btn span{color:#4f46e5}\n.shopiva-hero-v5 .hero-arrow{width:48px;height:48px;background:rgba(255,255,255,.88);border:1px solid rgba(17,24,39,.12);color:#111827;box-shadow:0 8px 24px rgba(17,24,39,.10)}\n.shopiva-hero-v5 .hero-arrow:hover{background:#fff}\n.shopiva-hero-v5 .hero-dot{background:rgba(17,24,39,.20);height:6px;width:20px}\n.shopiva-hero-v5 .hero-dot.is-active{background:#4f46e5;width:46px}\n.shopiva-hero-v5 .hero-progress{background:rgba(17,24,39,.08);height:3px}\n.shopiva-hero-v5 .hero-progress span{background:linear-gradient(90deg,#4f46e5,#76e4ff)}\n.shopiva-hero-v5 .hero-status{color:#475467}\n.shopiva-hero-v5 .hero-status strong{color:#059669}\n.shopiva-hero-v5 .hero-live-dot{background:#34d399;box-shadow:0 0 0 5px rgba(52,211,153,.12)}\n@keyframes shopivaHeroProgressV5{from{width:0}to{width:100%}}\n@media(max-width:900px){.shopiva-hero-v5 .hero-content{padding:44px}.shopiva-hero-v5 .hero-content:before{left:28px;width:70%}.shopiva-hero-v5 .hero-status{display:none}}\n@media(max-width:650px){.hero.shopiva-hero-v5{height:600px;margin:15px;border-radius:24px}.shopiva-hero-v5 .hero-overlay{background:linear-gradient(180deg,rgba(15,23,42,.10),rgba(15,23,42,.02))}.shopiva-hero-v5 .hero-content{padding:30px 26px;align-self:flex-end;margin-bottom:26px}.shopiva-hero-v5 .hero-content:before{left:14px;right:14px;top:18px;bottom:18px;width:auto;border-radius:22px;background:rgba(255,255,255,.90)}.shopiva-hero-v5 .hero h1{font-size:40px}.shopiva-hero-v5 .hero p{font-size:16px}.shopiva-hero-v5 .hero-dots{left:26px;bottom:22px;max-width:72%;overflow:hidden}.shopiva-hero-v5 .hero-arrow{width:42px;height:42px}.shopiva-hero-v5 .hero-prev{left:10px}.shopiva-hero-v5 .hero-next{right:10px}}\n</style>\n'''
text = text.replace('</head>', css + '\n</head>', 1)

js = '''\n<script id="shopiva-hero-v5-js">\n(function(){\n const root=document.querySelector('.shopiva-hero-v5');\n if(!root)return;\n const slides=[...root.querySelectorAll('.hero-slide')];\n const dots=[...root.querySelectorAll('.hero-dot')];\n const prev=root.querySelector('.hero-prev');\n const next=root.querySelector('.hero-next');\n const progress=root.querySelector('.hero-progress span');\n if(!slides.length)return;\n let index=0,timer=null;\n const duration=3000;\n const render=i=>{index=(i+slides.length)%slides.length;slides.forEach((s,n)=>s.classList.toggle('is-active',n===index));dots.forEach((d,n)=>d.classList.toggle('is-active',n===index));if(progress){progress.style.animation='none';void progress.offsetWidth;progress.style.animation='shopivaHeroProgressV5 '+duration+'ms linear forwards';}};\n const schedule=()=>{clearTimeout(timer);timer=setTimeout(()=>{render(index+1);schedule();},duration);};\n prev?.addEventListener('click',()=>{render(index-1);schedule();});\n next?.addEventListener('click',()=>{render(index+1);schedule();});\n dots.forEach((d,n)=>d.addEventListener('click',()=>{render(n);schedule();}));\n root.addEventListener('mouseenter',()=>clearTimeout(timer));\n root.addEventListener('mouseleave',schedule);\n render(0);schedule();\n})();\n</script>\n'''
# Remove an earlier generated hero-v4 script if present, then add v5 behavior.
text = re.sub(r'<script id="shopiva-hero-v4-js">[\s\S]*?</script>\s*', '', text, count=1)
text = text.replace('</body>', js + '\n</body>', 1)
TEMPLATE.write_text(text, encoding='utf-8')
print(f"Wrote Shopiva Hero V5 with {len(slides)} slides.")
