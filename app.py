import streamlit as st
import sqlite3

# Page Setup
st.set_page_config(
    page_title="Shirdi Sai Canonical Knowledge Base & Guidance",
    page_icon="🙏",
    layout="wide"
)

# Custom Styling
st.markdown("""
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
    .story-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

DB_PATH = "sai_knowledge_base.db"

def fetch_guidance_records(user_worry):
    search_term = f"%{user_worry.strip()}%"
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Search for matching records where Baba gives a direct quote
        sql = """
            SELECT record_id, source_title, primary_category, sub_category, 
                   raw_text_excerpt, baba_direct_quote, canonical_summary, cross_references
            FROM records
            WHERE (raw_text_excerpt LIKE ? OR canonical_summary LIKE ? OR tags LIKE ? OR sub_category LIKE ?)
              AND baba_direct_quote IS NOT NULL 
              AND baba_direct_quote != ''
            LIMIT 5
        """
        cursor.execute(sql, (search_term, search_term, search_term, search_term))
        results = cursor.fetchall()
        
        # Fallback to general comfort quotes if no specific keyword match is found
        if not results:
            fallback_sql = """
                SELECT record_id, source_title, primary_category, sub_category, 
                       raw_text_excerpt, baba_direct_quote, canonical_summary, cross_references
                FROM records
                WHERE primary_category IN ('CAT-PROTECT', 'CAT-SPIRIT')
                  AND baba_direct_quote IS NOT NULL 
                  AND baba_direct_quote != ''
                ORDER BY RANDOM()
                LIMIT 3
            """
            cursor.execute(fallback_sql)
            results = cursor.fetchall()
            
    return results

def search_knowledge_base(query_term):
    search_pattern = f"%{query_term}%"
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT record_id, source_title, sub_category, raw_text_excerpt, baba_direct_quote, canonical_summary
            FROM records
            WHERE raw_text_excerpt LIKE ? OR canonical_summary LIKE ? OR tags LIKE ?
            LIMIT 10
        """, (search_pattern, search_pattern, search_pattern))
        results = cursor.fetchall()
    return results

# Navigation
st.title("🙏 Shirdi Sai Knowledge & Guidance Portal")
tab1, tab2 = st.tabs(["🙏 Seek Baba's Guidance", "🔍 Search Literature"])

# -------------------------------------------------------------------
# TAB 1: SEEK BABA'S GUIDANCE
# -------------------------------------------------------------------
with tab1:
    st.markdown("### Place Your Worries at Sainath's Feet")
    st.caption("Describe what you are going through (e.g., suffering, waiting for a long time, disease, financial loss, anxiety).")

    preset = st.selectbox(
        "Or choose a common situation:",
        [
            "Select or type your own below...",
            "I am suffering a lot in life, when will this pain end?",
            "I feel anxious and uncertain about my future and job",
            "I am dealing with sickness and physical suffering",
            "I have been waiting for a long time and losing patience",
            "Someone is speaking ill of me and spreading slander"
        ]
    )

    user_input = st.text_input("What is on your heart?", value="" if preset.startswith("Select") else preset)

    if user_input and not user_input.startswith("Select"):
        input_lower = user_input.lower()
        if "sickness" in input_lower or "health" in input_lower or "disease" in input_lower:
            keyword = "health"
        elif "anxious" in input_lower or "job" in input_lower or "future" in input_lower:
            keyword = "anxiety"
        elif "patience" in input_lower or "waiting" in input_lower or "losing" in input_lower:
            keyword = "Saburi"
        elif "slander" in input_lower or "speaking ill" in input_lower:
            keyword = "slander"
        else:
            keyword = "suffering"

        guidance_results = fetch_guidance_records(keyword)

        st.markdown("---")
        st.subheader("🕊️ Sainath's Assurance & Direct Words")

        for row in guidance_results:
            rec_id, source, cat, sub_cat, excerpt, quote, summary, cross_refs = row
            
            st.markdown(f"""
                <div class="guidance-box">
                    <div class="quote-text">"{quote}"</div>
                    <p style="margin-top: 10px; color: #555;">— <b>Sai Baba</b> in <i>{source}</i> [{rec_id}]</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"📖 Read How Baba Guided Devotees in This Situation ({sub_cat})", expanded=False):
                st.markdown(f"**Canonical Summary:** {summary}")
                st.markdown(f"**Historical Context:** *\"{excerpt}\"*")
                if cross_refs:
                    st.caption(f"🔗 Related Canonical Passages: {cross_refs}")

# -------------------------------------------------------------------
# TAB 2: REGULAR SEARCH
# -------------------------------------------------------------------
with tab2:
    st.markdown("### Search 230 Canonically Validated Records")
    query_term = st.text_input("Search keywords:", placeholder="e.g., Kakasaheb Dixit, Udi, Cholera, Dakshina")
    
    if query_term:
        res = search_knowledge_base(query_term)
        for r in res:
            st.markdown(f"**[{r[0]}] {r[1]} — {r[2]}**")
            st.write(r[5])
            if r[4]:
                st.info(f"\"{r[4]}\"")
            st.markdown("---")
