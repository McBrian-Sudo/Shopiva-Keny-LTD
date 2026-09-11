from pathlib import Path

TEMPLATE = r'''<section class="shopiva-map-card {% if delivery_admin_mode %}shopiva-map-admin{% endif %}">
  <div class="shopiva-map-head">
    <div>
      <span class="shopiva-map-kicker">SHOPIVA SMART DELIVERY NETWORK</span>
      <h2>{% if delivery_admin_mode %}Kenya Delivery Command Map{% else %}Your Delivery in Real-Time{% endif %}</h2>
      <p>{% if delivery_admin_mode %}Monitor delivery partners, routes and the latest GPS positions.{% else %}Follow your order journey, rider location, route and delivery progress from one place.{% endif %}</p>
    </div>
    <div id="shopiva-map-live-label" class="shopiva-map-live"><span></span>{% if delivery_admin_mode %}Operations Live{% else %}Tracking Ready{% endif %}</div>
  </div>

  {% if delivery_admin_mode %}
  <div class="gm-admin-grid">
    <div class="gm-map-wrap">
      <div id="shopiva-live-map" class="gm-map"></div>
      <div class="gm-map-toolbar"><span>🇰🇪 Kenya</span><a id="gm-admin-google-link" href="https://www.google.com/maps/search/?api=1&query=Kenya" target="_blank" rel="noopener">Open Google Maps ↗</a></div>
      <div id="shopiva-map-provider-error" class="shopiva-map-provider-error" hidden><strong>Map tiles temporarily unavailable</strong><span>Google Maps links remain available.</span></div>
    </div>
    <aside class="gm-side">
      <div class="gm-stat"><span>📦 Total orders</span><strong>{{ shopiva_stats.orders }}</strong></div>
      <div class="gm-stat"><span>🚚 In fulfilment</span><strong>{{ shopiva_stats.processing_orders }}</strong></div>
      <div class="gm-stat"><span>👤 Assigned</span><strong>{{ shopiva_stats.assigned_orders }}</strong></div>
      <div class="gm-stat"><span>✅ Delivered</span><strong>{{ shopiva_stats.delivered_orders }}</strong></div>
      <div class="gm-section-title"><h3>Delivery partners</h3><span>Live feed</span></div>
      <div class="gm-agent-list">
        {% for agent in delivery_agents %}
        <div class="gm-agent" data-agent-name="{{ agent.display_name }}">
          <div><strong>{{ agent.display_name }}</strong><span>{{ agent.get_status_display }}{% if agent.vehicle_number %} · {{ agent.vehicle_number }}{% endif %}</span></div>
          <div class="gm-agent-right"><small>{% if agent.last_location_at %}GPS {{ agent.last_location_at|date:"H:i" }}{% else %}No GPS yet{% endif %}</small></div>
        </div>
        {% empty %}
        <p class="gm-empty">No delivery partners are configured yet.</p>
        {% endfor %}
      </div>
    </aside>
  </div>
  {% else %}
  <div class="gm-customer-grid">
    <aside class="gm-delivery-panel">
      {% if latest_order %}
        <div class="gm-order-chip">Order {{ latest_order.tracking_code|default:"#"|add:latest_order.id|stringformat:"s" }}</div>
        <div class="gm-timeline">
          {% for event in latest_order.events.all|slice:":8" %}
          <div class="gm-step {% if forloop.first %}is-active{% endif %}">
            <span class="gm-step-dot">{% if forloop.first %}●{% else %}✓{% endif %}</span>
            <div><strong>{{ event.get_event_type_display }}</strong><small>{{ event.created_at|date:"d M Y, H:i" }}{% if event.note %} · {{ event.note }}{% endif %}</small></div>
          </div>
          {% empty %}
          <div class="gm-step is-active"><span class="gm-step-dot">✓</span><div><strong>Order Confirmed</strong><small>We are preparing your delivery.</small></div></div>
          {% endfor %}
        </div>
        {% if latest_order.delivery_agent %}
        <div class="gm-rider-card">
          <div class="gm-rider-avatar">🚚</div>
          <div class="gm-rider-main"><strong>{{ latest_order.delivery_agent.display_name }}</strong><span>Trusted Shopiva Delivery Partner</span><small>{% if latest_order.delivery_agent.vehicle_type %}🏍️ {{ latest_order.delivery_agent.vehicle_type }}{% endif %}{% if latest_order.delivery_agent.vehicle_number %} · {{ latest_order.delivery_agent.vehicle_number }}{% endif %}</small><small id="shopiva-customer-agent-status">{% if latest_order.delivery_agent.last_location_at %}Last GPS: {{ latest_order.delivery_agent.last_location_at|date:"d M Y, H:i" }}{% else %}GPS not shared yet{% endif %}</small></div>
          {% if latest_order.delivery_agent.phone %}<div class="gm-rider-actions"><a href="tel:{{ latest_order.delivery_agent.phone }}">📞 Call Rider</a><a href="https://wa.me/{{ latest_order.delivery_agent.phone }}" target="_blank" rel="noopener">💬 Chat</a></div>{% endif %}
        </div>
        {% endif %}
      {% else %}
        <div class="gm-order-chip">No active order yet</div>
        <h3>Your delivery journey starts here</h3>
        <p>Place an order and Shopiva will connect it to fulfilment, rider tracking and delivery updates.</p>
        <a class="gm-shop-button" href="/products/">Start Shopping →</a>
      {% endif %}
    </aside>

    <div class="gm-map-column">
      <div class="gm-map-wrap">
        <div id="shopiva-live-map" class="gm-map"></div>
        <div class="gm-map-toolbar"><span>🇰🇪 Kenya</span><span id="gm-live-pill">📍 Live Tracking</span><a id="gm-customer-google-link" href="https://www.google.com/maps/search/?api=1&query=Kenya" target="_blank" rel="noopener">Google Maps ↗</a></div>
        <div id="shopiva-map-empty-state" class="gm-map-empty"><div class="gm-map-empty-icon">📡</div><strong>Waiting for live delivery GPS</strong><span>Your rider will appear here as soon as the delivery workspace shares a location.</span></div>
        <div id="shopiva-map-provider-error" class="shopiva-map-provider-error" hidden><strong>Map tiles temporarily unavailable</strong><span>The delivery tracker is still active. You can continue in Google Maps.</span></div>
        <div class="gm-map-legend"><span><i class="legend-dot customer"></i>Your Location</span><span><i class="legend-dot rider"></i>Rider Location</span><span><i class="legend-line"></i>Delivery Route</span><span>🏠 Delivery Address</span></div>
      </div>
      {% if latest_order %}
      <div class="gm-map-bottom"><div><strong>Distance to rider</strong><span id="shopiva-distance-value">Waiting for location…</span></div><div><strong>Estimated arrival</strong><span id="shopiva-eta-value">Waiting for rider GPS…</span></div><div><strong>Order status</strong><span>{{ latest_order.get_status_display }}</span></div></div>
      {% endif %}
    </div>
  </div>
  {% endif %}
</section>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="anonymous">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin="anonymous"></script>
<script>
(function(){
  const mapEl=document.getElementById('shopiva-live-map');
  if(!mapEl||typeof L==='undefined') return;
  const isAdmin={{ delivery_admin_mode|yesno:"true,false" }};
  const feedUrl=isAdmin?"{% url 'shopiva_admin:delivery_locations' %}":"{% url 'customer_delivery_location' %}";
  const errorBox=document.getElementById('shopiva-map-provider-error');
  const empty=document.getElementById('shopiva-map-empty-state');
  const livePill=document.getElementById('gm-live-pill');
  const map=L.map(mapEl,{scrollWheelZoom:false,zoomControl:true,minZoom:3}).setView([-1.286389,36.817223],11);
  const base=L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map);
  base.on('tileerror',()=>{if(errorBox)errorBox.hidden=false;});
  const riderMarkers=[];const customerMarkers=[];const routeLayers=[];let customerLocation=null;let firstFix=true;
  const riderIcon=L.divIcon({className:'shopiva-rider-marker',html:'🚚',iconSize:[40,40],iconAnchor:[20,20]});
  const customerIcon=L.divIcon({className:'shopiva-customer-marker',html:'📍',iconSize:[34,34],iconAnchor:[17,30]});
  function clear(list){list.forEach(m=>map.removeLayer(m));list.length=0;}
  function clearRoutes(){routeLayers.forEach(l=>map.removeLayer(l));routeLayers.length=0;}
  function hav(a,b){const R=6371,dLat=(b[0]-a[0])*Math.PI/180,dLon=(b[1]-a[1])*Math.PI/180,la1=a[0]*Math.PI/180,la2=b[0]*Math.PI/180;const x=Math.sin(dLat/2)**2+Math.sin(dLon/2)**2*Math.cos(la1)*Math.cos(la2);return R*2*Math.atan2(Math.sqrt(x),Math.sqrt(1-x));}
  function mapsSearch(lat,lng){return 'https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(lat+','+lng);}
  function mapsDirections(lat,lng){return 'https://www.google.com/maps/dir/?api=1&destination='+encodeURIComponent(lat+','+lng);}
  function renderPayload(p){
    clear(riderMarkers);clearRoutes();
    const agents=isAdmin?(p.agents||[]):(p.agent?[p.agent]:[]);const pts=[];
    agents.forEach(a=>{
      if(a.latitude==null||a.longitude==null)return;
      const lat=Number(a.latitude),lng=Number(a.longitude),pt=[lat,lng];pts.push(pt);
      const google=mapsSearch(lat,lng);const directions=mapsDirections(lat,lng);
      const popup='<strong>'+String(a.name||'Shopiva Rider').replace(/</g,'&lt;')+'</strong>'+(a.vehicle_number?'<br>🚐 '+String(a.vehicle_number).replace(/</g,'&lt;'):'')+'<br>'+String(a.status||'On delivery').replace(/</g,'&lt;')+(a.live?'<br>🟢 LIVE GPS':'<br>Last known position')+'<br><a href="'+directions+'" target="_blank" rel="noopener">🧭 Get directions in Google Maps</a>';
      riderMarkers.push(L.marker(pt,{icon:riderIcon}).addTo(map).bindPopup(popup));
      if(isAdmin){const btn=document.getElementById('gm-admin-google-link');if(btn&&!btn.dataset.locked){btn.href=google;btn.dataset.locked='1';}}
    });
    if(!isAdmin&&customerLocation&&agents[0]?.latitude!=null){
      const rider=[Number(agents[0].latitude),Number(agents[0].longitude)];
      clear(customerMarkers);customerMarkers.push(L.marker(customerLocation,{icon:customerIcon}).addTo(map).bindPopup('📍 Your current location'));
      routeLayers.push(L.polyline([customerLocation,rider],{color:'#059669',weight:5,opacity:.9,dashArray:'10 8'}).addTo(map));
      const km=hav(customerLocation,rider);const dist=document.getElementById('shopiva-distance-value');if(dist)dist.textContent=km<1?Math.round(km*1000)+' m':km.toFixed(1)+' km';
      const speed=Number(agents[0].speed_mps||0);const eta=document.getElementById('shopiva-eta-value');if(eta)eta.textContent=speed>1?Math.max(1,Math.ceil(km*1000/speed/60))+' min':'Calculating…';
      const link=document.getElementById('gm-customer-google-link');if(link)link.href=mapsDirections(rider[0],rider[1]);
      if(livePill)livePill.textContent=agents[0].live?'🟢 Rider Live':'📍 Tracking Ready';
      const status=document.getElementById('shopiva-customer-agent-status');if(status&&p.agent){status.textContent=p.agent.live&&p.agent.updated?'🟢 Live GPS · updated '+new Date(p.agent.updated).toLocaleTimeString():(p.agent.updated?'Last GPS: '+new Date(p.agent.updated).toLocaleString():'GPS not shared yet');}
    }
    if(empty)empty.hidden=pts.length>0;
    if(pts.length&&firstFix){map.setView(pts[0],14);firstFix=false;}
  }
  async function fetchData(){try{const r=await fetch(feedUrl,{credentials:'same-origin',cache:'no-store'});if(!r.ok)throw new Error('GPS feed unavailable');renderPayload(await r.json());}catch(e){if(errorBox)errorBox.hidden=false;}}
  if(!isAdmin&&navigator.geolocation){navigator.geolocation.getCurrentPosition(pos=>{customerLocation=[pos.coords.latitude,pos.coords.longitude];customerMarkers.push(L.marker(customerLocation,{icon:customerIcon}).addTo(map).bindPopup('📍 Your current location'));fetchData();},()=>fetchData(),{enableHighAccuracy:true,timeout:8000,maximumAge:30000});}else fetchData();
  setInterval(fetchData,15000);setTimeout(()=>map.invalidateSize(),250);
})();
</script>
<style>
.shopiva-map-card{margin-top:18px;background:#fff;border:1px solid #dce7e1;border-radius:24px;padding:20px;box-shadow:0 14px 36px rgba(16,24,40,.07);overflow:hidden}.shopiva-map-head{display:flex;justify-content:space-between;gap:18px;margin-bottom:16px}.shopiva-map-kicker{font-size:10px;font-weight:900;letter-spacing:.14em;color:#059669}.shopiva-map-head h2{margin:5px 0 4px;font-size:25px}.shopiva-map-head p{margin:0;color:#68766f;font-size:13px}.shopiva-map-live{display:flex;align-items:center;gap:7px;background:#ecfdf5;color:#047857;border:1px solid #bbf7d0;padding:8px 12px;border-radius:999px;font-size:11px;font-weight:900;white-space:nowrap;height:max-content}.shopiva-map-live span{width:8px;height:8px;border-radius:50%;background:#10b981;box-shadow:0 0 0 4px rgba(16,185,129,.13)}.gm-admin-grid,.gm-customer-grid{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(260px,.65fr);gap:16px}.gm-customer-grid{grid-template-columns:minmax(280px,.72fr) minmax(0,1.65fr)}.gm-map-column{min-width:0}.gm-map-wrap{height:420px;min-height:360px;position:relative;border-radius:18px;overflow:hidden;border:1px solid #dce7e1;background:#eef5f1}.gm-map{height:100%;width:100%}.gm-map-toolbar{position:absolute;z-index:600;top:13px;left:13px;right:13px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;pointer-events:none}.gm-map-toolbar>*{pointer-events:auto;background:rgba(255,255,255,.95);border:1px solid #dfe9e3;border-radius:999px;padding:7px 10px;font-size:11px;font-weight:800;box-shadow:0 4px 12px rgba(0,0,0,.08);color:#23332c;text-decoration:none}.gm-map-toolbar a{color:#047857}.gm-side,.gm-delivery-panel{background:#f8fbfa;border:1px solid #e2ece7;border-radius:18px;padding:15px}.gm-stat{display:flex;justify-content:space-between;gap:10px;padding:11px 0;border-bottom:1px solid #e7efeb}.gm-stat:last-of-type{border-bottom:0}.gm-stat span{font-size:12px;color:#53635b}.gm-stat strong{font-size:19px}.gm-section-title{display:flex;justify-content:space-between;align-items:center;margin-top:14px}.gm-section-title h3{margin:0;font-size:14px}.gm-section-title span{font-size:10px;color:#0a8d67;background:#e9f9f2;border-radius:999px;padding:5px 8px}.gm-agent-list{margin-top:8px}.gm-agent{display:flex;justify-content:space-between;gap:10px;padding:10px;border-top:1px solid #e7efeb}.gm-agent strong{display:block;font-size:12px}.gm-agent span,.gm-agent small{display:block;color:#68766f;font-size:10px;margin-top:3px}.gm-empty{font-size:11px;color:#718078}.gm-order-chip{display:inline-block;background:#e7f8f0;color:#087f5b;border:1px solid #c6e9d8;border-radius:999px;padding:6px 9px;font-size:11px;font-weight:900;margin-bottom:12px}.gm-delivery-panel h3{font-size:19px;margin:9px 0}.gm-delivery-panel>p{font-size:12px;line-height:1.5;color:#62716a}.gm-timeline{margin-bottom:16px}.gm-step{display:flex;gap:10px;padding:10px 0;border-bottom:1px solid #e7efeb}.gm-step:last-child{border-bottom:0}.gm-step-dot{width:23px;height:23px;border-radius:50%;background:#e7efeb;color:#586760;display:flex;align-items:center;justify-content:center;font-size:10px;flex:0 0 auto}.gm-step.is-active .gm-step-dot{background:#10b981;color:#fff;box-shadow:0 0 0 4px rgba(16,185,129,.12)}.gm-step strong{display:block;font-size:12px}.gm-step small{display:block;color:#6d7a73;font-size:10px;margin-top:3px;line-height:1.4}.gm-rider-card{background:#fff;border:1px solid #dae7e0;border-radius:15px;padding:12px;display:grid;grid-template-columns:42px 1fr;gap:10px}.gm-rider-avatar{width:42px;height:42px;border-radius:12px;background:#e7f8f0;display:flex;align-items:center;justify-content:center;font-size:21px}.gm-rider-main strong{display:block;font-size:13px}.gm-rider-main span,.gm-rider-main small{display:block;color:#6d7a73;font-size:10px;margin-top:3px}.gm-rider-actions{grid-column:1/-1;display:flex;gap:7px}.gm-rider-actions a{flex:1;text-align:center;text-decoration:none;background:#059669;color:#fff;padding:8px;border-radius:9px;font-size:11px;font-weight:900}.gm-rider-actions a+a{background:#fff;color:#26352f;border:1px solid #ccd9d2}.gm-shop-button{display:block;text-align:center;text-decoration:none;background:#059669;color:#fff;border-radius:10px;padding:11px;font-weight:900;font-size:12px}.gm-map-empty,.shopiva-map-provider-error{position:absolute;z-index:550;left:50%;top:50%;transform:translate(-50%,-50%);width:min(330px,78%);background:rgba(255,255,255,.96);border:1px solid #dce8e1;border-radius:16px;padding:17px;text-align:center;box-shadow:0 18px 35px rgba(16,24,40,.12)}.gm-map-empty-icon{font-size:28px;margin-bottom:7px}.gm-map-empty strong,.shopiva-map-provider-error strong{display:block;font-size:13px}.gm-map-empty span,.shopiva-map-provider-error span{display:block;color:#6c7a73;font-size:10px;line-height:1.45;margin-top:5px}.shopiva-map-provider-error{border-color:#fed7aa}.gm-map-legend{position:absolute;z-index:600;left:10px;right:10px;bottom:10px;display:flex;flex-wrap:wrap;gap:12px;background:rgba(255,255,255,.94);border:1px solid #dfe9e3;border-radius:11px;padding:8px 10px;color:#46564e;font-size:10px}.legend-dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px}.legend-dot.customer{background:#2563eb}.legend-dot.rider{background:#10b981}.legend-line{display:inline-block;width:18px;border-top:3px dashed #059669;margin-right:5px;vertical-align:middle}.gm-map-bottom{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:9px}.gm-map-bottom>div{border:1px solid #e0e9e4;border-radius:12px;padding:10px;background:#fbfdfc}.gm-map-bottom strong,.gm-map-bottom span{display:block}.gm-map-bottom strong{font-size:10px;color:#637069}.gm-map-bottom span{font-size:12px;font-weight:800;margin-top:3px}.shopiva-rider-marker,.shopiva-customer-marker{background:none;border:0;font-size:30px;text-align:center}.leaflet-popup-content{font-family:Arial,sans-serif;font-size:11px;line-height:1.45}.leaflet-popup-content a{color:#047857;font-weight:800}.leaflet-control-zoom a{font-weight:900}@media(max-width:900px){.gm-admin-grid,.gm-customer-grid{grid-template-columns:1fr}.gm-map-wrap{height:380px}}@media(max-width:560px){.shopiva-map-card{padding:14px}.shopiva-map-head{flex-direction:column}.gm-map-wrap{height:350px}.gm-map-bottom{grid-template-columns:1fr}.gm-rider-actions{flex-direction:column}}
</style>
'''

path = Path("home/templates/includes/delivery_network_map.html")
path.write_text(TEMPLATE, encoding="utf-8")
print("Keyless delivery maps template installed.")
