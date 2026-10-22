import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

# Page configuration
st.set_page_config(page_title="Job Market Skills Tracker", layout="wide")

st.title("📊 Job Market Skills Tracker")
st.markdown("**Question:** What skills are most in demand in the current tech job market?")
st.caption("Data Source: Arbeitnow API · Extracted via Python Rule-Based NLP")

# Load data (cached for speed)
@st.cache_data
def load_data():
    with sqlite3.connect("jobs.db") as con:
        # Get top skills
        skills = pd.read_sql("""
            SELECT s.name, COUNT(DISTINCT ps.posting_id) as count
            FROM posting_skills ps
            JOIN skills s USING(skill_id)
            GROUP BY s.name
            ORDER BY count DESC
            LIMIT 15
        """, con)
        
        # Get seniority mix
        sen = pd.read_sql("""
            SELECT seniority, COUNT(*) as count
            FROM extractions
            GROUP BY seniority
            ORDER BY count DESC
        """, con)
        
        # Get total count
        total = con.execute("SELECT COUNT(*) FROM postings").fetchone()[0]
        
    return skills, sen, total

skills, sen, total = load_data()

# Top Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric("Total Job Postings Analyzed", f"{total:,}")
if not skills.empty:
    col2.metric("Top Skill", skills.iloc[0]['name'])
else:
    col2.metric("Top Skill", "N/A")

if not sen.empty:
    most_common_sen = sen.iloc[0]['seniority']
    col3.metric("Most Common Level", most_common_sen.capitalize())
else:
    col3.metric("Most Common Level", "N/A")

st.divider()

# Charts
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Top 15 Most In-Demand Skills")
    if not skills.empty:
        fig1 = px.bar(
            skills, x='count', y='name', orientation='h',
            labels={'count': 'Number of Postings', 'name': 'Skill'},
            color='count', color_continuous_scale='Blues'
        )
        fig1.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.write("No skill data found.")

with col_chart2:
    st.subheader("Job Postings by Seniority Level")
    if not sen.empty:
        fig2 = px.pie(
            sen, values='count', names='seniority', 
            hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.write("No seniority data found.")

# Data Table Section
st.subheader("Raw Skill Data")
if not skills.empty:
    st.dataframe(skills, use_container_width=True)