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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sai_knowledge_base.db")


# =====================================================================
# 2. DATABASE HELPER FUNCTIONS
# =====================================================================
def get_prashnavali_dual_data(number_1_to_720):
    """Fetches both traditional 720 Prashnavali answer and canonical literature record."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Fetch Traditional Answer from prashnavali_720
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

    # 2. Fetch Mapped Canonical Literature Record (1 to 230)
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


def fetch_guidance_records(keywords, primary_cat=None):
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

        # 1. Traditional Prashnavali Answer Box
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

        # 2. Matching Canonical Backing Record
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
# TAB 2: SEEK GUIDANCE BY QUERY
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
            "I feel fear, danger, and anxiety about the future",
        ],
    )

    user_input = st.text_input(
        "What is on your heart?",
        value="" if preset.startswith("Select") else preset,
    )

    if user_input and not user_input.startswith("Select"):
        input_lower = user_input.lower()

        if any(
            w in input_lower
            for w in [
                "job",
                "employment",
                "unemployed",
                "interview",
                "salary",
                "promotion",
                "demotion",
                "get job",
                "career",
                "appointment",
            ]
        ):
            target_keywords = [
                "job",
                "employment",
                "service",
                "appointment",
                "post",
                "work",
                "livelihood",
                "demotion",
            ]
            primary_cat = "CAT-FINANCE"

        elif any(
            w in input_lower
            for w in [
                "business",
                "money",
                "finance",
                "debt",
                "trade",
                "loss",
                "poverty",
                "penniless",
                "rich",
                "speculation",
            ]
        ):
            target_keywords = [
                "trade",
                "business",
                "earnings",
                "debt",
                "money",
                "finance",
                "wealth",
                "speculation",
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
                "operation",
                "medicine",
                "plague",
                "cholera",
                "cancer",
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
                "fever",
                "plague",
                "Udi",
            ]
            primary_cat = "CAT-HEALTH"

        elif any(
            w in input_lower
            for w in [
                "marriage",
                "wedding",
                "child",
                "children",
                "baby",
                "son",
                "daughter",
                "husband",
                "wife",
                "family",
                "barren",
                "pregnant",
            ]
        ):
            target_keywords = [
                "marriage",
                "child",
                "issue",
                "pregnancy",
                "son",
                "family",
                "lineage",
                "blessing",
            ]
            primary_cat = "CAT-RELATION"

        elif any(
            w in input_lower
            for w in [
                "court",
                "legal",
                "police",
                "case",
                "magistrate",
                "summons",
                "lawyer",
                "inquiry",
                "jail",
            ]
        ):
            target_keywords = [
                "court",
                "magistrate",
                "summons",
                "legal",
                "inquiry",
                "official",
                "lawyer",
                "case",
            ]
            primary_cat = "CAT-PROTECT"

        elif any(
            w in input_lower
            for w in [
                "slander",
                "speaking ill",
                "gossip",
                "enemy",
                "critic",
                "quarrel",
                "insult",
                "jealousy",
            ]
        ):
            target_keywords = [
                "slander",
                "critic",
                "quarrel",
                "enemy",
                "talk",
                "tongue",
                "insult",
            ]
            primary_cat = "CAT-RELATION"

        elif any(
            w in input_lower
            for w in [
                "fear",
                "scared",
                "danger",
                "travel",
                "accident",
                "snake",
                "scorpion",
                "evil",
                "protection",
            ]
        ):
            target_keywords = [
                "protect",
                "fear",
                "danger",
                "shelter",
                "snake",
                "scorpion",
                "travel",
                "storm",
            ]
            primary_cat = "CAT-PROTECT"

        elif any(
            w in input_lower
            for w in [
                "patience",
                "waiting",
                "delay",
                "losing",
                "how long",
                "when will",
                "future",
                "destiny",
            ]
        ):
            target_keywords = [
                "Saburi",
                "patience",
                "endure",
                "wait",
                "time",
                "Shraddha",
                "destiny",
            ]
            primary_cat = "CAT-SPIRIT"

        else:
            target_keywords = [
                "protect",
                "fear",
                "anxiety",
                "worry",
                "surrender",
                "shelter",
                "karma",
                "cleansing",
            ]
            primary_cat = "CAT-PROTECT"

        guidance_results = fetch_guidance_records(
            target_keywords, primary_cat=primary_cat
        )

        st.markdown("---")

        if "when" in input_lower or "how long" in input_lower:
            st.info(
                "⏳ **Sainath's Message on Divine Timing (*Saburi*):** *'Every"
                " event matures in its appointed time. Have firm faith"
                " (Shraddha) and patient endurance (Saburi). What is destined"
                " for you will never pass you by.'*"
            )

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