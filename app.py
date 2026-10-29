import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, date
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

st.set_page_config(page_title="Local SEO Intelligence OS", page_icon="📍", layout="wide", initial_sidebar_state="expanded")

NAVY = "#17263C"
TEAL = "#167D83"
PALE = "#F1F6F7"
MUTED = "#657487"

st.markdown(f"""
<style>
  :root {{ --ink:#17263C; --teal:#167D83; --muted:#657487; --line:#E6E9E8; }}
  .stApp {{ background: #FBFAF7; color: #17263C; }}
  [data-testid="stSidebar"] {{ background: #F5F3EF; border-right: 1px solid #E6E3DD; }}
  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ color:#586576; }}
  .block-container {{ padding-top: 1.3rem; padding-bottom: 3rem; max-width: 1380px; }}
  .hero {{ background: #F0EEE8; color: {NAVY}; padding: 42px 44px; border-radius: 22px; margin: 8px 0 24px; border:1px solid #E8E4DB; }}
  .hero h1 {{ color: {NAVY}; font-size: clamp(34px,4vw,54px); line-height:1.04; letter-spacing:-2px; margin: 0 0 14px; max-width:760px; }}
  .hero p {{ color: #596675; font-size:16px; line-height:1.55; margin: 0; max-width:760px; }}
  .eyebrow {{ text-transform:uppercase; letter-spacing:1.5px; font-size:11px; font-weight:750; color:{TEAL}; margin-bottom:12px; }}
  .section-title {{ color: {NAVY}; font-size: 21px; font-weight: 720; letter-spacing:-.4px; margin: 22px 0 10px; }}
  .section-subtitle {{ color:{MUTED}; font-size:14px; margin:-4px 0 16px; }}
  .feature-card {{ background:white; border:1px solid #E7E8E5; border-radius:16px; padding:20px 21px; min-height:168px; box-shadow:0 2px 8px #17263C08; }}
  .feature-kicker {{ font-size:11px; letter-spacing:1px; text-transform:uppercase; color:{TEAL}; font-weight:750; margin-bottom:12px; }}
  .feature-title {{ font-size:18px; line-height:1.25; font-weight:720; color:{NAVY}; margin-bottom:8px; }}
  .feature-copy {{ font-size:13px; line-height:1.55; color:{MUTED}; }}
  .callout {{ background:#EAF3F1; border:1px solid #DCEAE6; border-radius:14px; padding:18px 20px; color:#334E50; }}
  .small-note {{ color: {MUTED}; font-size: 12px; }}
  .status-pill {{ display: inline-block; border-radius: 99px; padding: 4px 9px; font-size: 12px; background: #FFF4DB; color: #8B5A00; }}
  div[data-testid="stMetric"] {{ background: white; border: 1px solid #E6E9E7; padding: 16px; border-radius: 14px; box-shadow:0 2px 8px #17263C06; }}
  div[data-testid="stMetricLabel"] {{ color:#657487; }}
  div[data-testid="stMetricValue"] {{ color:#17263C; }}
  .stButton>button, .stDownloadButton>button {{ border-radius:10px; font-weight:650; }}
  .stTextInput input, .stTextArea textarea {{ border-radius:10px; }}
  [data-testid="stDataFrame"] {{ border:1px solid #E6E9E7; border-radius:12px; overflow:hidden; }}
  @media print {{ [data-testid="stSidebar"], header, footer, .stButton, .stDownloadButton {{ display:none !important; }} .stApp {{ background:white; }} }}
</style>
""", unsafe_allow_html=True)

def sample_data():
    clients = pd.DataFrame([
        {"Client": "Sample Cafe Shah Alam", "Website": "https://example.com", "Location": "Shah Alam, Selangor", "Status": "Sample"},
        {"Client": "Sample Dental Clinic", "Website": "https://example.org", "Location": "Petaling Jaya, Selangor", "Status": "Sample"},
    ])
    keywords = pd.DataFrame([
        {"Keyword": "cafe shah alam", "Location": "Shah Alam", "Rank": None, "Data source": "Sample / not measured"},
        {"Keyword": "dentist petaling jaya", "Location": "Petaling Jaya", "Rank": None, "Data source": "Sample / not measured"},
        {"Keyword": "local seo malaysia", "Location": "Malaysia", "Rank": None, "Data source": "Sample / not measured"},
    ])
    ai = pd.DataFrame([
        {"Prompt": "Best cafe in Shah Alam", "Engine": "Manual check", "Brand mentioned": "Not checked", "Evidence URL": ""},
        {"Prompt": "Best local SEO consultant in Malaysia", "Engine": "Manual check", "Brand mentioned": "Not checked", "Evidence URL": ""},
    ])
    competitors = pd.DataFrame([
        {"Competitor": "Sample competitor A", "Website": "https://example.net", "Location": "Shah Alam", "Notes": "Example record only"}
    ])
    return clients, keywords, ai, competitors

if "clients" not in st.session_state:
    st.session_state.clients, st.session_state.keywords, st.session_state.ai_checks, st.session_state.competitors = sample_data()
    st.session_state.gbp_checks = pd.DataFrame(columns=["Client", "Checklist item", "Status", "Notes"])
    st.session_state.audit_history = []

def safe_url(url):
    p = urlparse(url.strip())
    return p.scheme in ("http", "https") and bool(p.netloc)

def audit_page(url):
    r = requests.get(url, timeout=15, headers={"User-Agent": "LocalSEOIntelligenceOS/1.0"}, allow_redirects=True)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    desc_tag = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "description"})
    desc = (desc_tag.get("content") or "").strip() if desc_tag else ""
    h1 = [x.get_text(" ", strip=True) for x in soup.find_all("h1")]
    canon_tag = soup.find("link", rel=lambda x: x and "canonical" in x)
    canonical = canon_tag.get("href", "") if canon_tag else ""
    imgs = soup.find_all("img")
    no_alt = sum(1 for img in imgs if not (img.get("alt") or "").strip())
    host = urlparse(r.url).netloc.lower()
    internal = 0
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("/") or urlparse(href).netloc.lower() == host:
            internal += 1
    robots_tag = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "robots"})
    robots = (robots_tag.get("content") or "").strip() if robots_tag else "Not specified"
    checks = [
        ("HTTPS enabled", r.url.startswith("https://"), r.url),
        ("Page title exists", bool(title), title or "Missing"),
        ("Meta description exists", bool(desc), desc or "Missing"),
        ("At least one H1", len(h1) >= 1, f"{len(h1)} found"),
        ("Exactly one H1", len(h1) == 1, f"{len(h1)} found"),
        ("Canonical tag", bool(canonical), canonical or "Not found"),
        ("No noindex directive", "noindex" not in robots.lower(), robots),
        ("Image alt text", no_alt == 0, f"{no_alt} missing alt of {len(imgs)} images"),
        ("Internal links", internal > 0, f"{internal} detected"),
    ]
    df = pd.DataFrame([{"Check": n, "Result": "PASS" if ok else "REVIEW", "Finding": f} for n, ok, f in checks])
    details = {"URL": r.url, "HTTP status": r.status_code, "Title": title, "Meta description": desc, "H1 headings": " | ".join(h1), "Images": len(imgs), "Images missing alt": no_alt, "Internal links": internal}
    return df, details

def make_pdf(client, website, location, period, summary, actions, audit_df=None, kw_df=None, ai_df=None):
    buff = BytesIO()
    doc = SimpleDocTemplate(buff, pagesize=A4, rightMargin=17*mm, leftMargin=17*mm, topMargin=17*mm, bottomMargin=17*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BrandTitle", parent=styles["Title"], textColor=colors.HexColor(NAVY), fontSize=22, leading=26, alignment=TA_LEFT, spaceAfter=5))
    styles.add(ParagraphStyle(name="Subtle", parent=styles["Normal"], textColor=colors.HexColor(MUTED), fontSize=9, leading=13))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], textColor=colors.HexColor(TEAL), fontSize=13, leading=16, spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="BodySmall", parent=styles["BodyText"], fontSize=9, leading=13))
    story = [
        Paragraph("LOCAL SEO PERFORMANCE REPORT", styles["BrandTitle"]),
        Paragraph("Local SEO Intelligence OS · Malaysia Edition", styles["Subtle"]),
        Spacer(1, 8*mm),
    ]
    meta = [
        ["Client / business", client or "Not specified"],
        ["Website", website or "Not specified"],
        ["Target location", location or "Not specified"],
        ["Reporting period", period],
        ["Generated", datetime.now().strftime("%d %b %Y, %H:%M")],
    ]
    t = Table(meta, colWidths=[42*mm, 125*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1),colors.HexColor(PALE)),
        ("TEXTCOLOR",(0,0),(0,-1),colors.HexColor(NAVY)),
        ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
        ("FONTSIZE",(0,0),(-1,-1),9),
        ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#DCE4EA")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
    ]))
    story += [t, Paragraph("Executive summary", styles["Section"]), Paragraph(summary.replace("\n","<br/>"), styles["BodySmall"])]
    story += [Paragraph("Priority actions", styles["Section"])]
    action_rows = [["Priority", "Recommended action"]] + [[str(i+1), x] for i, x in enumerate(actions)]
    at = Table(action_rows, colWidths=[20*mm, 147*mm], repeatRows=1)
    at.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor(NAVY)),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#DCE4EA")),("FONTSIZE",(0,0),(-1,-1),8),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
    ]))
    story.append(at)
    if audit_df is not None and len(audit_df):
        story.append(Paragraph("Website audit findings", styles["Section"]))
        rows = [["Check","Result","Finding"]]
        rows += [[str(r["Check"]), str(r["Result"]), str(r["Finding"])[:180]] for _, r in audit_df.iterrows()]
        tbl = Table(rows, colWidths=[42*mm, 23*mm, 102*mm], repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor(NAVY)),("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#DCE4EA")),("FONTSIZE",(0,0),(-1,-1),7),
            ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ]))
        story.append(tbl)
    if kw_df is not None and len(kw_df):
        story.append(Paragraph("Keyword tracking snapshot", styles["Section"]))
        rows = [["Keyword","Location","Rank","Source"]]
        for _, r in kw_df.head(25).iterrows():
            rank = r.get("Rank", r.get("Current rank", ""))
            rows.append([str(r.get("Keyword","")), str(r.get("Location", r.get("Target location",""))), "Not measured" if pd.isna(rank) or rank is None else str(rank), str(r.get("Data source", r.get("Source","")))])
        tbl = Table(rows, colWidths=[54*mm, 37*mm, 25*mm, 51*mm], repeatRows=1)
        tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor(NAVY)),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#DCE4EA")),("FONTSIZE",(0,0),(-1,-1),7),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        story.append(tbl)
    story += [Spacer(1, 8*mm), Paragraph("Data integrity note", styles["Section"]), Paragraph("This report only includes data entered, imported, or audited within the application. Blank ranks mean no verified ranking data was supplied. A basic HTML audit is not a full technical crawl and does not guarantee ranking improvements. Google Maps grid rankings and automated AI visibility are not connected in this MVP.", styles["BodySmall"]), Spacer(1, 5*mm), Paragraph("Prepared with Local SEO Intelligence OS · Not affiliated with Google.", styles["Subtle"])]
    doc.build(story)
    buff.seek(0)
    return buff.getvalue()

# Sidebar
with st.sidebar:
    st.markdown(f"<div style='font-size:11px;color:{TEAL};font-weight:800;letter-spacing:1.6px;'>VERITAS-INSPIRED</div><div style='font-size:24px;font-weight:780;color:{NAVY};margin:4px 0 4px;'>Search Studio</div><div style='font-size:11px;color:{MUTED};margin-bottom:18px;'>SEO · AI visibility · Local</div>", unsafe_allow_html=True)
    pages = ["Dashboard", "Clients", "Website Audit", "Keywords", "Local SEO & GBP", "Competitors", "AI Visibility", "Client Report"]
    jump_to = st.session_state.pop("page_jump", "Dashboard")
    page = st.radio("WORKSPACE", pages, index=pages.index(jump_to), label_visibility="visible")
    st.divider()
    st.caption("Workspace tools")
    st.caption("Demo records are clearly marked")

if page == "Dashboard":
    st.markdown("<div class='hero'><div class='eyebrow'>Search visibility, all in one place</div><h1>Rank on Google.<br>Get cited by AI.</h1><p>Understand what is holding your site back, where your brand appears in AI answers, and what to improve next. Explore audits, keyword research, local SEO and AI visibility from one workspace.</p></div>", unsafe_allow_html=True)
    url_col, button_col = st.columns([4,1])
    with url_col:
        quick_url = st.text_input("Start with your website", placeholder="https://yourwebsite.com", label_visibility="collapsed", key="quick_site_url")
    with button_col:
        if st.button("Analyze my site", type="primary", use_container_width=True):
            if safe_url(quick_url):
                st.session_state.audit_url = quick_url
                st.session_state.page_jump = "Website Audit"
                st.rerun()
            else:
                st.warning("Enter a complete website URL to start your audit.")
    st.markdown("<div class='small-note'>✓ Public page audit &nbsp;&nbsp; ✓ No account needed for this demo &nbsp;&nbsp; ✓ Sample metrics are never presented as live</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>One workspace for every search channel</div><div class='section-subtitle'>Find the issues, track your visibility, and turn the findings into practical next steps.</div>", unsafe_allow_html=True)
    features = st.columns(4)
    feature_cards = [
        ("SEO", "Audit and improve your site", "Check page titles, descriptions, headings, canonicals and links. Import verified keyword data as it becomes available."),
        ("AI VISIBILITY", "Know when AI names your brand", "Log reproducible checks across ChatGPT, Gemini, Perplexity and Google AI results with evidence."),
        ("LOCAL SEO", "Strengthen your local presence", "Review your Business Profile details, keep a local SEO checklist and import map grid results."),
        ("CONTENT & REPORTING", "Make the next step clear", "Track competitors and build a concise PDF report with findings and prioritized actions."),
    ]
    for col, (kicker, title, copy) in zip(features, feature_cards):
        col.markdown(f"<div class='feature-card'><div class='feature-kicker'>{kicker}</div><div class='feature-title'>{title}</div><div class='feature-copy'>{copy}</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Your workspace</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Client workspaces", len(st.session_state.clients), "sample + your records")
    c2.metric("Tracked keywords", len(st.session_state.keywords), "positions need verified imports")
    c3.metric("Competitors", len(st.session_state.competitors), "manual / imported")
    c4.metric("Connected data sources", "0", "integrations not configured")
    left,right = st.columns([1.3,1])
    with left:
        st.markdown("<div class='section-title'>Client workspaces</div>", unsafe_allow_html=True)
        st.dataframe(st.session_state.clients, use_container_width=True, hide_index=True)
        st.markdown("<div class='section-title'>Recommended next steps</div>", unsafe_allow_html=True)
        st.markdown("1. Run a website audit for a client URL.\n2. Import verified keyword performance from Search Console or a rank tracker.\n3. Complete the Google Business Profile checklist.\n4. Record AI visibility checks with evidence URLs.\n5. Generate a client report with the findings.")
    with right:
        st.markdown("<div class='section-title'>Data source status</div>", unsafe_allow_html=True)
        st.markdown("""<div class='callout'>
        <b>Website HTML audit</b> · Available<br><br>
        <b>Search Console</b> · CSV import<br><br>
        <b>Maps geogrid</b> · Manual / import<br><br>
        <b>AI engine monitoring</b> · Evidence log<br><br>
        <b>Business Profile API</b> · Not connected<br><br>
        <b>Search volume & backlinks</b> · Not connected
        </div>""", unsafe_allow_html=True)
        st.caption("Sample rows are examples. No sample ranking, traffic or AI mention is presented as a live measurement.")

elif page == "Clients":
    st.markdown("<div class='section-title'>Client workspaces</div>", unsafe_allow_html=True)
    with st.form("client_form"):
        a,b = st.columns(2)
        name = a.text_input("Business / client name")
        website = b.text_input("Website URL")
        location = a.text_input("Target location", placeholder="Shah Alam, Selangor")
        status = b.selectbox("Record status", ["Active client", "Prospect", "Sample"])
        if st.form_submit_button("Add client"):
            if name.strip():
                st.session_state.clients = pd.concat([st.session_state.clients, pd.DataFrame([{"Client":name.strip(),"Website":website.strip(),"Location":location.strip(),"Status":status}])], ignore_index=True)
                st.success("Client added for this session.")
            else: st.error("Enter a business name.")
    st.dataframe(st.session_state.clients, use_container_width=True, hide_index=True)
    st.download_button("Export clients CSV", st.session_state.clients.to_csv(index=False).encode(), "clients.csv", "text/csv")

elif page == "Website Audit":
    st.markdown("<div class='section-title'>Website SEO audit</div>", unsafe_allow_html=True)
    st.caption("A fast check of public HTML. It does not crawl the full site or measure Core Web Vitals.")
    url = st.text_input("Page URL", value=st.session_state.get("audit_url", ""), placeholder="https://yourdomain.com/")
    if st.button("Run website audit", type="primary"):
        if not safe_url(url):
            st.error("Enter a complete https:// or http:// URL.")
        else:
            try:
                with st.spinner("Checking public page HTML…"):
                    checks, details = audit_page(url)
                st.session_state.last_audit = checks
                st.session_state.last_audit_details = details
                st.session_state.audit_history.append({"URL":details["URL"],"Audited":datetime.now().strftime("%Y-%m-%d %H:%M"),"Review items":int((checks["Result"]=="REVIEW").sum())})
                st.success("Audit completed.")
            except Exception as e: st.error(f"Audit could not complete: {e}")
    if "last_audit" in st.session_state:
        d=st.session_state.last_audit_details; df=st.session_state.last_audit
        st.markdown(f"**Audited URL:** {d['URL']}  \n**HTTP status:** {d['HTTP status']}  \n**Title:** {d['Title'] or 'Missing'}  \n**Meta description:** {d['Meta description'] or 'Missing'}")
        a,b,c=st.columns(3); a.metric("Checks passed",int((df.Result=="PASS").sum())); b.metric("Items to review",int((df.Result=="REVIEW").sum())); c.metric("Images missing alt",d["Images missing alt"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download audit CSV",df.to_csv(index=False).encode(),"website-audit.csv","text/csv")
    if st.session_state.audit_history:
        st.markdown("<div class='section-title'>Recent audit history (current session)</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(st.session_state.audit_history),use_container_width=True,hide_index=True)

elif page == "Keywords":
    st.markdown("<div class='section-title'>Keyword tracking</div>", unsafe_allow_html=True)
    st.caption("Rank fields remain blank until a verified source supplies positions.")
    with st.form("keyword_form"):
        a,b = st.columns(2); kw=a.text_input("Keyword"); loc=b.text_input("Location")
        if st.form_submit_button("Add keyword"):
            if kw.strip():
                st.session_state.keywords = pd.concat([st.session_state.keywords,pd.DataFrame([{"Keyword":kw.strip(),"Location":loc.strip(),"Rank":None,"Data source":"Manual / not measured"}])],ignore_index=True)
                st.success("Keyword added.")
            else: st.error("Enter a keyword.")
    f=st.file_uploader("Import rank tracking CSV",type=["csv"])
    if f:
        try:
            imp=pd.read_csv(f); st.dataframe(imp.head(30),use_container_width=True)
            if st.button("Append imported keyword rows"):
                st.session_state.keywords=pd.concat([st.session_state.keywords,imp],ignore_index=True); st.success("Imported rows appended.")
        except Exception as e: st.error(f"CSV import failed: {e}")
    st.dataframe(st.session_state.keywords,use_container_width=True,hide_index=True)
    st.download_button("Export keyword CSV",st.session_state.keywords.to_csv(index=False).encode(),"keywords.csv","text/csv")

elif page == "Local SEO & GBP":
    st.markdown("<div class='section-title'>Local SEO & Google Business Profile checklist</div>", unsafe_allow_html=True)
    st.info("Live Google Business Profile sync and Maps geogrid queries are not connected. This is a manual audit and evidence log.")
    fields=["Business name consistency","Primary category","Additional categories","Address / service area","Phone and website","Opening hours","Services and products","Business description","Photos","Review response process","Landing page relevance","NAP citations","Duplicate listing check"]
    with st.form("gbp_form"):
        client=st.selectbox("Client",st.session_state.clients.Client.astype(str).tolist())
        field=st.selectbox("Checklist item",fields); status=st.selectbox("Status",["Not checked","Pass","Needs action","Not applicable"]); notes=st.text_area("Evidence / recommended action")
        if st.form_submit_button("Save checklist item"):
            st.session_state.gbp_checks=pd.concat([st.session_state.gbp_checks,pd.DataFrame([{"Client":client,"Checklist item":field,"Status":status,"Notes":notes}])],ignore_index=True)
            st.success("Checklist item saved.")
    if len(st.session_state.gbp_checks):
        st.dataframe(st.session_state.gbp_checks,use_container_width=True,hide_index=True)
        st.download_button("Export GBP checklist",st.session_state.gbp_checks.to_csv(index=False).encode(),"gbp-checklist.csv","text/csv")
    st.markdown("**Geogrid import**")
    grid=st.file_uploader("Import an existing local rank grid CSV",type=["csv"],key="grid")
    if grid:
        try:
            grid_df=pd.read_csv(grid); st.dataframe(grid_df,use_container_width=True); st.download_button("Download grid data",grid_df.to_csv(index=False).encode(),"local-grid.csv","text/csv")
        except Exception as e: st.error(f"Could not read file: {e}")

elif page == "Competitors":
    st.markdown("<div class='section-title'>Competitor intelligence</div>", unsafe_allow_html=True)
    with st.form("competitor_form"):
        a,b=st.columns(2); name=a.text_input("Competitor"); site=b.text_input("Website"); loc=a.text_input("Location"); notes=b.text_input("Observed strengths / gaps")
        if st.form_submit_button("Add competitor"):
            if name.strip():
                st.session_state.competitors=pd.concat([st.session_state.competitors,pd.DataFrame([{"Competitor":name.strip(),"Website":site.strip(),"Location":loc.strip(),"Notes":notes.strip()}])],ignore_index=True); st.success("Competitor saved.")
            else: st.error("Enter competitor name.")
    st.dataframe(st.session_state.competitors,use_container_width=True,hide_index=True)
    st.download_button("Export competitors CSV",st.session_state.competitors.to_csv(index=False).encode(),"competitors.csv","text/csv")

elif page == "AI Visibility":
    st.markdown("<div class='section-title'>AI visibility tracking</div>", unsafe_allow_html=True)
    st.caption("Log reproducible checks and evidence. This module does not automatically query AI engines.")
    with st.form("ai_form"):
        prompt=st.text_input("Exact prompt tested"); engine=st.selectbox("AI platform",["ChatGPT","Gemini","Perplexity","Google AI Overviews / AI Mode","Other"]); mentioned=st.selectbox("Brand mentioned?",["Yes","No","Unknown"]); evidence=st.text_area("Evidence excerpt / notes"); url=st.text_input("Source or citation URL")
        if st.form_submit_button("Save AI visibility check"):
            st.session_state.ai_checks=pd.concat([st.session_state.ai_checks,pd.DataFrame([{"Prompt":prompt,"Engine":engine,"Brand mentioned":mentioned,"Evidence URL":url,"Evidence notes":evidence,"Checked at":datetime.now().strftime("%Y-%m-%d %H:%M")}])],ignore_index=True); st.success("Check saved.")
    st.dataframe(st.session_state.ai_checks,use_container_width=True,hide_index=True)
    st.download_button("Export AI visibility CSV",st.session_state.ai_checks.to_csv(index=False).encode(),"ai-visibility.csv","text/csv")

elif page == "Client Report":
    st.markdown("<div class='section-title'>Client report builder</div>", unsafe_allow_html=True)
    st.caption("Generate a clean PDF report for printing or emailing. Only available data is included; missing live metrics are clearly marked.")
    client_options=st.session_state.clients.Client.astype(str).tolist()
    selected=st.selectbox("Client",client_options)
    row=st.session_state.clients[st.session_state.clients.Client.astype(str)==selected].iloc[0] if len(st.session_state.clients) else {}
    website=st.text_input("Website",str(row.get("Website","")))
    location=st.text_input("Target location",str(row.get("Location","")))
    period=st.text_input("Reporting period",f"{date.today().replace(day=1).strftime('%d %b %Y')} – {date.today().strftime('%d %b %Y')}")
    summary=st.text_area("Executive summary", "This report summarizes the SEO checks and information recorded in the Local SEO Intelligence OS workspace. Ranking and AI visibility metrics are not reported as live unless verified data has been imported.")
    default_actions = "Fix the highest-priority on-page issues identified in the audit.\nVerify Google Business Profile categories, services, hours and contact details.\nImport verified keyword rankings and track changes over time.\nRecord AI search checks with dated evidence and citation URLs."
    actions_text=st.text_area("Priority actions (one per line)",default_actions,height=130)
    use_audit=st.checkbox("Include latest website audit if available",value="last_audit" in st.session_state)
    use_keywords=st.checkbox("Include keyword snapshot",value=True)
    if st.button("Generate client PDF",type="primary"):
        actions=[x.strip("- •\t ") for x in actions_text.splitlines() if x.strip()]
        pdf=make_pdf(selected,website,location,period,summary,actions,
                     st.session_state.last_audit if use_audit and "last_audit" in st.session_state else None,
                     st.session_state.keywords if use_keywords else None,
                     st.session_state.ai_checks)
        filename="local-seo-report-"+ "".join(c.lower() if c.isalnum() else "-" for c in selected).strip("-") + ".pdf"
        st.session_state.report_pdf=pdf; st.session_state.report_filename=filename
        st.success("PDF report generated.")
    if "report_pdf" in st.session_state:
        st.download_button("Download printable client report (PDF)",st.session_state.report_pdf,st.session_state.report_filename,"application/pdf",type="primary")
        st.caption("Open the downloaded PDF and print or email it to your client.")

st.divider()
st.caption("Local SEO Intelligence OS · Prototype inspired by common SEO and AI visibility workflows. Not affiliated with Google or Veritas. Sample records are not real client data.")
