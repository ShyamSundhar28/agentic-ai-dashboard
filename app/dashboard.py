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
    
    # Initialize DuckDB and load
    conn = duckdb.connect(':memory:')
    table_name = "uploaded_data"
    load_csv_to_duckdb(temp_path, table_name, conn)
    
    # Dashboard Layout
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Data Preview (First 20 rows)")
        preview_df = get_table_preview(conn, table_name, limit=20)
        st.dataframe(preview_df, use_container_width=True)
        
    with col2:
        st.subheader("🔍 Schema Inference")
        profile = profile_data(df_raw)
        st.write(f"**Rows:** {profile['num_rows']}")
        st.write(f"**Columns:** {profile['num_columns']}")
        
        st.write("**Inferred Types:**")
        st.json(profile['inferred_types'])
        
    # Cleanup (optional, keep for session if needed)
    # os.remove(temp_path)
else:
    st.info("Waiting for data upload...")
