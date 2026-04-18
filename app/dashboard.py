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
    uploaded_file = st.file_uploader("Upload your data (CSV or Excel)", type=["csv", "xlsx", "xls"], help="Upload a business dataset to begin.")

    if uploaded_file:
        # Create temp path for ingestion
        temp_dir = "artifacts/temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{run_ctx.run_id}_{uploaded_file.name}")

        try:
            # Save the file
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Read based on file extension
            if uploaded_file.name.endswith('.csv'):
                df_raw = pd.read_csv(temp_path)
            else:
                df_raw = pd.read_excel(temp_path)
            
            # Check if file is empty
            if df_raw.empty:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                st.warning("⚠️ The uploaded file contains no data rows. Please upload a valid business dataset.")
                return
            
            # --- Aggressive Data Cleaning & Preprocessing ---
            # 1. Identify and Drop columns that are completely empty
            original_cols = list(df_raw.columns)
            df_raw.dropna(axis=1, how='all', inplace=True)
            remaining_cols = list(df_raw.columns)
            dropped_cols = [c for c in original_cols if c not in remaining_cols]
            
            # 2. Drop rows that are completely empty
            df_raw.dropna(axis=0, how='all', inplace=True)

            # 3. Drop unnamed columns that have no actual data rows
            cols_to_drop = []
            for col in df_raw.columns:
                if "Unnamed" in str(col):
                    is_null = df_raw[col].isnull()
                    if (hasattr(is_null, "all") and is_null.all() if not isinstance(is_null, pd.DataFrame) else is_null.all().all()):
                        cols_to_drop.append(col)
            
            if cols_to_drop:
                df_raw.drop(columns=cols_to_drop, inplace=True)
                remaining_cols = list(df_raw.columns)

            # 4. Clean up remaining column names dynamically
            new_cols = []
            for i, col in enumerate(df_raw.columns):
                cleaned = clean_column_name(str(col))
                if 'unnamed' in cleaned or not cleaned:
                    cleaned = f"col_{i+1}"
                elif cleaned.isdigit():
                    cleaned = f"n_header_{cleaned}"
                new_cols.append(cleaned)
            
            df_raw.columns = new_cols
            
            # Update store
            store.create_table_from_df(df_raw, run_ctx.table_name)
            
            # Profile data
            profile = profile_data(df_raw)
            run_ctx.schema_info = profile['inferred_types']
            writer.save_json(run_ctx.run_id, "profile.json", profile)

            st.success(f"Successfully loaded {len(df_raw)} rows and {len(remaining_cols)} active columns.")
            if dropped_cols:
                st.info(f"🧹 Automatically removed {len(dropped_cols)} empty columns: {', '.join(dropped_cols[:3])}{'...' if len(dropped_cols) > 3 else ''}")

            # --- Data Preparation Section ---
            if not run_ctx.is_schema_finalized:
                st.markdown("### 🛠️ Finalize Column Names")
                st.info("The columns below have been identified from your data. Please verify or rename them before starting the analysis.")
                
                col_btn1, col_btn2 = st.columns([1, 4])
                with col_btn1:
                    if st.button("✨ AI Suggest Names"):
                        with st.spinner("Analyzing data samples..."):
                            try:
                                from core.llm_service import LLMService
                                llm = LLMService()
                                suggestions = {}
                                for col in df_raw.columns:
                                    col_str = str(col)
                                    # Samples for better inference
                                    samples = df_raw[col].dropna().astype(str).head(5).tolist()
                                    inferred = llm.infer_column_name(col_str, samples)
                                    suggestions[col_str] = inferred
                                run_ctx.suggested_column_renames = suggestions
                                st.rerun()
                            except Exception as e:
                                st.error(f"AI suggestion failed: {e}")

                # Display interactive renaming form
                with st.form("schema_confirmation_form"):
                    st.write("#### Column Mapping & Selection")
                    st.info("Select the columns you want to include in the analysis and provide final names.")
                    
                    column_settings = {}
                    grid_cols = st.columns(3)
                    for i, old_name in enumerate(df_raw.columns):
                        with grid_cols[i % 3]:
                            with st.container(border=True):
                                # Selection Toggle
                                is_selected = st.checkbox("Include in Analysis", value=True, key=f"select_{old_name}_{run_ctx.run_id}")
                                
                                # Renaming Input (only if selected)
                                default_val = run_ctx.suggested_column_renames.get(old_name, old_name)
                                new_name = st.text_input(
                                    f"Rename: {old_name}", 
                                    value=default_val, 
                                    key=f"rename_{old_name}_{run_ctx.run_id}",
                                    disabled=not is_selected
                                )
                                column_settings[old_name] = {"selected": is_selected, "name": new_name}
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    submitted = st.form_submit_button("📢 Finalize Selection & Start Analysis", use_container_width=True)
                    
                    if submitted:
                        # 1. Filter only selected columns
                        selected_old_names = [old for old, settings in column_settings.items() if settings["selected"]]
                        
                        if not selected_old_names:
                            st.error("Please select at least one column for analysis.")
                        else:
                            # 2. Extract and clean names for selected columns
                            clean_renames = {}
                            for old in selected_old_names:
                                new_raw = column_settings[old]["name"]
                                clean_renames[old] = new_raw.strip() if new_raw.strip() else old
                            
                            # 3. Handle duplicates in final names
                            final_names = []
                            seen = {}
                            for old_name, new_name in clean_renames.items():
                                base = clean_column_name(new_name)
                                if base in seen:
                                    seen[base] += 1
                                    final_names.append(f"{base}_{seen[base]}")
                                else:
                                    seen[base] = 0
                                    final_names.append(base)
                            
                            # 4. Create final filtered dataframe
                            df_final = df_raw[selected_old_names].copy()
                            df_final.columns = final_names
                            
                            # 5. Re-sync everything
                            store.create_table_from_df(df_final, run_ctx.table_name)
                            new_profile = profile_data(df_final)
                            run_ctx.schema_info = new_profile['inferred_types']
                            run_ctx.is_schema_finalized = True
                            st.success(f"✅ Schema Locked! {len(selected_old_names)} columns selected. Unlocking analytics...")
                            st.rerun()

            # --- Analytics Section (Only shown after finalization) ---
            if run_ctx.is_schema_finalized:
                # Re-fetch the cleaned dataframe for downstream agents
                df_clean = store.conn.execute(f"SELECT * FROM {run_ctx.table_name}").df()
                
                st.markdown("---")
                st.subheader("📊 Analytics Overview")
                
                # Show Preview of the Finalized Data (Renamed and Filtered)
                with st.expander("👀 View Finalized Data Preview", expanded=True):
                    st.write("This is how your data looks after selection and renaming:")
                    st.dataframe(df_clean.head(10), use_container_width=True)
                    st.caption(f"Showing first 10 rows of {len(df_clean)} total records across {len(df_clean.columns)} selected columns.")

                st.subheader("💡 Intelligent Insights")
                query = st.text_input(
                    "Ask a question about your data or a specific category",
                    placeholder="e.g., 'What are the main drivers of spend?' or 'Total amount for Walden food bank in Jan'",
                    key="query_input"
                )

                if query:
                    with st.spinner("🧠 Agents are analyzing..."):
                        try:
                            supervisor = SupervisorAgent()
                            response: SupervisorResponse = supervisor.run_pipeline(
                                query, 
                                df_clean, 
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
                                        render_chart(df_clean, viz_items[i].chart_type, viz_items[i].config)
                                    if i+1 < len(viz_items):
                                        with cols[1]:
                                            st.write(f"**{viz_items[i+1].title}**")
                                            render_chart(df_clean, viz_items[i+1].chart_type, viz_items[i+1].config)

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
                col1.write("**Finalized Schema**")
                col1.json(run_ctx.schema_info)
                col2.write("**Missing Values**")
                col2.json(profile['missing_values'])
                
            with tabs[2]:
                suggested_charts = ChartSelector.recommend_charts(df_clean, run_ctx.schema_info)
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
