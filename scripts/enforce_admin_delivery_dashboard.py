from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADMIN = ROOT / "home/admin.py"
TEMPLATE = ROOT / "home/templates/admin/delivery_map.html"

NEW_METHODS = r'''    def delivery_map(self, request):
        counties = [
            "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Uasin Gishu", "Kiambu",
            "Machakos", "Kajiado", "Nyeri", "Meru", "Kakamega", "Kilifi",
            "Bungoma", "Kericho", "Kisii", "Homa Bay", "Siaya", "Trans Nzoia",
            "Nandi", "Bomet", "Narok", "Laikipia", "Nyandarua", "Murang'a",
            "Embu", "Tharaka Nithi", "Kitui", "Makueni", "Taita Taveta",
            "Kwale", "Lamu", "Tana River", "Garissa", "Wajir", "Mandera",
            "Marsabit", "Isiolo", "Samburu", "Turkana", "West Pokot", "Elgeyo-Marakwet",
            "Baringo", "Vihiga", "Busia", "Migori", "Nyamira", "Kirinyaga",
        ]
        selected_county = request.GET.get("county", "").strip()
        active_qs = Order.objects.select_related("delivery_agent").filter(
            delivery_agent__isnull=False,
            status__in=["confirmed", "paid", "packed", "processing", "shipped", "out_for_delivery"],
        )
        if selected_county:
            active_qs = active_qs.filter(address__icontains=selected_county)
        active_orders = list(active_qs.order_by("-created_at")[:50])

        now = timezone.now()
        rider_qs = DeliveryAgent.objects.filter(is_active=True).select_related("user")
        rider_rows = []
        for agent in rider_qs:
            latest_order = (
                agent.orders.select_related("delivery_agent")
                .exclude(status__in=["cancelled"])
                .order_by("-created_at")
                .first()
            )
            if selected_county and latest_order and selected_county.lower() not in (latest_order.address or "").lower():
                continue
            live = agent.location_is_live
            stale_minutes = None
            if agent.last_location_at:
                stale_minutes = max(0, int((now - agent.last_location_at).total_seconds() // 60))
            rider_rows.append(
                {
                    "agent": agent,
                    "latest_order": latest_order,
                    "live": live,
                    "stale_minutes": stale_minutes,
                }
            )

        active_count = len(active_orders)
        online_count = sum(1 for row in rider_rows if row["agent"].status in {"available", "on_delivery"} and row["live"])
        delayed_count = sum(
            1 for order in active_orders
            if order.delivery_agent and order.delivery_agent.last_location_at and not order.delivery_agent.location_is_live
        )
        on_time_count = max(0, active_count - delayed_count)
        today_deliveries = Order.objects.filter(created_at__date=timezone.localdate(), delivery_agent__isnull=False)

        context = {
            **self.each_context(request),
            "shopiva_stats": self._stats(),
            "delivery_agents": rider_qs,
            "rider_rows": rider_rows,
            "recent_deliveries": active_orders[:8] + list(
                Order.objects.select_related("delivery_agent").filter(delivery_agent__isnull=False).order_by("-created_at")[:8]
            ),
            "counties": counties,
            "selected_county": selected_county,
            "delivery_dashboard": {
                "active": active_count,
                "on_time": on_time_count,
                "delayed": delayed_count,
                "riders_online": online_count,
                "today": today_deliveries.count(),
            },
        }
        return TemplateResponse(request, "admin/delivery_map.html", context)

    def delivery_locations(self, request):
        county = request.GET.get("county", "").strip()
        agents = DeliveryAgent.objects.filter(is_active=True).select_related("user")
        data = []
        for agent in agents:
            if agent.current_latitude is None or agent.current_longitude is None:
                continue
            latest_order = agent.orders.select_related("delivery_agent").exclude(status="cancelled").order_by("-created_at").first()
            address = latest_order.address if latest_order else ""
            if county and county.lower() not in address.lower():
                continue
            data.append(
                {
                    "id": agent.id,
                    "name": agent.display_name,
                    "phone": agent.phone,
                    "vehicle_type": agent.vehicle_type,
                    "vehicle_number": agent.vehicle_number,
                    "status": agent.get_status_display(),
                    "status_code": agent.status,
                    "live": agent.location_is_live,
                    "latitude": float(agent.current_latitude),
                    "longitude": float(agent.current_longitude),
                    "updated": agent.last_location_at.isoformat() if agent.last_location_at else None,
                    "order_id": latest_order.id if latest_order else None,
                    "tracking_code": latest_order.tracking_code if latest_order else "",
                    "order_status": latest_order.get_status_display() if latest_order else "No active order",
                    "address": address[:120],
                }
            )
        return JsonResponse({"agents": data, "updated_at": timezone.now().isoformat()})

'''

text = ADMIN.read_text(encoding="utf-8")
start = text.index("    def delivery_map(self, request):")
end = text.index("    def product_manager(self, request):", start)
ADMIN.write_text(text[:start] + NEW_METHODS + text[end:], encoding="utf-8")

TEMPLATE.write_text(r'''{% extends "admin/base_site.html" %}
{% load i18n %}

{% block title %}Live Delivery Map | Shopiva{% endblock %}

{% block extrastyle %}
{{ block.super }}
<style>
:root{--sd-green:#08a66d;--sd-dark:#0b1720;--sd-ink:#17232d;--sd-muted:#6b7780;--sd-line:#e2e9ed;--sd-blue:#2188ff;--sd-red:#ef4444}
body{background:#f3f6f8}.content,#content{max-width:none!important;padding:0!important}.delivery-shell{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--sd-ink);padding:0 18px 34px}.delivery-top{display:flex;justify-content:space-between;align-items:center;gap:14px;padding:12px 4px 18px}.delivery-title h1{margin:0;font-size:28px;line-height:1.1}.delivery-title p{margin:6px 0 0;color:var(--sd-muted);font-size:12px}.live-chip{display:flex;align-items:center;gap:7px;background:#eafff6;border:1px solid #b9f2d8;color:#06744e;border-radius:999px;padding:8px 11px;font-size:11px;font-weight:900}.live-chip i{width:8px;height:8px;border-radius:50%;background:#12b981;box-shadow:0 0 0 4px rgba(18,185,129,.12)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:13px}.stat{background:#fff;border:1px solid var(--sd-line);border-radius:13px;padding:13px 14px;display:flex;align-items:center;gap:11px;box-shadow:0 6px 20px rgba(25,40,50,.04)}.stat .ico{width:32px;height:32px;border-radius:10px;display:grid;place-items:center;font-size:17px;background:#ecfaf4}.stat .ico.blue{background:#eef5ff}.stat .ico.red{background:#fff0f0}.stat .ico.teal{background:#edfafa}.stat small{display:block;color:#79858d;font-size:9px;text-transform:uppercase;letter-spacing:.04em}.stat strong{display:block;font-size:20px;line-height:1.15;margin-top:3px}
.toolbar{background:#fff;border:1px solid var(--sd-line);border-radius:13px;padding:10px;display:flex;gap:8px;align-items:center;justify-content:space-between;margin-bottom:11px}.toolbar-left{display:flex;gap:8px;align-items:center}.toolbar select{border:1px solid #d7e0e6;border-radius:9px;padding:8px 10px;font-size:11px;background:#fff}.toolbar button,.toolbar a{border:0;border-radius:9px;padding:8px 11px;font-size:11px;font-weight:900;text-decoration:none;cursor:pointer}.toolbar button{background:var(--sd-green);color:#fff}.toolbar a{background:#f5f8fa;color:#33424c;border:1px solid var(--sd-line)}
.main-grid{display:grid;grid-template-columns:minmax(0,1.72fr) minmax(285px,.72fr);gap:12px}.map-panel,.side-panel{background:#fff;border:1px solid var(--sd-line);border-radius:15px;box-shadow:0 8px 25px rgba(25,40,50,.05);overflow:hidden}.map-wrap{height:520px;position:relative;background:#eef3f4}.map{height:100%;width:100%}.map-overlay{position:absolute;z-index:700;top:11px;left:11px;display:flex;gap:7px}.map-overlay span,.map-overlay a{background:rgba(255,255,255,.96);border:1px solid #e3e9ed;border-radius:999px;padding:7px 9px;font-size:10px;font-weight:900;color:#23323d;text-decoration:none;box-shadow:0 4px 12px rgba(0,0,0,.08)}.map-overlay a{color:#06744e}.map-controls{position:absolute;right:11px;top:11px;z-index:700;display:grid;gap:6px}.map-controls button{width:34px;height:34px;border:1px solid #dfe7eb;background:#fff;border-radius:9px;font-size:15px;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,.08)}.legend{position:absolute;left:11px;right:11px;bottom:10px;z-index:700;display:flex;gap:14px;flex-wrap:wrap;background:rgba(255,255,255,.94);border:1px solid #e4ebee;border-radius:10px;padding:8px 10px;font-size:9px;color:#57636b}.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:5px}.green{background:#0ba976}.red{background:#ef4444}.gray{background:#7a8790}.blue{background:#2188ff}
.side-panel{padding:12px}.side-title{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}.side-title h2{font-size:13px;margin:0}.side-title a{font-size:9px;color:#2188ff;text-decoration:none;font-weight:900}.delivery-list{display:grid;gap:7px}.delivery-row,.rider-row{display:grid;grid-template-columns:26px 1fr auto;gap:8px;align-items:center;border:1px solid #edf1f3;border-radius:10px;padding:8px;background:#fff}.mini-truck{width:26px;height:26px;border-radius:8px;background:#edf9f4;display:grid;place-items:center;font-size:13px}.delivery-row strong,.rider-row strong{font-size:10px}.delivery-row small,.rider-row small{display:block;color:#7b878e;font-size:8px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:170px}.badge{padding:5px 7px;border-radius:999px;font-size:8px;font-weight:900;white-space:nowrap}.badge.on{background:#ddfaeb;color:#08764f}.badge.delayed{background:#ffe5e5;color:#c53636}.badge.delivered{background:#e7f0ff;color:#2563eb}.badge.pending{background:#eef1f4;color:#5d6972}.section-gap{height:13px}.rider-row{grid-template-columns:30px 1fr auto}.avatar{width:30px;height:30px;border-radius:50%;display:grid;place-items:center;background:linear-gradient(145deg,#d9efe6,#b9d6cc);font-size:13px}.online{background:#dcfaeb;color:#0b8f61}.offline{background:#eef1f3;color:#6b757d}.map-status{position:absolute;z-index:750;left:50%;top:50%;transform:translate(-50%,-50%);background:rgba(255,255,255,.95);border:1px solid #dfe7ea;border-radius:12px;padding:13px 16px;text-align:center;box-shadow:0 16px 35px rgba(0,0,0,.12);display:none}.map-status.show{display:block}.map-status strong{display:block;font-size:12px}.map-status span{display:block;font-size:9px;color:#6d7a82;margin-top:4px}.bottom-strip{background:#042b24;color:#fff;margin-top:12px;border-radius:13px;padding:15px 18px;display:flex;justify-content:space-between;gap:16px}.bottom-strip strong{font-size:16px}.bottom-strip span{display:block;font-size:9px;color:#b9d7cf;margin-top:3px}
@media(max-width:1050px){.stats{grid-template-columns:repeat(2,1fr)}.main-grid{grid-template-columns:1fr}.map-wrap{height:470px}}@media(max-width:650px){.delivery-shell{padding:0 8px 25px}.stats{grid-template-columns:1fr 1fr}.delivery-top{align-items:flex-start}.toolbar{align-items:flex-start;flex-direction:column}.toolbar-left{width:100%;flex-wrap:wrap}.main-grid{grid-template-columns:1fr}.map-wrap{height:390px}.bottom-strip{flex-direction:column}}
</style>
{% endblock %}

{% block content %}
<div class="delivery-shell">
  <div class="delivery-top">
    <div class="delivery-title"><h1>Live Delivery Map</h1><p>Monitor all Shopiva deliveries across Kenya in real-time.</p></div>
    <div class="live-chip"><i></i> Live operations</div>
  </div>

  <div class="stats">
    <div class="stat"><div class="ico">🚚</div><div><small>Active Deliveries</small><strong id="sd-active">{{ delivery_dashboard.active }}</strong></div></div>
    <div class="stat"><div class="ico blue">●</div><div><small>On Time</small><strong id="sd-ontime">{{ delivery_dashboard.on_time }}</strong></div></div>
    <div class="stat"><div class="ico red">◷</div><div><small>Delayed</small><strong id="sd-delayed">{{ delivery_dashboard.delayed }}</strong></div></div>
    <div class="stat"><div class="ico teal">👤</div><div><small>Riders Online</small><strong id="sd-riders">{{ delivery_dashboard.riders_online }}</strong></div></div>
  </div>

  <form class="toolbar" method="get">
    <div class="toolbar-left">
      <strong style="font-size:11px">Delivery network</strong>
      <select name="county" onchange="this.form.submit()">
        <option value="">All Counties</option>
        {% for county in counties %}<option value="{{ county }}" {% if selected_county == county %}selected{% endif %}>{{ county }}</option>{% endfor %}
      </select>
      <a href="{% url 'shopiva_admin:delivery_map' %}">Reset</a>
    </div>
    <div><button type="button" id="sd-refresh">↻ Refresh</button></div>
  </form>

  <div class="main-grid">
    <section class="map-panel">
      <div class="map-wrap">
        <div id="sd-map" class="map"></div>
        <div class="map-overlay"><span>🇰🇪 Kenya</span><a id="sd-google" href="https://www.google.com/maps/search/?api=1&query=Kenya" target="_blank" rel="noopener">Open Google Maps ↗</a></div>
        <div class="map-controls"><button type="button" id="sd-zoom-in">+</button><button type="button" id="sd-zoom-out">−</button><button type="button" id="sd-home">⌂</button></div>
        <div id="sd-map-status" class="map-status"><strong>Waiting for live rider GPS</strong><span>The map is ready. Rider markers appear when location data is shared.</span></div>
        <div class="legend"><span><i class="dot green"></i>On Time</span><span><i class="dot red"></i>Delayed</span><span><i class="dot gray"></i>Not Started</span><span><i class="dot blue"></i>Delivered</span></div>
      </div>
    </section>

    <aside class="side-panel">
      <div class="side-title"><h2>Recent Deliveries</h2><a href="{% url 'shopiva_admin:home_order_changelist' %}">View All</a></div>
      <div class="delivery-list" id="sd-deliveries">
        {% for order in recent_deliveries|slice:":8" %}
        <div class="delivery-row"><div class="mini-truck">{% if order.status == 'delivered' %}🚚{% elif order.status == 'cancelled' %}⛔{% else %}🚚{% endif %}</div><div><strong>#{{ order.tracking_code|default:order.id }}</strong><small>{{ order.delivery_agent.display_name|default:"Unassigned" }} · {{ order.address|truncatechars:28 }}</small></div><span class="badge {% if order.status == 'delivered' %}delivered{% elif order.status == 'out_for_delivery' %}on{% elif order.status == 'cancelled' %}delayed{% else %}pending{% endif %}">{{ order.get_status_display }}</span></div>
        {% empty %}<p style="font-size:10px;color:#7a858c">No deliveries recorded yet.</p>{% endfor %}
      </div>
      <div class="section-gap"></div>
      <div class="side-title"><h2>Rider Locations</h2><a href="{% url 'shopiva_admin:home_deliveryagent_changelist' %}">View All</a></div>
      <div class="delivery-list" id="sd-riders-list">
        {% for row in rider_rows|slice:":8" %}
        <div class="rider-row"><div class="avatar">🧑🏽</div><div><strong>{{ row.agent.display_name }}</strong><small>{{ row.latest_order.address|truncatechars:28|default:"Kenya" }}</small></div><span class="badge {% if row.live %}online{% else %}offline{% endif %}">{% if row.live %}Online{% else %}Offline{% endif %}</span></div>
        {% empty %}<p style="font-size:10px;color:#7a858c">No active riders configured.</p>{% endfor %}
      </div>
    </aside>
  </div>

  <div class="bottom-strip"><div><strong>Stronger Admin Control</strong><span>Full logistics visibility</span><span>Happier customers</span></div><div><strong>Shopiva Kenya LTD</strong><span>More than a marketplace.</span><span>A smarter Kenya.</span></div></div>
</div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="anonymous">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin="anonymous"></script>
<script>
(function(){
 const el=document.getElementById('sd-map'); if(!el||typeof L==='undefined') return;
 const feedUrl="{% url 'shopiva_admin:delivery_locations' %}" + ("{% if selected_county %}?county={{ selected_county|urlencode }}{% endif %}");
 const home=[-1.2921,36.8219];
 const map=L.map(el,{zoomControl:false,scrollWheelZoom:false,minZoom:5}).setView(home,6);
 L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',{maxZoom:18,attribution:'Tiles © Esri'}).addTo(map);
 L.control.zoom({position:'bottomright'}).addTo(map);
 const markerLayer=L.layerGroup().addTo(map); let first=true;
 const markerIcons={green:L.divIcon({className:'',html:'<div style="width:25px;height:25px;border-radius:50%;background:#0ba976;border:3px solid #fff;box-shadow:0 3px 10px rgba(0,0,0,.25);display:grid;place-items:center;color:#fff;font-size:12px">🚚</div>',iconSize:[25,25],iconAnchor:[12,12]}),red:L.divIcon({className:'',html:'<div style="width:25px;height:25px;border-radius:50%;background:#ef4444;border:3px solid #fff;box-shadow:0 3px 10px rgba(0,0,0,.25);display:grid;place-items:center;color:#fff;font-size:12px">🚚</div>',iconSize:[25,25],iconAnchor:[12,12]})};
 function esc(v){return String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));}
 async function refresh(){
   try{
     const r=await fetch(feedUrl,{credentials:'same-origin',cache:'no-store'}); if(!r.ok) throw new Error('feed');
     const payload=await r.json(); markerLayer.clearLayers();
     let count=0; let online=0; let delayed=0;
     payload.agents.forEach(a=>{
       count++; if(a.live) online++; else delayed++;
       const pos=[Number(a.latitude),Number(a.longitude)];
       const status=a.live?'On time':'Delayed';
       const popup='<strong>'+esc(a.name)+'</strong><br>'+esc(a.vehicle_type||'Delivery vehicle')+(a.vehicle_number?' · '+esc(a.vehicle_number):'')+'<br>'+esc(status)+'<br>'+ (a.tracking_code?'Order '+esc(a.tracking_code)+'<br>':'') +'<a href="https://www.google.com/maps/dir/?api=1&destination='+encodeURIComponent(a.latitude+','+a.longitude)+'" target="_blank" rel="noopener">🧭 Navigate in Google Maps</a>';
       L.marker(pos,{icon:a.live?markerIcons.green:markerIcons.red}).addTo(markerLayer).bindPopup(popup);
       if(first){map.setView(pos,7);first=false;}
     });
     document.getElementById('sd-active').textContent=count;
     document.getElementById('sd-riders').textContent=online;
     document.getElementById('sd-delayed').textContent=delayed;
     document.getElementById('sd-ontime').textContent=Math.max(0,count-delayed);
     document.getElementById('sd-map-status').classList.toggle('show',count===0);
   }catch(e){document.getElementById('sd-map-status').classList.add('show');}
 }
 document.getElementById('sd-refresh')?.addEventListener('click',()=>{first=true;refresh()});
 document.getElementById('sd-zoom-in')?.addEventListener('click',()=>map.zoomIn());
 document.getElementById('sd-zoom-out')?.addEventListener('click',()=>map.zoomOut());
 document.getElementById('sd-home')?.addEventListener('click',()=>map.setView(home,6));
 refresh(); setInterval(refresh,15000); setTimeout(()=>map.invalidateSize(),300);
})();
</script>
{% endblock %}
''', encoding="utf-8")
print("Admin delivery dashboard enforced")
