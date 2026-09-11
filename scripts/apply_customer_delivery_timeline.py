from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "home" / "templates" / "includes" / "delivery_network_map.html"
VIEWS = ROOT / "home" / "views.py"

text = TEMPLATE.read_text(encoding="utf-8")
views = VIEWS.read_text(encoding="utf-8")

# Build a fixed five-stage delivery journey matching the requested customer experience.
timeline_pattern = re.compile(
    r'<div class="shopiva-timeline" id="shopiva-delivery-timeline">[\s\S]*?</div>\n\n            \{% if latest_order\.delivery_agent %}',
    re.M,
)
new_timeline = r'''<div class="shopiva-timeline shopiva-timeline-v2" id="shopiva-delivery-timeline">
                <div class="shopiva-step {% if latest_order.status in "confirmed paid packed processing shipped out_for_delivery delivered" %}is-complete{% endif %}">
                    <span class="step-dot">✓</span>
                    <div><strong>Order Confirmed</strong><small>{{ latest_order.created_at|date:"d M Y, H:i" }}</small></div>
                </div>
                <div class="shopiva-step {% if latest_order.status in "packed processing shipped out_for_delivery delivered" or latest_order.packed_at %}is-complete{% endif %}">
                    <span class="step-dot">✓</span>
                    <div><strong>Packed at Warehouse</strong><small>{% if latest_order.packed_at %}{{ latest_order.packed_at|date:"d M Y, H:i" }}{% else %}Preparing your package{% endif %}</small></div>
                </div>
                <div class="shopiva-step {% if latest_order.status in "out_for_delivery delivered" %}is-complete{% endif %}">
                    <span class="step-dot">✓</span>
                    <div><strong>Out for Delivery</strong><small>{% if latest_order.assigned_at %}{{ latest_order.assigned_at|date:"d M Y, H:i" }}{% else %}Waiting for dispatch{% endif %}</small></div>
                </div>
                <div class="shopiva-step {% if latest_order.status == "out_for_delivery" %}is-active{% elif latest_order.status == "delivered" %}is-complete{% endif %}">
                    <span class="step-dot">{% if latest_order.status == "out_for_delivery" %}●{% else %}✓{% endif %}</span>
                    <div><strong>On the Way</strong><small>{% if latest_order.status == "out_for_delivery" %}Your package is on the move{% elif latest_order.status == "delivered" %}Completed{% else %}Waiting for rider{% endif %}</small></div>
                </div>
                <div class="shopiva-step {% if latest_order.status == "delivered" %}is-complete{% endif %}">
                    <span class="step-dot">{% if latest_order.status == "delivered" %}✓{% else %}○{% endif %}</span>
                    <div><strong>Delivered</strong><small>{% if latest_order.status == "delivered" %}Delivered successfully{% else %}Estimated after dispatch{% endif %}</small></div>
                </div>
            </div>

            {% if latest_order.delivery_agent %}'''
text, timeline_count = timeline_pattern.subn(new_timeline, text, count=1)
if timeline_count != 1:
    raise SystemExit("Could not locate customer delivery timeline block")

rider_pattern = re.compile(
    r'<div class="shopiva-rider-card" id="shopiva-customer-agent-box">[\s\S]*?</div>\n            \{% endif %}\n            \{% else %}',
    re.M,
)
new_rider = r'''<div class="shopiva-rider-card shopiva-rider-card-v2" id="shopiva-customer-agent-box">
                <div class="shopiva-rider-avatar shopiva-rider-avatar-v2"><span>{{ latest_order.delivery_agent.display_name|first|upper }}</span></div>
                <div class="shopiva-rider-main">
                    <strong>{{ latest_order.delivery_agent.display_name }}</strong>
                    <span>Your Delivery Rider</span>
                    <small>🟢 Verified Shopiva Delivery Partner{% if latest_order.delivery_agent.vehicle_type %} · {{ latest_order.delivery_agent.vehicle_type }}{% endif %}</small>
                    <small>{% if delivery_count %}({{ delivery_count }}+ deliveries){% else %}New delivery partner{% endif %}{% if latest_order.delivery_agent.vehicle_number %} · 🚐 {{ latest_order.delivery_agent.vehicle_number }}{% endif %}</small>
                    <small id="shopiva-customer-agent-status">{% if latest_order.delivery_agent.last_location_at %}Last GPS: {{ latest_order.delivery_agent.last_location_at|date:"d M Y, H:i" }}{% else %}GPS not shared yet{% endif %}</small>
                </div>
                <div class="shopiva-rider-actions shopiva-rider-actions-v2">
                    {% if latest_order.delivery_agent.phone %}
                    <a href="tel:{{ latest_order.delivery_agent.phone }}">☎ Call Rider</a>
                    <a href="https://wa.me/{{ latest_order.delivery_agent.phone }}?text=Hello%20Shopiva%20rider%2C%20I%20am%20checking%20on%20my%20order%20%23{{ latest_order.id }}." target="_blank" rel="noopener">💬 Chat</a>
                    {% else %}
                    <span class="shopiva-rider-no-phone">Rider contact not available</span>
                    {% endif %}
                </div>
            </div>
            {% endif %}
            {% else %}'''
text, rider_count = rider_pattern.subn(new_rider, text, count=1)
if rider_count != 1:
    raise SystemExit("Could not locate customer rider card block")

# Add a polished visual override block, preserving the existing map implementation.
css = r'''
<style id="shopiva-customer-delivery-v3">
.shopiva-timeline-v2{position:relative;padding:4px 2px 4px 0;margin-bottom:18px}
.shopiva-timeline-v2:before{content:"";position:absolute;left:11px;top:15px;bottom:15px;width:2px;background:#d7e4dc}
.shopiva-timeline-v2 .shopiva-step{position:relative;display:flex;gap:12px;border:0;padding:10px 0;min-height:48px}
.shopiva-timeline-v2 .shopiva-step:after{content:"";position:absolute;left:11px;top:37px;height:20px;width:2px;background:#d7e4dc}
.shopiva-timeline-v2 .shopiva-step:last-child:after{display:none}
.shopiva-timeline-v2 .step-dot{position:relative;z-index:2;width:23px;height:23px;flex:0 0 23px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#fff;border:2px solid #9aada4;color:#7b8c85;font-weight:900;font-size:10px;box-shadow:0 0 0 3px #fff}
.shopiva-timeline-v2 .shopiva-step.is-complete .step-dot{background:#0aa66d;border-color:#0aa66d;color:#fff;box-shadow:0 0 0 4px rgba(10,166,109,.10)}
.shopiva-timeline-v2 .shopiva-step.is-active .step-dot{background:#2785ff;border-color:#2785ff;color:#fff;box-shadow:0 0 0 4px rgba(39,133,255,.14)}
.shopiva-timeline-v2 .shopiva-step.is-complete:after{background:#0aa66d}
.shopiva-timeline-v2 .shopiva-step.is-active:after{background:linear-gradient(#2785ff,#d7e4dc)}
.shopiva-timeline-v2 .shopiva-step strong{font-size:12px;color:#16231e;line-height:1.2}
.shopiva-timeline-v2 .shopiva-step small{font-size:10px;color:#708079;margin-top:4px;display:block;line-height:1.35}
.shopiva-rider-card-v2{grid-template-columns:52px 1fr;padding:11px;border-radius:14px;margin-top:4px}
.shopiva-rider-avatar-v2{width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#e7f8f0,#cdeedf);color:#087f5b;border:2px solid #fff;box-shadow:0 3px 12px rgba(12,45,33,.12);font-size:23px;font-weight:900;display:flex;align-items:center;justify-content:center}
.shopiva-rider-main strong{font-size:13px}.shopiva-rider-main span{font-size:11px;color:#5d6c65}.shopiva-rider-main small{font-size:10px;color:#66746d;line-height:1.35}
.shopiva-rider-actions-v2{gap:6px}.shopiva-rider-actions-v2 a{padding:8px 7px;font-size:10px}.shopiva-rider-no-phone{flex:1;text-align:center;padding:8px;border-radius:9px;background:#f3f6f4;color:#6a7871;font-size:10px}
.shopiva-map-bottom{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:9px}.shopiva-map-bottom>div{background:#f8fbfa;border:1px solid #e0e9e4;border-radius:10px;padding:9px}.shopiva-map-bottom strong{display:block;font-size:10px;color:#65746c}.shopiva-map-bottom span{display:block;margin-top:3px;font-size:12px;font-weight:800;color:#19352a}
@media(max-width:850px){.shopiva-map-bottom{grid-template-columns:1fr}.shopiva-delivery-layout{grid-template-columns:1fr}}
</style>
'''
if "shopiva-customer-delivery-v3" not in text:
    text = text.replace('</section>\n\n<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"', '</section>\n' + css + '\n<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"', 1)

TEMPLATE.write_text(text, encoding="utf-8")

# Expose delivered-order count for the rider card without inventing ratings.
if '"delivery_count": delivery_count' not in views:
    target = '    return render(\n        request,\n        "accounts/dashboard.html",\n        {"orders": orders[:5], "latest_order": orders.first()},\n    )'
    replacement = '''    latest_order = orders.first()\n    delivery_count = 0\n    if latest_order and latest_order.delivery_agent:\n        delivery_count = latest_order.delivery_agent.orders.filter(status="delivered").count()\n\n    return render(\n        request,\n        "accounts/dashboard.html",\n        {"orders": orders[:5], "latest_order": latest_order, "delivery_count": delivery_count},\n    )'''
    if target not in views:
        raise SystemExit("Could not locate customer_dashboard context")
    views = views.replace(target, replacement, 1)
    VIEWS.write_text(views, encoding="utf-8")

print("Customer delivery journey v3 applied.")
