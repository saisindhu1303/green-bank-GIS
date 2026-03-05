import pandas as pd
import folium
from folium.plugins import MarkerCluster
from jinja2 import Template

# Load data
df = pd.read_excel("Green Innovation Banks.xlsx")

# Create map and cluster group
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
marker_cluster = MarkerCluster().add_to(m)

bank_info = list(zip(df['Name'], df['Address']))

# Add markers to cluster
for idx, bank in df.iterrows():
    contact_html = f'<a href="{bank["Contact"]}" target="_blank">{bank["Contact"]}</a>' if pd.notna(bank["Contact"]) else "N/A"
    popup_html = f"""
    <div style="width: 300px;">
        <strong>{bank['Name']}</strong><br>
        <b>Type:</b> {bank['Type']}<br>
        <b>Focus:</b> {bank['Focus Area']}<br>
        <b>Address:</b> {bank['Address']}<br>
        <b>Contact:</b> {contact_html}
    </div>
    """.replace("\n", "").replace('"', '\\"').strip()

    popup = folium.Popup(popup_html, max_width=300)
    marker = folium.Marker(
        location=[bank['Latitude'], bank['Longitude']],
        popup=popup,
        tooltip=bank['Name'],
        icon=folium.Icon(color="green", icon="leaf")
    )
    marker.add_to(marker_cluster)

map_id = m.get_name()
print("Map variable name:", map_id)

sidebar_template = Template("""
<style>
  #sidebar {
    position: fixed;
    top: 10px;
    left: 10px;
    width: 300px;
    max-height: 90vh;
    overflow-y: auto;
    background: white;
    padding: 10px;
    border: 2px solid gray;
    font-family: Arial, sans-serif;
    font-size: 14px;
    z-index: 9999;
  }
  #sidebar h2 {
    margin-top: 0;
  }
  #sidebar ul {
    list-style: none;
    padding-left: 5px;
  }
  #sidebar li {
    cursor: pointer;
    margin: 7px 0;
    color: darkgreen;
  }
  #sidebar li:hover {
    text-decoration: underline;
  }
</style>

<div id="sidebar">
  <h2>Green Innovation Banks</h2>
  <ul>
    {% for idx, (name, address) in enumerate(bank_info) %}
      <li onclick="zoomToMarker({{ idx }})"><strong>{{ name }}</strong> — {{ address }}</li>
    {% endfor %}
  </ul>
</div>

<script>
  window.addEventListener('load', function() {
    var map = window.{{ map_id }} || {{ map_id }};
    var bankMarkers = [];

    // Find the MarkerClusterGroup layer on the map
    var markerClusterGroup = null;
    map.eachLayer(function(layer){
      if(layer instanceof L.MarkerClusterGroup){
        markerClusterGroup = layer;
      }
    });

    if(markerClusterGroup === null){
      console.error("MarkerClusterGroup not found!");
      return;
    }

    // Get all markers inside the cluster group
    bankMarkers = [];
    markerClusterGroup.eachLayer(function(layer){
      if(layer instanceof L.Marker){
        bankMarkers.push(layer);
      }
    });

    console.log("Collected markers from cluster group:", bankMarkers.length);

    window.zoomToMarker = function(idx){
      if(bankMarkers.length === 0){
        alert("Markers not loaded yet, please wait a moment and try again.");
        return;
      }
      var marker = bankMarkers[idx];
      if(marker){
        map.setView(marker.getLatLng(), 13);
        marker.openPopup();
      }
    }
  });
</script>
""")

sidebar_html = sidebar_template.render(
    bank_info=bank_info,
    map_id=map_id,
    enumerate=enumerate
)

m.get_root().html.add_child(folium.Element(sidebar_html))

m.save("clean_energy_banks_map_with_sidebar.html")
print("Map saved as 'clean_energy_banks_map_with_sidebar.html'")
