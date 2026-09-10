import html
import os
import re
import time
import urllib.parse
import itertools
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

HISTORY_FILE = "ultimate_leads_vault.csv"

# 🔥 COMPACT & SCALABLE GLOBAL ATLAS
GLOBAL_ATLAS = {
    "United States": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "Austin", "Jacksonville", "San Jose", "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis", "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville", "Detroit", "Oklahoma City", "Portland", "Las Vegas", "Memphis", "Louisville", "Baltimore", "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Mesa", "Sacramento", "Atlanta", "Kansas City", "Colorado Springs", "Miami", "Raleigh", "Omaha", "Long Beach", "Virginia Beach", "Oakland", "Minneapolis", "Tulsa", "Tampa", "Arlington", "New Orleans"],
    "United Kingdom": ["London", "Birmingham", "Manchester", "Glasgow", "Liverpool", "Bristol", "Sheffield", "Leeds", "Edinburgh", "Leicester", "Coventry", "Bradford", "Cardiff", "Belfast", "Nottingham", "Hull", "Newcastle", "Stoke-on-Trent", "Southampton", "Derby", "Portsmouth", "Brighton", "Plymouth", "Northampton", "Reading", "Luton", "Wolverhampton", "Bolton", "Aberdeen", "Bournemouth", "Norwich", "Swindon", "Swansea", "Milton Keynes", "Southend", "Middlesbrough", "Sunderland", "Warrington", "Slough", "Huddersfield", "Oxford", "York", "Poole", "Ipswich", "Telford", "Cambridge", "Dundee", "Gloucester", "Blackpool", "Birkenhead"],
    "Canada": ["Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton", "Ottawa", "Winnipeg", "Quebec City", "Hamilton", "Kitchener", "London", "Victoria", "Halifax", "Oshawa", "Windsor", "Saskatoon", "St. Catharines", "Regina", "St. John's", "Kelowna", "Barrie", "Sherbrooke", "Guelph", "Abbotsford", "Kingston", "Kanata", "Trois-Rivières", "Moncton", "Chicoutimi", "Milton", "Red Deer", "Lethbridge", "Nanaimo", "Kamloops", "Belleville", "Chatham", "Fredericton", "Chilliwack", "Sarnia", "Drummondville", "Prince George", "Sault Ste. Marie", "Medicine Hat", "Grande Prairie", "Airdrie", "Halton Hills", "Saint John", "Beloeil", "Granby", "Charlottetown"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Gold Coast", "Newcastle", "Canberra", "Sunshine Coast", "Wollongong", "Hobart", "Geelong", "Townsville", "Cairns", "Darwin", "Toowoomba", "Ballarat", "Bendigo", "Albury", "Launceston", "Mackay", "Rockhampton", "Bunbury", "Coffs Harbour", "Bundaberg", "Wagga Wagga", "Hervey Bay", "Mildura", "Warrnambool", "Gladstone", "Port Macquarie", "Tamworth", "Traralgon", "Orange", "Bowral", "Busselton", "Dubbo", "Nowra", "Bathurst", "Geraldton", "Warragul", "Kalgoorlie", "Albany", "Mount Gambier", "Devonport", "Alice Springs", "Maryborough", "Victor Harbor", "Ballina", "Taree"],
    "Pakistan": ["Karachi", "Lahore", "Faisalabad", "Rawalpindi", "Gujranwala", "Peshawar", "Multan", "Hyderabad", "Islamabad", "Quetta", "Bahawalpur", "Sargodha", "Sialkot", "Sukkur", "Larkana", "Chiniot", "Sheikhupura", "Jhang", "Dera Ghazi Khan", "Gujrat", "Rahim Yar Khan", "Kasur", "Mardan", "Mingora", "Nawabshah", "Sahiwal", "Mirpur Khas", "Okara", "Mandi Bahauddin", "Jacobabad", "Jhelum", "Shikarpur", "Khuzdar", "Dadu", "Hafizabad", "Kohat", "Vehari", "Khanewal", "Gojra", "Bahawalnagar", "Muridke", "Pakpattan", "Abbottabad", "Tando Adam", "Jaranwala", "Chishtian", "Daska", "Kamoke", "Turbat", "Muzaffarabad"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Surat", "Pune", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Kalyan-Dombivli", "Vasai-Virar", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar", "Navi Mumbai", "Allahabad", "Howrah", "Ranchi", "Gwalior", "Jabalpur", "Coimbatore", "Vijayawada", "Jodhpur", "Madurai", "Raipur", "Chandigarh", "Guwahati", "Solapur", "Hubli", "Mysore"],
    "Germany": ["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Stuttgart", "Düsseldorf", "Leipzig", "Dortmund", "Essen", "Bremen", "Dresden", "Hanover", "Nuremberg", "Duisburg", "Bochum", "Wuppertal", "Bielefeld", "Bonn", "Münster", "Karlsruhe", "Mannheim", "Augsburg", "Wiesbaden", "Gelsenkirchen", "Mönchengladbach", "Braunschweig", "Chemnitz", "Kiel", "Aachen", "Halle", "Magdeburg", "Freiburg", "Krefeld", "Lübeck", "Oberhausen", "Erfurt", "Mainz", "Rostock", "Kassel", "Hagen", "Hamm", "Saarbrücken", "Mülheim", "Potsdam", "Ludwigshafen", "Oldenburg", "Leverkusen", "Osnabrück", "Solingen"],
    "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille", "Rennes", "Reims", "Le Havre", "Saint-Étienne", "Toulon", "Grenoble", "Dijon", "Nîmes", "Angers", "Villeurbanne", "Le Mans", "Saint-Denis", "Aix-en-Provence", "Clermont-Ferrand", "Brest", "Limoges", "Tours", "Amiens", "Perpignan", "Metz", "Besançon", "Boulogne-Billancourt", "Orléans", "Mulhouse", "Rouen", "Caen", "Argenteuil", "Saint-Paul", "Montreuil", "Nancy", "Nouméa", "Roubaix", "Tourcoing", "Nanterre", "Avignon", "Vitry-sur-Seine", "Créteil", "Dunkerque", "Poitiers", "Versailles"],
    "Italy": ["Rome", "Milan", "Naples", "Turin", "Palermo", "Genoa", "Bologna", "Florence", "Bari", "Catania", "Venice", "Verona", "Messina", "Padua", "Trieste", "Taranto", "Brescia", "Parma", "Prato", "Modena", "Reggio Calabria", "Reggio Emilia", "Perugia", "Ravenna", "Livorno", "Cagliari", "Foggia", "Rimini", "Salerno", "Ferrara", "Sassari", "Latina", "Giugliano in Campania", "Monza", "Siracusa", "Pescara", "Bergamo", "Forlì", "Trento", "Vicenza", "Terni", "Bolzano", "Novara", "Piacenza", "Ancona", "Andria", "Arezzo", "Udine", "Cesena", "Lecce"],
    "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza", "Málaga", "Murcia", "Palma", "Las Palmas", "Bilbao", "Alicante", "Córdoba", "Valladolid", "Vigo", "Gijón", "L'Hospitalet", "Vitoria", "A Coruña", "Granada", "Elche", "Oviedo", "Terrassa", "Badalona", "Cartagena", "Jerez", "Sabadell", "Móstoles", "Tenerife", "Pamplona", "Almería", "Alcalá", "Fuenlabrada", "Leganés", "San Sebastián", "Getafe", "Burgos", "Santander", "Albacete", "Castellón", "Alcorcón", "La Laguna", "Logroño", "Badajoz", "Salamanca", "Huelva", "Lleida", "Marbella", "Tarragona", "Dos Hermanas", "León"],
    "Brazil": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza", "Belo Horizonte", "Manaus", "Curitiba", "Recife", "Goiânia", "Belém", "Porto Alegre", "Guarulhos", "Campinas", "São Luís", "São Gonçalo", "Maceió", "Duque de Caxias", "Campo Grande", "Natal", "Teresina", "São Bernardo do Campo", "Nova Iguaçu", "João Pessoa", "São José dos Campos", "Santo André", "Ribeirão Preto", "Jaboatão dos Guararapes", "Osasco", "Uberlândia", "Sorocaba", "Contagem", "Aracaju", "Feira de Santana", "Cuiabá", "Joinville", "Aparecida de Goiânia", "Londrina", "Juiz de Fora", "Ananindeua", "Porto Velho", "Niterói", "Belford Roxo", "Serra", "Caxias do Sul", "Macapá", "Florianópolis", "Vila Velha", "Mauá", "São João de Meriti"],
    "Mexico": ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Toluca", "Tijuana", "León", "Ciudad Juárez", "Torreón", "Querétaro", "San Luis Potosí", "Mérida", "Aguascalientes", "Cuernavaca", "Acapulco", "Tampico", "Chihuahua", "Saltillo", "Morelia", "Veracruz", "Villahermosa", "Reynosa", "Tuxtla Gutiérrez", "Cancún", "Xalapa", "Oaxaca", "Celaya", "Hermosillo", "Mexicali", "Culiacán", "Pachuca", "Ensenada", "Mazatlán", "Irapuato", "Nuevo Laredo", "Matamoros", "Ciudad Obregón", "Gómez Palacio", "Uruapan", "Tehuacán", "Coatzacoalcos", "Los Mochis", "Ciudad Victoria", "Zacatecas", "Colima", "Tepic", "Chilpancingo", "Poza Rica", "Córdoba", "Minatitlán"],
    "South Africa": ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", "Bloemfontein", "East London", "Polokwane", "Nelspruit", "Kimberley", "Pietermaritzburg", "Rustenburg", "George", "Mossel Bay", "Stellenbosch", "Paarl", "Potchefstroom", "Welkom", "Upington", "Worcester", "Mahikeng", "Soweto", "Springs", "Benoni", "Boksburg", "Vereeniging", "Krugersdorp", "Brakpan", "Vanderbijlpark", "Sasolburg", "Ermelo", "Kroonstad", "Bethlehem", "Middelburg", "Witbank", "Tzaneen", "Phalaborwa", "Mokopane", "Thohoyandou", "Makhanda", "Uitenhage", "Oudtshoorn", "Graaff-Reinet", "Knysna", "Plettenberg Bay", "Hermanus", "Saldanha", "Vredenburg", "Malmesbury", "Beaufort West"],
    "Japan": ["Tokyo", "Yokohama", "Osaka", "Nagoya", "Sapporo", "Fukuoka", "Kobe", "Kyoto", "Kawasaki", "Saitama", "Hiroshima", "Sendai", "Chiba", "Kitakyushu", "Sakai", "Niigata", "Hamamatsu", "Kumamoto", "Sagamihara", "Shizuoka", "Okayama", "Funabashi", "Hachioji", "Kagoshima", "Kawaguchi", "Himeji", "Matsuyama", "Utsunomiya", "Matsudo", "Nishinomiya", "Kurashiki", "Ichikawa", "Oita", "Amagasaki", "Kanazawa", "Nagasaki", "Yokosuka", "Toyama", "Toyota", "Takamatsu", "Gifu", "Hirakata", "Fujisawa", "Kashiwa", "Toyonaka", "Nagano", "Toyohashi", "Ichinomiya", "Okazaki", "Miyazaki"],
    "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah", "Al Ain", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain", "Khor Fakkan", "Kalba", "Dibba Al-Fujairah", "Dibba Al-Hisn", "Hatta", "Zayed City", "Ruwais", "Liwa Oasis", "Al Dhaid", "Ghantoot", "Masdar City", "Al Madam", "Ar-Rams", "Dhaid", "Ghiyathi", "Ruwais", "Bida Zayed", "Sila", "Muzairah", "Madinat Zayed", "Al Jazirah Al Hamra", "Al Heera", "Al Qasimi", "Al Khalidiyah", "Al Markaziyah", "Al Karamah", "Al Zahiyah", "Al Maryah", "Al Reem", "Al Bateen", "Al Mushrif", "Al Muroor", "Al Nahyan", "Al Rowdah", "Al Maqtaa", "Al Bahia", "Al Shahama", "Al Rahba", "Al Samha", "Al Mafraq", "Al Shawamekh", "Al Wathba"],
    "Saudi Arabia": ["Riyadh", "Jeddah", "Mecca", "Medina", "Dammam", "Taif", "Tabuk", "Buraydah", "Khamis Mushait", "Abha", "Al Mubarraz", "Hail", "Najran", "Jubail", "Al Kharj", "Qatif", "Yanbu", "Al Qunfudhah", "Hafar Al-Batin", "Bisha", "Al Zulfi", "Dhahran", "Al Khobar", "Jizan", "Arar", "Sakaka", "Baha", "Al Qurayyat", "Tarout", "Al Khafji", "Unaizah", "Al Duwadimi", "Rafha", "Turaif", "Sabya", "Abu Arish", "Samtah", "Al Wajh", "Al Namas", "Badr", "Dawadmi", "Majmaah", "Rabigh", "Turabah", "Thadiq", "Diriyah", "Dhurma", "Huraymila", "Al Ula", "Khaibar"],
    "Egypt": ["Cairo", "Alexandria", "Giza", "Shubra El-Kheima", "Port Said", "Suez", "Mansoura", "El Mahalla El Kubra", "Tanta", "Asyut", "Ismailia", "Fayoum", "Zagazig", "Damietta", "Aswan", "Minya", "Damanhur", "Beni Suef", "Hurghada", "Qena", "Sohag", "Shibin El Kom", "Banha", "Kafr El Sheikh", "Arish", "Mallawi", "10th of Ramadan", "Bilbais", "Marsa Matruh", "Idfu", "Mit Ghamr", "Al Hawamdeya", "Desouk", "Qalyub", "Abu Kabir", "Kafr El Dawwar", "Girga", "Akhmim", "Matareya", "Qus", "Bishbish", "Giza", "Helwan", "Badr", "Obour", "Shorouk", "New Cairo", "6th of October", "Sadat", "Borg El Arab"],
    "Nigeria": ["Lagos", "Kano", "Ibadan", "Kaduna", "Port Harcourt", "Benin City", "Maiduguri", "Zaria", "Aba", "Jos", "Ilorin", "Oyo", "Enugu", "Abeokuta", "Abuja", "Sokoto", "Onitsha", "Warri", "Ebute Ikorodu", "Okene", "Calabar", "Katsina", "Akure", "Ogbomosho", "Ife", "Bauchi", "Minna", "Effon Alaiye", "Ilesa", "Owo", "Umuahia", "Ondo", "Ikot Ekpene", "Iwo", "Gombe", "Jimeta", "Gusau", "Mubi", "Shagamu", "Owerri", "Ugep", "Ijebu Ode", "Ise", "Gboko", "Ila Orangun", "Sapele", "Ijero", "Ikirun", "Awka", "Lokoja"],
    "Turkey": ["Istanbul", "Ankara", "Izmir", "Bursa", "Adana", "Gaziantep", "Konya", "Antalya", "Kayseri", "Mersin", "Eskisehir", "Diyarbakir", "Samsun", "Denizli", "Sanliurfa", "Adapazari", "Malatya", "Kahramanmaras", "Erzurum", "Van", "Batman", "Elazig", "Izmit", "Manisa", "Sivas", "Gebze", "Balikesir", "Tarsus", "Kutahya", "Trabzon", "Corum", "Corlu", "Adiyaman", "Osmaniye", "Kirikkale", "Antakya", "Aydin", "Iskenderun", "Usak", "Aksaray", "Afyon", "Isparta", "Inegol", "Tekirdag", "Edirne", "Darica", "Ordu", "Karaman", "Golcuk", "Siirt"],
    "Russia": ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Nizhny Novgorod", "Kazan", "Chelyabinsk", "Omsk", "Samara", "Rostov-on-Don", "Ufa", "Krasnoyarsk", "Perm", "Voronezh", "Volgograd", "Krasnodar", "Saratov", "Tyumen", "Tolyatti", "Izhevsk", "Barnaul", "Ulyanovsk", "Irkutsk", "Khabarovsk", "Yaroslavl", "Vladivostok", "Makhachkala", "Tomsk", "Orenburg", "Kemerovo", "Novokuznetsk", "Ryazan", "Astrakhan", "Naberezhnye Chelny", "Penza", "Lipetsk", "Kirov", "Tula", "Cheboksary", "Kaliningrad", "Kursk", "Ulan-Ude", "Stavropol", "Magnitogorsk", "Tver", "Ivanovo", "Bryansk", "Sochi", "Belgorod", "Nizhny Tagil"],
    "China": ["Shanghai", "Beijing", "Guangzhou", "Shenzhen", "Chengdu", "Chongqing", "Dongguan", "Wuhan", "Hangzhou", "Xi'an", "Tianjin", "Suzhou", "Nanjing", "Shenyang", "Harbin", "Qingdao", "Dalian", "Jinan", "Zhengzhou", "Changsha", "Kunming", "Changchun", "Urumqi", "Shantou", "Hefei", "Shijiazhuang", "Ningbo", "Taiyuan", "Nanning", "Zhongshan", "Xiamen", "Fuzhou", "Changzhou", "Nanchang", "Guiyang", "Tangshan", "Wuxi", "Qiqihar", "Lanzhou", "Luoyang", "Zibo", "Hohhot", "Baotou", "Handan", "Yantai", "Jilin", "Datong", "Xuzhou", "Fushun", "Anshan"],
    "Argentina": ["Buenos Aires", "Córdoba", "Rosario", "Mendoza", "Tucumán", "La Plata", "Mar del Plata", "Salta", "Santa Fe", "San Juan", "Resistencia", "Santiago del Estero", "Corrientes", "Neuquén", "Posadas", "San Salvador de Jujuy", "Bahía Blanca", "Paraná", "Formosa", "San Fernando del Valle de Catamarca", "San Luis", "La Rioja", "Comodoro Rivadavia", "Río Cuarto", "Concordia", "San Nicolás", "Trelew", "San Rafael", "Santa Rosa", "Tandil", "Villa Mercedes", "Bariloche", "Zárate", "Río Gallegos", "Pergamino", "Olavarría", "Goya", "Reconquista", "Ushuaia", "Campana", "Junín", "Presidencia Roque Sáenz Peña", "Gualeguaychú", "San Martín", "Chivilcoy", "Puerto Madryn", "Mercedes", "San Francisco", "Gualeguay", "Azul"],
    "Indonesia": ["Jakarta", "Surabaya", "Bandung", "Medan", "Semarang", "Makassar", "Palembang", "Tangerang", "Depok", "Batam", "Padang", "Denpasar", "Bandar Lampung", "Bogor", "Malang", "Pekanbaru", "Banjarmasin", "Yogyakarta", "Surakarta", "Balikpapan", "Jambi", "Pontianak", "Manado", "Mataram", "Cimahi", "Kupang", "Jayapura", "Ambon", "Bengkulu", "Palu", "Kendari", "Sukabumi", "Cirebon", "Pekalongan", "Kediri", "Tegal", "Binjai", "Purwokerto", "Dumai", "Madiun", "Salatiga", "Probolinggo", "Lubuklinggau", "Banjarbaru", "Tarakan", "Magelang", "Batu", "Ternate", "Bitung", "Gorontalo"],
    "Philippines": ["Manila", "Quezon City", "Davao City", "Caloocan", "Cebu City", "Zamboanga City", "Taguig", "Antipolo", "Pasig", "Cagayan de Oro", "Parañaque", "Valenzuela", "Bacoor", "General Santos", "Makati", "Las Piñas", "Bacolod", "Muntinlupa", "San Jose del Monte", "Iloilo City", "Marikina", "Pasay", "Dasmariñas", "Angeles", "Lapu-Lapu", "Imus", "Mandaluyong", "Malabon", "Mandaue", "Santa Rosa", "Baguio", "Iligan", "Tarlac City", "Butuan", "Batangas City", "Cabuyao", "San Pedro", "Biñan", "Cabanatuan", "Cotabato City", "Lucena", "San Pablo", "Tagum", "Navotas", "Olongapo", "Tacloban", "Ormoc", "Lipa", "Dagupan", "Meycauayan"],
    "Vietnam": ["Ho Chi Minh City", "Hanoi", "Da Nang", "Hai Phong", "Bien Hoa", "Hue", "Nha Trang", "Can Tho", "Rach Gia", "Qui Nhon", "Vung Tau", "Da Lat", "Nam Dinh", "Vinh", "Phan Thiet", "Long Xuyen", "Hong Gai", "Cam Ranh", "Cam Pha", "Thai Nguyen", "Thanh Hoa", "Pleiku", "Bac Lieu", "Ca Mau", "Yen Bai", "Song Cau", "Tuy Hoa", "Phan Rang-Thap Cham", "Ha Tinh", "Dong Hoi", "Tra Vinh", "Sa Dec", "Tam Ky", "Soc Trang", "Bao Loc", "Kon Tum", "Vinh Long", "Hoa Binh", "Ben Tre", "Tuyen Quang", "Hai Duong", "Bac Giang", "Thai Binh", "Phu Ly", "Lang Son", "Son La", "Cao Bang", "Lao Cai", "Dien Bien Phu", "Ha Giang"],
    "Thailand": ["Bangkok", "Nonthaburi", "Nakhon Ratchasima", "Chiang Mai", "Hat Yai", "Udon Thani", "Pak Kret", "Khon Kaen", "Chaophraya Surasak", "Ubon Ratchathani", "Nakhon Si Thammarat", "Nakhon Sawan", "Nakhon Pathom", "Phitsanulok", "Pattaya", "Songkhla", "Surat Thani", "Rangsit", "Yala", "Phuket", "Samut Prakan", "Lampang", "Laem Chabang", "Chiang Rai", "Trang", "Ayutthaya", "Koh Samui", "Samut Sakhon", "Rayong", "Mae Sot", "Saraburi", "Phra Pradaeng", "Chonburi", "Mukdahan", "Chachoengsao", "Maha Sarakham", "Chumphon", "Ratchaburi", "Nong Khai", "Sakhon Nakhon", "Kanchanaburi", "Phetchaburi", "Hua Hin", "Trat", "Nakhon Phanom", "Kamphaeng Phet", "Prachinburi", "Phayao", "Krabi", "Phrae"],
    "Malaysia": ["Kuala Lumpur", "Seberang Perai", "Kajang", "Klang", "Subang Jaya", "Penang", "Ipoh", "Petaling Jaya", "Selayang", "Shah Alam", "Iskandar Puteri", "Seremban", "Johor Bahru", "Melaka", "Ampang Jaya", "Kota Kinabalu", "Sungai Petani", "Kuantan", "Alor Setar", "Tawau", "Sandakan", "Kuala Terengganu", "Kuching", "Kota Bharu", "Muar", "Kulim", "Batu Pahat", "Sepang", "Kulai", "Kluang", "Taiping", "Miri", "Sibu", "Temerloh", "Bintulu", "Teluk Intan", "Kangar", "Pasir Gudang", "Lahad Datu", "Segamat", "Ulu Tiram", "Kemaman", "Port Dickson", "Gombak", "Puchong", "Kinabatangan", "Putrajaya", "Cyberjaya", "Labuan", "Bentong"],
    "Colombia": ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", "Cúcuta", "Bucaramanga", "Pereira", "Santa Marta", "Ibagué", "Bello", "Pasto", "Manizales", "Neiva", "Soledad", "Villavicencio", "Armenia", "Soacha", "Valledupar", "Montería", "Sincelejo", "Popayán", "Floridablanca", "Palmira", "Buenaventura", "Tuluá", "Dosquebradas", "Itagüí", "Tunja", "Riohacha", "Envigado", "Girardot", "Florencia", "Cartago", "Quibdó", "Barrancabermeja", "Maicao", "Malambo", "Magangué", "Sogamoso", "Apartadó", "Piedecuesta", "Girón", "Yopal", "Ipiales", "Facatativá", "Fusagasugá", "San Andrés", "Pitalito", "Caucasia"],
    "Peru": ["Lima", "Arequipa", "Trujillo", "Chiclayo", "Piura", "Iquitos", "Cusco", "Chimbote", "Huancayo", "Tacna", "Pucallpa", "Juliaca", "Ica", "Sullana", "Huánuco", "Ayacucho", "Chincha Alta", "Cajamarca", "Tumbes", "Huaraz", "Puno", "Tarapoto", "Talara", "Pisco", "Moyobamba", "Tingo María", "Moquegua", "Abancay", "Jaén", "Yurimaguas", "Tarma", "Barranca", "Sicuani", "Chulucanas", "Huacho", "Ilo", "Chepén", "Cerro de Pasco", "Huaral", "Paita", "Huancavelica", "Catacaos", "Chachapoyas", "Sechura", "Pacasmayo", "Casma", "Ferreñafe", "Imperial", "Mala", "Chancay"],
    "Chile": ["Santiago", "Puente Alto", "Maipú", "La Florida", "Antofagasta", "Viña del Mar", "Valparaíso", "Talcahuano", "San Bernardo", "Temuco", "Iquique", "Concepción", "Rancagua", "La Pintana", "Talca", "Arica", "Coquimbo", "Puerto Montt", "La Serena", "Chillán", "Osorno", "Valdivia", "Quilpué", "Calama", "Copiapó", "Los Ángeles", "Punta Arenas", "Curicó", "Villa Alemana", "Coronel", "San Antonio", "Chiguayante", "Ovalle", "Linares", "Quillota", "Melipilla", "Los Andes", "San Felipe", "Talagante", "San Carlos", "Rengo", "Villarrica", "Puerto Varas", "Buin", "Lota", "Castro", "Coyhaique", "Limache", "Illapel", "Angol"],
    "Venezuela": ["Caracas", "Maracaibo", "Valencia", "Barquisimeto", "Maracay", "Ciudad Guayana", "Maturín", "Barcelona", "San Cristóbal", "Cumaná", "Ciudad Bolívar", "Mérida", "Barinas", "Los Teques", "Punto Fijo", "Coro", "Valera", "Cabimas", "Puerto la Cruz", "Guatire", "San Fernando de Apure", "Carúpano", "Acarigua", "Ocumare del Tuy", "El Tigre", "Cagua", "Guanare", "San Juan de los Morros", "La Victoria", "Carora", "Porlamar", "El Tocuyo", "Villa de Cura", "Araure", "Guacara", "Charallave", "El Limón", "San Felipe", "Anaco", "Machiques", "Cúa", "Palo Negro", "Ejido", "Bachaquero", "San Carlos", "Valle de la Pascua", "Upata", "Rubio", "Calabozo", "Zaraza"],
    "Poland": ["Warsaw", "Kraków", "Łódź", "Wrocław", "Poznań", "Gdańsk", "Szczecin", "Bydgoszcz", "Lublin", "Białystok", "Katowice", "Gdynia", "Częstochowa", "Radom", "Toruń", "Sosnowiec", "Kielce", "Rzeszów", "Gliwice", "Olsztyn", "Zabrze", "Bielsko-Biała", "Bytom", "Dąbrowa Górnicza", "Chorzów", "Elbląg", "Gorzów Wielkopolski", "Koszalin", "Ruda Śląska", "Kalisz", "Płock", "Zielona Góra", "Rybnik", "Tychy", "Wałbrzych", "Opole", "Tarnów", "Włocławek", "Legnica", "Jelenia Góra", "Grudziądz", "Słupsk", "Jaworzno", "Jastrzębie-Zdrój", "Nowy Sącz", "Lubin", "Konin", "Ostrów Wielkopolski", "Suwałki", "Gniezno"],
    "Netherlands": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven", "Tilburg", "Groningen", "Almere", "Breda", "Nijmegen", "Apeldoorn", "Enschede", "Haarlem", "Arnhem", "Zaanstad", "Amersfoort", "'s-Hertogenbosch", "Haarlemmermeer", "Zwolle", "Zoetermeer", "Leiden", "Maastricht", "Dordrecht", "Ede", "Alphen aan den Rijn", "Leeuwarden", "Alkmaar", "Emmen", "Westland", "Delft", "Venlo", "Deventer", "Sittard-Geleen", "Oss", "Gouda", "Amstelveen", "Hilversum", "Heerlen", "Purmerend", "Roosendaal", "Spijkenisse", "Schiedam", "Lelystad", "Leidschendam-Voorburg", "Almelo", "Hoorn", "Vlaardingen", "Assen", "Bergen op Zoom", "Veenendaal"],
    "Belgium": ["Antwerp", "Ghent", "Charleroi", "Liège", "Brussels", "Schaerbeek", "Bruges", "Anderlecht", "Namur", "Leuven", "Mons", "Molenbeek-Saint-Jean", "Ixelles", "Mechelen", "Aalst", "Uccle", "La Louvière", "Hasselt", "Kortrijk", "Sint-Niklaas", "Ostend", "Tournai", "Genk", "Roeselare", "Seraing", "Mouscron", "Woluwe-Saint-Lambert", "Forest", "Verviers", "Jette", "Sint-Lambrechts-Woluwe", "Evere", "Beveren", "Beringen", "Dendermonde", "Etterbeek", "Braine-l'Alleud", "Turnhout", "Vilvoorde", "Heist-op-den-Berg", "Dilbeek", "Sint-Truiden", "Grimbergen", "Lokeren", "Geel", "Brasschaat", "Halle", "Maasmechelen", "Ninove", "Waregem"],
    "Sweden": ["Stockholm", "Gothenburg", "Malmö", "Uppsala", "Västerås", "Örebro", "Linköping", "Helsingborg", "Jönköping", "Norrköping", "Lund", "Umeå", "Gävle", "Borås", "Eskilstuna", "Södertälje", "Karlstad", "Halmstad", "Växjö", "Täby", "Sundsvall", "Luleå", "Trollhättan", "Östersund", "Borlänge", "Lidingö", "Tumba", "Kalmar", "Skövde", "Kristianstad", "Falun", "Karlskrona", "Skellefteå", "Uddevalla", "Motala", "Landskrona", "Örnsköldsvik", "Nyköping", "Karlskoga", "Varberg", "Åkersberga", "Lidköping", "Alingsås", "Piteå", "Märsta", "Sandviken", "Kungälv", "Ängelholm", "Visby", "Enköping"],
    "Switzerland": ["Zurich", "Geneva", "Basel", "Lausanne", "Bern", "Winterthur", "Lucerne", "St. Gallen", "Lugano", "Biel/Bienne", "Thun", "Bellinzona", "Köniz", "Fribourg", "Schaffhausen", "La Chaux-de-Fonds", "Chur", "Vernier", "Neuchâtel", "Uster", "Sion", "Yverdon-les-Bains", "Lancy", "Dietikon", "Zug", "Kriens", "Meyrin", "Dübendorf", "Montreux", "Frauenfeld", "Baar", "Wetzikon", "Rapperswil-Jona", "Bülach", "Wil", "Kreuzlingen", "Nyon", "Aarau", "Kloten", "Carouge", "Renens", "Baden", "Riehen", "Vevey", "Bülach", "Wettswil", "Opfikon", "Morges", "Bülach", "Pratteln"],
    "Austria": ["Vienna", "Graz", "Linz", "Salzburg", "Innsbruck", "Klagenfurt", "Villach", "Wels", "Sankt Pölten", "Dornbirn", "Wiener Neustadt", "Steyr", "Feldkirch", "Bregenz", "Wolfsberg", "Baden bei Wien", "Leoben", "Klosterneuburg", "Krems an der Donau", "Traun", "Leonding", "Amstetten", "Kapfenberg", "Mödling", "Lustenau", "Hallein", "Kufstein", "Traiskirchen", "Schwechat", "Braunau am Inn", "Saalfelden", "Tulln", "Stockerau", "Spittal an der Drau", "Telfs", "Ansfelden", "Hohenems", "Ternitz", "Perchtoldsdorf", "Bludenz", "Feldkirchen", "Bad Ischl", "Schwaz", "Wörgl", "Hard", "Gmunden", "Wals-Siezenheim", "Marchtrenk", "Korneuburg", "Neunkirchen"],
    "Greece": ["Athens", "Thessaloniki", "Patras", "Heraklion", "Larissa", "Volos", "Ioannina", "Trikala", "Chalcis", "Serres", "Alexandroupoli", "Xanthi", "Katerini", "Agrinio", "Kalamata", "Kavala", "Chania", "Lamia", "Komotini", "Rhodes", "Drama", "Evosmos", "Veroia", "Acharnes", "Kozani", "Karditsa", "Nikaia", "Nea Ionia", "Chaidari", "Keratsini", "Peristeri", "Kallithea", "Piraeus", "Halepa", "Korydallos", "Ilioupoli", "Galatsi", "Glyfada", "Vyronas", "Zografou", "Agios Dimitrios", "Palaio Faliro", "Aigaleo", "Nea Smyrni", "Marousi", "Petroupoli", "Gerakas", "Voula", "Salamina", "Argos"],
    "Portugal": ["Lisbon", "Porto", "Amadora", "Braga", "Setúbal", "Coimbra", "Queluz", "Funchal", "Cacém", "Vila Nova de Gaia", "Algueirão", "Loures", "Rio de Tinto", "Odivelas", "Aveiro", "Amora", "Corroios", "Ermesinde", "Barreiro", "Évora", "Ponta Delgada", "Faro", "Guimarães", "Leiria", "Portimão", "Maia", "Matosinhos", "Viana do Castelo", "Covilhã", "Castelo Branco", "Sintra", "Almada", "Póvoa de Varzim", "Montijo", "Figueira da Foz", "Caldas da Rainha", "Santo Tirso", "Chaves", "Olhão", "Vila Real", "Gondomar", "Ovar", "Loulé", "Beja", "Bragança", "Tomar", "Elvas", "Portalegre", "Mirandela", "Angra do Heroísmo"],
    "Ireland": ["Dublin", "Cork", "Limerick", "Galway", "Waterford", "Drogheda", "Dundalk", "Swords", "Bray", "Navan", "Kilkenny", "Ennis", "Carlow", "Tralee", "Newbridge", "Portlaoise", "Balbriggan", "Naas", "Athlone", "Mullingar", "Celbridge", "Wexford", "Letterkenny", "Sligo", "Greystones", "Clonmel", "Malahide", "Carrigaline", "Leixlip", "Tullamore", "Killarney", "Maynooth", "Arklow", "Ashbourne", "Cobh", "Enniscorthy", "Castlebar", "Midleton", "Mallow", "Shannon", "Cavan", "Tramore", "Gorey", "Longford", "Athy", "Ballina", "Dungarvan", "Enniscorthy", "Roscommon", "Nenagh"],
    "New Zealand": ["Auckland", "Wellington", "Christchurch", "Hamilton", "Tauranga", "Napier-Hastings", "Dunedin", "Palmerston North", "Nelson", "Rotorua", "New Plymouth", "Whangarei", "Invercargill", "Whanganui", "Gisborne", "Blenheim", "Timaru", "Pukekohe", "Taupo", "Masterton", "Levin", "Ashburton", "Tokoroa", "Richmond", "Oamaru", "Gore", "Hawera", "Greymouth", "Waiuku", "Motueka", "Thames", "Huntly", "Morrinsville", "Matamata", "Stratford", "Kaitaia", "Dannevirke", "Alexandra", "Taumarunui", "Wairoa", "Marton", "Cromwell", "Balclutha", "Katikati", "Temuka", "Picton", "Te Kuiti", "Westport", "Pahiatua", "Opotiki"],
    "South Korea": ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon", "Gwangju", "Suwon", "Ulsan", "Changwon", "Seongnam", "Goyang", "Yongin", "Bucheon", "Cheongju", "Ansan", "Jeonju", "Cheonan", "Namyangju", "Hwaseong", "Anyang", "Pohang", "Gimhae", "Pyeongtaek", "Uijeongbu", "Gumi", "Jeju", "Siheung", "Paju", "Jinju", "Gwangmyeong", "Wonju", "Asan", "Gwangju (Gyeonggi)", "Iksan", "Yangsan", "Gunpo", "Chuncheon", "Gyeongsan", "Gunsan", "Mokpo", "Suncheon", "Gangneung", "Yeosu", "Gyeongju", "Hanam", "Uiwang", "Osan", "Icheon", "Gimpo", "Guri"],
    "Morocco": ["Casablanca", "Rabat", "Fes", "Marrakech", "Tangier", "Agadir", "Meknes", "Oujda", "Kenitra", "Tetouan", "Safi", "Mohammedia", "Khouribga", "Beni Mellal", "El Jadida", "Taza", "Nador", "Settat", "Ksar El Kebir", "Larache", "Khemisset", "Guelmim", "Berrechid", "Oued Zem", "Fkih Ben Salah", "Taourirt", "Berkane", "Sidi Slimane", "Sidi Kacem", "Khenifra", "Essaouira", "Tiznit", "Taroudant", "El Kelaa des Sraghna", "Youssoufia", "Ouezzane", "Chefchaouen", "Al Hoceima", "Ouarzazate", "Sefrou", "Tan-Tan", "Sidi Yahya El Gharb", "Tiflet", "Souk El Arbaa", "Azrou", "Tinghir", "Ben Guerir", "Midelt", "Martil", "Fnideq"],
    "Algeria": ["Algiers", "Oran", "Constantine", "Annaba", "Blida", "Batna", "Djelfa", "Sétif", "Sidi Bel Abbès", "Biskra", "Tébessa", "El Oued", "Skikda", "Tiaret", "Béjaïa", "Tlemcen", "Ouargla", "Béchar", "Mostaganem", "Bordj Bou Arréridj", "Chlef", "Souk Ahras", "Médéa", "El Eulma", "Touggourt", "Ghardaïa", "Saïda", "Laghouat", "M'Sila", "Jijel", "Relizane", "Guelma", "Aïn Beïda", "Khenchela", "Bousaada", "Mascara", "Tissemsilt", "Khouribga", "Barika", "Aïn Oussera", "El Khroub", "Aflou", "Aïn Defla", "Sig", "Akbou", "Bouïra", "Bir el Ater", "Tindouf", "El Bayadh", "Guelma"],
    "Tunisia": ["Tunis", "Sfax", "Sousse", "Kairouan", "Bizerte", "Gabès", "Aryanah", "Gafsa", "Monastir", "Ben Arous", "Kasserine", "Médenine", "Nabeul", "Tataouine", "Béja", "El Kef", "Mahdia", "Sidi Bouzid", "Jendouba", "Tozeur", "Manouba", "Siliana", "Zaghouan", "Kébili", "Douz", "Hammamet", "Zarzis", "Menzel Bourguiba", "Djerba", "Djemmal", "Ksar Hellal", "Moknine", "Téboulba", "Oued Ellil", "Radès", "Kelibia", "Dar Chaabane", "Mateur", "Ghardimaou", "Bou Salem", "Tajerouine", "Makthar", "Sbeïtla", "Thala", "Grombalia", "Soliman", "Korba", "Menzel Temime", "El Hamma", "Fériana"],
    "Saudi Arabia": ["Riyadh", "Jeddah", "Mecca", "Medina", "Dammam", "Taif", "Tabuk", "Buraydah", "Khamis Mushait", "Abha", "Al Mubarraz", "Hail", "Najran", "Jubail", "Al Kharj", "Qatif", "Yanbu", "Al Qunfudhah", "Hafar Al-Batin", "Bisha", "Al Zulfi", "Dhahran", "Al Khobar", "Jizan", "Arar", "Sakaka", "Baha", "Al Qurayyat", "Tarout", "Al Khafji", "Unaizah", "Al Duwadimi", "Rafha", "Turaif", "Sabya", "Abu Arish", "Samtah", "Al Wajh", "Al Namas", "Badr", "Dawadmi", "Majmaah", "Rabigh", "Turabah", "Thadiq", "Diriyah", "Dhurma", "Huraymila", "Al Ula", "Khaibar"],
    "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah", "Al Ain", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain", "Khor Fakkan", "Kalba", "Dibba Al-Fujairah", "Dibba Al-Hisn", "Hatta", "Zayed City", "Ruwais", "Liwa Oasis", "Al Dhaid", "Ghantoot", "Masdar City", "Al Madam", "Ar-Rams", "Dhaid", "Ghiyathi", "Bida Zayed", "Sila", "Muzairah", "Madinat Zayed", "Al Jazirah Al Hamra", "Al Heera", "Al Qasimi", "Al Khalidiyah", "Al Markaziyah", "Al Karamah", "Al Zahiyah", "Al Maryah", "Al Reem", "Al Bateen", "Al Mushrif", "Al Muroor", "Al Nahyan", "Al Rowdah", "Al Maqtaa", "Al Bahia", "Al Shahama", "Al Rahba", "Al Samha", "Al Mafraq", "Al Shawamekh", "Al Wathba", "Sweihan"],
    "Kenya": ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Kehancha", "Ruiru", "Kikuyu", "Kangundo-Talia", "Malindi", "Naivasha", "Kitui", "Machakos", "Thika", "Athi River", "Karuri", "Nyeri", "Kilifi", "Garissa", "Vihiga", "Mumias", "Bomet", "Molo", "Ngong", "Kitale", "Litein", "Limuru", "Kericho", "Kimilili", "Awasi", "Kakamega", "Kapsabet", "Mariakani", "Kiambu", "Mandera", "Nyamira", "Mwingi", "Kisii", "Wajir", "Rongo", "Bungoma", "Ahero", "Nandi Hills", "Makuyu", "Kapenguria", "Taveta", "Narok", "Ol Kalou", "Kakuma", "Webuye"],
    "Ghana": ["Accra", "Kumasi", "Tamale", "Takoradi", "Achiaman", "Tema", "Teshie", "Cape Coast", "Sekondi-Takoradi", "Obuasi", "Madina", "Koforidua", "Wa", "Techiman", "Nungua", "Ho", "Sunyani", "Bawku", "Bolgatanga", "Taifa", "Swedru", "Berekum", "Nkawkaw", "Oduponkpehe", "Winneba", "Aflao", "Agona Swedru", "Tarkwa", "Yendi", "Kintampo", "Mampong", "Navrongo", "Ejura", "Prestea", "Nsawam", "Suhum", "Wenchi", "Kasoa", "Asamankese", "Mpraeso", "Begoro", "Saltpond", "Keta", "Akim Oda", "Anloga", "Elmina", "Kpandu", "Bole", "Gbawe", "Salaga"],
    "Tanzania": ["Dar es Salaam", "Mwanza", "Zanzibar", "Arusha", "Mbeya", "Morogoro", "Tanga", "Dodoma", "Kigoma", "Moshi", "Tabora", "Songea", "Musoma", "Iringa", "Katumba", "Bukoba", "Mtwara", "Kilwa Masoko", "Sumbawanga", "Shinyanga", "Ushirombo", "Njombe", "Geita", "Kibaha", "Kahama", "Mpanda", "Makambako", "Bariadi", "Masasi", "Singida", "Mabamba", "Babati", "Bagamoyo", "Lindi", "Mafia", "Korogwe", "Tarime", "Nansio", "Mlandizi", "Chake Chake", "Tunduma", "Vwawa", "Kasulu", "Ngara", "Urambo", "Mwanga", "Kondoa", "Igunga", "Tukuyu", "Nachingwea"],
    "Uganda": ["Kampala", "Nansana", "Kira", "Ssabagabo", "Entebbe", "Mbarara", "Mukono", "Gulu", "Lugazi", "Masaka", "Kasese", "Hoima", "Lira", "Mityana", "Mubende", "Masindi", "Mbale", "Jinja", "Busia", "Fort Portal", "Iganga", "Soroti", "Arua", "Tororo", "Koboko", "Mpondwe", "Gomba", "Luweero", "Manafwa", "Kaberamaido", "Nakapiripirit", "Bugiri", "Njeru", "Rukungiri", "Kamwenge", "Kyotera", "Apac", "Kumi", "Pallisa", "Kamuli", "Kitgum", "Ntungamo", "Nebbi", "Oyam", "Kayunga", "Kiboga", "Sironko", "Amuria", "Isingiro", "Moyo"],
    "Ethiopia": ["Addis Ababa", "Dire Dawa", "Mek'ele", "Nazret", "Bahir Dar", "Gondar", "Hawassa", "Dessie", "Jimma", "Jijiga", "Shashamane", "Bishoftu", "Sodo", "Arba Minch", "Hosaena", "Dilla", "Nekemte", "Debre Birhan", "Asella", "Debre Markos", "Kombolcha", "Debre Tabor", "Adigrat", "Weldiya", "Sebeta", "Burayu", "Shire", "Ambo", "Arsi Negele", "Aksum", "Bale Robe", "Goba", "Zway", "Gode", "Metu", "Yirgalem", "Woliso", "Adwa", "Fiche", "Bonga", "Alamata", "Gimbi", "Mendi", "Wukro", "Mota", "Degehabur", "Aleta Wendo", "Negele Borana", "Bako", "Dembi Dolo"],
    "Iraq": ["Baghdad", "Basra", "Mosul", "Erbil", "Kirkuk", "Najaf", "Karbala", "Nasiriyah", "Amarah", "Diwaniyah", "Kut", "Hillah", "Duhok", "Sulaymaniyah", "Baqubah", "Ramadi", "Fallujah", "Zakho", "Halabja", "Tikrit", "Samarra", "Tal Afar", "Sinjar", "Al Diwaniyah", "Khanaqin", "Al-Qaim", "Balad", "Al-Faw", "Hit", "Haditha", "Rutba", "Ranya", "Kalar", "Aqrah", "Soran", "Amedi", "Shaqlawa", "Rwanduz", "Bashiqa", "Tuz Khurmatu", "Makhmur", "Al-Daur", "Baiji", "Sharqat", "Al-Hamdaniya", "Qaraqosh", "Kufa", "Abu Ghraib", "Taji", "Zubair"],
    "Iran": ["Tehran", "Mashhad", "Isfahan", "Karaj", "Shiraz", "Tabriz", "Qom", "Ahvaz", "Kermanshah", "Urmia", "Rasht", "Zahedan", "Hamadan", "Kerman", "Yazd", "Ardabil", "Bandar Abbas", "Arak", "Eslamshahr", "Zanjan", "Sanandaj", "Qazvin", "Khorramabad", "Gorgan", "Sari", "Shahriar", "Kashan", "Dezful", "Nishapur", "Babol", "Amol", "Khomeyni Shahr", "Sabzevar", "Golestan", "Borujerd", "Abadan", "Najafabad", "Malayer", "Saveh", "Bojnord", "Bushehr", "Qarchak", "Sirjan", "Birjand", "Ilam", "Mahabad", "Bukan", "Maragheh", "Shahr-e Kord", "Nasimshahr"],
    "Afghanistan": ["Kabul", "Kandahar", "Herat", "Mazar-i-Sharif", "Kunduz", "Taloqan", "Jalalabad", "Puli Khumri", "Charikar", "Lashkargah", "Sheberghan", "Ghazni", "Khost", "Sar-e Pol", "Chaghcharan", "Mihtarlam", "Farah", "Gereshk", "Kholm", "Paghman", "Faizabad", "Asadabad", "Aybak", "Zaranj", "Mahmud-i-Raqi", "Tarin Kowt", "Maimana", "Andkhoy", "Qala i Naw", "Rustaq", "Khanabad", "Gulran", "Baharak", "Shindand", "Shahrak", "Samangan", "Baglan", "Kushk", "Ghormach", "Ghorian", "Obey", "Qarqeen", "Aqcha", "Tashkurgan", "Tiwara", "Zebak", "Gereshk", "Nili", "Sayyad", "Spin Boldak"],
    "Bangladesh": ["Dhaka", "Chittagong", "Khulna", "Rajshahi", "Sylhet", "Mymensingh", "Barisal", "Rangpur", "Comilla", "Narayanganj", "Gazipur", "Bogra", "Kushtia", "Jessore", "Cox's Bazar", "Brahmanbaria", "Dinajpur", "Nawabganj", "Pabna", "Tangail", "Sirajganj", "Feni", "Jamalpur", "Noakhali", "Faridpur", "Saidpur", "Naogaon", "Joypurhat", "Bhola", "Magura", "Habiganj", "Madaripur", "Lakshmipur", "Chandpur", "Manikganj", "Chuadanga", "Moulvibazar", "Thakurgaon", "Kishoreganj", "Netrokona", "Jhenaidah", "Satkhira", "Munshiganj", "Patuakhali", "Bagerhat", "Narsingdi", "Sunamganj", "Sherpur", "Kurigram", "Bandarban"],
    "Myanmar": ["Yangon", "Mandalay", "Naypyidaw", "Bago", "Mawlamyine", "Taunggyi", "Monywa", "Meiktila", "Pathein", "Mrauk U", "Lashio", "Pakokku", "Sittwe", "Myingyan", "Magway", "Pyin Oo Lwin", "Hinthada", "Dawei", "Bhamo", "Pyay", "Kyaukse", "Minbu", "Shwebo", "Kengtung", "Taungoo", "Myeik", "Kayan", "Thanlyin", "Tharrawaddy", "Loikaw", "Nyaunglebin", "Thaton", "Tachileik", "Ye", "Mudon", "Thongwa", "Kyauktan", "Letpadan", "Myanaung", "Hakha", "Sagaing", "Yenangyaung", "Shwedaung", "Wakema", "Kawkareik", "Myawaddy", "Falam", "Kalay", "Mindat", "Putao"],
    "Uzbekistan": ["Tashkent", "Samarkand", "Namangan", "Andijan", "Bukhara", "Nukus", "Qarshi", "Kokand", "Margilan", "Navoiy", "Urgench", "Jizzakh", "Angren", "Chirchiq", "Termez", "Olmaliq", "Denov", "Bekabad", "Shahrisabz", "Kattaqo'rg'on", "Guliston", "Chust", "Kogon", "Zarafshon", "Shahrixon", "Qo'ng'irot", "Taxiatosh", "Asaka", "Khiva", "Yangiyo'l", "Urgut", "Buloqboshi", "G'ijduvon", "Kosonsoy", "Oqtosh", "G'uzor", "Qamashi", "Rishton", "Yangiyer", "Qibray", "Toshbuloq", "Tuytepa", "Chiroqchi", "Pskent", "Beshariq", "Haqqulobod", "Shofirkon", "To'raqo'rg'on", "Xonobod", "Zomin"],
    "Ukraine": ["Kyiv", "Kharkiv", "Odesa", "Dnipro", "Donetsk", "Zaporizhzhia", "Lviv", "Kryvyi Rih", "Mykolaiv", "Mariupol", "Luhansk", "Vinnytsia", "Makiivka", "Sevastopol", "Simferopol", "Kherson", "Poltava", "Chernihiv", "Cherkasy", "Zhytomyr", "Sumy", "Khmelnytskyi", "Chernivtsi", "Horlivka", "Rivne", "Kamianske", "Kropyvnytskyi", "Ivano-Frankivsk", "Kremenchuk", "Ternopil", "Lutsk", "Bila Tserkva", "Kramatorsk", "Melitopol", "Kerch", "Nikopol", "Sloviansk", "Berdiansk", "Sievierodonetsk", "Alchevsk", "Pavlohrad", "Uzhhorod", "Lysychansk", "Yevpatoria", "Yenakiieve", "Kamianets-Podilskyi", "Kostyantynivka", "Khrustalnyi", "Oleksandriya", "Khrustalny"]
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
            time.sleep(2)

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
