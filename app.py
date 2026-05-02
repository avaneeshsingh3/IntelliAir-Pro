import base64
import hmac
import json
import math
import os
import hashlib
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from pymongo import GEOSPHERE, MongoClient
from pymongo.errors import PyMongoError
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from streamlit_folium import st_folium


OPENWEATHER_GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
OPENWEATHER_AIR_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

CITY_DATA = {
    "Adilabad": {"state": "Telangana", "lat": 19.6641, "lon": 78.5320},
    "Agartala": {"state": "Tripura", "lat": 23.8315, "lon": 91.2868},
    "Agra": {"state": "Uttar Pradesh", "lat": 27.1767, "lon": 78.0081},
    "Ahmedabad": {"state": "Gujarat", "lat": 23.0225, "lon": 72.5714},
    "Aizawl": {"state": "Mizoram", "lat": 23.7307, "lon": 92.7173},
    "Ajmer": {"state": "Rajasthan", "lat": 26.4499, "lon": 74.6399},
    "Alappuzha": {"state": "Kerala", "lat": 9.4981, "lon": 76.3388},
    "Aligarh": {"state": "Uttar Pradesh", "lat": 27.8974, "lon": 78.0880},
    "Ambala": {"state": "Haryana", "lat": 30.3782, "lon": 76.7767},
    "Amravati": {"state": "Maharashtra", "lat": 20.9374, "lon": 77.7796},
    "Amritsar": {"state": "Punjab", "lat": 31.6340, "lon": 74.8723},
    "Anantapur": {"state": "Andhra Pradesh", "lat": 14.6819, "lon": 77.6006},
    "Anantnag": {"state": "Jammu and Kashmir", "lat": 33.7311, "lon": 75.1487},
    "Arrah": {"state": "Bihar", "lat": 25.5560, "lon": 84.6603},
    "Asansol": {"state": "West Bengal", "lat": 23.6739, "lon": 86.9524},
    "Aurangabad": {"state": "Maharashtra", "lat": 19.8762, "lon": 75.3433},
    "Ayodhya": {"state": "Uttar Pradesh", "lat": 26.7922, "lon": 82.1998},
    "Balasore": {"state": "Odisha", "lat": 21.4934, "lon": 86.9135},
    "Baramulla": {"state": "Jammu and Kashmir", "lat": 34.2090, "lon": 74.3429},
    "Bareilly": {"state": "Uttar Pradesh", "lat": 28.3670, "lon": 79.4304},
    "Bathinda": {"state": "Punjab", "lat": 30.2110, "lon": 74.9455},
    "Begusarai": {"state": "Bihar", "lat": 25.4182, "lon": 86.1272},
    "Belagavi": {"state": "Karnataka", "lat": 15.8497, "lon": 74.4977},
    "Bengaluru": {"state": "Karnataka", "lat": 12.9716, "lon": 77.5946},
    "Berhampur": {"state": "Odisha", "lat": 19.3149, "lon": 84.7941},
    "Bhagalpur": {"state": "Bihar", "lat": 25.2425, "lon": 86.9842},
    "Bharatpur": {"state": "Rajasthan", "lat": 27.2152, "lon": 77.5030},
    "Bhilai": {"state": "Chhattisgarh", "lat": 21.1938, "lon": 81.3509},
    "Bhiwani": {"state": "Haryana", "lat": 28.7975, "lon": 76.1322},
    "Bhopal": {"state": "Madhya Pradesh", "lat": 23.2599, "lon": 77.4126},
    "Bhubaneswar": {"state": "Odisha", "lat": 20.2961, "lon": 85.8245},
    "Bhuj": {"state": "Gujarat", "lat": 23.2419, "lon": 69.6669},
    "Bidar": {"state": "Karnataka", "lat": 17.9104, "lon": 77.5199},
    "Bikaner": {"state": "Rajasthan", "lat": 28.0229, "lon": 73.3119},
    "Bilaspur": {"state": "Chhattisgarh", "lat": 22.0797, "lon": 82.1409},
    "Bokaro": {"state": "Jharkhand", "lat": 23.6693, "lon": 86.1511},
    "Chandigarh": {"state": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
    "Chennai": {"state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707},
    "Churachandpur": {"state": "Manipur", "lat": 24.3335, "lon": 93.6690},
    "Coimbatore": {"state": "Tamil Nadu", "lat": 11.0168, "lon": 76.9558},
    "Cuddalore": {"state": "Tamil Nadu", "lat": 11.7447, "lon": 79.7680},
    "Cuttack": {"state": "Odisha", "lat": 20.4625, "lon": 85.8828},
    "Dadra": {"state": "Dadra and Nagar Haveli and Daman and Diu", "lat": 20.3255, "lon": 72.9662},
    "Daman": {"state": "Dadra and Nagar Haveli and Daman and Diu", "lat": 20.3974, "lon": 72.8328},
    "Darbhanga": {"state": "Bihar", "lat": 26.1542, "lon": 85.8918},
    "Dehradun": {"state": "Uttarakhand", "lat": 30.3165, "lon": 78.0322},
    "Delhi": {"state": "Delhi", "lat": 28.6139, "lon": 77.2090},
    "Dhanbad": {"state": "Jharkhand", "lat": 23.7957, "lon": 86.4304},
    "Dharamshala": {"state": "Himachal Pradesh", "lat": 32.2190, "lon": 76.3234},
    "Dibrugarh": {"state": "Assam", "lat": 27.4728, "lon": 94.9120},
    "Dimapur": {"state": "Nagaland", "lat": 25.9091, "lon": 93.7266},
    "Dispur": {"state": "Assam", "lat": 26.1433, "lon": 91.7898},
    "Diu": {"state": "Dadra and Nagar Haveli and Daman and Diu", "lat": 20.7144, "lon": 70.9874},
    "Durgapur": {"state": "West Bengal", "lat": 23.5204, "lon": 87.3119},
    "Eluru": {"state": "Andhra Pradesh", "lat": 16.7107, "lon": 81.0952},
    "Faridabad": {"state": "Haryana", "lat": 28.4089, "lon": 77.3178},
    "Firozabad": {"state": "Uttar Pradesh", "lat": 27.1592, "lon": 78.3957},
    "Gandhinagar": {"state": "Gujarat", "lat": 23.2156, "lon": 72.6369},
    "Gangtok": {"state": "Sikkim", "lat": 27.3389, "lon": 88.6065},
    "Gaya": {"state": "Bihar", "lat": 24.7955, "lon": 85.0002},
    "Ghaziabad": {"state": "Uttar Pradesh", "lat": 28.6692, "lon": 77.4538},
    "Gorakhpur": {"state": "Uttar Pradesh", "lat": 26.7606, "lon": 83.3732},
    "Gulbarga": {"state": "Karnataka", "lat": 17.3297, "lon": 76.8343},
    "Guntur": {"state": "Andhra Pradesh", "lat": 16.3067, "lon": 80.4365},
    "Gurugram": {"state": "Haryana", "lat": 28.4595, "lon": 77.0266},
    "Guwahati": {"state": "Assam", "lat": 26.1445, "lon": 91.7362},
    "Gwalior": {"state": "Madhya Pradesh", "lat": 26.2183, "lon": 78.1828},
    "Haldwani": {"state": "Uttarakhand", "lat": 29.2183, "lon": 79.5130},
    "Haridwar": {"state": "Uttarakhand", "lat": 29.9457, "lon": 78.1642},
    "Hisar": {"state": "Haryana", "lat": 29.1492, "lon": 75.7217},
    "Hubballi": {"state": "Karnataka", "lat": 15.3647, "lon": 75.1240},
    "Hyderabad": {"state": "Telangana", "lat": 17.3850, "lon": 78.4867},
    "Imphal": {"state": "Manipur", "lat": 24.8170, "lon": 93.9368},
    "Indore": {"state": "Madhya Pradesh", "lat": 22.7196, "lon": 75.8577},
    "Itanagar": {"state": "Arunachal Pradesh", "lat": 27.0844, "lon": 93.6053},
    "Jabalpur": {"state": "Madhya Pradesh", "lat": 23.1815, "lon": 79.9864},
    "Jaipur": {"state": "Rajasthan", "lat": 26.9124, "lon": 75.7873},
    "Jalandhar": {"state": "Punjab", "lat": 31.3260, "lon": 75.5762},
    "Jalgaon": {"state": "Maharashtra", "lat": 21.0077, "lon": 75.5626},
    "Jammu": {"state": "Jammu and Kashmir", "lat": 32.7266, "lon": 74.8570},
    "Jamnagar": {"state": "Gujarat", "lat": 22.4707, "lon": 70.0577},
    "Jamshedpur": {"state": "Jharkhand", "lat": 22.8046, "lon": 86.2029},
    "Jhansi": {"state": "Uttar Pradesh", "lat": 25.4484, "lon": 78.5685},
    "Jodhpur": {"state": "Rajasthan", "lat": 26.2389, "lon": 73.0243},
    "Jorhat": {"state": "Assam", "lat": 26.7509, "lon": 94.2037},
    "Kakinada": {"state": "Andhra Pradesh", "lat": 16.9891, "lon": 82.2475},
    "Kalyani": {"state": "West Bengal", "lat": 22.9751, "lon": 88.4345},
    "Kannur": {"state": "Kerala", "lat": 11.8745, "lon": 75.3704},
    "Kanpur": {"state": "Uttar Pradesh", "lat": 26.4499, "lon": 80.3319},
    "Kargil": {"state": "Ladakh", "lat": 34.5539, "lon": 76.1349},
    "Karimnagar": {"state": "Telangana", "lat": 18.4386, "lon": 79.1288},
    "Karnal": {"state": "Haryana", "lat": 29.6857, "lon": 76.9905},
    "Kavaratti": {"state": "Lakshadweep", "lat": 10.5593, "lon": 72.6358},
    "Kochi": {"state": "Kerala", "lat": 9.9312, "lon": 76.2673},
    "Kohima": {"state": "Nagaland", "lat": 25.6751, "lon": 94.1086},
    "Kolar": {"state": "Karnataka", "lat": 13.1367, "lon": 78.1292},
    "Kolhapur": {"state": "Maharashtra", "lat": 16.7050, "lon": 74.2433},
    "Kolkata": {"state": "West Bengal", "lat": 22.5726, "lon": 88.3639},
    "Kollam": {"state": "Kerala", "lat": 8.8932, "lon": 76.6141},
    "Kota": {"state": "Rajasthan", "lat": 25.2138, "lon": 75.8648},
    "Kozhikode": {"state": "Kerala", "lat": 11.2588, "lon": 75.7804},
    "Kurnool": {"state": "Andhra Pradesh", "lat": 15.8281, "lon": 78.0373},
    "Leh": {"state": "Ladakh", "lat": 34.1526, "lon": 77.5771},
    "Lucknow": {"state": "Uttar Pradesh", "lat": 26.8467, "lon": 80.9462},
    "Ludhiana": {"state": "Punjab", "lat": 30.9010, "lon": 75.8573},
    "Madurai": {"state": "Tamil Nadu", "lat": 9.9252, "lon": 78.1198},
    "Malappuram": {"state": "Kerala", "lat": 11.0510, "lon": 76.0711},
    "Mangaluru": {"state": "Karnataka", "lat": 12.9141, "lon": 74.8560},
    "Mathura": {"state": "Uttar Pradesh", "lat": 27.4924, "lon": 77.6737},
    "Meerut": {"state": "Uttar Pradesh", "lat": 28.9845, "lon": 77.7064},
    "Moradabad": {"state": "Uttar Pradesh", "lat": 28.8386, "lon": 78.7733},
    "Mumbai": {"state": "Maharashtra", "lat": 19.0760, "lon": 72.8777},
    "Muzaffarpur": {"state": "Bihar", "lat": 26.1209, "lon": 85.3647},
    "Mysuru": {"state": "Karnataka", "lat": 12.2958, "lon": 76.6394},
    "Nagpur": {"state": "Maharashtra", "lat": 21.1458, "lon": 79.0882},
    "Nanded": {"state": "Maharashtra", "lat": 19.1383, "lon": 77.3210},
    "Nashik": {"state": "Maharashtra", "lat": 19.9975, "lon": 73.7898},
    "Navi Mumbai": {"state": "Maharashtra", "lat": 19.0330, "lon": 73.0297},
    "Noida": {"state": "Uttar Pradesh", "lat": 28.5355, "lon": 77.3910},
    "Panaji": {"state": "Goa", "lat": 15.4909, "lon": 73.8278},
    "Panipat": {"state": "Haryana", "lat": 29.3909, "lon": 76.9635},
    "Panjim": {"state": "Goa", "lat": 15.4909, "lon": 73.8278},
    "Patiala": {"state": "Punjab", "lat": 30.3398, "lon": 76.3869},
    "Patna": {"state": "Bihar", "lat": 25.5941, "lon": 85.1376},
    "Port Blair": {"state": "Andaman and Nicobar Islands", "lat": 11.6234, "lon": 92.7265},
    "Prayagraj": {"state": "Uttar Pradesh", "lat": 25.4358, "lon": 81.8463},
    "Puducherry": {"state": "Puducherry", "lat": 11.9416, "lon": 79.8083},
    "Pune": {"state": "Maharashtra", "lat": 18.5204, "lon": 73.8567},
    "Puri": {"state": "Odisha", "lat": 19.8135, "lon": 85.8312},
    "Raipur": {"state": "Chhattisgarh", "lat": 21.2514, "lon": 81.6296},
    "Rajahmundry": {"state": "Andhra Pradesh", "lat": 17.0005, "lon": 81.8040},
    "Rajkot": {"state": "Gujarat", "lat": 22.3039, "lon": 70.8022},
    "Ranchi": {"state": "Jharkhand", "lat": 23.3441, "lon": 85.3096},
    "Rewa": {"state": "Madhya Pradesh", "lat": 24.5362, "lon": 81.3037},
    "Rohtak": {"state": "Haryana", "lat": 28.8955, "lon": 76.6066},
    "Rourkela": {"state": "Odisha", "lat": 22.2604, "lon": 84.8536},
    "Sagar": {"state": "Madhya Pradesh", "lat": 23.8388, "lon": 78.7378},
    "Salem": {"state": "Tamil Nadu", "lat": 11.6643, "lon": 78.1460},
    "Sambalpur": {"state": "Odisha", "lat": 21.4669, "lon": 83.9812},
    "Shillong": {"state": "Meghalaya", "lat": 25.5788, "lon": 91.8933},
    "Shimla": {"state": "Himachal Pradesh", "lat": 31.1048, "lon": 77.1734},
    "Silchar": {"state": "Assam", "lat": 24.8333, "lon": 92.7789},
    "Siliguri": {"state": "West Bengal", "lat": 26.7271, "lon": 88.3953},
    "Silvassa": {"state": "Dadra and Nagar Haveli and Daman and Diu", "lat": 20.2763, "lon": 73.0083},
    "Solapur": {"state": "Maharashtra", "lat": 17.6599, "lon": 75.9064},
    "Sonipat": {"state": "Haryana", "lat": 28.9931, "lon": 77.0151},
    "Srinagar": {"state": "Jammu and Kashmir", "lat": 34.0837, "lon": 74.7973},
    "Surat": {"state": "Gujarat", "lat": 21.1702, "lon": 72.8311},
    "Thane": {"state": "Maharashtra", "lat": 19.2183, "lon": 72.9781},
    "Thanjavur": {"state": "Tamil Nadu", "lat": 10.7867, "lon": 79.1378},
    "Thiruvananthapuram": {"state": "Kerala", "lat": 8.5241, "lon": 76.9366},
    "Thrissur": {"state": "Kerala", "lat": 10.5276, "lon": 76.2144},
    "Tiruchirappalli": {"state": "Tamil Nadu", "lat": 10.7905, "lon": 78.7047},
    "Tirupati": {"state": "Andhra Pradesh", "lat": 13.6288, "lon": 79.4192},
    "Tura": {"state": "Meghalaya", "lat": 25.5148, "lon": 90.2024},
    "Udaipur": {"state": "Rajasthan", "lat": 24.5854, "lon": 73.7125},
    "Ujjain": {"state": "Madhya Pradesh", "lat": 23.1765, "lon": 75.7885},
    "Vadodara": {"state": "Gujarat", "lat": 22.3072, "lon": 73.1812},
    "Varanasi": {"state": "Uttar Pradesh", "lat": 25.3176, "lon": 82.9739},
    "Vellore": {"state": "Tamil Nadu", "lat": 12.9165, "lon": 79.1325},
    "Vijayawada": {"state": "Andhra Pradesh", "lat": 16.5062, "lon": 80.6480},
    "Visakhapatnam": {"state": "Andhra Pradesh", "lat": 17.6868, "lon": 83.2185},
    "Warangal": {"state": "Telangana", "lat": 17.9689, "lon": 79.5941},
}

SAMPLE_HOSPITALS = [
    {"name": "AIIMS Delhi", "city": "Delhi", "specialization": "Respiratory", "rating": 4.8, "coordinates": [77.2100, 28.5672]},
    {"name": "Max Super Speciality Hospital", "city": "Delhi", "specialization": "Cardiology", "rating": 4.6, "coordinates": [77.2167, 28.5276]},
    {"name": "Apollo Hospital Delhi", "city": "Delhi", "specialization": "Respiratory", "rating": 4.5, "coordinates": [77.2832, 28.5403]},
    {"name": "Kokilaben Hospital", "city": "Mumbai", "specialization": "Respiratory", "rating": 4.7, "coordinates": [72.8258, 19.1312]},
    {"name": "Lilavati Hospital", "city": "Mumbai", "specialization": "Pulmonology", "rating": 4.4, "coordinates": [72.8295, 19.0506]},
    {"name": "Manipal Hospital", "city": "Bengaluru", "specialization": "Respiratory", "rating": 4.5, "coordinates": [77.6486, 12.9606]},
    {"name": "Narayana Institute of Cardiac Sciences", "city": "Bengaluru", "specialization": "Cardiology", "rating": 4.7, "coordinates": [77.6950, 12.8050]},
    {"name": "Apollo Hospitals Greams Road", "city": "Chennai", "specialization": "Cardiology", "rating": 4.6, "coordinates": [80.2517, 13.0635]},
    {"name": "Kauvery Hospital", "city": "Chennai", "specialization": "Respiratory", "rating": 4.3, "coordinates": [80.2526, 13.0358]},
    {"name": "Apollo Gleneagles Hospital", "city": "Kolkata", "specialization": "Pulmonology", "rating": 4.4, "coordinates": [88.3990, 22.5748]},
    {"name": "BM Birla Heart Research Centre", "city": "Kolkata", "specialization": "Cardiology", "rating": 4.5, "coordinates": [88.3514, 22.5393]},
    {"name": "CARE Hospitals", "city": "Hyderabad", "specialization": "Cardiology", "rating": 4.4, "coordinates": [78.4505, 17.4126]},
    {"name": "Yashoda Hospitals", "city": "Hyderabad", "specialization": "Respiratory", "rating": 4.5, "coordinates": [78.4983, 17.4435]},
    {"name": "Ruby Hall Clinic", "city": "Pune", "specialization": "Cardiology", "rating": 4.3, "coordinates": [73.8767, 18.5335]},
    {"name": "Deenanath Mangeshkar Hospital", "city": "Pune", "specialization": "Respiratory", "rating": 4.5, "coordinates": [73.8326, 18.5027]},
    {"name": "Apollo Hospitals Ahmedabad", "city": "Ahmedabad", "specialization": "Respiratory", "rating": 4.4, "coordinates": [72.6252, 23.1127]},
    {"name": "Sterling Hospital", "city": "Ahmedabad", "specialization": "Cardiology", "rating": 4.3, "coordinates": [72.5318, 23.0522]},
    {"name": "Fortis Escorts Hospital", "city": "Jaipur", "specialization": "Cardiology", "rating": 4.4, "coordinates": [75.8047, 26.8494]},
    {"name": "EHCC Hospital", "city": "Jaipur", "specialization": "Respiratory", "rating": 4.2, "coordinates": [75.8080, 26.8384]},
    {"name": "Medanta Hospital", "city": "Lucknow", "specialization": "Cardiology", "rating": 4.5, "coordinates": [80.9735, 26.7589]},
    {"name": "Sahara Hospital", "city": "Lucknow", "specialization": "Respiratory", "rating": 4.2, "coordinates": [81.0204, 26.8486]},
    {"name": "United Medicity", "city": "Prayagraj", "specialization": "Respiratory", "rating": 4.1, "coordinates": [81.8640, 25.3917]},
    {"name": "Phoenix Hospital", "city": "Prayagraj", "specialization": "Pulmonology", "rating": 4.0, "coordinates": [81.8330, 25.4484]},
]


st.set_page_config(page_title="IntelliAir Pro", page_icon="IA", layout="wide", initial_sidebar_state="expanded")


def apply_custom_css(theme):
    is_dark = theme == "Dark"
    bg = "#07111f" if is_dark else "#f4f8ff"
    panel = "rgba(10, 24, 45, 0.72)" if is_dark else "rgba(255, 255, 255, 0.72)"
    text = "#eaf6ff" if is_dark else "#0f1f38"
    muted = "#9fb5cf" if is_dark else "#5b6d82"
    accent = "#42e8f4" if is_dark else "#2167ff"
    accent_2 = "#a855f7" if is_dark else "#00a8a8"
    card_border = "rgba(66, 232, 244, 0.22)" if is_dark else "rgba(33, 103, 255, 0.18)"
    shadow = "0 18px 60px rgba(0, 0, 0, 0.35)" if is_dark else "0 18px 45px rgba(33, 103, 255, 0.12)"

    st.markdown(
        f"""
        <style>
        footer {{visibility: hidden;}}
        .stApp {{
            background:
                radial-gradient(circle at 20% 20%, {accent}22 0, transparent 28%),
                radial-gradient(circle at 82% 10%, {accent_2}20 0, transparent 24%),
                {bg};
            color: {text};
        }}
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {{
            display: none;
        }}
        h1, h2, h3, h4, p, label, span {{color: {text};}}
        .muted {{color: {muted};}}
        .hero {{
            padding: 28px 30px;
            border: 1px solid {card_border};
            border-radius: 24px;
            background: linear-gradient(135deg, {panel}, rgba(255,255,255,0.04));
            box-shadow: {shadow};
            backdrop-filter: blur(18px);
            animation: fadeIn 650ms ease both;
        }}
        .hero-title {{
            font-size: clamp(2.3rem, 5vw, 4.6rem);
            line-height: 1;
            margin: 0;
            font-weight: 900;
            letter-spacing: 0;
            background: linear-gradient(90deg, {accent}, {accent_2});
            -webkit-background-clip: text;
            color: transparent;
        }}
        .kpi-card, .glass-card, .alert-card {{
            border: 1px solid {card_border};
            border-radius: 22px;
            background: {panel};
            box-shadow: {shadow};
            backdrop-filter: blur(18px);
            padding: 22px;
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
            animation: fadeIn 700ms ease both;
        }}
        .kpi-card:hover, .glass-card:hover {{
            transform: translateY(-4px) scale(1.01);
            border-color: {accent};
        }}
        .kpi-label {{
            color: {muted};
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        }}
        .kpi-value {{
            color: {text};
            font-size: clamp(2rem, 4vw, 3.2rem);
            font-weight: 850;
            line-height: 1.05;
        }}
        .pill {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 999px;
            background: {accent}24;
            color: {accent};
            border: 1px solid {accent}55;
            font-weight: 700;
        }}
        .alert-card {{
            border-color: rgba(255, 70, 70, 0.55);
            background: linear-gradient(135deg, rgba(255, 70, 70, 0.22), {panel});
            animation: pulseAlert 1.6s ease-in-out infinite;
        }}
        .stTabs [data-baseweb="tab-list"] {{gap: 10px;}}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 999px;
            padding: 10px 18px;
            background: {panel};
            border: 1px solid {card_border};
        }}
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(90deg, {accent}55, {accent_2}55);
            border-color: {accent};
        }}
        div[data-testid="stMetric"] {{
            background: {panel};
            border-radius: 18px;
            border: 1px solid {card_border};
            padding: 16px;
        }}
        @keyframes fadeIn {{
            from {{opacity: 0; transform: translateY(12px);}}
            to {{opacity: 1; transform: translateY(0);}}
        }}
        @keyframes pulseAlert {{
            0%, 100% {{box-shadow: 0 0 0 rgba(255,70,70,0.1);}}
            50% {{box-shadow: 0 0 32px rgba(255,70,70,0.36);}}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_secret(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


def get_mongo_uri():
    return get_secret("MONGO_URI", "mongodb+srv://avaneesh5116as_db_user:H3qJCS55OoUIX0Su@intelliair-pro.dohoyp6.mongodb.net/")


@st.cache_resource(show_spinner=False)
def get_mongo_client():
    client = MongoClient(get_mongo_uri(), serverSelectionTimeoutMS=2500)
    client.admin.command("ping")
    return client


def get_app_db():
    return get_mongo_client()["intelliair"]


def get_states():
    return sorted({info["state"] for info in CITY_DATA.values()})


def get_cities_for_state(state):
    return sorted([city for city, info in CITY_DATA.items() if info["state"] == state])


def base64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def base64url_decode(data):
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def jwt_secret():
    return get_secret("JWT_SECRET", "intelliair-dev-secret-change-me")


def create_jwt(payload, expires_in=86400):
    header = {"alg": "HS256", "typ": "JWT"}
    body = dict(payload)
    body["iat"] = int(time.time())
    body["exp"] = int(time.time()) + expires_in
    signing_input = f"{base64url_encode(json.dumps(header, separators=(',', ':')).encode())}.{base64url_encode(json.dumps(body, separators=(',', ':')).encode())}"
    signature = hmac.new(jwt_secret().encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    return f"{signing_input}.{base64url_encode(signature)}"


def verify_jwt(token):
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}"
        expected = hmac.new(jwt_secret().encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
        if not hmac.compare_digest(base64url_encode(expected), signature_b64):
            return None
        payload = json.loads(base64url_decode(payload_b64))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except (ValueError, json.JSONDecodeError):
        return None


def hash_password(password, salt):
    value = f"{salt}:{password}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def create_password_record(password):
    salt = base64url_encode(os.urandom(16))
    return salt, hash_password(password, salt)


def verify_password(password, user):
    return hash_password(password, user.get("salt", "")) == user.get("password_hash", "")


def get_users_collection():
    db = get_app_db()
    users = db["users"]
    users.create_index("username", unique=True)
    users.create_index("email", unique=True, sparse=True)
    return users


def get_user_history_collection():
    history = get_app_db()["user_history"]
    history.create_index([("username", 1), ("created_at", -1)])
    return history


def save_user_history(username, aqi_data, predicted_aqi, category, health_risk):
    if not username:
        return None

    signature = (
        username,
        aqi_data["city"],
        aqi_data["aqi"],
        predicted_aqi,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    if st.session_state.get("last_history_signature") == signature:
        return None

    record = {
        "username": username,
        "city": aqi_data["city"],
        "state": aqi_data["state"],
        "aqi": int(aqi_data["aqi"]),
        "category": category,
        "health_risk": health_risk,
        "predicted_aqi": int(predicted_aqi),
        "dominant_pollutant": aqi_data["dominant"],
        "pm25": float(aqi_data["pollutants"]["PM2.5"]),
        "pm10": float(aqi_data["pollutants"]["PM10"]),
        "co": float(aqi_data["pollutants"]["CO"]),
        "no2": float(aqi_data["pollutants"]["NO2"]),
        "source": aqi_data["source"],
        "created_at": datetime.utcnow(),
    }

    try:
        get_user_history_collection().insert_one(record)
        st.session_state["last_history_signature"] = signature
        return None
    except PyMongoError as exc:
        return f"Could not save user history: {exc}"


def load_user_history(username, limit=25):
    if not username:
        return pd.DataFrame()
    try:
        rows = list(
            get_user_history_collection()
            .find({"username": username}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )
    except PyMongoError:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def seed_admin_user():
    try:
        users = get_users_collection()
        if users.count_documents({"username": "admin"}) == 0:
            salt, password_hash = create_password_record("admin123")
            users.insert_one(
                {
                    "username": "admin",
                    "email": "admin@intelliair.local",
                    "salt": salt,
                    "password_hash": password_hash,
                    "provider": "local",
                    "created_at": datetime.utcnow(),
                }
            )
    except PyMongoError:
        pass


def login_user(user):
    token = create_jwt({"sub": str(user.get("_id", user.get("username"))), "username": user["username"]})
    st.session_state["jwt_token"] = token
    st.session_state["authenticated"] = True
    st.session_state["current_user"] = user["username"]


def google_oauth_url():
    client_id = get_secret("GOOGLE_CLIENT_ID", "")
    redirect_uri = get_secret("GOOGLE_REDIRECT_URI", "http://localhost:8503/")
    if not client_id:
        return ""
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)


def handle_google_oauth_callback():
    code = st.query_params.get("code")
    if not code or st.session_state.get("authenticated"):
        return
    client_id = get_secret("GOOGLE_CLIENT_ID", "")
    client_secret = get_secret("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = get_secret("GOOGLE_REDIRECT_URI", "http://localhost:8503/")
    if not client_id or not client_secret:
        st.error("Google OAuth is not configured. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to Streamlit secrets.")
        return
    try:
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]
        profile_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        profile_response.raise_for_status()
        profile = profile_response.json()
        email = profile["email"]
        username = profile.get("name") or email.split("@")[0]
        users = get_users_collection()
        users.update_one(
            {"email": email},
            {
                "$set": {
                    "username": username,
                    "email": email,
                    "provider": "google",
                    "google_id": profile.get("id"),
                    "updated_at": datetime.utcnow(),
                },
                "$setOnInsert": {"created_at": datetime.utcnow()},
            },
            upsert=True,
        )
        user = users.find_one({"email": email})
        login_user(user)
        st.query_params.clear()
        st.rerun()
    except (requests.RequestException, KeyError, PyMongoError) as exc:
        st.error(f"Google OAuth failed: {exc}")


def init_auth_state():
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("current_user", "")
    st.session_state.setdefault("jwt_token", "")
    seed_admin_user()
    payload = verify_jwt(st.session_state.get("jwt_token", ""))
    if payload:
        st.session_state["authenticated"] = True
        st.session_state["current_user"] = payload.get("username", "")


def render_auth_page(theme):
    apply_custom_css(theme)
    handle_google_oauth_callback()
    st.markdown(
        """
        <div class="hero">
            <div class="pill">Secure access</div>
            <h1 class="hero-title">IntelliAir Pro</h1>
            <p class="muted">Login or create an account to access AQI prediction, smart hospital navigation and health insights.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    left, center, right = st.columns([1, 1.2, 1])
    with center:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        mode = st.radio("Account", ["Login", "Sign up"], horizontal=True, label_visibility="collapsed")

        if mode == "Login":
            username = st.text_input("Username", placeholder="your_username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            if st.button("Login", use_container_width=True):
                try:
                    user = get_users_collection().find_one({"username": username.strip()})
                    if user and verify_password(password, user):
                        login_user(user)
                        st.rerun()
                    st.error("Invalid username or password.")
                except PyMongoError as exc:
                    st.error(f"MongoDB login unavailable: {exc}")
        else:
            email = st.text_input("Email", placeholder="name@example.com")
            username = st.text_input("Username", placeholder="Choose a username")
            password = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
            confirm = st.text_input("Confirm password", type="password", placeholder="Re-enter password")
            if st.button("Create account", use_container_width=True):
                clean_email = email.strip().lower()
                clean_username = username.strip()
                if "@" not in clean_email or "." not in clean_email.split("@")[-1]:
                    st.error("Enter a valid email.")
                elif not clean_username:
                    st.error("Enter a username.")
                elif len(clean_username) < 3:
                    st.error("Username must be at least 3 characters.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        salt, password_hash = create_password_record(password)
                        user_doc = {
                            "username": clean_username,
                            "email": clean_email,
                            "salt": salt,
                            "password_hash": password_hash,
                            "provider": "local",
                            "created_at": datetime.utcnow(),
                        }
                        result = get_users_collection().insert_one(user_doc)
                        user_doc["_id"] = result.inserted_id
                        login_user(user_doc)
                        st.rerun()
                    except PyMongoError as exc:
                        st.error(f"Could not create account in MongoDB: {exc}")

        oauth_url = google_oauth_url()
        if oauth_url:
            st.link_button("Continue with Google", oauth_url, use_container_width=True)
        else:
            st.caption("Google OAuth: add GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI to secrets.")
        st.caption("Demo login: admin / admin123")
        st.caption("MongoDB URI: mongodb://localhost:27017/")
        st.markdown("</div>", unsafe_allow_html=True)


def aqi_from_openweather_scale(scale_value):
    mapping = {1: 35, 2: 75, 3: 125, 4: 180, 5: 260}
    return mapping.get(int(scale_value), 100)


def calculate_indian_aqi(pm25, pm10, co, no2):
    def sub_index(value, breakpoints):
        for c_low, c_high, i_low, i_high in breakpoints:
            if c_low <= value <= c_high:
                return ((i_high - i_low) / (c_high - c_low)) * (value - c_low) + i_low
        return 500

    co_mg = co / 1000
    indices = {
        "PM2.5": sub_index(pm25, [(0, 30, 0, 50), (30, 60, 51, 100), (60, 90, 101, 200), (90, 120, 201, 300), (120, 250, 301, 400)]),
        "PM10": sub_index(pm10, [(0, 50, 0, 50), (50, 100, 51, 100), (100, 250, 101, 200), (250, 350, 201, 300), (350, 430, 301, 400)]),
        "CO": sub_index(co_mg, [(0, 1, 0, 50), (1, 2, 51, 100), (2, 10, 101, 200), (10, 17, 201, 300), (17, 34, 301, 400)]),
        "NO2": sub_index(no2, [(0, 40, 0, 50), (40, 80, 51, 100), (80, 180, 101, 200), (180, 280, 201, 300), (280, 400, 301, 400)]),
    }
    dominant = max(indices, key=indices.get)
    return int(round(max(indices.values()))), dominant, indices


def fetch_aqi_data(city):
    city_info = CITY_DATA[city]
    api_key = st.session_state.get("openweather_key", "").strip()
    lat, lon = city_info["lat"], city_info["lon"]

    if api_key:
        try:
            geo_response = requests.get(
                OPENWEATHER_GEO_URL,
                params={"q": city, "limit": 1, "appid": api_key},
                timeout=10,
            )
            geo_response.raise_for_status()
            geo = geo_response.json()
            if geo:
                lat, lon = float(geo[0]["lat"]), float(geo[0]["lon"])

            response = requests.get(
                OPENWEATHER_AIR_URL,
                params={"lat": lat, "lon": lon, "appid": api_key},
                timeout=10,
            )
            response.raise_for_status()
            record = response.json()["list"][0]
            components = record["components"]
            computed_aqi, dominant, sub_indices = calculate_indian_aqi(
                components.get("pm2_5", 0),
                components.get("pm10", 0),
                components.get("co", 0),
                components.get("no2", 0),
            )
            return {
                "city": city,
                "state": city_info["state"],
                "lat": lat,
                "lon": lon,
                "aqi": computed_aqi,
                "openweather_scale": record["main"].get("aqi"),
                "dominant": dominant,
                "sub_indices": sub_indices,
                "pollutants": {
                    "PM2.5": components.get("pm2_5", 0),
                    "PM10": components.get("pm10", 0),
                    "CO": components.get("co", 0),
                    "NO2": components.get("no2", 0),
                },
                "source": "OpenWeather Air Pollution API",
                "updated_at": datetime.fromtimestamp(record.get("dt", datetime.now().timestamp())),
                "error": None,
            }
        except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
            return mock_aqi_data(city, f"Live API unavailable: {exc}")

    return mock_aqi_data(city, "No OpenWeather API key found. Showing realistic demo data.")


def mock_aqi_data(city, error):
    city_info = CITY_DATA[city]
    seed = sum(ord(ch) for ch in city)
    rng = np.random.default_rng(seed)
    pm25 = float(rng.integers(28, 150))
    pm10 = float(rng.integers(55, 280))
    co = float(rng.integers(420, 1700))
    no2 = float(rng.integers(18, 110))
    aqi, dominant, sub_indices = calculate_indian_aqi(pm25, pm10, co, no2)
    return {
        "city": city,
        "state": city_info["state"],
        "lat": city_info["lat"],
        "lon": city_info["lon"],
        "aqi": aqi,
        "openweather_scale": None,
        "dominant": dominant,
        "sub_indices": sub_indices,
        "pollutants": {"PM2.5": pm25, "PM10": pm10, "CO": co, "NO2": no2},
        "source": "Demo fallback dataset",
        "updated_at": datetime.now(),
        "error": error,
    }


@st.cache_resource(show_spinner=False)
def train_model():
    rng = np.random.default_rng(7)
    n = 420
    temperature = rng.normal(29, 6, n).clip(8, 46)
    humidity = rng.normal(58, 18, n).clip(12, 96)
    wind = rng.normal(8, 4, n).clip(1, 28)
    traffic = rng.normal(65, 20, n).clip(15, 100)
    industrial = rng.normal(45, 25, n).clip(0, 100)
    seasonal = rng.normal(0, 18, n)
    aqi = 38 + temperature * 1.55 + humidity * 0.56 - wind * 2.1 + traffic * 1.2 + industrial * 0.95 + seasonal
    aqi = aqi.clip(20, 430)

    df = pd.DataFrame(
        {
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind,
            "traffic_index": traffic,
            "industrial_index": industrial,
            "aqi": aqi,
        }
    )
    x = df[["temperature", "humidity", "wind_speed", "traffic_index", "industrial_index"]]
    y = df["aqi"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.22, random_state=42)
    model = RandomForestRegressor(n_estimators=180, max_depth=12, random_state=42)
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    metrics = {"mae": mean_absolute_error(y_test, y_pred), "r2": r2_score(y_test, y_pred)}
    comparison = pd.DataFrame({"Actual AQI": y_test.values, "Predicted AQI": y_pred}).head(80)
    return model, df, comparison, metrics


def predict_aqi(model, current_aqi, city):
    seed = sum(ord(ch) for ch in city) + int(current_aqi)
    rng = np.random.default_rng(seed)
    temperature = float(rng.normal(31, 3))
    humidity = float(rng.normal(57, 10))
    wind = float(rng.normal(8, 2))
    traffic = min(100, max(20, current_aqi / 2.5 + rng.normal(20, 9)))
    industrial = min(100, max(10, current_aqi / 3 + rng.normal(18, 11)))
    features = pd.DataFrame(
        [{
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind,
            "traffic_index": traffic,
            "industrial_index": industrial,
        }]
    )
    return int(round(model.predict(features)[0])), features.iloc[0].to_dict()


def health_advisory(aqi):
    if aqi <= 50:
        return "Good", "Low", "Air quality is healthy. Outdoor activity is safe.", ["Enjoy normal outdoor plans.", "Keep windows open if local dust is low."], "#22c55e"
    if aqi <= 100:
        return "Moderate", "Mild", "Sensitive people may feel minor breathing discomfort.", ["Limit long outdoor workouts.", "Stay hydrated."], "#facc15"
    if aqi <= 150:
        return "Unhealthy", "Respiratory", "Children, elderly people and asthma patients should reduce exposure.", ["Wear a mask outdoors.", "Avoid heavy traffic zones.", "Keep inhalers available if prescribed."], "#fb923c"
    return "Hazardous", "Severe respiratory", "Pollution is high enough to affect healthy adults.", ["Avoid outdoor activity.", "Use indoor filtration if available.", "Seek medical help for chest pain or breathing distress."], "#ef4444"


def get_mongo_collection():
    try:
        collection = get_app_db()["hospitals"]
        collection.create_index([("location", GEOSPHERE)])
        if collection.count_documents({}) == 0:
            docs = [
                {
                    "name": h["name"],
                    "city": h["city"],
                    "specialization": h["specialization"],
                    "rating": h["rating"],
                    "location": {"type": "Point", "coordinates": h["coordinates"]},
                }
                for h in SAMPLE_HOSPITALS
            ]
            collection.insert_many(docs)
        return collection
    except PyMongoError:
        return None


def distance_km(lat1, lon1, lat2, lon2):
    radius = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def get_nearby_hospitals(lat, lon, city, risk, radius_m=50000):
    specialization = "Respiratory" if risk in ["Respiratory", "Severe respiratory"] else None
    collection = get_mongo_collection()

    if collection is not None:
        query = {
            "location": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "$maxDistance": radius_m,
                }
            }
        }
        if specialization:
            query["specialization"] = {"$in": [specialization, "Pulmonology", "Cardiology"]}
        try:
            docs = list(collection.find(query, {"_id": 0}).limit(5))
            if docs:
                return normalize_hospital_docs(docs, lat, lon), "MongoDB geospatial query"
        except PyMongoError:
            pass

    docs = []
    for hospital in SAMPLE_HOSPITALS:
        if hospital["city"].lower() == city.lower():
            if specialization and hospital["specialization"] not in [specialization, "Pulmonology", "Cardiology"]:
                continue
            docs.append(
                {
                    "name": hospital["name"],
                    "city": hospital["city"],
                    "specialization": hospital["specialization"],
                    "rating": hospital["rating"],
                    "location": {"type": "Point", "coordinates": hospital["coordinates"]},
                }
            )
    if not docs:
        docs = [
            {
                "name": h["name"],
                "city": h["city"],
                "specialization": h["specialization"],
                "rating": h["rating"],
                "location": {"type": "Point", "coordinates": h["coordinates"]},
            }
            for h in SAMPLE_HOSPITALS
        ]
    return normalize_hospital_docs(docs, lat, lon), "Sample hospital dataset"


def normalize_hospital_docs(docs, lat, lon, limit=5):
    rows = []
    for doc in docs:
        h_lon, h_lat = doc["location"]["coordinates"]
        rows.append(
            {
                "name": doc["name"],
                "city": doc.get("city", ""),
                "specialization": doc["specialization"],
                "rating": doc["rating"],
                "lat": h_lat,
                "lon": h_lon,
                "distance_km": distance_km(lat, lon, h_lat, h_lon),
            }
        )
    return pd.DataFrame(rows).sort_values(["distance_km", "rating"], ascending=[True, False]).head(limit)


def create_map(aqi_data, hospitals, color, selected_hospital=None):
    center = [aqi_data["lat"], aqi_data["lon"]]
    if selected_hospital is not None:
        center = [selected_hospital["lat"], selected_hospital["lon"]]
    m = folium.Map(location=center, zoom_start=12, tiles="CartoDB dark_matter")
    folium.CircleMarker(
        [aqi_data["lat"], aqi_data["lon"]],
        radius=16,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.85,
        popup=f"{aqi_data['city']} AQI: {aqi_data['aqi']}<br>Dominant: {aqi_data['dominant']}",
    ).add_to(m)
    map_hospitals = hospitals
    if selected_hospital is not None:
        map_hospitals = pd.DataFrame([selected_hospital])

    for _, row in map_hospitals.iterrows():
        folium.Marker(
            [row["lat"], row["lon"]],
            popup=f"{row['name']}<br>{row['specialization']}<br>Rating: {row['rating']}<br>{row['distance_km']:.1f} km",
            tooltip=row["name"],
            icon=folium.Icon(color="green" if selected_hospital is not None else "red", icon="plus-sign"),
        ).add_to(m)
        folium.PolyLine(
            [[aqi_data["lat"], aqi_data["lon"]], [row["lat"], row["lon"]]],
            color=color,
            weight=2,
            opacity=0.65,
        ).add_to(m)
    return m


def build_trend(city, current_aqi):
    rng = np.random.default_rng(sum(ord(c) for c in city))
    dates = [datetime.now() - timedelta(days=13 - i) for i in range(14)]
    values = [max(20, current_aqi + math.sin(i / 2) * 18 + rng.normal(0, 10)) for i in range(14)]
    return pd.DataFrame({"date": dates, "AQI": np.round(values).astype(int)})


def build_city_comparison(selected_city):
    rows = []
    for city, info in CITY_DATA.items():
        seed = sum(ord(ch) for ch in city)
        rng = np.random.default_rng(seed)
        rows.append({"City": city, "State": info["state"], "AQI": int(rng.integers(45, 230))})
    df = pd.DataFrame(rows)
    if selected_city in df["City"].values:
        df.loc[df["City"] == selected_city, "AQI"] = st.session_state.get("current_aqi", df.loc[df["City"] == selected_city, "AQI"].iloc[0])
    return df.sort_values("AQI", ascending=False)


def card(label, value, detail):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="muted">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


init_auth_state()
selected_theme = st.session_state.get("selected_theme", "Dark")
apply_custom_css(selected_theme)

if not st.session_state["authenticated"]:
    render_auth_page(selected_theme)
    st.stop()

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
ctrl_1, ctrl_2, ctrl_3, ctrl_4 = st.columns([1.1, 1.2, 1.2, 0.8])
with ctrl_1:
    selected_theme = st.radio("Theme", ["Dark", "Light"], horizontal=True, key="selected_theme")
with ctrl_2:
    states = get_states()
    default_state = st.session_state.get("selected_state", "Delhi")
    selected_state = st.selectbox(
        "Select State",
        states,
        index=states.index(default_state) if default_state in states else states.index("Delhi"),
        key="selected_state",
    )
with ctrl_3:
    city_options = get_cities_for_state(selected_state)
    default_city = st.session_state.get("selected_city", city_options[0])
    selected_city = st.selectbox(
        "Select City",
        city_options,
        index=city_options.index(default_city) if default_city in city_options else 0,
        key="selected_city",
    )
with ctrl_4:
    st.write("")
    st.write("")
    if st.button("Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = ""
        st.session_state["jwt_token"] = ""
        st.rerun()
st.caption(f"Signed in as {st.session_state['current_user']} | API key is loaded securely from secrets/environment.")
st.markdown("</div>", unsafe_allow_html=True)

st.session_state["openweather_key"] = get_secret("OPENWEATHER_API_KEY", "")

model, training_df, model_comparison, model_metrics = train_model()
aqi_data = fetch_aqi_data(selected_city)
category, health_risk, advisory_text, tips, risk_color = health_advisory(aqi_data["aqi"])
predicted_aqi, feature_snapshot = predict_aqi(model, aqi_data["aqi"], selected_city)
st.session_state["current_aqi"] = aqi_data["aqi"]
history_warning = save_user_history(
    st.session_state.get("current_user", ""),
    aqi_data,
    predicted_aqi,
    category,
    health_risk,
)
hospitals_df, hospital_source = get_nearby_hospitals(aqi_data["lat"], aqi_data["lon"], selected_city, health_risk)
if st.session_state.get("selected_hospital_name") not in hospitals_df["name"].tolist():
    st.session_state["selected_hospital_name"] = hospitals_df.iloc[0]["name"]
trend_df = build_trend(selected_city, aqi_data["aqi"])
comparison_df = build_city_comparison(selected_city)

st.markdown(
    f"""
    <div class="hero">
        <div class="pill">Live intelligence for {selected_city}, {aqi_data['state']}</div>
        <h1 class="hero-title">IntelliAir Pro</h1>
        <p class="muted">Advanced AQI prediction and smart health navigation system powered by ML, maps and hospital intelligence.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if aqi_data["error"]:
    st.warning(aqi_data["error"])

if history_warning:
    st.warning(history_warning)

if aqi_data["aqi"] > 150:
    st.markdown(
        f"""
        <div class="alert-card">
            <h3>High Pollution Alert</h3>
            <p>AQI is {aqi_data['aqi']}. Avoid outdoor activity, wear a mask, and prioritize respiratory safety.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
k1, k2, k3 = st.columns(3)
with k1:
    card("AQI Value", aqi_data["aqi"], f"{category} | Dominant {aqi_data['dominant']}")
with k2:
    card("Health Risk", health_risk, advisory_text)
with k3:
    card("Predicted AQI", predicted_aqi, f"RF model | MAE {model_metrics['mae']:.1f}")

tabs = st.tabs(["Overview", "Prediction", "City Compare", "Hospitals & Map", "History"])

with tabs[0]:
    c1, c2 = st.columns([1.05, 0.95])
    with c1:
        pollutant_df = pd.DataFrame(
            {
                "Pollutant": list(aqi_data["pollutants"].keys()),
                "Concentration": list(aqi_data["pollutants"].values()),
                "AQI Sub Index": [aqi_data["sub_indices"].get(k, 0) for k in aqi_data["pollutants"].keys()],
            }
        )
        fig = px.bar(
            pollutant_df,
            x="Pollutant",
            y="AQI Sub Index",
            color="Pollutant",
            text_auto=".0f",
            title="Pollutant Impact",
            color_discrete_sequence=["#42e8f4", "#a855f7", "#fb923c", "#ef4444"],
        )
        fig.update_layout(template="plotly_dark" if selected_theme == "Dark" else "plotly_white", height=390)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Health Suggestions")
        st.write(advisory_text)
        for tip in tips:
            st.write(f"- {tip}")
        st.metric("Data Source", aqi_data["source"])
        st.metric("Updated", aqi_data["updated_at"].strftime("%Y-%m-%d %H:%M"))
        st.markdown("</div>", unsafe_allow_html=True)

    trend_fig = px.line(trend_df, x="date", y="AQI", markers=True, title="AQI Trend")
    trend_fig.update_layout(template="plotly_dark" if selected_theme == "Dark" else "plotly_white", height=380)
    st.plotly_chart(trend_fig, use_container_width=True)

with tabs[1]:
    p1, p2 = st.columns([1, 1])
    with p1:
        actual_pred = model_comparison.reset_index(drop=True)
        line = go.Figure()
        line.add_trace(go.Scatter(y=actual_pred["Actual AQI"], mode="lines", name="Actual AQI"))
        line.add_trace(go.Scatter(y=actual_pred["Predicted AQI"], mode="lines", name="Predicted AQI"))
        line.update_layout(
            title="Actual vs Predicted AQI",
            template="plotly_dark" if selected_theme == "Dark" else "plotly_white",
            height=420,
        )
        st.plotly_chart(line, use_container_width=True)
    with p2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Model Snapshot")
        st.metric("Predicted AQI", predicted_aqi)
        st.metric("R2 Score", f"{model_metrics['r2']:.2f}")
        st.metric("Mean Absolute Error", f"{model_metrics['mae']:.1f}")
        st.dataframe(pd.DataFrame([feature_snapshot]).round(2), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("City AQI Comparison")
    default_compare = [selected_city]
    for city_name in ["Delhi", "Mumbai", "Bengaluru", "Kolkata", "Chennai"]:
        if city_name != selected_city and city_name in CITY_DATA and len(default_compare) < 5:
            default_compare.append(city_name)
    compare_cities = st.multiselect(
        "Choose cities to compare",
        options=sorted(CITY_DATA.keys()),
        default=default_compare,
    )
    if not compare_cities:
        st.warning("Select at least one city to compare.")
    else:
        compare_df = comparison_df[comparison_df["City"].isin(compare_cities)].copy()
        compare_df = compare_df.sort_values("AQI", ascending=False)
        comp_fig = px.bar(
            compare_df,
            x="City",
            y="AQI",
            color="AQI",
            hover_data=["State"],
            title="Selected City Comparison",
            color_continuous_scale="Turbo",
        )
        comp_fig.update_layout(template="plotly_dark" if selected_theme == "Dark" else "plotly_white", height=430)
        st.plotly_chart(comp_fig, use_container_width=True)
        st.dataframe(compare_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[3]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Nearby Hospitals and Map")
    st.caption(f"Source: {hospital_source}. Hospitals are filtered from {selected_city} and matched to the AQI health risk.")
    h_left, h_right = st.columns([0.95, 1.05])
    with h_left:
        hospital_names = hospitals_df["name"].tolist()
        selected_hospital_name = st.selectbox("Select hospital", hospital_names)
        st.session_state["selected_hospital_name"] = selected_hospital_name
        st.dataframe(hospitals_df.round({"distance_km": 2}), use_container_width=True, hide_index=True)
        st.caption("MongoDB schema: name, specialization, rating, location GeoJSON.")
    with h_right:
        selected_name = st.session_state.get("selected_hospital_name", hospitals_df.iloc[0]["name"])
        selected_hospital = hospitals_df[hospitals_df["name"] == selected_name]
        selected_hospital_dict = selected_hospital.iloc[0].to_dict() if not selected_hospital.empty else hospitals_df.iloc[0].to_dict()
        st.success(f"Map route: {selected_city} AQI marker to {selected_hospital_dict['name']}")
        directions_url = "https://www.google.com/maps/dir/?" + urlencode(
            {
                "api": 1,
                "origin": "Current Location",
                "destination": f"{selected_hospital_dict['lat']},{selected_hospital_dict['lon']}",
                "destination_place": selected_hospital_dict["name"],
                "travelmode": "driving",
            }
        )
        st.link_button("Open hospital route in Google Maps", directions_url, use_container_width=True)
        st_folium(create_map(aqi_data, hospitals_df, risk_color, selected_hospital_dict), height=520, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[4]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("User History")
    st.caption(f"Saved AQI checks for {st.session_state['current_user']}.")

    history_df = load_user_history(st.session_state.get("current_user", ""))
    if history_df.empty:
        st.info("No saved history yet. Select a city to create your first history record.")
    else:
        history_df["created_at"] = pd.to_datetime(history_df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
        display_columns = [
            "created_at",
            "city",
            "state",
            "aqi",
            "category",
            "health_risk",
            "predicted_aqi",
            "dominant_pollutant",
            "pm25",
            "pm10",
            "co",
            "no2",
            "source",
        ]
        history_df = history_df[[column for column in display_columns if column in history_df.columns]]
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download User History CSV",
            data=history_df.to_csv(index=False).encode("utf-8"),
            file_name=f"intelliair_history_{st.session_state['current_user']}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

report = pd.DataFrame(
    [
        {
            "city": selected_city,
            "state": aqi_data["state"],
            "aqi": aqi_data["aqi"],
            "category": category,
            "health_risk": health_risk,
            "predicted_aqi": predicted_aqi,
            "dominant_pollutant": aqi_data["dominant"],
            "pm25": aqi_data["pollutants"]["PM2.5"],
            "pm10": aqi_data["pollutants"]["PM10"],
            "co": aqi_data["pollutants"]["CO"],
            "no2": aqi_data["pollutants"]["NO2"],
            "source": aqi_data["source"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    ]
)

st.download_button(
    "Download IntelliAir Report CSV",
    data=report.to_csv(index=False).encode("utf-8"),
    file_name=f"intelliair_report_{selected_city.lower().replace(' ', '_')}.csv",
    mime="text/csv",
)
