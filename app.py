import streamlit as st
import sqlite3
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Shirdi Sai Canonical Knowledge Base",
    page_icon="🙏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .stApp { max-width: 1200px; margin: 0 auto; }
    .quote-box {
        background-color: #f0f7ff;
        border-left: 4px solid #1E88E5;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
        font-style: italic;
    }
    .ref-badge {
        background-color: #e0e0e0;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Database Connection with Caching
@st.cache_resource
def get_db_connection():
    return sqlite3.connect("sai_knowledge_base.db", check_same_thread=False)

def search_records(query_term, category, source_filter):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    conditions = []
    params = []

    if category != "All Categories":
        conditions.append("primary_category = ?")
        params.append(category)

    if source_filter != "All Sources":
        conditions.append("source_title LIKE ?")
        params.append(f"%{source_filter}%")

    if query_term.strip():
        search_pattern = f"%{query_term.strip()}%"
        conditions.append("(raw_text_excerpt LIKE ? OR canonical_summary LIKE ? OR tags LIKE ? OR historical_figures LIKE ?)")
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    
    sql = f"""
        SELECT record_id, source_title, primary_category, sub_category, 
               raw_text_excerpt, baba_direct_quote, canonical_summary, 
               cross_references, tags, historical_figures
        FROM records
        {where_clause}
        ORDER BY record_id ASC
        LIMIT 50
    """
    
    cursor.execute(sql, params)
    return cursor.fetchall()

# Header Section
st.title("🙏 Shirdi Sai Canonical Knowledge Base")
st.caption("Search across 230 validated records from Sri Sai Satcharita, Devotees' Experiences, Charters & Sayings, and Khaparde's Shirdi Diary.")

# Sidebar Filters
st.sidebar.header("🔍 Search & Filter")

selected_category = st.sidebar.selectbox(
    "Primary Category",
    ["All Categories", "CAT-PROTECT", "CAT-SPIRIT", "CAT-RELATION", "CAT-FINANCE", "CAT-HEALTH"]
)

selected_source = st.sidebar.selectbox(
    "Source Literature",
    ["All Sources", "Sri Sai Satcharita", "Devotees' Experiences", "Charters and Sayings", "Shirdi Diary"]
)

search_input = st.text_input(
    "Enter a keyword, name, or topic:",
    placeholder="e.g., Bhimaji Patil, Udi, Shraddha and Saburi, Snakebite..."
)

# Search Execution
results = search_records(search_input, selected_category, selected_source)

# Results Display
st.markdown("---")
st.subheader(f"Results ({len(results)} matches found)")

if not results:
    st.warning("No canonical records matched your search parameters. Try broadening your keywords.")
else:
    for row in results:
        rec_id, source, cat, sub_cat, excerpt, quote, summary, cross_refs, tags, figures = row
        
        with st.expander(f"[{rec_id}] {source} — {sub_cat}", expanded=False):
            st.markdown(f"**Category:** `{cat}` | **Figures:** `{figures or 'N/A'}`")
            st.markdown(f"**Canonical Summary:** {summary}")
            st.markdown(f"**Excerpt:** \"{excerpt}\"")
            
            if quote and quote.strip():
                st.markdown(f'<div class="quote-box"><b>Baba\'s Direct Quote:</b> "{quote}"</div>', unsafe_allow_html=True)
                
            col1, col2 = st.columns(2)
            with col1:
                if cross_refs and cross_refs.strip():
                    st.caption(f"🔗 **Cross-References:** {cross_refs}")
            with col2:
                if tags and tags.strip():
                    st.caption(f"🏷️ **Tags:** {tags}")