import html
import os
import re
import time
import urllib.parse
import itertools
from pathlib import Path

import pandas as pd
import streamlit as st
import requests
from ddgs import DDGS

# ================= PAGE CONFIG & PREMIUM UI =================
st.set_page_config(page_title="EmailScraper Pro - By Solo Tech", page_icon="🚀", layout="wide")

# 🔥 MASSIVE PREMIUM CSS INJECTION 🔥
st.markdown("""
<style>
    /* Premium Dark Slate Background */
    .stApp { 
        background: radial-gradient(circle at top, #1e293b, #0f172a); 
        color: #f8fafc; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    }
    header, #MainMenu, footer { visibility: hidden !important; }
    
    /* Sleek Floating Cards for Columns */
    [data-testid="column"] {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        padding: 25px 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        border: 1px solid #334155;
    }
    
    /* Input Fields & Text Areas - Glassmorphism */
    .stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div { 
        background-color: #0f172a !important; 
        color: white !important; 
        border: 1px solid #334155 !important; 
        border-radius: 10px !important; 
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox div[data-baseweb="select"] > div:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;
    }
    
    /* Premium Gradient Buttons */
    .stButton > button[kind="primary"] { 
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important; 
        color: white !important; 
        border-radius: 10px !important; 
        font-weight: bold !important; 
        border: none; 
        width: 100%; 
        padding: 12px !important;
        transition: all 0.3s ease; 
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }
    .stButton > button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6); }
    
    .stButton > button[kind="secondary"] { 
        background: linear-gradient(90deg, #10b981, #059669) !important; 
        color: white !important; 
        border-radius: 10px !important; 
        font-weight: bold !important; 
        border: none; 
        width: 100%; 
        padding: 12px !important;
        transition: all 0.3s ease; 
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }
    .stButton > button[kind="secondary"]:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6); }
    
    /* Section Headers */
    .card-header { font-size: 24px; font-weight: 800; background: -webkit-linear-gradient(#f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; border-bottom: 1px solid #334155; padding-bottom: 15px; margin-bottom: 25px; display: flex; align-items: center; gap: 10px;}
    
    /* Terminal Console */
    .terminal-box { background-color: #020617; color: #38bdf8; padding: 18px; border-radius: 12px; font-family: 'Consolas', monospace; font-size: 13px; border: 1px solid #1e293b; margin-top: 20px; box-shadow: inset 0 0 15px rgba(0,0,0,0.8);}
</style>
""", unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "ultimate_leads_vault.csv"

# 🔥 COMPACT & SCALABLE GLOBAL ATLAS
GLOBAL_ATLAS = {

    "United States": [
        "New York City", "Los Angeles", "Chicago", "Houston", "Phoenix",
        "Philadelphia", "San Antonio", "San Diego", "Dallas", "Fort Worth",
        "Jacksonville", "Austin", "San Jose", "Charlotte", "Columbus",
        "Indianapolis", "San Francisco", "Seattle", "Denver", "Washington",
        "Nashville", "Oklahoma City", "Boston", "Las Vegas", "Portland",
        "Detroit", "Memphis", "Louisville", "Baltimore", "Milwaukee",
        "Albuquerque", "Tucson", "Fresno", "Sacramento", "Kansas City",
        "Atlanta", "Miami", "Tampa", "Minneapolis", "Cleveland",
        "Pittsburgh", "Cincinnati", "Orlando", "St. Louis", "New Orleans",
        "Raleigh", "Salt Lake City", "San Antonio", "Omaha", "Honolulu"
    ],

    "United Kingdom": [
        "London", "Birmingham", "Manchester", "Liverpool", "Leeds",
        "Glasgow", "Newcastle upon Tyne", "Nottingham", "Sheffield", "Bristol",
        "Edinburgh", "Leicester", "Coventry", "Cardiff", "Belfast",
        "Bradford", "Stoke-on-Trent", "Wolverhampton", "Plymouth", "Derby",
        "Southampton", "Reading", "Sunderland", "Brighton", "Hull",
        "Preston", "Swansea", "Norwich", "Cambridge", "Oxford",
        "Milton Keynes", "Northampton", "Luton", "York", "Bolton",
        "Bournemouth", "Swindon", "Peterborough", "Exeter", "Blackpool"
    ],

    "Canada": [
        "Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton",
        "Ottawa", "Winnipeg", "Quebec City", "Hamilton", "Kitchener",
        "London", "Victoria", "Halifax", "Oshawa", "Windsor",
        "Saskatoon", "Regina", "St. John's", "Barrie", "Kelowna",
        "Abbotsford", "Kingston", "Guelph", "Sherbrooke", "Moncton",
        "Sudbury", "Thunder Bay", "Waterloo", "Vaughan", "Burlington"
    ],

    "Australia": [
        "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide",
        "Gold Coast", "Canberra", "Newcastle", "Wollongong", "Geelong",
        "Hobart", "Townsville", "Cairns", "Toowoomba", "Darwin",
        "Ballarat", "Bendigo", "Albury", "Launceston", "Mackay",
        "Rockhampton", "Bunbury", "Bundaberg", "Hervey Bay", "Wagga Wagga",
        "Coffs Harbour", "Gladstone", "Mildura", "Shepparton", "Tamworth"
    ],

    "Germany": [
        "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt",
        "Stuttgart", "Dusseldorf", "Leipzig", "Dortmund", "Essen",
        "Bremen", "Dresden", "Hanover", "Nuremberg", "Duisburg",
        "Bochum", "Wuppertal", "Bielefeld", "Bonn", "Munster",
        "Karlsruhe", "Mannheim", "Augsburg", "Wiesbaden", "Gelsenkirchen",
        "Aachen", "Braunschweig", "Kiel", "Magdeburg", "Freiburg"
    ],

    "France": [
        "Paris", "Marseille", "Lyon", "Toulouse", "Nice",
        "Nantes", "Montpellier", "Strasbourg", "Bordeaux", "Lille",
        "Rennes", "Reims", "Toulon", "Saint-Etienne", "Le Havre",
        "Grenoble", "Dijon", "Angers", "Nimes", "Villeurbanne",
        "Clermont-Ferrand", "Aix-en-Provence", "Brest", "Tours", "Amiens",
        "Rouen", "Metz", "Perpignan", "Orleans", "Cannes"
    ],

    "Italy": [
        "Rome", "Milan", "Naples", "Turin", "Palermo",
        "Genoa", "Bologna", "Florence", "Bari", "Catania",
        "Venice", "Verona", "Messina", "Padua", "Trieste",
        "Taranto", "Brescia", "Prato", "Parma", "Modena",
        "Reggio Calabria", "Perugia", "Livorno", "Ravenna", "Cagliari",
        "Foggia", "Rimini", "Salerno", "Ferrara", "Bergamo"
    ],

    "Spain": [
        "Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza",
        "Malaga", "Murcia", "Palma", "Las Palmas", "Bilbao",
        "Alicante", "Cordoba", "Valladolid", "Vigo", "Gijon",
        "A Coruna", "Vitoria-Gasteiz", "Granada", "Elche", "Oviedo",
        "Santa Cruz de Tenerife", "Badalona", "Cartagena", "Terrassa",
        "Jerez de la Frontera", "Sabadell", "Pamplona", "Almeria",
        "Santander", "Tarragona"
    ],

    "India": [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad",
        "Chennai", "Kolkata", "Pune", "Surat", "Jaipur",
        "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
        "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad",
        "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
        "Rajkot", "Varanasi", "Srinagar", "Amritsar", "Chandigarh",
        "Coimbatore", "Kochi", "Kozhikode", "Bhubaneswar", "Guwahati"
    ],

    "China": [
        "Shanghai", "Beijing", "Guangzhou", "Shenzhen", "Chongqing",
        "Tianjin", "Chengdu", "Wuhan", "Nanjing", "Xi'an",
        "Hangzhou", "Suzhou", "Dongguan", "Shenyang", "Qingdao",
        "Changsha", "Harbin", "Dalian", "Jinan", "Zhengzhou",
        "Kunming", "Xiamen", "Fuzhou", "Hefei", "Ningbo",
        "Nanchang", "Urumqi", "Lanzhou", "Taiyuan", "Shijiazhuang",
        "Changchun", "Nanning", "Guiyang", "Wenzhou", "Foshan"
    ],

    "Japan": [
        "Tokyo", "Yokohama", "Osaka", "Nagoya", "Sapporo",
        "Fukuoka", "Kobe", "Kyoto", "Kawasaki", "Saitama",
        "Hiroshima", "Sendai", "Kitakyushu", "Chiba", "Sakai",
        "Niigata", "Hamamatsu", "Kumamoto", "Sagamihara", "Okayama",
        "Shizuoka", "Kagoshima", "Matsuyama", "Kanazawa", "Nagasaki",
        "Himeji", "Utsunomiya", "Oita", "Nara", "Toyama"
    ],

    "United Arab Emirates": [
        "Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Al Ain",
        "Ras Al Khaimah", "Fujairah", "Umm Al Quwain", "Khor Fakkan",
        "Kalba", "Dibba Al-Fujairah", "Dibba Al-Hisn", "Madinat Zayed",
        "Ruwais", "Jebel Ali", "Hatta", "Al Dhaid", "Al Madam",
        "Mussafah", "Masdar City", "Al Hamriyah", "Ghayathi",
        "Liwa", "Dalma", "Suweihan"
    ],

    "Armenia": [
        "Yerevan", "Gyumri", "Vanadzor", "Vagharshapat", "Hrazdan",
        "Abovyan", "Kapan", "Armavir", "Artashat", "Gavar",
        "Charentsavan", "Ijevan", "Sevan", "Ararat", "Ashtarak",
        "Dilijan", "Spitak", "Sisian", "Goris", "Masis",
        "Aparan", "Maralik", "Berd", "Vardenis", "Yeghvard"
    ],

    "Azerbaijan": [
        "Baku", "Ganja", "Sumqayit", "Mingachevir", "Lankaran",
        "Nakhchivan", "Shaki", "Yevlakh", "Shirvan", "Qabala",
        "Quba", "Shamakhi", "Agdam", "Barda", "Salyan",
        "Khirdalan", "Naftalan", "Sabirabad", "Bilasuvar", "Jalilabad",
        "Astara", "Masalli", "Zaqatala", "Qusar", "Imishli"
    ],

    "Bahrain": [
        "Manama", "Riffa", "Muharraq", "Hamad Town", "Isa Town",
        "A'ali", "Sitra", "Budaiya", "Jidhafs", "Al Hidd",
        "Juffair", "Sanabis", "Tubli", "Diraz", "Barbar",
        "Saar", "Karzakan", "Daih", "Bani Jamra", "Jannusan",
        "Galali", "Dumistan", "Karranah", "Shahrakan", "Malikiya"
    ],

    "Bangladesh": [
        "Dhaka", "Chattogram", "Khulna", "Rajshahi", "Sylhet",
        "Rangpur", "Mymensingh", "Barisal", "Comilla", "Narayanganj",
        "Gazipur", "Bogra", "Jessore", "Dinajpur", "Cox's Bazar",
        "Tangail", "Feni", "Brahmanbaria", "Narsingdi", "Saidpur",
        "Pabna", "Kushtia", "Faridpur", "Noakhali", "Jamalpur"
    ],

    "Bhutan": [
        "Thimphu", "Phuntsholing", "Punakha", "Paro", "Wangdue Phodrang",
        "Samdrup Jongkhar", "Trashigang", "Mongar", "Trongsa", "Jakar",
        "Sarpang", "Samtse", "Tsirang", "Dagana", "Lhuentse",
        "Pemagatshel", "Trashiyangtse", "Haa", "Gasa", "Tashigang",
        "Gelephu", "Nganglam", "Chukha", "Damphu", "Kanglung"
    ],

    "Brunei": [
        "Bandar Seri Begawan", "Kuala Belait", "Seria", "Tutong",
        "Bangar", "Muara", "Jerudong", "Mentiri", "Berakas",
        "Gadong", "Kiulap", "Sengkurong", "Lumut", "Labi",
        "Liang", "Kampong Ayer", "Tanah Jambu", "Katimahar",
        "Rimba", "Telisai", "Lamunin", "Kuala Lurah", "Bukit Shahbandar",
        "Sungai Liang", "Pekan Tutong"
    ],

    "Cambodia": [
        "Phnom Penh", "Siem Reap", "Battambang", "Sihanoukville", "Poipet",
        "Kampong Cham", "Kampong Chhnang", "Kampong Speu", "Kampong Thom",
        "Kampot", "Kep", "Kratie", "Pursat", "Sisophon", "Stung Treng",
        "Svay Rieng", "Takeo", "Pailin", "Suong", "Samraong",
        "Banlung", "Sen Monorom", "Prey Veng", "Ta Khmau", "Chbar Mon"
    ],

    "China": [
        "Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chongqing",
        "Tianjin", "Chengdu", "Wuhan", "Nanjing", "Xi'an",
        "Hangzhou", "Suzhou", "Dongguan", "Shenyang", "Qingdao",
        "Changsha", "Harbin", "Dalian", "Jinan", "Zhengzhou",
        "Kunming", "Xiamen", "Fuzhou", "Hefei", "Ningbo",
        "Nanchang", "Urumqi", "Lanzhou", "Taiyuan", "Shijiazhuang"
    ],

    "Georgia": [
        "Tbilisi", "Batumi", "Kutaisi", "Rustavi", "Gori",
        "Zugdidi", "Poti", "Kobuleti", "Khashuri", "Samtredia",
        "Senaki", "Zestafoni", "Marneuli", "Telavi", "Akhaltsikhe",
        "Borjomi", "Ozurgeti", "Kaspi", "Gardabani", "Chiatura",
        "Sagarejo", "Bolnisi", "Tkibuli", "Mtskheta", "Ambrolauri"
    ],

    "India": [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
        "Kolkata", "Ahmedabad", "Pune", "Surat", "Jaipur",
        "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
        "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad",
        "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
        "Rajkot", "Varanasi", "Srinagar", "Amritsar", "Chandigarh"
    ],

    "Indonesia": [
        "Jakarta", "Surabaya", "Bandung", "Medan", "Semarang",
        "Makassar", "Palembang", "Tangerang", "Depok", "Bekasi",
        "Bogor", "Malang", "Padang", "Denpasar", "Pekanbaru",
        "Bandar Lampung", "Banjarmasin", "Samarinda", "Yogyakarta",
        "Manado", "Balikpapan", "Pontianak", "Mataram", "Jambi",
        "Cirebon"
    ],

    "Iran": [
        "Tehran", "Mashhad", "Isfahan", "Shiraz", "Tabriz",
        "Karaj", "Ahvaz", "Qom", "Kermanshah", "Urmia",
        "Rasht", "Zahedan", "Hamadan", "Kerman", "Ardabil",
        "Yazd", "Qazvin", "Bandar Abbas", "Sanandaj", "Khorramabad",
        "Arak", "Sari", "Gorgan", "Ilam", "Bushehr"
    ],

    "Iraq": [
        "Baghdad", "Basra", "Mosul", "Erbil", "Kirkuk",
        "Najaf", "Karbala", "Sulaymaniyah", "Nasiriyah", "Ramadi",
        "Fallujah", "Hillah", "Diwaniyah", "Kut", "Samarra",
        "Tikrit", "Baqubah", "Duhok", "Zakho", "Amarah",
        "Samawah", "Tal Afar", "Sinjar", "Najaf", "Halabja"
    ],

    "Israel": [
        "Jerusalem", "Tel Aviv", "Haifa", "Rishon LeZion", "Petah Tikva",
        "Ashdod", "Netanya", "Beer Sheva", "Bnei Brak", "Holon",
        "Ramat Gan", "Ashkelon", "Rehovot", "Bat Yam", "Beit Shemesh",
        "Kfar Saba", "Herzliya", "Hadera", "Modi'in", "Nazareth",
        "Lod", "Ramla", "Acre", "Eilat", "Tiberias"
    ],

    "Japan": [
        "Tokyo", "Yokohama", "Osaka", "Nagoya", "Sapporo",
        "Fukuoka", "Kobe", "Kyoto", "Kawasaki", "Saitama",
        "Hiroshima", "Sendai", "Kitakyushu", "Chiba", "Sakai",
        "Niigata", "Hamamatsu", "Kumamoto", "Sagamihara", "Okayama",
        "Shizuoka", "Kagoshima", "Matsuyama", "Kanazawa", "Nagasaki"
    ],

    "Jordan": [
        "Amman", "Zarqa", "Irbid", "Aqaba", "Madaba",
        "Salt", "Jerash", "Mafraq", "Karak", "Tafilah",
        "Ma'an", "Ramtha", "Sahab", "Russeifa", "Ajloun",
        "Fuheis", "Naour", "Wadi Musa", "Shobak", "Al Husn",
        "As-Salt", "Dhiban", "Azraq", "Kufranjah", "Al Jizah"
    ],

    "Kazakhstan": [
        "Almaty", "Astana", "Shymkent", "Karaganda", "Aktobe",
        "Taraz", "Pavlodar", "Ust-Kamenogorsk", "Semey", "Atyrau",
        "Kostanay", "Kyzylorda", "Petropavl", "Aktau", "Oral",
        "Temirtau", "Turkistan", "Kokshetau", "Ekibastuz", "Rudny",
        "Zhezkazgan", "Balkhash", "Kentau", "Taldykorgan", "Kapshagay"
    ],

    "Kuwait": [
        "Kuwait City", "Hawalli", "Salmiya", "Farwaniya", "Jahra",
        "Mubarak Al-Kabeer", "Fahaheel", "Mangaf", "Mahboula", "Abu Halifa",
        "Sabah Al Salem", "Al Ahmadi", "Ardiya", "Shuwaikh", "Qurain",
        "Jaber Al Ahmad", "Saad Al Abdullah", "Sulaibikhat", "Qadsiya",
        "Rumaithiya", "Salwa", "Bayan", "Mishref", "Jabriya", "Surra"
    ],

    "Kyrgyzstan": [
        "Bishkek", "Osh", "Jalal-Abad", "Karakol", "Tokmok",
        "Uzgen", "Naryn", "Talas", "Balykchy", "Kara-Balta",
        "Kyzyl-Kiya", "Tash-Kumyr", "Batken", "Kant", "Isfana",
        "Kochkor-Ata", "Kemin", "Mailuu-Suu", "Kerben", "Cholpon-Ata",
        "Bazar-Korgon", "Kara-Suu", "Shopokov", "Kadamjay", "Toktogul"
    ],

    "Laos": [
        "Vientiane", "Luang Prabang", "Pakse", "Savannakhet", "Thakhek",
        "Phonsavan", "Muang Xay", "Vang Vieng", "Luang Namtha",
        "Saravan", "Phongsali", "Attapeu", "Xam Neua", "Pakbeng",
        "Muang Kasi", "Vieng Xay", "Muang Sing", "Nong Khiaw",
        "Khong Island", "Salavan", "Paksan", "Thoulakhom", "Hinheup",
        "Kaysone Phomvihane", "Champasak"
    ],

    "Lebanon": [
        "Beirut", "Tripoli", "Sidon", "Tyre", "Zahle",
        "Jounieh", "Baalbek", "Byblos", "Aley", "Batroun",
        "Nabatieh", "Bint Jbeil", "Hermel", "Jezzine", "Chouf",
        "Antelias", "Broummana", "Jal el Dib", "Dekwaneh", "Baabda",
        "Bikfaya", "Amchit", "Marjayoun", "Rashaya", "Hasbaya"
    ],

    "Malaysia": [
        "Kuala Lumpur", "George Town", "Johor Bahru", "Ipoh", "Shah Alam",
        "Kota Kinabalu", "Kuching", "Malacca City", "Alor Setar", "Kuala Terengganu",
        "Kota Bharu", "Seremban", "Kuantan", "Petaling Jaya", "Subang Jaya",
        "Klang", "Miri", "Sandakan", "Tawau", "Sibu",
        "Batu Pahat", "Taiping", "Kajang", "Putrajaya", "Cyberjaya"
    ],

    "Maldives": [
        "Male", "Addu City", "Fuvahmulah", "Kulhudhuffushi", "Thinadhoo",
        "Naifaru", "Hithadhoo", "Viligili", "Eydhafushi", "Dhidhdhoo",
        "Mahibadhoo", "Hulhumale", "Hinnavaru", "Felidhoo", "Ungoofaaru",
        "Muli", "Dhangethi", "Thulusdhoo", "Rasdhoo", "Huraa",
        "Gaafu Dhaalu", "Meedhoo", "Maradhoo", "Fonadhoo", "Kudahuvadhoo"
    ],

    "Mongolia": [
        "Ulaanbaatar", "Erdenet", "Darkhan", "Choibalsan", "Mörön",
        "Nalaikh", "Ölgii", "Arvaikheer", "Bayankhongor", "Dalanzadgad",
        "Sükhbaatar", "Zuunmod", "Uliastai", "Baruun-Urt", "Mandalgovi",
        "Tsetserleg", "Ulgii", "Altai", "Bulgan", "Kharkhorin",
        "Baganuur", "Zamyn-Uud", "Sharyngol", "Khorgos", "Undurkhaan"
    ],

    "Myanmar": [
        "Yangon", "Mandalay", "Naypyidaw", "Mawlamyine", "Bago",
        "Taunggyi", "Pathein", "Monywa", "Sittwe", "Myitkyina",
        "Meiktila", "Myeik", "Dawei", "Hpa-An", "Lashio",
        "Pyin Oo Lwin", "Magway", "Pakokku", "Sagaing", "Tachileik",
        "Kalay", "Hinthada", "Thayet", "Kyaikto", "Kengtung"
    ],

    "Nepal": [
        "Kathmandu", "Pokhara", "Lalitpur", "Biratnagar", "Birgunj",
        "Bharatpur", "Butwal", "Dharan", "Hetauda", "Janakpur",
        "Nepalgunj", "Dhangadhi", "Itahari", "Bhaktapur", "Birtamod",
        "Mechinagar", "Ghorahi", "Tulsipur", "Damak", "Kirtipur",
        "Banepa", "Dhankuta", "Baglung", "Besisahar", "Tikapur"
    ],

    "North Korea": [
        "Pyongyang", "Hamhung", "Chongjin", "Nampo", "Wonsan",
        "Sinuiju", "Kaesong", "Sariwon", "Pyongsong", "Hyesan",
        "Kanggye", "Haeju", "Rason", "Tanchon", "Kusong",
        "Anju", "Songnim", "Hoeryong", "Kimchaek", "Musan",
        "Manpo", "Tokchon", "Sunchon", "Sakchu", "Kapsan"
    ],

    "Oman": [
        "Muscat", "Salalah", "Sohar", "Nizwa", "Sur",
        "Ibri", "Rustaq", "Barka", "Khasab", "Al Buraimi",
        "Ibra", "Bahla", "Duqm", "Shinas", "Nakhal",
        "Bidbid", "Samail", "Al Hamra", "Adam", "Mahout",
        "Thumrait", "Mirbat", "Taqah", "Karak", "Liwa"
    ],

    "Pakistan": [
        "Karachi", "Lahore", "Islamabad", "Faisalabad", "Rawalpindi",
        "Multan", "Peshawar", "Quetta", "Gujranwala", "Sialkot",
        "Bahawalpur", "Sargodha", "Sukkur", "Jhang", "Sheikhupura",
        "Larkana", "Gujrat", "Mardan", "Kasur", "Rahim Yar Khan",
        "Sahiwal", "Okara", "Wah Cantt", "Dera Ghazi Khan", "Abbottabad",
        "Mingora", "Nawabshah", "Mirpur", "Chiniot", "Muzaffarabad"
    ],

    "Palestine": [
        "Gaza City", "Ramallah", "Hebron", "Nablus", "Jenin",
        "Bethlehem", "Jericho", "Tulkarm", "Qalqilya", "Rafah",
        "Khan Yunis", "Deir al-Balah", "Salfit", "Tubas", "Dura",
        "Beit Jala", "Beit Sahour", "Yatta", "Bani Na'im", "Abu Dis",
        "Al-Bireh", "Anabta", "Arraba", "Birzeit", "Jaba"
    ],

    "Philippines": [
        "Manila", "Quezon City", "Davao City", "Cebu City", "Zamboanga City",
        "Antipolo", "Pasig", "Taguig", "Cagayan de Oro", "Parañaque",
        "Dasmariñas", "Valenzuela", "Las Piñas", "Caloocan", "General Santos",
        "Bacolod", "Iloilo City", "Lapu-Lapu", "Makati", "Muntinlupa",
        "Angeles", "Baguio", "Batangas City", "Naga", "Legazpi"
    ],

    "Qatar": [
        "Doha", "Al Rayyan", "Al Wakrah", "Al Khor", "Dukhan",
        "Umm Salal", "Mesaieed", "Al Shamal", "Lusail", "Al Wukair",
        "Al Daayen", "Al Ruwais", "Al Thakhira", "Simaisma", "Fuwayrit",
        "Zubarah", "Madinat ash Shamal", "Abu Samra", "Rawdat Rashed",
        "Umm Bab", "Al Ghuwairiya", "Al Jumailiya", "Al Karaana",
        "Al Shahaniya", "Birkat Al Awamer"
    ],

    "Saudi Arabia": [
        "Riyadh", "Jeddah", "Mecca", "Medina", "Dammam",
        "Khobar", "Taif", "Tabuk", "Buraidah", "Abha",
        "Khamis Mushait", "Hail", "Najran", "Jizan", "Yanbu",
        "Al Hofuf", "Jubail", "Al Qatif", "Arar", "Sakaka",
        "Al Bahah", "Al Kharj", "Dhahran", "Qurayyat", "Ras Tanura"
    ],

    "Singapore": [
        "Singapore", "Tampines", "Woodlands", "Jurong West", "Bedok",
        "Hougang", "Sengkang", "Yishun", "Choa Chu Kang", "Bukit Batok",
        "Bukit Panjang", "Pasir Ris", "Punggol", "Ang Mo Kio", "Clementi",
        "Toa Payoh", "Serangoon", "Bishan", "Queenstown", "Geylang",
        "Kallang", "Marine Parade", "Novena", "Orchard", "Sentosa"
    ],

    "South Korea": [
        "Seoul", "Busan", "Incheon", "Daegu", "Daejeon",
        "Gwangju", "Suwon", "Ulsan", "Changwon", "Goyang",
        "Yongin", "Seongnam", "Bucheon", "Cheongju", "Jeonju",
        "Ansan", "Anyang", "Pohang", "Hwaseong", "Gimhae",
        "Pyeongtaek", "Jeju City", "Gimpo", "Gwangmyeong", "Gangneung"
    ],

    "Sri Lanka": [
        "Colombo", "Kandy", "Galle", "Jaffna", "Negombo",
        "Batticaloa", "Trincomalee", "Kurunegala", "Anuradhapura",
        "Ratnapura", "Matara", "Badulla", "Nuwara Eliya", "Kegalle",
        "Kalutara", "Hambantota", "Ampara", "Vavuniya", "Mannar",
        "Polonnaruwa", "Chilaw", "Panadura", "Moratuwa", "Dehiwala",
        "Mount Lavinia"
    ],

    "Syria": [
        "Damascus", "Aleppo", "Homs", "Latakia", "Hama",
        "Deir ez-Zor", "Raqqa", "Daraa", "Idlib", "Tartus",
        "Hasakah", "Qamishli", "Palmyra", "Douma", "Jableh",
        "Safita", "Manbij", "Afrin", "Azaz", "Al-Bab",
        "Salamiyah", "Masyaf", "Maarat al-Numan", "Tadmur", "Yabrud"
    ],

    "Tajikistan": [
        "Dushanbe", "Khujand", "Kulob", "Bokhtar", "Istaravshan",
        "Tursunzoda", "Vahdat", "Panjakent", "Isfara", "Konibodom",
        "Hisor", "Nurek", "Rogun", "Khorugh", "Danghara",
        "Farkhor", "Yovon", "Vose", "Norak", "Buston",
        "Ghafurov", "Taboshar", "Qubodiyon", "Shahritus", "Rasht"
    ],

    "Thailand": [
        "Bangkok", "Chiang Mai", "Phuket", "Pattaya", "Nonthaburi",
        "Hat Yai", "Nakhon Ratchasima", "Udon Thani", "Khon Kaen",
        "Chiang Rai", "Ayutthaya", "Surat Thani", "Nakhon Si Thammarat",
        "Ubon Ratchathani", "Rayong", "Hua Hin", "Krabi", "Lampang",
        "Phitsanulok", "Samut Prakan", "Chon Buri", "Sukhothai",
        "Kanchanaburi", "Trang", "Mae Sot"
    ],

    "Timor-Leste": [
        "Dili", "Baucau", "Maliana", "Suai", "Same",
        "Lospalos", "Aileu", "Ainaro", "Ermera", "Liquica",
        "Manatuto", "Viqueque", "Gleno", "Pante Macassar", "Tutuala",
        "Venilale", "Maubisse", "Los Palos", "Atsabe", "Balibo",
        "Bazartete", "Fatuberlio", "Hato-Udo", "Laclubar", "Metinaro"
    ],

    "Turkey": [
        "Istanbul", "Ankara", "Izmir", "Bursa", "Antalya",
        "Adana", "Konya", "Gaziantep", "Mersin", "Diyarbakir",
        "Kayseri", "Eskisehir", "Samsun", "Denizli", "Sanliurfa",
        "Malatya", "Kahramanmaras", "Erzurum", "Van", "Batman",
        "Elazig", "Izmit", "Manisa", "Balikesir", "Trabzon"
    ],

    "Turkmenistan": [
        "Ashgabat", "Turkmenabat", "Dashoguz", "Mary", "Balkanabat",
        "Turkmenbashi", "Bayramaly", "Tejen", "Serdar", "Abadan",
        "Kaka", "Atamyrat", "Kerki", "Gokdepe", "Buzmeyin",
        "Annau", "Magdanly", "Seydi", "Farap", "Gazojak",
        "Bereket", "Gumdag", "Hazar", "Serhetabat", "Tagtabazar"
    ],

    "United Arab Emirates": [
        "Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Al Ain",
        "Ras Al Khaimah", "Fujairah", "Umm Al Quwain", "Khor Fakkan",
        "Kalba", "Dibba Al-Fujairah", "Dibba Al-Hisn", "Madinat Zayed",
        "Ruwais", "Liwa Oasis", "Ghayathi", "Jebel Ali", "Hatta",
        "Masdar City", "Al Dhaid", "Mleiha", "Al Madam", "Dhaid",
        "Al Hamriyah", "Mussafah"
    ],

    "Uzbekistan": [
        "Tashkent", "Samarkand", "Namangan", "Andijan", "Bukhara",
        "Nukus", "Qarshi", "Fergana", "Kokand", "Jizzakh",
        "Termez", "Urgench", "Navoi", "Gulistan", "Chirchiq",
        "Angren", "Margilan", "Shahrisabz", "Bekabad", "Olmaliq",
        "Zarafshan", "Denov", "Kattakurgan", "Khiva", "Yangiyul"
    ],

    "Vietnam": [
        "Ho Chi Minh City", "Hanoi", "Haiphong", "Da Nang", "Can Tho",
        "Bien Hoa", "Hue", "Nha Trang", "Buon Ma Thuot", "Vung Tau",
        "Quy Nhon", "Thai Nguyen", "Nam Dinh", "Vinh", "Long Xuyen",
        "Rach Gia", "My Tho", "Phan Thiet", "Cam Ranh", "Da Lat",
        "Thanh Hoa", "Hai Duong", "Bac Ninh", "Ha Long", "Pleiku"
    ],

    "Yemen": [
        "Sanaa", "Aden", "Taiz", "Hodeidah", "Ibb",
        "Mukalla", "Dhamar", "Saada", "Hajjah", "Zinjibar",
        "Marib", "Amran", "Bayt al-Faqih", "Rada'a", "Ataq",
        "Lahij", "Seiyun", "Shibam", "Al Ghaydah", "Zabid",
        "Khamir", "Jiblah", "Bajil", "Abs", "Bani Matar"
    ],

    # =========================
    # EUROPE
    # =========================

    "Albania": [
        "Tirana", "Durres", "Vlore", "Shkoder", "Fier",
        "Elbasan", "Korce", "Berat", "Lushnje", "Kukes",
        "Gjirokaster", "Sarande", "Lezhe", "Pogradec", "Kavaje",
        "Laç", "Patos", "Burrel", "Kruje", "Librazhd",
        "Gramsh", "Permet", "Peshkopi", "Himare", "Tepelene"
    ],

    "Andorra": [
        "Andorra la Vella", "Escaldes-Engordany", "Encamp", "Sant Julia de Loria",
        "La Massana", "Canillo", "Ordino", "Pas de la Casa", "Arinsal",
        "El Pas de la Casa", "Soldeu", "Anyos", "Erts", "La Cortinada",
        "Llorts", "Sispony", "Aixirivall", "Bixessarri", "Fontaneda",
        "Aubinyà", "Vila", "Engolasters", "Ransol", "Prats", "Bordes d'Envalira"
    ],

    "Austria": [
        "Vienna", "Graz", "Linz", "Salzburg", "Innsbruck",
        "Klagenfurt", "Villach", "Wels", "Sankt Pölten", "Dornbirn",
        "Wiener Neustadt", "Steyr", "Feldkirch", "Bregenz", "Leonding",
        "Klosterneuburg", "Baden", "Wolfsberg", "Leoben", "Krems",
        "Traun", "Amstetten", "Kapfenberg", "Mödling", "Hallein"
    ],

    "Belarus": [
        "Minsk", "Gomel", "Mogilev", "Vitebsk", "Grodno",
        "Brest", "Babruysk", "Baranavichy", "Barysaw", "Pinsk",
        "Orsha", "Mozyr", "Lida", "Polotsk", "Novopolotsk",
        "Slutsk", "Zhlobin", "Svetlogorsk", "Rechitsa", "Slonim",
        "Kobryn", "Volkovysk", "Krichev", "Dobrush", "Osipovichi"
    ],

    "Belgium": [
        "Brussels", "Antwerp", "Ghent", "Charleroi", "Liège",
        "Bruges", "Namur", "Leuven", "Mons", "Mechelen",
        "Aalst", "Kortrijk", "Hasselt", "Ostend", "Sint-Niklaas",
        "Roeselare", "Turnhout", "Genk", "Tournai", "Verviers",
        "Dendermonde", "Mouscron", "Lokeren", "Beringen", "Herentals"
    ],

    "Bosnia and Herzegovina": [
        "Sarajevo", "Banja Luka", "Tuzla", "Zenica", "Mostar",
        "Bijeljina", "Brcko", "Prijedor", "Trebinje", "Travnik",
        "Cazin", "Doboj", "Gorazde", "Gradacac", "Visoko",
        "Livno", "Bugojno", "Konjic", "Sanski Most", "Gracanica",
        "Srebrenik", "Zvornik", "Foca", "Jajce", "Vitez"
    ],

    "Bulgaria": [
        "Sofia", "Plovdiv", "Varna", "Burgas", "Ruse",
        "Stara Zagora", "Pleven", "Sliven", "Dobrich", "Shumen",
        "Pernik", "Haskovo", "Yambol", "Pazardzhik", "Blagoevgrad",
        "Veliko Tarnovo", "Vratsa", "Gabrovo", "Asenovgrad", "Vidin",
        "Kyustendil", "Kazanlak", "Montana", "Targovishte", "Silistra"
    ],

    "Croatia": [
        "Zagreb", "Split", "Rijeka", "Osijek", "Zadar",
        "Slavonski Brod", "Pula", "Karlovac", "Varazdin", "Sibenik",
        "Sisak", "Dubrovnik", "Bjelovar", "Vinkovci", "Koprivnica",
        "Cakovec", "Samobor", "Solin", "Vukovar", "Pozega",
        "Metkovic", "Zapresic", "Knin", "Makarska", "Trogir"
    ],

    "Czech Republic": [
        "Prague", "Brno", "Ostrava", "Plzen", "Liberec",
        "Olomouc", "Ceske Budejovice", "Hradec Kralove", "Pardubice",
        "Usti nad Labem", "Zlin", "Havířov", "Kladno", "Most",
        "Opava", "Jihlava", "Frydek-Mistek", "Teplice", "Karvina",
        "Decin", "Chomutov", "Mlada Boleslav", "Prostejov", "Prerov",
        "Trinec"
    ],

    "Denmark": [
        "Copenhagen", "Aarhus", "Odense", "Aalborg", "Esbjerg",
        "Randers", "Kolding", "Horsens", "Vejle", "Roskilde",
        "Herning", "Silkeborg", "Næstved", "Fredericia", "Viborg",
        "Køge", "Holstebro", "Taastrup", "Slagelse", "Hillerød",
        "Sønderborg", "Svendborg", "Hjørring", "Frederikshavn", "Helsingør"
    ],

    "Estonia": [
        "Tallinn", "Tartu", "Narva", "Pärnu", "Kohtla-Järve",
        "Viljandi", "Maardu", "Rakvere", "Kuressaare", "Sillamäe",
        "Võru", "Valga", "Jõhvi", "Haapsalu", "Paide",
        "Keila", "Saue", "Elva", "Põlva", "Tapa",
        "Kiviõli", "Põltsamaa", "Rapla", "Jõgeva", "Paldiski"
    ],

    "Finland": [
        "Helsinki", "Espoo", "Tampere", "Vantaa", "Oulu",
        "Turku", "Jyväskylä", "Lahti", "Kuopio", "Pori",
        "Kouvola", "Joensuu", "Lappeenranta", "Hämeenlinna", "Vaasa",
        "Seinäjoki", "Rovaniemi", "Mikkeli", "Kotka", "Salo",
        "Porvoo", "Kokkola", "Hyvinkää", "Lohja", "Järvenpää"
    ],

    "France": [
        "Paris", "Marseille", "Lyon", "Toulouse", "Nice",
        "Nantes", "Montpellier", "Strasbourg", "Bordeaux", "Lille",
        "Rennes", "Reims", "Toulon", "Saint-Étienne", "Le Havre",
        "Grenoble", "Dijon", "Angers", "Nîmes", "Villeurbanne",
        "Clermont-Ferrand", "Aix-en-Provence", "Brest", "Tours", "Amiens"
    ],

    "Germany": [
        "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt",
        "Stuttgart", "Düsseldorf", "Leipzig", "Dortmund", "Essen",
        "Bremen", "Dresden", "Hanover", "Nuremberg", "Duisburg",
        "Bochum", "Wuppertal", "Bielefeld", "Bonn", "Münster",
        "Karlsruhe", "Mannheim", "Augsburg", "Wiesbaden", "Gelsenkirchen"
    ],

    "Greece": [
        "Athens", "Thessaloniki", "Patras", "Heraklion", "Larissa",
        "Volos", "Ioannina", "Chania", "Agrinio", "Kalamata",
        "Katerini", "Alexandroupoli", "Rhodes", "Corfu", "Tripoli",
        "Lamia", "Komotini", "Kavala", "Serres", "Chalcis",
        "Veria", "Xanthi", "Kos", "Mytilene", "Rethymno"
    ],

    "Hungary": [
        "Budapest", "Debrecen", "Szeged", "Miskolc", "Pecs",
        "Gyor", "Nyiregyhaza", "Kecskemet", "Szekesfehervar", "Szombathely",
        "Szolnok", "Tatabanya", "Kaposvar", "Bekescsaba", "Eger",
        "Zalaegerszeg", "Sopron", "Veszprem", "Nagykanizsa", "Dunaujvaros",
        "Hodmezovasarhely", "Cegled", "Baja", "Esztergom", "Vac"
    ],

    "Iceland": [
        "Reykjavik", "Kopavogur", "Hafnarfjordur", "Akureyri", "Reykjanesbaer",
        "Gardabaer", "Mosfellsbaer", "Akranes", "Selfoss", "Seltjarnarnes",
        "Vestmannaeyjar", "Grindavik", "Isafjordur", "Egilsstadir", "Husavik",
        "Borgarnes", "Sauðarkrokur", "Hofn", "Neskaupstadur", "Dalvik",
        "Siglufjordur", "Stykkisholmur", "Bolungarvik", "Olafsfjordur", "Hella"
    ],

    "Ireland": [
        "Dublin", "Cork", "Limerick", "Galway", "Waterford",
        "Drogheda", "Dundalk", "Swords", "Bray", "Navan",
        "Ennis", "Kilkenny", "Carlow", "Tralee", "Athlone",
        "Letterkenny", "Wexford", "Sligo", "Clonmel", "Naas",
        "Mullingar", "Killarney", "Portlaoise", "Arklow", "Castlebar"
    ],

    "Italy": [
        "Rome", "Milan", "Naples", "Turin", "Palermo",
        "Genoa", "Bologna", "Florence", "Bari", "Catania",
        "Venice", "Verona", "Messina", "Padua", "Trieste",
        "Taranto", "Brescia", "Prato", "Parma", "Modena",
        "Reggio Calabria", "Perugia", "Livorno", "Ravenna", "Cagliari"
    ],

    "Latvia": [
        "Riga", "Daugavpils", "Liepaja", "Jelgava", "Jurmala",
        "Ventspils", "Rezekne", "Valmiera", "Ogre", "Jekabpils",
        "Tukums", "Salaspils", "Cesis", "Kuldiga", "Saldus",
        "Bauska", "Sigulda", "Ludza", "Dobele", "Gulbene",
        "Madona", "Aizkraukle", "Talsi", "Limbaži", "Aluksne"
    ],

    "Liechtenstein": [
        "Vaduz", "Schaan", "Triesen", "Balzers", "Eschen",
        "Mauren", "Triesenberg", "Ruggell", "Gamprin", "Schellenberg",
        "Planken", "Nendeln", "Malbun", "Steg", "Bendern",
        "Masescha", "Silum", "Gaflei", "Rotenboden", "Rietli",
        "Frommenhaus", "Hinterschellenberg", "Mitteldorf", "Forst",
        "Wangerberg"
    ],

    "Lithuania": [
        "Vilnius", "Kaunas", "Klaipeda", "Siauliai", "Panevezys",
        "Alytus", "Marijampole", "Mazeikiai", "Jonava", "Utena",
        "Kedainiai", "Taurage", "Telšiai", "Ukmerge", "Visaginas",
        "Plunge", "Kretinga", "Palanga", "Silute", "Radviliskis",
        "Druskininkai", "Elektrenai", "Jurbarkas", "Pakruojis", "Birzai"
    ],

    "Luxembourg": [
        "Luxembourg City", "Esch-sur-Alzette", "Differdange", "Dudelange",
        "Ettelbruck", "Diekirch", "Strassen", "Bertrange", "Petange",
        "Schifflange", "Bettembourg", "Grevenmacher", "Remich", "Mamer",
        "Mondorf-les-Bains", "Wiltz", "Echternach", "Kayl", "Rumelange",
        "Sanem", "Hesperange", "Steinfort", "Junglinster", "Walferdange", "Vianden"
    ],

    "Malta": [
        "Valletta", "Birkirkara", "Mosta", "Qormi", "Zabbar",
        "Sliema", "San Gwann", "Naxxar", "Rabat", "St. Paul's Bay",
        "Marsaskala", "Fgura", "Zejtun", "Hamrun", "Paola",
        "Mellieha", "Birgu", "Senglea", "Cospicua", "Mdina",
        "Attard", "Balzan", "Dingli", "Mtarfa", "Mgarr"
    ],

    "Moldova": [
        "Chisinau", "Balti", "Bender", "Tiraspol", "Ribnita",
        "Cahul", "Ungheni", "Soroca", "Orhei", "Comrat",
        "Ceadir-Lunga", "Hincesti", "Edinet", "Straseni", "Calarasi",
        "Drochia", "Falesti", "Floresti", "Ialoveni", "Leova",
        "Rezina", "Singerei", "Taraclia", "Vulcanesti", "Criuleni"
    ],

    "Monaco": [
        "Monaco", "Monte Carlo", "La Condamine", "Fontvieille",
        "Larvotto", "Moneghetti", "Monaco-Ville", "Saint-Roman",
        "Les Révoires", "La Colle", "Les Moneghetti", "Port Hercules",
        "Larvotto Beach", "Condamine Harbour", "Fontvieille Harbour",
        "Jardin Exotique", "Beausoleil", "Moneghetti District",
        "Monte-Carlo District", "Larvotto District",
        "Portier", "Spélugues", "Grimaldi Forum", "Carré d'Or", "Tenao"
    ],

    "Montenegro": [
        "Podgorica", "Niksic", "Herceg Novi", "Pljevlja", "Budva",
        "Bar", "Cetinje", "Bijelo Polje", "Berane", "Tivat",
        "Ulcinj", "Rozaje", "Danilovgrad", "Kotor", "Mojkovac",
        "Kolasin", "Plav", "Andrijevica", "Petnjica", "Savnik",
        "Zabljak", "Tuzi", "Gusinje", "Risan", "Perast"
    ],

    "Netherlands": [
        "Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven",
        "Tilburg", "Groningen", "Almere", "Breda", "Nijmegen",
        "Apeldoorn", "Haarlem", "Arnhem", "Enschede", "Amersfoort",
        "Zaanstad", "Haarlemmermeer", "Zwolle", "Leiden", "Dordrecht",
        "Maastricht", "Ede", "Delft", "Venlo", "Deventer"
    ],

    "North Macedonia": [
        "Skopje", "Bitola", "Kumanovo", "Prilep", "Tetovo",
        "Veles", "Ohrid", "Gostivar", "Strumica", "Stip",
        "Kavadarci", "Kocani", "Kicevo", "Gevgelija", "Radovis",
        "Kriva Palanka", "Debar", "Negotino", "Resen", "Berovo",
        "Valandovo", "Delcevo", "Vinica", "Probishtip", "Demir Kapija"
    ],

    "Norway": [
        "Oslo", "Bergen", "Trondheim", "Stavanger", "Drammen",
        "Fredrikstad", "Kristiansand", "Sandnes", "Tromso", "Sarpsborg",
        "Skien", "Alesund", "Sandefjord", "Haugesund", "Tonsberg",
        "Moss", "Bodo", "Arendal", "Hamar", "Larvik",
        "Halden", "Lillehammer", "Molde", "Kongsberg", "Harstad"
    ],

    "Poland": [
        "Warsaw", "Krakow", "Lodz", "Wroclaw", "Poznan",
        "Gdansk", "Szczecin", "Bydgoszcz", "Lublin", "Katowice",
        "Bialystok", "Gdynia", "Czestochowa", "Radom", "Sosnowiec",
        "Torun", "Kielce", "Rzeszow", "Gliwice", "Olsztyn",
        "Zabrze", "Bielsko-Biala", "Bytom", "Zielona Gora", "Rybnik"
    ],

    "Portugal": [
        "Lisbon", "Porto", "Amadora", "Braga", "Coimbra",
        "Funchal", "Setubal", "Almada", "Agualva-Cacem", "Queluz",
        "Aveiro", "Evora", "Faro", "Leiria", "Viseu",
        "Guimaraes", "Vila Nova de Gaia", "Matosinhos", "Portimao", "Sintra",
        "Cascais", "Odivelas", "Barreiro", "Maia", "Torres Vedras"
    ],

    "Romania": [
        "Bucharest", "Cluj-Napoca", "Timisoara", "Iasi", "Constanta",
        "Craiova", "Brasov", "Galati", "Ploiesti", "Oradea",
        "Braila", "Arad", "Pitesti", "Sibiu", "Bacau",
        "Targu Mures", "Baia Mare", "Buzau", "Satu Mare", "Botosani",
        "Drobeta-Turnu Severin", "Suceava", "Piatra Neamt", "Targoviste", "Focsani"
    ],

    "Russia": [
        "Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan",
        "Nizhny Novgorod", "Chelyabinsk", "Samara", "Omsk", "Rostov-on-Don",
        "Ufa", "Krasnoyarsk", "Voronezh", "Perm", "Volgograd",
        "Krasnodar", "Saratov", "Tyumen", "Tolyatti", "Izhevsk",
        "Barnaul", "Ulyanovsk", "Irkutsk", "Khabarovsk", "Vladivostok"
    ],

    "San Marino": [
        "San Marino", "Serravalle", "Borgo Maggiore", "Domagnano",
        "Fiorentino", "Acquaviva", "Faetano", "Montegiardino",
        "Chiesanuova", "Murata", "Cailungo", "Dogana",
        "Falciano", "Valdragone", "Ca' Berlone", "Rovereta",
        "Fiorina", "Galavotto", "Cerbaiola", "Ventoso",
        "Montalbo", "Poggio Casalino", "Baldasserona", "Cà Rigo", "Monte Pulito"
    ],

    "Serbia": [
        "Belgrade", "Novi Sad", "Nis", "Kragujevac", "Subotica",
        "Zrenjanin", "Pancevo", "Cacak", "Novi Pazar", "Kraljevo",
        "Smederevo", "Leskovac", "Valjevo", "Kruševac", "Vranje",
        "Sabac", "Uzice", "Sombor", "Pozarevac", "Jagodina",
        "Loznica", "Sremska Mitrovica", "Vrsac", "Bor", "Prokuplje"
    ],

    "Slovakia": [
        "Bratislava", "Kosice", "Presov", "Zilina", "Nitra",
        "Banska Bystrica", "Trnava", "Trencin", "Martin", "Poprad",
        "Prievidza", "Zvolen", "Povazska Bystrica", "Michalovce",
        "Spisska Nova Ves", "Komarno", "Levice", "Liptovsky Mikulas",
        "Bardejov", "Humenne", "Lucenec", "Pezinok", "Dunajska Streda",
        "Dubnica nad Vahom", "Rimavska Sobota"
    ],

    "Slovenia": [
        "Ljubljana", "Maribor", "Kranj", "Celje", "Koper",
        "Velenje", "Novo Mesto", "Ptuj", "Trbovlje", "Kamnik",
        "Jesenice", "Nova Gorica", "Domzale", "Skofja Loka", "Murska Sobota",
        "Izola", "Postojna", "Logatec", "Slovenj Gradec", "Ravne na Koroskem",
        "Brežice", "Krško", "Sežana", "Ajdovščina", "Idrija"
    ],

    "Spain": [
        "Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza",
        "Malaga", "Murcia", "Palma", "Las Palmas", "Bilbao",
        "Alicante", "Cordoba", "Valladolid", "Vigo", "Gijon",
        "Hospitalet de Llobregat", "A Coruna", "Vitoria-Gasteiz", "Granada",
        "Elche", "Oviedo", "Santa Cruz de Tenerife", "Badalona", "Cartagena",
        "Terrassa"
    ],

    "Sweden": [
        "Stockholm", "Gothenburg", "Malmo", "Uppsala", "Vasteras",
        "Orebro", "Linkoping", "Helsingborg", "Jonkoping", "Norrkoping",
        "Lund", "Umea", "Gavle", "Boras", "Sodertalje",
        "Eskilstuna", "Halmstad", "Vaxjo", "Karlstad", "Sundsvall",
        "Ostersund", "Trollhattan", "Lulea", "Borlange", "Falun"
    ],

    "Switzerland": [
        "Zurich", "Geneva", "Basel", "Lausanne", "Bern",
        "Winterthur", "Lucerne", "St. Gallen", "Lugano", "Biel",
        "Thun", "Köniz", "La Chaux-de-Fonds", "Fribourg", "Schaffhausen",
        "Chur", "Neuchatel", "Vernier", "Uster", "Sion",
        "Emmen", "Yverdon-les-Bains", "Zug", "Kriens", "Rapperswil"
    ],

    "Ukraine": [
        "Kyiv", "Kharkiv", "Odesa", "Dnipro", "Donetsk",
        "Lviv", "Zaporizhzhia", "Kryvyi Rih", "Mykolaiv", "Mariupol",
        "Vinnytsia", "Poltava", "Chernihiv", "Cherkasy", "Sumy",
        "Zhytomyr", "Khmelnytskyi", "Chernivtsi", "Rivne", "Ivano-Frankivsk",
        "Ternopil", "Lutsk", "Uzhhorod", "Kremenchuk", "Bila Tserkva"
    ],

    "United Kingdom": [
        "London", "Birmingham", "Manchester", "Glasgow", "Liverpool",
        "Leeds", "Edinburgh", "Sheffield", "Bristol", "Cardiff",
        "Leicester", "Coventry", "Bradford", "Belfast", "Nottingham",
        "Kingston upon Hull", "Newcastle upon Tyne", "Stoke-on-Trent",
        "Southampton", "Plymouth", "Derby", "Swansea", "Aberdeen",
        "Northampton", "Reading"
    ],

    "Kosovo": [
        "Pristina", "Prizren", "Peja", "Ferizaj", "Gjakova",
        "Gjilan", "Mitrovica", "Vushtrri", "Podujeva", "Suhareka",
        "Rahovec", "Lipjan", "Drenas", "Kamenica", "Skenderaj",
        "Viti", "Istog", "Deçan", "Malisheva", "Klinë",
        "Dragash", "Kaçanik", "Fushë Kosovë", "Obiliq", "Shtime"
    ],

    "Vatican City": [
        "Vatican City", "Vatican Gardens", "St. Peter's Square",
        "Borgo", "Prati", "Aurelio", "Trionfale", "Della Vittoria",
        "Flaminio", "Parioli", "Monte Mario", "Balduina",
        "Primavalle", "Ottavia", "Pineta Sacchetti", "Valle Aurelia",
        "Cipro", "Ottaviano", "Lepanto", "Musei Vaticani",
        "San Pietro", "Via della Conciliazione", "Gregorio VII",
        "Clivio di Scauro", "Porta Angelica"
    ]

}

EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}'
PHONE_REGEX = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,5}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,5}'
ALLOWED_WEBMAILS = ("gmail.com", "yahoo.com", "outlook.com", "hotmail.com")

def load_vault():
    if os.path.exists(HISTORY_FILE):
        try:
            df = pd.read_csv(HISTORY_FILE)
            if "Email" in df.columns: return set(df["Email"].astype(str).str.lower().str.strip())
        except Exception: pass
    return set()

vault_emails = load_vault()

def save_to_vault(records):
    if not records: return
    df_new = pd.DataFrame(records)
    df_new.to_csv(HISTORY_FILE, mode='a' if os.path.exists(HISTORY_FILE) else 'w', 
                  header=not os.path.exists(HISTORY_FILE), index=False, encoding='utf-8-sig')

def fetch_native_search(query):
    results = []
    try:
        with DDGS() as ddg:
            for r in ddg.text(query, max_results=20): results.append(r)
    except Exception: pass
    return results

def send_brevo_email(api_key, sender_name, sender_email, recipient_email, business_name, subject_tmpl, body_tmpl):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {"accept": "application/json", "api-key": api_key, "content-type": "application/json"}
    
    biz_display = business_name if business_name and business_name != "N/A" else "Valued Partner"
    subject = subject_tmpl.replace("{business}", biz_display)
    body_html = body_tmpl.replace("{business}", biz_display).replace('\n', '<br>')
    
    payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": recipient_email, "name": biz_display}],
        "subject": subject,
        "htmlContent": f"<html><body>{body_html}</body></html>"
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code in [200, 201, 202]: return True, "Success"
        else: return False, resp.text
    except Exception as e: return False, str(e)

if "engine_leads" not in st.session_state: st.session_state.engine_leads = []

# ================= TOP BRANDING HEADER =================
st.markdown("""
<div style="text-align: center; margin-bottom: 40px; margin-top: 10px;">
    <h1 style="font-size: 3.5rem; font-weight: 900; margin-bottom: 0; background: -webkit-linear-gradient(#38bdf8, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px;">🚀 EmailScraper Pro</h1>
    <p style="color: #10b981; font-weight: bold; letter-spacing: 2px; font-size: 14px; margin-top: 5px;">● SYSTEM ONLINE | ANTI-SPAM PROTECTED | NATIVE ENGINE</p>
</div>
""", unsafe_allow_html=True)

# ================= UI SPLIT LAYOUT =================
col_email, col_scraper = st.columns([1, 1], gap="large")

# ----------------- LEFT SIDE: BREVO EMAIL OUTREACH -----------------
with col_email:
    st.markdown('<div class="card-header">📩 Direct Inbox Campaigns</div>', unsafe_allow_html=True)
    st.caption("Auto-trigger personalized emails directly to the inbox via Brevo Marketing Servers.")
    
    with st.expander("🔑 Brevo API Configuration (Protected)", expanded=True):
        brevo_key = st.text_input("Brevo API Key (v3):", type="password", placeholder="xkeysib-...")
        c1, c2 = st.columns(2)
        with c1: sender_name = st.text_input("Sender Name:", placeholder="John Doe")
        with c2: sender_email = st.text_input("Sender Email:", placeholder="john@example.com")
        
        test_api_btn = st.button("🔌 Test API Connection", use_container_width=True)
        test_log = st.empty()
        
        if test_api_btn:
            if not brevo_key or not sender_email:
                test_log.error("⚠️ Please enter API Key and Sender Email first.")
            else:
                test_log.info("Testing connection to Brevo Servers...")
                is_sent, error_msg = send_brevo_email(brevo_key, sender_name, sender_email, sender_email, "Test Business", "System Test: API is Working", "Hello! If you are reading this, your API Key and Email Configuration is 100% correct.")
                if is_sent: test_log.success("✅ API Connected! Test Email successfully sent to your inbox.")
                else: test_log.error(f"❌ Connection Failed. Brevo says:\n{error_msg}")

    st.markdown("### 📝 Smart Template Builder")
    st.info("💡 Tag `{business}` will auto-replace with the lead's exact business name.")
    
    subject_tmpl = st.text_input("Email Subject:", value="Quick question for {business}")
    body_tmpl = st.text_area("Email Body:", value="Hello {business},\n\nI was looking at businesses in your area and noticed your profile. We help businesses like {business} increase their local footprint.\n\nLet's connect!\nBest,\n[Your Name]", height=180)
    
    send_trigger = st.button("📤 Trigger Auto-Emails to Extracted Batch", type="secondary")
    campaign_log = st.empty()
    
    if send_trigger:
        if not brevo_key or not sender_email:
            campaign_log.error("⚠️ Please configure Brevo API Key and Sender Email first.")
        elif not st.session_state.engine_leads:
            campaign_log.warning("⚠️ No leads available. Please run the Scraper first.")
        else:
            campaign_log.info("Initiating Anti-Spam Inbox Sequence...")
            success_count = 0
            
            progress_text = st.empty()
            email_bar = st.progress(0)
            
            total_leads = len(st.session_state.engine_leads)
            for idx, lead in enumerate(st.session_state.engine_leads):
                progress_text.text(f"Sending to {lead['Email']} ({lead['Business Name']})...")
                
                is_sent, error_msg = send_brevo_email(brevo_key, sender_name, sender_email, lead['Email'], lead['Business Name'], subject_tmpl, body_tmpl)
                
                if is_sent: success_count += 1
                else:
                    campaign_log.error(f"⚠️ Failed to send to {lead['Email']}. Reason: {error_msg}")
                    break 
                    
                email_bar.progress((idx + 1) / total_leads)
                time.sleep(2)
                
            progress_text.empty()
            if success_count > 0:
                campaign_log.success(f"✅ Campaign Complete! Successfully delivered {success_count}/{total_leads} emails directly to Inbox.")

# ----------------- RIGHT SIDE: SCRAPER ENGINE -----------------
with col_scraper:
    st.markdown('<div class="card-header">⚡ Lead Extraction Engine</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([2, 1.5, 1])
    with c1: niches_input = st.text_input("🎯 Target Niches:", value="Gym, Cafe, Plumber")
    
    with c2: 
        country_options = ["🌍 All Over The World"] + sorted(list(GLOBAL_ATLAS.keys()))
        selected_country = st.selectbox("📍 Select Country:", country_options)
        
    with c3: daily_quota = st.number_input("⚙️ Leads:", min_value=1, max_value=10000, value=30)
    
    start_engine = st.button("🚀 Ignite Scraping Engine", type="primary")
    
    status_console = st.empty()
    progress = st.progress(0)
    data_grid = st.empty()
    dl_btn_spot = st.empty()
    
    if st.session_state.engine_leads:
        df_current = pd.DataFrame(st.session_state.engine_leads)
        data_grid.dataframe(df_current, use_container_width=True, height=265, column_config={"Source": st.column_config.LinkColumn("Profile Source"), "Google Proof": st.column_config.LinkColumn("Google Proof")})
        dl_btn_spot.download_button(f"📥 Save Extracted Leads ({len(df_current)})", df_current.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'), "Scraped_Leads.csv", "text/csv")

    if start_engine:
        st.session_state.engine_leads = []
        target_niches = [n.strip() for n in niches_input.split(",") if n.strip()]
        num_niches = len(target_niches)
        
        if selected_country == "🌍 All Over The World":
            target_cities = [city for cities in GLOBAL_ATLAS.values() for city in cities]
        else:
            target_cities = GLOBAL_ATLAS[selected_country]
            
        base_quota = daily_quota // num_niches
        remainder = daily_quota % num_niches
        
        niche_quotas = {n: base_quota + (1 if i < remainder else 0) for i, n in enumerate(target_niches)}
        niche_acquired = {n: 0 for n in target_niches}
            
        search_permutations = itertools.cycle(itertools.product(target_cities, ["facebook", "instagram"], ["gmail com", "yahoo com"], target_niches))
        
        status_console.markdown(f'<div class="terminal-box">> [SYSTEM] Initiating Balanced Sweep in <b>{selected_country}</b>...<br>> [SYSTEM] Targeting ~{base_quota} leads per niche.</div>', unsafe_allow_html=True)
        
        while len(st.session_state.engine_leads) < daily_quota:
            city, plat, prov, niche = next(search_permutations)
            
            if niche_acquired[niche] >= niche_quotas[niche]: continue
                
            status_console.markdown(f'<div class="terminal-box">> SCANNING: <b>[{niche}]</b> in <b>[{city}]</b><br>> SECURED: <span style="color:#fcd34d;">{len(st.session_state.engine_leads)} / {daily_quota}</span> | ({niche}: {niche_acquired[niche]}/{niche_quotas[niche]})</div>', unsafe_allow_html=True)
            
            query = f'{niche} in {city} {plat} {prov}'
            results = fetch_native_search(query)
            
            for it in results:
                if niche_acquired[niche] >= niche_quotas[niche]: break
                    
                title, snippet, link = it.get("title", ""), it.get("body", ""), it.get("href", "")
                corpus = f"{title} {snippet}"
                
                if "facebook.com" not in link and "instagram.com" not in link: continue
                if re.search(r'website:\s*www|visit:\s*http', snippet, re.IGNORECASE): continue
                    
                emails = re.findall(EMAIL_REGEX, corpus)
                if not emails: continue
                
                primary_email = emails[0].strip().lower().rstrip('.')
                if not any(primary_email.endswith(p) for p in ALLOWED_WEBMAILS): continue
                
                if primary_email in vault_emails or any(x['Email'] == primary_email for x in st.session_state.engine_leads): continue
                    
                biz_name = html.unescape(title).split("|")[0].split("-")[0].strip()
                phones = re.findall(PHONE_REGEX, corpus)
                proof = f"https://www.google.com/search?q={urllib.parse.quote(f'\"{biz_name}\" \"{city}\" official website')}"
                
                st.session_state.engine_leads.append({
                    "Niche": niche, "Business Name": biz_name, 
                    "Country": selected_country if selected_country != "🌍 All Over The World" else "Global", "City": city,
                    "Email": primary_email, "Phone": phones[0].strip() if phones else "N/A", 
                    "Source": link, "Google Proof": proof
                })
                
                niche_acquired[niche] += 1 
                
                df_current = pd.DataFrame(st.session_state.engine_leads)
                data_grid.dataframe(df_current, use_container_width=True, height=265, column_config={"Source": st.column_config.LinkColumn("Profile Source"), "Google Proof": st.column_config.LinkColumn("Google Proof Link")})
                progress.progress(min(len(st.session_state.engine_leads) / daily_quota, 1.0))
                
                if len(st.session_state.engine_leads) >= daily_quota: break
            time.sleep(1.5)

        if len(st.session_state.engine_leads) >= daily_quota:
            save_to_vault(st.session_state.engine_leads)
            vault_emails.update([lead['Email'] for lead in st.session_state.engine_leads])
            status_console.success(f"🎯 Exact Quota Reached & Balanced Across Niches in {selected_country}!")
            st.rerun()

# ================= BOTTOM FOOTER =================
st.markdown("""
<div style="text-align: center; margin-top: 60px; padding: 25px; border-top: 1px solid #1e293b;">
    <p style="color: #64748b; font-size: 14px; letter-spacing: 3px; font-weight: 600;">POWERED BY <span style="color: #38bdf8; font-weight: 900; font-size: 16px;">SOLO TECH</span></p>
</div>
""", unsafe_allow_html=True)