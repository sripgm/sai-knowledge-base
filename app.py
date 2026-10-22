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

# Custom CSS for Divine Styling
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
    .prashna-card {
        background-color: #f0f7ff;
        border: 2px solid #1E88E5;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin: 20px 0;
    }
    .prashna-number {
        font-size: 1.5em;
        color: #1565C0;
        font-weight: bold;
    }
    .prashna-msg {
        font-size: 1.3em;
        color: #2c3e50;
        margin-top: 10px;
        font-weight: 500;
    }
    </style>
""",
    unsafe_allow_html=True,
)

DB_PATH = "sai_knowledge_base.db"


# =====================================================================
# 2. DATABASE HELPER FUNCTIONS
# =====================================================================
def get_record_by_index(number_1_to_720):
    """Maps a Prashnavali number (1-720) cleanly to one of the 230 canonical records."""
    record_offset = (number_1_to_720 - 1) % 230

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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

    result = cursor.fetchone()
    conn.close()
    return result


def fetch_guidance_records(keywords, primary_cat=None):
    """Searches for records matching target intent keywords, prioritizing the relevant category."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    or_clauses = " OR ".join(
        [
            "(raw_text_excerpt LIKE ? OR canonical_summary LIKE ? OR tags LIKE"
            " ? OR sub_category LIKE ?)"
            for _ in keywords
        ]
    )

    params = []
    for kw in keywords:
        p = f"%{kw}%"
        params.extend([p, p, p, p])

    sql = f"""
        SELECT record_id, source_title, primary_category, sub_category, 
               raw_text_excerpt, baba_direct_quote, canonical_summary, cross_references
        FROM records
        WHERE ({or_clauses})
          AND baba_direct_quote IS NOT NULL 
          AND baba_direct_quote != ''
        ORDER BY CASE WHEN primary_category = ? THEN 1 ELSE 2 END
        LIMIT 5
    """

    params.append(primary_cat or "")
    cursor.execute(sql, params)
    results = cursor.fetchall()

    # Fallback to category defaults if specific terms return empty
    if not results and primary_cat:
        fallback_sql = """
            SELECT record_id, source_title, primary_category, sub_category, 
                   raw_text_excerpt, baba_direct_quote, canonical_summary, cross_references
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
    """Performs raw search across all canonical literature fields."""
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

# Display Centered Dwarakamai Photo (Local file 'baba.jpg' if present, else fallback URL)
col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    image_source = (
        "baba.jpg"
        if os.path.exists("baba.jpg")
        else "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Sai_Baba_of_Shirdi%2C_seated.jpg/800px-Sai_Baba_of_Shirdi%2C_seated.jpg"
    )
    st.image(
        image_source,
        caption="Why Fear When I Am Here — Sainath Maharaj in Dwarakamai",
        use_container_width=True,
    )

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(
    ["✨ Sri Sai Prashnavali (1–720)", "🙏 Seek Guidance", "🔍 Search Literature"]
)


# =====================================================================
# TAB 1: SRI SAI PRASHNAVALI (1–720)
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
        record = get_record_by_index(chosen_number)

        if record:
            (
                rec_id,
                source,
                cat,
                sub_cat,
                excerpt,
                quote,
                summary,
                cross_refs,
            ) = record

            st.markdown(
                f"""
                <div class="prashna-card">
                    <div class="prashna-number">Prashnavali Answer #{chosen_number}</div>
                    <div class="prashna-msg">"{quote if quote else summary}"</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

            with st.expander(
                f"📖 Canonical Context from Literature [{rec_id}] — {sub_cat}",
                expanded=True,
            ):
                st.markdown(f"**Source Literature:** *{source}*")
                st.markdown(f"**Summary:** {summary}")
                st.markdown(f'**Historical Excerpt:** *"{excerpt}"*')
                if cross_refs:
                    st.caption(f"🔗 Related Passages: {cross_refs}")


# =====================================================================
# TAB 2: SEEK GUIDANCE BY QUERY (INTENT ROUTING)
# =====================================================================
with tab2:
    st.markdown("### Place Your Worries at Sainath's Feet")
    preset = st.selectbox(
        "Choose a common situation or type below:",
        [
            "Select or type your own below...",
            "My brother lost his job, help him get a new job soon",
            "I am suffering a lot in life, when will this pain end?",
            "I feel anxious and uncertain about my future and job",
            "I am dealing with sickness and physical suffering",
            "I have been waiting for a long time and losing patience",
            "Someone is speaking ill of me and spreading slander",
        ],
    )

    user_input = st.text_input(
        "What is on your heart?",
        value="" if preset.startswith("Select") else preset,
    )

    if user_input and not user_input.startswith("Select"):
        input_lower = user_input.lower()

        # Multi-keyword Intent Detection
        if any(
            w in input_lower
            for w in [
                "job",
                "work",
                "career",
                "employment",
                "unemployed",
                "salary",
                "promotion",
                "demotion",
                "business",
                "money",
                "finance",
            ]
        ):
            target_keywords = [
                "job",
                "employment",
                "career",
                "work",
                "service",
                "maintenance",
                "starve",
                "livelihood",
                "demotion",
            ]
            primary_cat = "CAT-FINANCE"

        elif any(
            w in input_lower
            for w in [
                "sickness",
                "health",
                "disease",
                "pain",
                "illness",
                "fever",
                "cured",
                "tuberculosis",
                "doctor",
                "hospital",
            ]
        ):
            target_keywords = [
                "health",
                "cure",
                "disease",
                "illness",
                "doctor",
                "medicine",
                "healing",
                "tuberculosis",
            ]
            primary_cat = "CAT-HEALTH"

        elif any(
            w in input_lower
            for w in [
                "patience",
                "waiting",
                "delay",
                "losing",
                "how long",
                "when will",
            ]
        ):
            target_keywords = [
                "Saburi",
                "patience",
                "endure",
                "wait",
                "time",
                "Shraddha",
            ]
            primary_cat = "CAT-SPIRIT"

        elif any(
            w in input_lower
            for w in [
                "slander",
                "speaking ill",
                "gossip",
                "enemy",
                "critic",
                "quarrel",
            ]
        ):
            target_keywords = ["slander", "critic", "quarrel", "enemy", "talk"]
            primary_cat = "CAT-RELATION"

        else:
            target_keywords = [
                "protect",
                "fear",
                "anxiety",
                "worry",
                "surrender",
                "shelter",
            ]
            primary_cat = "CAT-PROTECT"

        guidance_results = fetch_guidance_records(
            target_keywords, primary_cat=primary_cat
        )

        st.markdown("---")
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
