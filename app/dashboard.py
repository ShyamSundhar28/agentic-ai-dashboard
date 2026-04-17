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
    
    # Initialize DuckDB Store and load
    from tools.duckdb_store import DuckDBStore
    store = DuckDBStore()
    table_name = "uploaded_data"
    store.create_table_from_df(df_raw, table_name)
    
    # Dashboard Layout
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Data Preview (First 20 rows)")
        preview_df = store.query(f"SELECT * FROM {table_name} LIMIT 20")
        st.dataframe(preview_df, use_container_width=True)
        
    with col2:
        st.subheader("🔍 Schema Inference & Stats")
        stats = store.get_table_stats(table_name)
        profile = profile_data(df_raw)
        
        st.write(f"**Rows:** {stats['row_count']}")
        st.write(f"**Columns:** {stats['col_count']}")
        
        st.write("**Inferred Types:**")
        st.json(profile['inferred_types'])
        
    # Cleanup (optional, keep for session if needed)
    # os.remove(temp_path)
else:
    st.info("Waiting for data upload...")
