from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "home" / "templates" / "home.html"
text = TEMPLATE.read_text(encoding="utf-8")

MARKER = '<!-- SHOPIVA-EXTRA-20-SLIDES -->'
if MARKER in text:
    print("Extra 20 homepage slides already applied.")
    raise SystemExit(0)

slides = [
    ("🛒 EASY CHECKOUT", "CART · CHECKOUT · CONVENIENCE", "From cart", "to confirmed.", "Review your items, enter your delivery details and move through checkout with less friction.", "Open Cart", "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=2200&q=88", "Online shopping checkout"),
    ("📍 DELIVERY TRACKING", "ORDER STATUS · GPS · DELIVERY JOURNEY", "Stay in the", "loop.", "Follow your order journey and see delivery-partner details when live GPS is available.", "Track My Order", "https://images.unsplash.com/photo-1521791055366-0d553872125f?auto=format&fit=crop&w=2200&q=88", "Delivery customer service"),
    ("💬 FAST HELP", "CUSTOMER CARE · QUESTIONS · SUPPORT", "Questions?", "Ask Shopiva.", "Get help with products, orders, delivery and account questions through Shopiva support tools.", "Get Support", "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=2200&q=88", "Customer support team"),
    ("📦 ORDER MANAGEMENT", "ORDERS · HISTORY · RECEIPTS", "Every order", "has a story.", "Keep your purchases organized with order history, tracking information and delivery updates.", "View Orders", "https://images.unsplash.com/photo-1586528116493-da8b5f5f3f33?auto=format&fit=crop&w=2200&q=88", "Packages ready for delivery"),
    ("🔎 SMART SEARCH", "DISCOVERY · FILTERS · PRODUCT SEARCH", "Search less.", "Find faster.", "Use Shopiva search to discover products by name, category and useful shopping terms.", "Search Products", "https://images.unsplash.com/photo-1516321497487-e288fb19713f?auto=format&fit=crop&w=2200&q=88", "Search and technology"),
    ("❤️ WISHLIST", "SAVED PRODUCTS · FAVOURITES · FUTURE BUYS", "Save what", "you love.", "Keep products close to your next purchase with a personal Shopiva wishlist.", "Open Wishlist", "https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?auto=format&fit=crop&w=2200&q=88", "Shopping wishlist"),
    ("⭐ VERIFIED REVIEWS", "RATINGS · FEEDBACK · TRUSTED BUYING", "Shop with", "more confidence.", "After a delivered purchase, customers can share verified ratings and product feedback.", "Explore Products", "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=2200&q=88", "Customer review discussion"),
    ("🔐 ACCOUNT SECURITY", "SIGN-IN · CUSTOMER ACCOUNT · PRIVACY", "Your account", "stays yours.", "Shopiva keeps customer access separated from seller and admin areas for a safer marketplace experience.", "Sign In", "https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&w=2200&q=88", "Digital account security"),
    ("🏪 SELLER DISCOVERY", "LOCAL BUSINESSES · PRODUCT SOURCES · MARKETPLACE", "Discover", "Shopiva sellers.", "Explore products from sellers building their businesses through the Shopiva marketplace.", "Browse Sellers", "https://images.unsplash.com/photo-1556742111-a301076d9d18?auto=format&fit=crop&w=2200&q=88", "Small business retail"),
    ("🚚 LAST-MILE CARE", "DELIVERY PARTNERS · VEHICLES · ROUTES", "From warehouse", "to your door.", "Shopiva connects order fulfilment with delivery partners and live location when available.", "Follow Delivery", "https://images.unsplash.com/photo-1605733160314-4fc7dac4bb16?auto=format&fit=crop&w=2200&q=88", "Delivery logistics"),
    ("💰 VALUE EVERY DAY", "OFFERS · DISCOUNTS · PROMOTIONS", "More value", "for your money.", "Find live promotions, discounts and special offers from Shopiva products.", "See Deals", "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&w=2200&q=88", "Shopping discounts"),
    ("🎁 GIFTS & SPECIAL PICKS", "GIFTS · ACCESSORIES · OCCASIONS", "Find something", "worth giving.", "Explore gift-ready products and standout finds for birthdays, celebrations and everyday surprises.", "Find Gifts", "https://images.unsplash.com/photo-1512909006721-3d6018887383?auto=format&fit=crop&w=2200&q=88", "Gift shopping"),
    ("👶 FAMILY SHOPPING", "FAMILY · BABY · KIDS · HOME NEEDS", "For every", "kind of family.", "Discover useful products for parents, children and busy Kenyan households.", "Shop Family", "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=2200&q=88", "Family lifestyle shopping"),
    ("🚗 TRAVEL & MOBILITY", "TRAVEL · AUTO · OUTDOOR ESSENTIALS", "Ready for", "the road.", "Find travel, mobility and outdoor essentials for commutes, trips and weekend adventures.", "Shop Travel", "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=2200&q=88", "Travel lifestyle"),
    ("🎧 ENTERTAINMENT", "AUDIO · MEDIA · GAMING · LEISURE", "Make room for", "more fun.", "Discover entertainment accessories and products for downtime, gaming and music.", "Explore Entertainment", "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=2200&q=88", "Entertainment and music"),
    ("🌱 SMART LIVING", "HOME · SUSTAINABILITY · EVERYDAY SOLUTIONS", "Live a little", "smarter.", "Find practical products and everyday solutions designed around modern living.", "Explore Smart Living", "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=2200&q=88", "Modern smart living"),
    ("🧑🏽‍💻 WORK FROM ANYWHERE", "PRODUCTIVITY · OFFICE · REMOTE WORK", "Work your", "way.", "Build a productive setup with devices, accessories and workspace essentials.", "Shop Workspace", "https://images.unsplash.com/photo-1497215842964-222b430dc094?auto=format&fit=crop&w=2200&q=88", "Remote work workspace"),
    ("📞 RESOLUTION CENTER", "ISSUES · SUPPORT REQUESTS · ORDER HELP", "Problems happen.", "Resolution matters.", "Shopiva gives customers a clear support path when an order or shopping issue needs attention.", "Get Order Help", "https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=2200&q=88", "Customer service resolution"),
    ("🧠 AI PRODUCT GUIDE", "RECOMMENDATIONS · NATURAL LANGUAGE · VOICE", "Tell us what", "you need.", "Use Shopiva AI to search, compare and explore products using natural language or voice.", "Ask AI", "https://images.unsplash.com/photo-1535378917042-10a22c95931a?auto=format&fit=crop&w=2200&q=88", "AI technology assistant"),
    ("🇰🇪 BUILT FOR KENYA", "LOCAL SHOPPING · KSH · M-PESA · DELIVERY", "Kenyan shopping", "made digital.", "Shopiva brings products, payments, sellers and delivery into one marketplace experience built for Kenya.", "Shop Shopiva", "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?auto=format&fit=crop&w=2200&q=88", "Kenya landscape and modern life"),
]

# Locate the current V4 hero controls; insert exactly once before the controls.
controls = '    <button class="hero-arrow hero-prev" type="button" aria-label="Previous slide">‹</button>'
insert_at = text.find(controls)
if insert_at == -1:
    raise SystemExit("Could not locate Shopiva hero controls.")

extra_parts = [MARKER]
for index, (badge, kicker, heading, emphasis, paragraph, button, image, alt) in enumerate(slides, start=16):
    extra_parts.extend([
        f'        <article class="hero-slide shopiva-extra-slide" data-index="{index}">',
        '            <div class="hero-slide-image">',
        f'                <img src="{image}" alt="{alt}" loading="lazy">',
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
extra_html = "\n".join(extra_parts) + "\n"
text = text[:insert_at] + extra_html + text[insert_at:]

# Replace the hero dots with 36 indicators.
dots_pattern = re.compile(r'(    <div class="hero-dots" aria-label="Slideshow controls">)[\s\S]*?(    </div>\n    <div class="hero-status">)', re.M)
dots = ['    <div class="hero-dots" aria-label="Slideshow controls">']
for index in range(36):
    dots.append(f'        <button class="hero-dot{" is-active" if index == 0 else ""}" type="button" data-slide="{index}" aria-label="Go to slide {index + 1}"></button>')
dots.append('    </div>')
dots.append('    <div class="hero-status">')
new_dots = "\n".join(dots)
text, count = dots_pattern.subn(new_dots, text, count=1)
if count != 1:
    raise SystemExit("Could not update slideshow indicators.")

TEMPLATE.write_text(text, encoding="utf-8")
print("Added 20 additional homepage slideshow slides (36 total).")
