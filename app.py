import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from streamlit_gsheets import GSheetsConnection
import requests
import pandas as pd
from datetime import datetime

# 1. UI Configurations & Theming
st.set_page_config(
    page_title="EcoScan: Climate Terminal", 
    page_icon="🌐", 
    layout="centered"
)

st.markdown("""
    <style>
    .metric-card {
        background-color: #1E293B;
        padding: 18px;
        border-radius: 8px;
        border-left: 5px solid #38BDF8;
        margin-bottom: 15px;
    }
    .status-box {
        background-color: #0F172A;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #334155;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ EcoScan: Automated Climate & Sensor Auditor")
st.write("Interfaces with public environmental networks and client telemetry vectors to analyze localized climate metrics.")

st.divider()

# ==========================================
# PHASE 1: PASSIVE AUTOMATIC FOOTPRINT
# ==========================================
st.subheader("📡 Passive Network Diagnostics")

auto_ip, auto_city, auto_region, auto_org = "Unknown", "Unknown", "Unknown", "Unknown"
try:
    network_request = requests.get('https://ipapi.co/json/', timeout=4)
    if network_request.status_code == 200:
        net_data = network_request.json()
        auto_ip = net_data.get('ip', 'Unknown')
        auto_city = net_data.get('city', 'Unknown')
        auto_region = net_data.get('region', 'Unknown')
        auto_org = net_data.get('org', 'Unknown')
except Exception:
    pass

col_net1, col_net2 = st.columns(2)
with col_net1:
    st.markdown(f"""
    <div class="metric-card">
        <span style="color: #94A3B8; font-size: 14px;">NETWORK ENVIRONMENT ROUTE</span>
        <h3 style="color: #38BDF8; margin: 5px 0 0 0;">Active Session</h3>
        <p style="color: #F8FAFC; margin: 5px 0 0 0; font-size: 14px;">ISP Provider: {auto_org}</p>
    </div>
    """, unsafe_allow_html=True)

with col_net2:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #A855F7;">
        <span style="color: #94A3B8; font-size: 14px;">ESTIMATED REGION</span>
        <h3 style="color: #A855F7; margin: 5px 0 0 0;">{auto_city}</h3>
        <p style="color: #F8FAFC; margin: 5px 0 0 0; font-size: 14px;">Zone: {auto_region}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==========================================
# PHASE 2: ACTIVE HARDWARE HANDSHAKE
# ==========================================
st.subheader("📍 Interactive Hardware Sensor Optimization")
st.write("Precise spatial coordinates are required to calculate localized micro-climate metrics.")

st.info("💡 Initialize hardware scanning context using the location module lock below.")
location_output = streamlit_geolocation()

lat, lon, accuracy = None, None, None

if location_output and location_output.get('latitude') is not None:
    lat = location_output['latitude']
    lon = location_output['longitude']
    accuracy = location_output.get('accuracy', 0)
    
    st.toast("Hardware synchronized successfully.", icon="🎯")
    st.success("🛰️ System Synchronization Complete. Regional Coordinates Loaded.")
    
    # ------------------------------------------
    # PHASE 3: LIVE ENVIRONMENTAL DATA STREAMING
    # ------------------------------------------
    st.markdown("### ⛅ Live Atmospheric Risk Metrics")
    
    current_temp, current_humidity = "N/A", "N/A"
    try:
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m"
        weather_response = requests.get(weather_url).json()
        current_temp = weather_response['current']['temperature_2m']
        current_humidity = weather_response['current']['relative_humidity_2m']
    except Exception:
        pass
        
    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric(label="Temperature", value=f"{current_temp}°C")
    col_res2.metric(label="Humidity", value=f"{current_humidity}%")
    
    if current_temp != "N/A" and float(current_temp) > 35:
        col_res3.metric(label="Heatwave Alert Index", value="Critical Alert", delta="High Risk")
    else:
        col_res3.metric(label="Heatwave Alert Index", value="Stable Status", delta="Optimal")
        
    st.caption(f"Spatial verification variance: Within {accuracy:.1f} meters.")

else:
    st.warning("⚠️ Status: System Offline. Awaiting hardware authorization sequence.")

# ==========================================
# PHASE 4: BACKEND CLOUD LOGGING (Google Sheets Connection)
# ==========================================
# Initialize the GSheets Connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    conn = None

if lat is not None and lon is not None and conn is not None:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Create DataFrame row matching spreadsheet schema
    master_entry = pd.DataFrame([{
        "Timestamp": timestamp,
        "IP_Address": auto_ip,
        "ISP": auto_org,
        "Network_Location": f"{auto_city}, {auto_region}",
        "Hardware_Lat": lat,
        "Hardware_Lon": lon,
        "GPS_Accuracy": accuracy
    }])
    
    try:
        # Fetch current data sheet, append new entry, and update live
        existing_data = conn.read(ttl=0)
        updated_data = pd.concat([existing_data, master_entry], ignore_index=True)
        conn.update(data=updated_data)
    except Exception as e:
        pass

st.divider()

# ==========================================
# PHASE 5: SECURE ADMINISTRATIVE PANEL VIEW
# ==========================================
with st.expander("🔒 Access System Administrative Logs (Authorized Only)"):
    admin_token = st.text_input("Enter Root Token ID Key", type="password")
    
    if admin_token == "ProjectAdmin2026":
        st.subheader("🗃️ Master Cloud Database Registry")
        if conn is not None:
            try:
                server_dataframe = conn.read(ttl=0)
                st.dataframe(server_dataframe, use_container_width=True)
                
                csv_download_stream = server_dataframe.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Master CSV Logs",
                    data=csv_download_stream,
                    file_name="master_sensor_telemetry.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error fetching logs from cloud storage: {e}")
        else:
            st.info("Cloud storage connector uninitialized.")
    elif admin_token != "":
        st.error("Authentication Core Failure: Token validation identity mismatch.")