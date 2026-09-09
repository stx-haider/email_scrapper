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
    "United States": ["New York", "Los Angeles", "Chicago", "Houston", "Miami"],
    "United Kingdom": ["London", "Birmingham", "Manchester", "Glasgow", "Liverpool"],
    "Canada": ["Toronto", "Montreal", "Vancouver", "Calgary", "Ottawa"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
    "Pakistan": ["Karachi", "Lahore", "Islamabad", "Faisalabad", "Multan"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
    "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah", "Ajman"]
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
