import streamlit as st
import pandas as pd
import duckdb
import os
from tools.data_loader import load_csv_to_duckdb, get_table_preview
from tools.schema_inference import clean_column_name, profile_data

st.set_page_config(page_title="Agentic AI Dashboard", layout="wide")

st.title("🤖 Agentic AI Dashboard")
st.write("Upload a CSV file to begin analysis.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Save temp file
    temp_path = f"artifacts/temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    
    # Load and Clean
    df_raw = pd.read_csv(temp_path)
    
    # Clean column names
    df_raw.columns = [clean_column_name(col) for col in df_raw.columns]
    
    # Refresh temp file with cleaned columns for DuckDB
    df_raw.to_csv(temp_path, index=False)
    
    # Initialize state and tools
    import uuid
    from tools.duckdb_store import DuckDBStore
    from tools.artifact_writer import ArtifactWriter
    from tools.chart_selector import ChartSelector
    import plotly.express as px
    
    if 'run_id' not in st.session_state or st.sidebar.button("New Analysis"):
        st.session_state.run_id = f"run_{uuid.uuid4().hex[:8]}"
        st.session_state.store = DuckDBStore()
    
    run_id = st.session_state.run_id
    store = st.session_state.store
    writer = ArtifactWriter()
    
    st.sidebar.info(f"Analysis ID: **{run_id}**")
    
    table_name = "uploaded_data"
    store.create_table_from_df(df_raw, table_name)
    
    # Phase 3: Profiling & Artifacts
    profile = profile_data(df_raw)
    writer.save_json(run_id, "profile.json", profile)
    
    # Phase 5 & 6: Agent Pipeline & Query
    from agents.supervisor import SupervisorAgent
    st.markdown("---")
    st.subheader("🤖 Ask your Data")
    user_query = st.text_input("Enter your question (e.g., 'Analyze trend and suggest recommendations')", placeholder="e.g. Please analyze this data and show some charts")
    
    if user_query:
        supervisor = SupervisorAgent()
        with st.spinner("Agents are working..."):
            response = supervisor.run_pipeline(user_query, df_raw, profile['inferred_types'], run_id)
            writer.save_json(run_id, "supervisor_response.json", response.model_dump())
            
            st.success(response.final_output)
            
            # Show results in dynamic sections
            if "analysis" in response.results:
                with st.expander("📝 Analysis Summary", expanded=True):
                    st.write(response.results["analysis"].summary)
            
            if "visualizations" in response.results:
                with st.expander("📈 Generated Visualizations", expanded=True):
                    for viz in response.results["visualizations"]:
                        st.write(f"#### {viz.title}")
                        # Simple dispatch based on VizAgent specs
                        if viz.chart_type == "histogram":
                            fig = px.histogram(df_raw, x=viz.config['column'])
                        elif viz.chart_type == "bar":
                            fig = px.bar(df_raw, x=viz.config['column'])
                        elif viz.chart_type == "line":
                            fig = px.line(df_raw, x=viz.config['x'], y=viz.config['y'])
                        st.plotly_chart(fig, use_container_width=True)
            
            if "root_cause" in response.results:
                with st.expander("🔍 Root Cause Analysis"):
                    rca = response.results["root_cause"]
                    st.write(f"**Primary Driver:** {rca.primary_driver}")
                    st.write(rca.details)
                    st.progress(rca.confidence, text=f"Confidence: {rca.confidence*100}%")

            if "recommendations" in response.results:
                with st.expander("💡 Recommendations"):
                    for rec in response.results["recommendations"]:
                        st.write(f"**- {rec.action}**")
                        st.write(f"  *{rec.rationale}*")

    # Original Tabs (static analysis)
    st.markdown("---")
    st.write("### 📎 Session Workspace")
    tabs = st.tabs(["预览 (Preview)", "分析 (Analysis)", "图表 (Charts)"])

    
    with tabs[0]:
        st.subheader("📊 Data Preview")
        preview_df = store.query(f"SELECT * FROM {table_name} LIMIT 20")
        st.dataframe(preview_df, use_container_width=True)
        
    with tabs[1]:
        st.subheader("🔍 Schema & Stats")
        stats = store.get_table_stats(table_name)
        st.write(f"**Rows:** {stats['row_count']} | **Columns:** {stats['col_count']}")
        
        col_type, col_miss = st.columns(2)
        col_type.write("**Column Types**")
        col_type.json(profile['inferred_types'])
        col_miss.write("**Missing Values**")
        col_miss.json(profile['missing_values'])

    with tabs[2]:
        st.subheader("📈 Automatic Visualizations")
        charts = ChartSelector.recommend_charts(df_raw, profile['inferred_types'])
        writer.save_json(run_id, "charts_metadata.json", {"charts": charts})
        
        for chart in charts:
            st.write(f"#### {chart['title']}")
            if chart['type'] == "histogram":
                fig = px.histogram(df_raw, x=chart['column'])
            elif chart['type'] == "bar":
                fig = px.bar(df_raw, x=chart['column'])
            elif chart['type'] == "line":
                fig = px.line(df_raw, x=chart['x'], y=chart['y'])
            st.plotly_chart(fig, use_container_width=True)

        
    # Cleanup (optional, keep for session if needed)
    # os.remove(temp_path)
else:
    st.info("Waiting for data upload...")
