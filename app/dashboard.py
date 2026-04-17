import streamlit as st
import pandas as pd
import uuid
import os
import plotly.express as px
from typing import Dict, Any, Optional

# Core imports
from core.config import settings
from core.models import SupervisorResponse
from core.run_context import RunContext
from core.logging_utils import setup_logging, logger

# Tool imports
from tools.duckdb_store import DuckDBStore
from tools.artifact_writer import ArtifactWriter
from tools.chart_selector import ChartSelector
from tools.schema_inference import clean_column_name, profile_data
from tools.data_loader import get_table_preview
from tools.query_engine import QueryEngine

# Agent imports
from agents.supervisor import SupervisorAgent

# Initialize logging
setup_logging()

# Page config
st.set_page_config(
    page_title="Agentic AI Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session():
    """Initializes the session state variables."""
    if 'run_context' not in st.session_state:
        st.session_state.run_context = RunContext.create()
    if 'store' not in st.session_state:
        st.session_state.store = DuckDBStore()
    if 'writer' not in st.session_state:
        st.session_state.writer = ArtifactWriter(base_path=settings.artifacts_dir)
    if 'query_engine' not in st.session_state:
        st.session_state.query_engine = QueryEngine(st.session_state.store)

def render_chart(df: pd.DataFrame, chart_type: str, config: Dict[str, Any]):
    """Renders a plotly chart based on type and config."""
    try:
        if chart_type == "histogram":
            fig = px.histogram(df, x=config['column'], template="plotly_white")
        elif chart_type == "bar":
            fig = px.bar(df, x=config['column'], template="plotly_white")
        elif chart_type == "line":
            fig = px.line(df, x=config['x'], y=config['y'], template="plotly_white")
        elif chart_type == "scatter":
            fig = px.scatter(df, x=config['x'], y=config['y'], template="plotly_white")
        else:
            st.warning(f"Unsupported chart type: {chart_type}")
            return
        
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to render chart: {str(e)}")

def main():
    st.title("🤖 Agentic AI Dashboard")
    st.markdown("---")

    initialize_session()
    run_ctx = st.session_state.run_context
    store = st.session_state.store
    writer = st.session_state.writer
    query_engine = st.session_state.query_engine

    st.sidebar.title("Configuration")
    if st.sidebar.button("🔄 New Analysis"):
        st.session_state.run_context = RunContext.create()
        st.rerun()

    st.sidebar.info(f"**Run ID:** `{run_ctx.run_id}`")
    st.sidebar.markdown("---")

    # File Upload
    uploaded_file = st.file_uploader("Upload your data (CSV)", type=["csv"], help="Upload a business dataset to begin.")

    if uploaded_file:
        # Create temp path for ingestion
        temp_dir = "artifacts/temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{run_ctx.run_id}_{uploaded_file.name}")

        try:
            # Save and clean
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            df_raw = pd.read_csv(temp_path)
            
            # 1. Drop columns that are completely empty (null)
            df_raw.dropna(axis=1, how='all', inplace=True)
            
            # 2. Clean up column names dynamically
            new_cols = []
            for i, col in enumerate(df_raw.columns):
                cleaned = clean_column_name(str(col))
                # Fix pandas 'Unnamed' or empty columns
                if 'unnamed' in cleaned or not cleaned:
                    cleaned = f"column_{i+1}"
                # If a column name is just a number (e.g. no header row)
                elif cleaned.isdigit():
                    cleaned = f"numeric_header_{cleaned}"
                new_cols.append(cleaned)
            
            df_raw.columns = new_cols
            
            # Update store
            store.create_table_from_df(df_raw, run_ctx.table_name)
            
            # Profile data
            profile = profile_data(df_raw)
            run_ctx.schema_info = profile['inferred_types']
            writer.save_json(run_ctx.run_id, "profile.json", profile)

            st.success(f"Successfully loaded {len(df_raw)} rows.")

            # --- Agentic Query Section ---
            st.subheader("💡 Intelligent Insights")
            query = st.text_input(
                "Ask a question about your data",
                placeholder="e.g., 'What are the main drivers of spend?' or 'Show me the trend of active users'",
                key="query_input"
            )

            if query:
                with st.spinner("🧠 Agents are analyzing..."):
                    try:
                        supervisor = SupervisorAgent()
                        response: SupervisorResponse = supervisor.run_pipeline(
                            query, 
                            df_raw, 
                            run_ctx.schema_info, 
                            run_ctx.run_id
                        )
                        
                        # Save result
                        writer.save_json(run_ctx.run_id, "supervisor_response.json", response.model_dump())
                        
                        # Render results
                        st.markdown(f"### Result: {response.final_output}")
                        
                        # Visualizations from Agents
                        if "visualizations" in response.results:
                            st.write("#### 📊 Generated Visualizations")
                            viz_items = response.results["visualizations"]
                            for i in range(0, len(viz_items), 2):
                                cols = st.columns(2)
                                with cols[0]:
                                    st.write(f"**{viz_items[i].title}**")
                                    render_chart(df_raw, viz_items[i].chart_type, viz_items[i].config)
                                if i+1 < len(viz_items):
                                    with cols[1]:
                                        st.write(f"**{viz_items[i+1].title}**")
                                        render_chart(df_raw, viz_items[i+1].chart_type, viz_items[i+1].config)

                        # RCA Details
                        if "root_cause" in response.results:
                            with st.expander("🔍 Deep Dive: Root Cause Analysis", expanded=False):
                                rca = response.results["root_cause"]
                                st.write(f"**Primary Driver:** {rca.primary_driver}")
                                st.info(rca.details)
                                m1, m2 = st.columns(2)
                                m1.metric("Impact (Abs)", f"{rca.absolute_change:,.2f}")
                                m2.metric("Impact (%)", f"{rca.percent_change:+.2f}%")
                                if rca.contribution_table:
                                    st.write("**Contribution Breakdown:**")
                                    st.dataframe(pd.DataFrame(rca.contribution_table), use_container_width=True)

                        # Recommendations
                        if "recommendations" in response.results:
                            with st.expander("🚀 Recommendations", expanded=True):
                                for rec in response.results["recommendations"]:
                                    st.markdown(f"- **{rec.action}**: *{rec.rationale}*")

                    except Exception as e:
                        logger.error(f"Agent pipeline failed: {str(e)}")
                        st.error(f"Analysis failed: {str(e)}")

            # --- Data Workspace ---
            st.markdown("---")
            tabs = st.tabs(["📊 Data Browser", "🔍 Automated Profiling", "📈 Suggested Charts", "🗄️ SQL Analytics"])

            with tabs[0]:
                st.dataframe(get_table_preview(store.conn, run_ctx.table_name), use_container_width=True)

            with tabs[1]:
                col1, col2 = st.columns(2)
                col1.write("**Inferred Types**")
                col1.json(profile['inferred_types'])
                col2.write("**Missing Values**")
                col2.json(profile['missing_values'])
                
            with tabs[2]:
                suggested_charts = ChartSelector.recommend_charts(df_raw, run_ctx.schema_info)
                for chart in suggested_charts:
                    st.write(f"#### {chart['title']}")
                    render_chart(df_raw, chart['type'], chart)

            with tabs[3]:
                st.subheader("SQL Analytics Engine")
                st.info(f"You can query the dataset using the table name: **{run_ctx.table_name}**")
                
                query_modes = st.radio("Choose interaction mode", ["Manual SQL", "Predefined Queries", "NL-to-SQL"])
                
                if query_modes == "Manual SQL":
                    user_sql = st.text_area("Enter your SQL query (DuckDB dialect)", f"SELECT * FROM {run_ctx.table_name} LIMIT 10;", height=150)
                    if st.button("▶️ Run Query"):
                        with st.spinner("Executing query..."):
                            try:
                                result_df = query_engine.execute_query(user_sql)
                                st.dataframe(result_df, use_container_width=True)
                                
                                if len(result_df) > 0 and len(result_df.columns) >= 2:
                                    st.write("#### Result Visualization")
                                    # Fallback schema inference for the result
                                    res_profile = profile_data(result_df)
                                    res_charts = ChartSelector.recommend_charts(result_df, res_profile['inferred_types'])
                                    if res_charts:
                                        render_chart(result_df, res_charts[0]['type'], res_charts[0])
                                    else:
                                        st.info("No suitable chart found for these results.")
                                        
                            except Exception as e:
                                st.error(f"Error executing query: {str(e)}")
                                
                elif query_modes == "Predefined Queries":
                    st.write("Select a quick query to run:")
                    col1, col2, col3 = st.columns(3)
                    
                    predef_query = None
                    with col1:
                        if st.button("Total Records"):
                            predef_query = f"SELECT COUNT(*) as total_records FROM {run_ctx.table_name}"
                        if st.button("Top 10 Categories"):
                            # Requires knowing a categorical column, let's pick the first string one
                            cat_cols = [c for c, t in profile['inferred_types'].items() if t == 'string']
                            if cat_cols:
                                predef_query = f"SELECT \"{cat_cols[0]}\", COUNT(*) as count FROM {run_ctx.table_name} GROUP BY 1 ORDER BY count DESC LIMIT 10"
                            else:
                                st.warning("No categorical columns found.")
                    with col2:
                        if st.button("Highest Values"):
                            num_cols = [c for c, t in profile['inferred_types'].items() if t in ['integer', 'float']]
                            if num_cols:
                                predef_query = f"SELECT * FROM {run_ctx.table_name} ORDER BY \"{num_cols[0]}\" DESC LIMIT 10"
                            else:
                                st.warning("No numeric columns found.")
                        if st.button("Average by Group"):
                            cat_cols = [c for c, t in profile['inferred_types'].items() if t == 'string']
                            num_cols = [c for c, t in profile['inferred_types'].items() if t in ['integer', 'float']]
                            if cat_cols and num_cols:
                                predef_query = f"SELECT \"{cat_cols[0]}\", AVG(\"{num_cols[0]}\") as avg_value FROM {run_ctx.table_name} GROUP BY 1 ORDER BY 2 DESC LIMIT 10"
                    with col3:
                        if st.button("Duplicates Check"):
                            predef_query = f"SELECT *, COUNT(*) as duplicates FROM {run_ctx.table_name} GROUP BY ALL HAVING COUNT(*) > 1 LIMIT 100"
                        if st.button("Null Check"):
                            cols_str = ", ".join([f"SUM(CASE WHEN \"{c}\" IS NULL THEN 1 ELSE 0 END) as \"{c}_nulls\"" for c in df_raw.columns[:5]])
                            predef_query = f"SELECT {cols_str} FROM {run_ctx.table_name}"
                            
                    if predef_query:
                        st.code(predef_query, language="sql")
                        with st.spinner("Executing query..."):
                            try:
                                result_df = query_engine.execute_query(predef_query)
                                st.dataframe(result_df, use_container_width=True)
                            except Exception as e:
                                st.error(f"Error executing query: {str(e)}")
                                
                elif query_modes == "NL-to-SQL":
                    nl_query = st.text_input("Ask a question in plain English")
                    if st.button("🔮 Generate SQL & Run"):
                        with st.spinner("Generating and executing SQL..."):
                            # We'll use a mocked NL-to-SQL here for now, or link it to the Analyst agent later.
                            st.info("The Supervisor Agent will handle this if run from the Intelligent Insights section, but here is a simple placeholder.")
                            try:
                                # Mocking simple logic based on keywords
                                if "count" in nl_query.lower() or "how many" in nl_query.lower():
                                    sql = f"SELECT COUNT(*) FROM {run_ctx.table_name}"
                                else:
                                    sql = f"SELECT * FROM {run_ctx.table_name} LIMIT 5"
                                
                                st.code(sql, language="sql")
                                result_df = query_engine.execute_query(sql)
                                st.dataframe(result_df, use_container_width=True)
                            except Exception as e:
                                st.error(f"Error executing query: {str(e)}")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    else:
        st.info("Please upload a CSV file to begin analysis.")

if __name__ == "__main__":
    main()
