import os
import random
import sqlite3
import streamlit as st

# =====================================================================
# 1. PAGE & LAYOUT CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="Shirdi Sai Canonical Knowledge & Prashnavali Portal",
    page_icon="🙏",
    layout="wide",
)

# Custom CSS for Devotional Portal Styling
st.markdown(
    """
    <style>
    .guidance-box {
        background-color: #fff9e6;
        border-left: 6px solid #f5a623;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
    }
    .quote-text {
        font-size: 1.25em;
        font-weight: 600;
        color: #7a4100;
        font-style: italic;
    }
    .prashna-card-trad {
        background-color: #f0f7ff;
        border: 2px solid #1E88E5;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin: 15px 0;
    }
    .prashna-number {
        font-size: 1.4em;
        color: #1565C0;
        font-weight: bold;
    }
    .prashna-msg-trad {
        font-size: 1.35em;
        color: #1a237e;
        margin-top: 10px;
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Absolute Path Resolution for Database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sai_knowledge_base.db")


# =====================================================================
# 2. DATABASE HELPER & INTENT ROUTING FUNCTIONS
# =====================================================================
def get_prashnavali_dual_data(number_1_to_720):
    """Fetches traditional 720 Prashnavali answer and canonical backing record."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Traditional Answer from prashnavali_720
    trad_answer = None
    try:
        cursor.execute(
            "SELECT answer FROM prashnavali_720 WHERE number = ?",
            (number_1_to_720,),
        )
        row = cursor.fetchone()
        if row:
            trad_answer = row[0]
    except sqlite3.OperationalError:
        pass

    # 2. Matching Canonical Literature Record (1 to 230 Offset)
    record_offset = (number_1_to_720 - 1) % 230
    cursor.execute(
        """
        SELECT record_id, source_title, primary_category, sub_category, 
               raw_text_excerpt, baba_direct_quote, canonical_summary, cross_references
        FROM records
        ORDER BY record_id ASC
        LIMIT 1 OFFSET ?
    """,
        (record_offset,),
    )

    canonical_rec = cursor.fetchone()
    conn.close()
    return trad_answer, canonical_rec


def resolve_user_intent(user_text):
    """Checks the pre-computed prashna_intent_map table across all 10 problem domains."""
    user_lower = user_text.lower()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT phrase, category, target_tags, banner_msg FROM"
            " prashna_intent_map"
        )
        rows = cursor.fetchall()
        conn.close()

        # Sort by phrase length descending so multi-word intent phrases match first
        rows.sort(key=lambda x: len(x[0]), reverse=True)

        for phrase, cat, tags_str, banner in rows:
            if phrase in user_lower:
                tags_list = [t.strip() for t in tags_str.split(",")]
                return cat, tags_list, banner
    except sqlite3.OperationalError:
        conn.close()

    # Fallback to general spiritual protection
    return (
        "CAT-PROTECT",
        ["protect", "fear", "anxiety", "worry", "surrender"],
        None,
    )


def fetch_guidance_records_ranked(keywords, primary_cat=None):
    """Searches canonical records using weighted relevance score ranking."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    exact_conditions = " OR ".join(
        [
            "(sub_category LIKE ? OR tags LIKE ? OR baba_direct_quote LIKE ? OR"
            " canonical_summary LIKE ?)"
            for _ in keywords
        ]
    )

    params = []
    for kw in keywords:
        p = f"%{kw}%"
        params.extend([p, p, p, p])

    sql = f"""
        SELECT record_id, source_title, primary_category, sub_category, 
               raw_text_excerpt, baba_direct_quote, canonical_summary, cross_references,
               (
                   (CASE WHEN primary_category = ? THEN 5 ELSE 0 END) +
                   (CASE WHEN sub_category LIKE ? THEN 4 ELSE 0 END) +
                   (CASE WHEN tags LIKE ? THEN 3 ELSE 0 END) +
                   (CASE WHEN baba_direct_quote LIKE ? THEN 2 ELSE 0 END)
               ) as relevance_score
        FROM records
        WHERE ({exact_conditions})
          AND baba_direct_quote IS NOT NULL 
          AND baba_direct_quote != ''
        ORDER BY relevance_score DESC, record_id ASC
        LIMIT 5
    """

    first_kw = f"%{keywords[0]}%" if keywords else "%"
    score_params = [
        primary_cat or "",
        first_kw,
        first_kw,
        first_kw,
    ] + params

    cursor.execute(sql, score_params)
    results = cursor.fetchall()

    # Category fallback if specific search misses
    if not results and primary_cat:
        fallback_sql = """
            SELECT record_id, source_title, primary_category, sub_category, 
                   raw_text_excerpt, baba_direct_quote, canonical_summary, cross_references, 1 as score
            FROM records
            WHERE primary_category = ?
              AND baba_direct_quote IS NOT NULL 
              AND baba_direct_quote != ''
            LIMIT 3
        """
        cursor.execute(fallback_sql, (primary_cat,))
        results = cursor.fetchall()

    conn.close()
    return results


def search_records(query_term):
    """Raw search engine across literature."""
    search_pattern = f"%{query_term.strip()}%"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT record_id, source_title, primary_category, sub_category, 
               raw_text_excerpt, baba_direct_quote, canonical_summary, 
               cross_references, tags, historical_figures
        FROM records
        WHERE raw_text_excerpt LIKE ? OR canonical_summary LIKE ? OR tags LIKE ? OR sub_category LIKE ? OR historical_figures LIKE ?
        ORDER BY record_id ASC
        LIMIT 20
    """,
        (
            search_pattern,
            search_pattern,
            search_pattern,
            search_pattern,
            search_pattern,
        ),
    )

    results = cursor.fetchall()
    conn.close()
    return results


# =====================================================================
# 3. HEADER & DWARAKAMAI PHOTO
# =====================================================================
st.title("🙏 Shirdi Sai Knowledge & Prashnavali Portal")

col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    local_image = os.path.join(BASE_DIR, "baba.jpg")
    try:
        if os.path.exists(local_image):
            st.image(
                local_image,
                caption="Why Fear When I Am Here — Sainath Maharaj in Dwarakamai",
            )
        else:
            st.image(
                "https://images.unsplash.com/photo-1544717305-2782549b5136?w=800",
                caption="Why Fear When I Am Here — Sainath Maharaj in Dwarakamai",
            )
    except Exception:
        st.info("🙏 *Why Fear When I Am Here — Sainath Maharaj in Dwarakamai*")

tab1, tab2, tab3 = st.tabs(
    ["✨ Sri Sai Prashnavali (1–720)", "🙏 Seek Guidance", "🔍 Search Literature"]
)


# =====================================================================
# TAB 1: SRI SAI PRASHNAVALI (DUAL-LAYERED TRADITIONAL + CANONICAL)
# =====================================================================
with tab1:
    st.markdown("### 🕉️ Sri Sai Baba Prashnavali")
    st.write(
        "Think of Sainath Maharaj, offer your prayer in your heart, and select"
        " a number from **1 to 720**."
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        chosen_number = st.number_input(
            "Enter a number between 1 and 720:",
            min_value=1,
            max_value=720,
            value=108,
            step=1,
        )

    with col2:
        st.write(" ")
        st.write(" ")
        if st.button("🎲 Pick Random Number"):
            chosen_number = random.randint(1, 720)

    if chosen_number:
        trad_ans, canonical_rec = get_prashnavali_dual_data(chosen_number)

        if trad_ans:
            st.markdown(
                f"""
                <div class="prashna-card-trad">
                    <div class="prashna-number">✨ Traditional Prashnavali Blessing #{chosen_number} (Shri Madhav Lele Bhat)</div>
                    <div class="prashna-msg-trad">"{trad_ans}"</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

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

            with st.expander(
                f"📖 Canonical Literature Backing [{rec_id}] — {sub_cat}",
                expanded=True,
            ):
                st.markdown(f"**Source Literature:** *{source}*")
                if quote:
                    st.info(f'**Sainath\'s Direct Words:** "{quote}"')
                st.markdown(f"**Canonical Summary:** {summary}")
                st.markdown(f'**Historical Excerpt:** *"{excerpt}"*')
                if cross_refs:
                    st.caption(f"🔗 Related Passages: {cross_refs}")


# =====================================================================
# TAB 2: SEEK GUIDANCE BY PROBLEM (ALL 10 DOMAINS COVERED)
# =====================================================================
with tab2:
    st.markdown("### Place Your Worries at Sainath's Feet")
    preset = st.selectbox(
        "Choose a common situation or type below:",
        [
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
        ],
    )

    user_input = st.text_input(
        "What is on your heart?",
        value="" if preset.startswith("Select") else preset,
    )

    if user_input and not user_input.startswith("Select"):
        # Resolve intent using offline pre-computed semantic map
        primary_cat, target_keywords, banner_msg = resolve_user_intent(
            user_input
        )

        guidance_results = fetch_guidance_records_ranked(
            target_keywords, primary_cat=primary_cat
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

            st.markdown(
                f"""
                <div class="guidance-box">
                    <div class="quote-text">"{quote}"</div>
                    <p style="margin-top: 10px; color: #555;">— <b>Sai Baba</b> in <i>{source}</i> [{rec_id}]</p>
                </div>
            """,
                unsafe_allow_html=True,
            )

            with st.expander(
                f"📖 Read How Baba Guided Devotees in This Situation"
                f" ({sub_cat})",
                expanded=False,
            ):
                st.markdown(f"**Canonical Summary:** {summary}")
                st.markdown(f'**Historical Context:** *"{excerpt}"*')
                if cross_refs:
                    st.caption(f"🔗 Related Canonical Passages: {cross_refs}")


# =====================================================================
# TAB 3: REGULAR SEARCH ENGINE
# =====================================================================
with tab3:
    st.markdown("### Search 230 Canonically Validated Records")
    query_term = st.text_input(
        "Search keywords:",
        placeholder="e.g., Kakasaheb Dixit, Udi, Cholera, Dakshina",
    )

    if query_term:
        res = search_records(query_term)
        if not res:
            st.warning("No canonical records matched your query.")
        for r in res:
            st.markdown(f"**[{r[0]}] {r[1]} — {r[3]}**")
            st.write(r[6])
            if r[5]:
                st.info(f'"{r[5]}"')
            st.markdown("---")