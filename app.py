import base64
from io import BytesIO
import os
import random
import sqlite3
import urllib.request
from PIL import Image
import streamlit as st

# =====================================================================
# 1. PAGE CONFIG & ENHANCED DEVOTIONAL STYLING
# =====================================================================
st.set_page_config(
    page_title="Shirdi Sai Canonical Knowledge & Prashnavali Portal",
    page_icon="🙏",
    layout="wide",
)

st.markdown(
    """
    <style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Entire Page Outer Layer Outline Frame */
    .main .block-container {
        max-width: 1080px !important;
        padding: 2.0rem 2.5rem !important;
        margin: 1.2rem auto !important;
        border: 3px solid #d97706 !important;
        outline: 2px solid #78350f !important;
        outline-offset: 4px !important;
        border-radius: 22px !important;
        background: linear-gradient(180deg, #fffdf8 0%, #ffffff 100%) !important;
        box-shadow: 0 16px 45px rgba(120, 53, 15, 0.15) !important;
    }

    /* Portal Title Header */
    .portal-title {
        font-family: 'Cinzel', serif;
        color: #78350F;
        font-size: 2.0rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
        line-height: 1.2;
        text-align: center;
    }
    .portal-subtitle {
        font-size: 0.92rem;
        color: #92400e;
        margin-top: 4px;
        font-weight: 500;
        text-align: center;
    }

    /* Om Header Icons */
    .header-om-icon {
        font-size: 2.4rem;
        color: #d97706;
        line-height: 1;
        margin-top: 4px;
    }

    /* Devotional Side Pillars (Shraddha & Saburi) */
    .devotional-pillar {
        background: linear-gradient(145deg, #ffffff 0%, #fffbe6 100%);
        border: 1.5px solid #fde68a;
        padding: 16px 12px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(217, 119, 6, 0.06);
        text-align: center;
        margin-top: 2px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .pillar-sanskrit {
        font-family: 'Cinzel', serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #d97706;
        margin-bottom: 2px;
    }
    .pillar-translation {
        font-family: 'Cinzel', serif;
        font-size: 0.98rem;
        font-weight: 700;
        color: #78350F;
        letter-spacing: 1px;
    }
    .pillar-desc {
        font-size: 0.8rem;
        color: #92400e;
        margin-top: 4px;
        font-style: italic;
    }

    /* Center-Aligned Baba Image Frame Container */
    .baba-frame-compact {
        background: linear-gradient(145deg, #ffffff 0%, #fffbe6 100%);
        border: 1.5px solid #fde68a;
        padding: 10px 14px;
        border-radius: 14px;
        box-shadow: 0 6px 18px -4px rgba(217, 119, 6, 0.12);
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        width: fit-content !important;
        margin: 0 auto !important;
    }

    /* =================================================================
       EXECUTIVE HORIZONTALLY EXTENDED NAVBAR
       ================================================================= */
    div[data-testid="stTabs"] {
        background: transparent !important;
    }

    /* Outer Mahogany Navbar Box */
    div[data-testid="stTabs"] > div:first-child {
        background: linear-gradient(135deg, #2e1202 0%, #451a03 100%) !important;
        border: 2.5px solid #d97706 !important;
        border-radius: 16px !important;
        padding: 10px 12px !important;
        margin-top: 18px !important;
        margin-bottom: 28px !important;
        box-shadow: 0 6px 20px rgba(46, 18, 2, 0.28) !important;
    }

    /* Tab List Container Flex */
    div[data-baseweb="tab-list"] {
        display: flex !important;
        width: 100% !important;
        gap: 12px !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    /* Individual Tab Buttons - Full Horizontal Width & Prominent Text */
    button[data-baseweb="tab"] {
        flex: 1 1 0% !important;
        width: 100% !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        background: #fffdf8 !important;
        border: 1.5px solid #fcd34d !important;
        color: #78350f !important;
        font-weight: 800 !important;
        font-size: 1.12rem !important;
        letter-spacing: 0.5px !important;
        text-align: center !important;
        justify-content: center !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.06) !important;
        transition: all 0.25s ease-in-out !important;
    }

    button[data-baseweb="tab"]:hover {
        background: #fef3c7 !important;
        color: #451a03 !important;
        border-color: #f59e0b !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(217, 119, 6, 0.25) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.15rem !important;
        border: 1.5px solid #ffffff !important;
        box-shadow: 0 5px 18px rgba(217, 119, 6, 0.45) !important;
    }

    /* Completely hide default tab underline elements */
    div[data-baseweb="tab-highlight"],
    div[data-baseweb="tab-border"] {
        display: none !important;
        height: 0px !important;
    }

    /* Section Header Banner with Accent Line Bar */
    .section-header-banner {
        background: linear-gradient(135deg, #2e1202 0%, #522104 100%);
        color: #fef3c7;
        padding: 14px 22px;
        border-radius: 12px;
        border-left: 6px solid #f59e0b;
        font-family: 'Cinzel', serif;
        font-size: 1.28rem;
        font-weight: 700;
        margin: 10px 0 20px 0;
        box-shadow: 0 4px 14px rgba(82, 33, 4, 0.18);
        display: flex;
        align-items: center;
        gap: 10px;
        letter-spacing: 0.5px;
    }

    /* Instruction Plaque Card */
    .prashna-input-card {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1.5px solid #fcd34d;
        border-left: 6px solid #d97706;
        padding: 18px 22px;
        border-radius: 12px;
        margin-bottom: 22px;
        box-shadow: 0 4px 12px rgba(217, 119, 6, 0.08);
        font-size: 1.0rem;
        color: #78350F;
        font-weight: 600;
        line-height: 1.5;
    }

    /* =================================================================
       HIGH-VISIBILITY INPUT CONTROLS, DROPDOWNS & TEXTBOXES
       ================================================================= */
    div[data-baseweb="input"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"],
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        background-color: #ffffff !important;
        border: 2px solid #d97706 !important;
        border-radius: 12px !important;
        color: #451a03 !important;
        font-size: 1.02rem !important;
        font-weight: 600 !important;
        box-shadow: 0 3px 10px rgba(217, 119, 6, 0.08) !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within > div,
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: #b45309 !important;
        box-shadow: 0 0 0 3.5px rgba(217, 119, 6, 0.25) !important;
        background-color: #fffdf8 !important;
    }

    /* Dropdown Options Popup Menu */
    ul[data-baseweb="menu"] {
        background-color: #fffdf8 !important;
        border: 2px solid #d97706 !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 24px rgba(120, 53, 15, 0.18) !important;
    }
    li[data-baseweb="option"] {
        color: #451a03 !important;
        font-weight: 600 !important;
        font-size: 0.98rem !important;
        padding: 10px 16px !important;
    }
    li[data-baseweb="option"]:hover,
    li[aria-selected="true"] {
        background-color: #fef3c7 !important;
        color: #78350F !important;
    }

    /* Label Styling Above Input Fields */
    label, div[data-testid="stWidgetLabel"] p {
        color: #78350F !important;
        font-weight: 800 !important;
        font-size: 0.98rem !important;
        margin-bottom: 6px !important;
        letter-spacing: 0.3px !important;
    }

    /* Action Buttons Custom Design */
    .stButton > button {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 0.98rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 11px 24px !important;
        box-shadow: 0 4px 14px rgba(180, 83, 9, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #b45309 0%, #78350f 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(120, 53, 15, 0.35) !important;
        color: #ffffff !important;
    }

    /* Traditional Prashnavali Blessing Plaque */
    .prashna-card-trad {
        background: linear-gradient(145deg, #ffffff 0%, #fffdf5 100%);
        border: 2px solid #f59e0b;
        border-left: 8px solid #d97706;
        padding: 24px 22px;
        border-radius: 16px;
        text-align: center;
        margin: 22px 0;
        box-shadow: 0 8px 24px -6px rgba(217, 119, 6, 0.15);
    }
    .prashna-number {
        font-family: 'Cinzel', serif;
        font-size: 1.2em;
        color: #b45309;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .prashna-msg-trad {
        font-size: 1.35em;
        color: #451a03;
        margin-top: 10px;
        font-weight: 600;
        line-height: 1.5;
    }

    /* Guidance Box */
    .guidance-box {
        background-color: #fffbeb;
        border-left: 6px solid #d97706;
        padding: 18px 22px;
        border-radius: 12px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }
    .quote-text {
        font-size: 1.12em;
        font-weight: 600;
        color: #78350F;
        font-style: italic;
        line-height: 1.48;
    }

    /* Dark Mahogany Footer Box Container */
    .footer-box {
        margin-top: 38px;
        padding: 28px 24px;
        background: linear-gradient(135deg, #1e0c02 0%, #3b1904 50%, #1e0c02 100%);
        color: #fef3c7;
        border-radius: 18px;
        text-align: center;
        border: 1.5px solid #92400e;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
    }
    .footer-logo-img {
        width: 100px;
        height: auto;
        border-radius: 50%;
        border: 2px solid #f59e0b;
        padding: 3px;
        background-color: #ffffff;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .footer-brand {
        font-family: 'Cinzel', serif;
        font-size: 1.28rem;
        font-weight: 700;
        color: #f59e0b;
        letter-spacing: 1.5px;
    }
    .footer-contact {
        margin: 10px 0 14px 0;
        font-size: 0.9rem;
        color: #fde68a;
    }
    .footer-contact a {
        color: #ffffff;
        background-color: rgba(217, 119, 6, 0.35);
        padding: 6px 16px;
        border-radius: 20px;
        text-decoration: none;
        font-weight: 600;
        border: 1px solid #f59e0b;
        transition: all 0.2s;
    }
    .footer-contact a:hover {
        background-color: #d97706;
        color: #ffffff;
    }
    .footer-disclaimer {
        font-size: 0.78rem;
        color: #d1d5db;
        line-height: 1.55;
        max-width: 860px;
        margin: 14px auto 10px auto;
        border-top: 1px solid rgba(245, 158, 11, 0.3);
        padding-top: 12px;
    }
    .footer-copyright {
        font-size: 0.75rem;
        color: #9ca3af;
        letter-spacing: 0.5px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Absolute Path Resolution for Database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sai_knowledge_base.db")


# =====================================================================
# 2. CACHED DATABASE HELPERS WITH FULL CATCH BLOCKS
# =====================================================================
@st.cache_data(ttl=300)
def get_prashnavali_dual_data(number_1_to_720):
    """Fetches traditional Prashnavali answer and mapped record with explicit JOIN, caching, and exception handling."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        query_sql = (
            "SELECT p.answer, r.record_id, r.source_title, r.primary_category, "
            "r.sub_category, r.raw_text_excerpt, r.baba_direct_quote, "
            "r.canonical_summary, r.cross_references "
            "FROM prashnavali_720 p "
            "LEFT JOIN records r ON p.mapped_record_id = r.record_id "
            "WHERE p.number = ?"
        )
        cursor.execute(query_sql, (number_1_to_720,))
        row = cursor.fetchone()
        if row:
            return row[0], row[1:] if row[1] else None
    except sqlite3.Error as e:
        st.error(f"⚠️ Database query error: {e}")
    finally:
        if conn:
            conn.close()

    return None, None


@st.cache_data(ttl=300)
def resolve_user_intent(user_text):
    """Checks the pre-computed prashna_intent_map table with caching and error fallback."""
    user_lower = user_text.lower().strip()
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT phrase, category, target_tags, banner_msg FROM prashna_intent_map")
        rows = cursor.fetchall()

        rows.sort(key=lambda x: len(x[0]), reverse=True)
        for phrase, cat, tags_str, banner in rows:
            if phrase in user_lower:
                tags_list = [t.strip() for t in tags_str.split(",")]
                return cat, tags_list, banner
    except sqlite3.Error:
        st.warning("⚠️ Intent resolution temporarily operating in direct protection mode.")
    finally:
        if conn:
            conn.close()

    return (
        "CAT-PROTECT",
        ["protect", "fear", "anxiety", "worry", "surrender"],
        None,
    )


@st.cache_data(ttl=300)
def fetch_guidance_records_ranked(keywords_tuple, primary_cat=None):
    """Searches canonical records using weighted relevance score ranking with caching."""
    conn = None
    results = []
    keywords = list(keywords_tuple)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cond_unit = "(sub_category LIKE ? OR tags LIKE ? OR baba_direct_quote LIKE ? OR canonical_summary LIKE ?)"
        exact_conditions = " OR ".join([cond_unit for _ in keywords])

        params = []
        for kw in keywords:
            p = f"%{kw}%"
            params.extend([p, p, p, p])

        sql = (
            "SELECT record_id, source_title, primary_category, sub_category, "
            "raw_text_excerpt, baba_direct_quote, canonical_summary, cross_references, "
            "((CASE WHEN primary_category = ? THEN 5 ELSE 0 END) + "
            "(CASE WHEN sub_category LIKE ? THEN 4 ELSE 0 END) + "
            "(CASE WHEN tags LIKE ? THEN 3 ELSE 0 END) + "
            "(CASE WHEN baba_direct_quote LIKE ? THEN 2 ELSE 0 END)) as relevance_score "
            "FROM records WHERE (" + exact_conditions + ") "
            "AND baba_direct_quote IS NOT NULL AND baba_direct_quote != '' "
            "ORDER BY relevance_score DESC, record_id ASC LIMIT 5"
        )

        first_kw = f"%{keywords[0]}%" if keywords else "%"
        score_params = [
            primary_cat or "",
            first_kw,
            first_kw,
            first_kw,
        ] + params

        cursor.execute(sql, score_params)
        results = cursor.fetchall()

        if not results and primary_cat:
            fallback_sql = (
                "SELECT record_id, source_title, primary_category, sub_category, "
                "raw_text_excerpt, baba_direct_quote, canonical_summary, cross_references, 1 as score "
                "FROM records WHERE primary_category = ? "
                "AND baba_direct_quote IS NOT NULL AND baba_direct_quote != '' LIMIT 3"
            )
            cursor.execute(fallback_sql, (primary_cat,))
            results = cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"⚠️ Guidance query failed: {e}")
    finally:
        if conn:
            conn.close()

    return results


@st.cache_data(ttl=300)
def search_records(query_term):
    """Raw search engine across canonical literature with caching."""
    conn = None
    results = []
    try:
        search_pattern = f"%{query_term.strip()}%"
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        search_sql = (
            "SELECT record_id, source_title, primary_category, sub_category, "
            "raw_text_excerpt, baba_direct_quote, canonical_summary, "
            "cross_references, tags, historical_figures "
            "FROM records "
            "WHERE raw_text_excerpt LIKE ? OR canonical_summary LIKE ? OR tags LIKE ? "
            "OR sub_category LIKE ? OR historical_figures LIKE ? "
            "ORDER BY record_id ASC LIMIT 20"
        )

        cursor.execute(
            search_sql,
            (
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
            ),
        )

        results = cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"⚠️ Search error: {e}")
    finally:
        if conn:
            conn.close()

    return results


# Safe Image Loader Helper
def load_image_safe(paths_list):
    for path in paths_list:
        if os.path.exists(path):
            try:
                return Image.open(path)
            except Exception:
                continue
    return None


# Base64 Image Encoder Helper
def get_image_base64(pil_img):
    if pil_img is None:
        return None
    try:
        buffered = BytesIO()
        pil_img.save(buffered, format="PNG" if pil_img.mode == "RGBA" else "JPEG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception:
        return None


# =====================================================================
# 3. HEADER WITH SACRED OM SYMBOLS & CENTERED TITLE
# =====================================================================
header_col1, header_col2, header_col3 = st.columns([0.6, 4, 0.6])

with header_col1:
    st.markdown('<div class="header-om-icon" style="text-align: left;">🕉️</div>', unsafe_allow_html=True)

with header_col2:
    st.markdown(
        """
        <div>
            <div class="portal-title">SHIRDI SAI KNOWLEDGE & PRASHNAVALI PORTAL</div>
            <div class="portal-subtitle">A Sacred Guidance & Canonical Literature Engine</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with header_col3:
    st.markdown('<div class="header-om-icon" style="text-align: right;">🕉️</div>', unsafe_allow_html=True)

st.markdown("<hr style='margin: 6px 0 12px 0; border-color: #fde68a;'>", unsafe_allow_html=True)

# =====================================================================
# 4. HERO SECTION: SHRADDHA | CENTERED BABA PHOTO | SABURI
# =====================================================================
col_left, col_center, col_right = st.columns([1, 1.1, 1])

# Left Pillar: Shraddha
with col_left:
    st.markdown(
        """
        <div class="devotional-pillar">
            <div class="pillar-sanskrit">श्रद्धा</div>
            <div class="pillar-translation">SHRADDHA</div>
            <div class="pillar-desc">Unwavering Faith & Devotion</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

# Center Column: Strictly Centered Compact Baba Photo Card
with col_center:
    baba_candidate_paths = [
        os.path.join(BASE_DIR, "sai_knowledge_base", "baba.jpg"),
        os.path.join(BASE_DIR, "sai_knowledge_base", "baba.jpeg"),
        os.path.join(BASE_DIR, "sai_knowledge_base", "baba.png"),
        os.path.join(BASE_DIR, "baba.jpg"),
        os.path.join(BASE_DIR, "baba.jpeg"),
        os.path.join(BASE_DIR, "baba.png"),
    ]

    baba_img = load_image_safe(baba_candidate_paths)

    if baba_img is None:
        try:
            online_url = "https://upload.wikimedia.org/wikipedia/commons/e/e0/Sai_Baba_of_Shirdi_1.jpg"
            req = urllib.request.Request(
                online_url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                baba_img = Image.open(resp)
        except Exception:
            baba_img = None

    baba_b64 = get_image_base64(baba_img)

    if baba_b64:
        baba_html = (
            '<div class="baba-frame-compact">'
            f'<img src="data:image/jpeg;base64,{baba_b64}" style="width:180px; border-radius:10px; display:block; margin:0 auto;" alt="Sainath Maharaj in Dwarakamai" />'
            '<div style="font-size:0.76rem; color:#78350F; font-weight:600; margin-top:6px; text-align:center; line-height:1.3;">'
            'Why Fear When I Am Here —<br/>Sainath Maharaj in Dwarakamai'
            '</div>'
            '</div>'
        )
        st.markdown(baba_html, unsafe_allow_html=True)
    else:
        st.info("🙏 **Why Fear When I Am Here — Sainath Maharaj in Dwarakamai**")

# Right Pillar: Saburi
with col_right:
    st.markdown(
        """
        <div class="devotional-pillar">
            <div class="pillar-sanskrit">सबूरी</div>
            <div class="pillar-translation">SABURI</div>
            <div class="pillar-desc">Patient Endurance & Trust</div>
        </div>
    """,
        unsafe_allow_html=True,
    )


# =====================================================================
# 5. NAVIGATION MENUS (FULL-WIDTH EXECUTIVE NAVBAR)
# =====================================================================
tab1, tab2, tab3 = st.tabs(
    ["✨ Sri Sai Prashnavali (1–720)", "🙏 Seek Guidance", "🔍 Search Literature"]
)


# =====================================================================
# TAB 1: SRI SAI PRASHNAVALI
# =====================================================================
with tab1:
    st.markdown(
        '<div class="section-header-banner">🕉️ Sri Sai Baba Prashnavali</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="prashna-input-card">'
        'Offer your prayer in your heart, meditate on Sainath Maharaj, and pick a sacred number between <b>1 and 720</b>:'
        '</div>',
        unsafe_allow_html=True,
    )

    if "prashna_number" not in st.session_state:
        st.session_state.prashna_number = 108

    col1, col2 = st.columns([2.2, 1])

    with col1:
        chosen_number = st.number_input(
            "Select Sacred Number (1–720):",
            min_value=1,
            max_value=720,
            value=st.session_state.prashna_number,
            step=1,
            key="num_input",
        )
        st.session_state.prashna_number = chosen_number

    with col2:
        st.write(" ")
        st.write(" ")
        if st.button("🎲 Pick Random Number"):
            st.session_state.prashna_number = random.randint(1, 720)
            st.rerun()

    if chosen_number:
        trad_ans, canonical_rec = get_prashnavali_dual_data(chosen_number)

        if trad_ans:
            card_html = (
                '<div class="prashna-card-trad">'
                '<div class="prashna-number">✨ Traditional Prashnavali Blessing #'
                + str(chosen_number)
                + " (Shri Madhav Lele Bhat)</div>"
                '<div class="prashna-msg-trad">"'
                + str(trad_ans)
                + '"</div>'
                "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)

        if canonical_rec:
            (
                rec_id,
                source,
                cat,
                sub_cat,
                excerpt,
                quote,
                summary,
                cross_refs,
            ) = canonical_rec

            expander_title = "📖 Canonical Literature Backing [" + str(rec_id) + "] — " + str(sub_cat)
            with st.expander(expander_title, expanded=True):
                st.markdown("**Source Literature:** *" + str(source) + "*")
                if quote:
                    st.info('**Sainath\'s Direct Words:** "' + str(quote) + '"')
                st.markdown("**Canonical Summary:** " + str(summary))
                st.markdown('**Historical Excerpt:** *"' + str(excerpt) + '"*')
                if cross_refs:
                    st.caption("🔗 Related Passages: " + str(cross_refs))


# =====================================================================
# TAB 2: SEEK GUIDANCE BY PROBLEM
# =====================================================================
with tab2:
    st.markdown(
        '<div class="section-header-banner">🙏 Place Your Worries at Sainath\'s Feet</div>',
        unsafe_allow_html=True,
    )

    preset_options = [
        "Select or type your own below...",
        "My brother lost his job, help him get a new job soon",
        "I am suffering from sickness and physical pain, please heal me",
        "I am in severe financial distress and debt",
        "I am waiting for a long time and losing patience, when will my problem resolve?",
        "Someone is spreading slander and false rumors against me",
        "I am facing a court case / legal trouble",
        "We are anxious about marriage and children for our family",
        "I am worried about my exams, studies, and concentration",
        "I feel heavy grief, depression, and anxiety about the future",
    ]

    preset = st.selectbox(
        "Choose a common life situation:",
        preset_options,
    )

    user_input = st.text_input(
        "What is on your heart? (Type your situation or prayer):",
        value="" if preset.startswith("Select") else preset,
    )

    if user_input and not user_input.startswith("Select"):
        primary_cat, target_keywords, banner_msg = resolve_user_intent(user_input)

        guidance_results = fetch_guidance_records_ranked(
            tuple(target_keywords), primary_cat=primary_cat
        )

        st.markdown("---")

        if banner_msg:
            st.info(banner_msg)

        st.subheader("🕊️ Sainath's Assurance & Direct Words")

        for row in guidance_results:
            (
                rec_id,
                source,
                cat,
                sub_cat,
                excerpt,
                quote,
                summary,
                cross_refs,
                score,
            ) = row

            box_html = (
                '<div class="guidance-box">'
                '<div class="quote-text">"' + str(quote) + '"</div>'
                '<p style="margin-top: 6px; color: #555;">— <b>Sai Baba</b> in <i>' + str(source) + "</i> [" + str(rec_id) + "]</p>"
                "</div>"
            )
            st.markdown(box_html, unsafe_allow_html=True)

            expander_label = "📖 Read How Baba Guided Devotees in This Situation (" + str(sub_cat) + ")"
            with st.expander(expander_label, expanded=False):
                st.markdown("**Canonical Summary:** " + str(summary))
                st.markdown("**Historical Context:** *" + str(excerpt) + "*")
                if cross_refs:
                    st.caption("🔗 Related Canonical Passages: " + str(cross_refs))


# =====================================================================
# TAB 3: REGULAR SEARCH ENGINE
# =====================================================================
with tab3:
    st.markdown(
        '<div class="section-header-banner">🔍 Search 230 Canonically Validated Records</div>',
        unsafe_allow_html=True,
    )

    query_term = st.text_input(
        "Search keywords:",
        placeholder="e.g., Kakasaheb Dixit, Udi, Cholera, Dakshina",
    )

    if query_term:
        res = search_records(query_term)
        if not res:
            st.warning("No canonical records matched your query.")
        for r in res:
            st.markdown("**[" + str(r[0]) + "] " + str(r[1]) + " — " + str(r[3]) + "**")
            st.write(r[6])
            if r[5]:
                st.info('"' + str(r[5]) + '"')
            st.markdown("---")


# =====================================================================
# 6. UNIFIED DARK MAHOGANY FOOTER BOX
# =====================================================================
ddn_logo_paths = [
    os.path.join(BASE_DIR, "sai_knowledge_base", "DDNProductions.jpeg"),
    os.path.join(BASE_DIR, "sai_knowledge_base", "DDN Productions.jpeg"),
    os.path.join(BASE_DIR, "sai_knowledge_base", "DDN Productions.jpg"),
    os.path.join(BASE_DIR, "sai_knowledge_base", "DDNProductions.jpg"),
    os.path.join(BASE_DIR, "DDNProductions.jpeg"),
    os.path.join(BASE_DIR, "DDN Productions.jpeg"),
    os.path.join(BASE_DIR, "DDN Productions.jpg"),
    os.path.join(BASE_DIR, "DDNProductions.jpg"),
    os.path.join(BASE_DIR, "sai_knowledge_base", "ddn_logo.jpg"),
    os.path.join(BASE_DIR, "ddn_logo.jpg"),
]

ddn_logo_img = load_image_safe(ddn_logo_paths)
logo_b64 = get_image_base64(ddn_logo_img)

logo_html_tag = ""
if logo_b64:
    logo_html_tag = f'<img src="data:image/jpeg;base64,{logo_b64}" class="footer-logo-img" alt="DDN Productions Logo" /><br/>'

footer_html = (
    '<div class="footer-box">'
    + logo_html_tag +
    '<div class="footer-brand">DDN PRODUCTIONS</div>'
    '<div style="font-size: 0.85rem; color: #fcd34d; font-style: italic; margin-top: 2px; margin-bottom: 8px;">A Father\'s Legacy in Every Note</div>'
    '<div class="footer-contact">'
    '📧 Contact & Inquiries: <a href="mailto:dsd.ddnproductions@gmail.com">dsd.ddnproductions@gmail.com</a>'
    '</div>'
    '<div class="footer-disclaimer">'
    '<b>Devotional & Canonical Disclaimer:</b> This portal is a non-commercial educational and spiritual resource dedicated to Shri Sai Baba of Shirdi. Answers and canonical backings are mapped directly from authentic literature including <i>Sri Sai Satcharita</i>, <i>Devotees\' Experiences of Sri Sai Baba</i>, <i>Khaparde\'s Shirdi Diary</i>, and historical archives. Users are encouraged to exercise personal faith, discernment, and devotion.'
    '</div>'
    '<div class="footer-copyright">'
    '© 2026 DDN Productions. All Rights Reserved.'
    '</div>'
    '</div>'
)

st.markdown(footer_html, unsafe_allow_html=True)