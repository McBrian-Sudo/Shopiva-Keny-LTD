from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VIEWS = ROOT / "home" / "views.py"
MAP = ROOT / "home" / "templates" / "includes" / "delivery_network_map.html"

views = VIEWS.read_text(encoding="utf-8")
map_text = MAP.read_text(encoding="utf-8")
changed = False

old_vehicle_block = '''        "name": agent.display_name,\n        "status": agent.get_status_display(),\n        "latitude": float(agent.current_latitude) if agent.current_latitude is not None else None,'''
new_vehicle_block = '''        "name": agent.display_name,\n        "vehicle_number": agent.vehicle_number or "",\n        "status": agent.get_status_display(),\n        "latitude": float(agent.current_latitude) if agent.current_latitude is not None else None,'''
if old_vehicle_block in views:
    views = views.replace(old_vehicle_block, new_vehicle_block, 1)
    changed = True

old_box = '''<div id="shopiva-customer-agent-box" class="shopiva-agent-box"><strong>🚚 Delivery partner</strong><span>{{ latest_order.delivery_agent.display_name }}</span><small id="shopiva-customer-agent-status">{% if latest_order.delivery_agent.last_location_at %}Last GPS: {{ latest_order.delivery_agent.last_location_at|date:"d M Y, H:i" }}{% else %}GPS not shared yet{% endif %}</small></div>'''
new_box = '''<div id="shopiva-customer-agent-box" class="shopiva-agent-box">\n    <strong>🚚 Delivery partner</strong>\n    <span>👤 {{ latest_order.delivery_agent.display_name }}</span>\n    <span>🚐 {% if latest_order.delivery_agent.vehicle_number %}{{ latest_order.delivery_agent.vehicle_number }}{% else %}Vehicle details not added yet{% endif %}</span>\n    <small id="shopiva-customer-agent-status">{% if latest_order.delivery_agent.last_location_at %}Last GPS: {{ latest_order.delivery_agent.last_location_at|date:"d M Y, H:i" }}{% else %}GPS not shared yet{% endif %}</small>\n</div>'''
if old_box in map_text:
    map_text = map_text.replace(old_box, new_box, 1)
    changed = True

old_popup = """            const popup = '<strong>' + agent.name + '</strong><br>' +\n                agent.status + '<br>' + liveLabel +\n                (agent.updated ? '<br>Updated: ' + new Date(agent.updated).toLocaleString() : '');"""
new_popup = """            const vehicle = agent.vehicle_number ? '<br>🚐 ' + agent.vehicle_number : '';\n            const popup = '<strong>' + agent.name + '</strong>' + vehicle + '<br>' +\n                agent.status + '<br>' + liveLabel +\n                (agent.updated ? '<br>Updated: ' + new Date(agent.updated).toLocaleString() : '');"""
if old_popup in map_text:
    map_text = map_text.replace(old_popup, new_popup, 1)
    changed = True

old_refresh_status = """                if (payload.agent.live && payload.agent.updated) {\n                    customerStatus.textContent = 'Live GPS · updated ' + new Date(payload.agent.updated).toLocaleTimeString();"""
new_refresh_status = """                if (payload.agent.live && payload.agent.updated) {\n                    const vehicle = payload.agent.vehicle_number ? ' · 🚐 ' + payload.agent.vehicle_number : '';\n                    customerStatus.textContent = 'Live GPS · updated ' + new Date(payload.agent.updated).toLocaleTimeString() + vehicle;"""
if old_refresh_status in map_text:
    map_text = map_text.replace(old_refresh_status, new_refresh_status, 1)
    changed = True

VIEWS.write_text(views, encoding="utf-8")
MAP.write_text(map_text, encoding="utf-8")
print("Customer delivery vehicle details enhanced." if changed else "Customer delivery vehicle details already enhanced.")
