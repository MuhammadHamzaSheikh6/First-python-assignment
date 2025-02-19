import streamlit as st
import pandas as pd
import os
from io import BytesIO
import openpyxl  # Ensure this is imported


# Set up our app - THIS MUST BE FIRST
st.set_page_config(page_title="Data Insights Toolkit", layout="wide")


# Function to load the CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")  # Load the CSS file



st.title("Data Insights Toolkit - Streamlining Your Data Workflow")
st.write(
    """
    Unlock the potential of your data with our intuitive toolkit! Seamlessly convert file formats,
    clean your data with powerful one-click options, visualize key trends, and extract actionable insights.
    Upload your data and let's get started!
    """
)

# File Uploader
with st.container():
    uploaded_files = st.file_uploader(
        "📂 Upload your CSV or Excel files:",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read File
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine='openpyxl')  # 🛠 Fix for Excel
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
            continue

        # Display File Details
        with st.container():
            st.write(f"📄 **File Name:** `{file.name}` | 📏 **Size:** `{file.size / 1024:.2f} KB`")

        # Show 5 rows of our df
        with st.container():
            st.subheader("📊 Data Preview")
            st.write("Get a quick glimpse of your data:")
            st.dataframe(df.head())

        # Option for Data cleaning
        with st.container():
            st.subheader("✨ Data Cleaning & Preparation")
            st.write(
                """
                Enhance data quality with our cleaning tools. Remove redundancies and handle missing values
                to ensure accurate analysis and modeling.
                """
            )
            if st.checkbox(f"🧹 Enable Data Cleaning for {file.name}"):
                col1, col2 = st.columns(2)

                with col1:
                    with st.container(): # Wrap the button
                        if st.button(f"Eliminate Duplicate Rows"):
                            initial_rows = len(df)
                            df.drop_duplicates(inplace=True)
                            final_rows = len(df)
                            duplicates_removed = initial_rows - final_rows
                            st.success(f"✅ **{duplicates_removed} duplicate rows successfully removed!**")

                with col2:
                    with st.container():  # Wrap the button
                        if st.button(f"Impute Missing Values"):
                            numeric_cols = df.select_dtypes(include=['number']).columns
                            missing_before = df[numeric_cols].isnull().sum().sum()  # Count missing values before
                            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                            missing_after = df[numeric_cols].isnull().sum().sum()  # Count after
                            filled_values = missing_before - missing_after
                            st.success(f"✅ **Successfully imputed {filled_values} missing values with the mean.**")

        # Choose Specific Columns to Keep or Convert
        with st.container():
            st.subheader("✂️ Column Selection")
            st.write("Select the relevant columns for your analysis:")
            columns = st.multiselect(f"Select columns for {file.name}", df.columns, default=df.columns)
            df = df[columns]

        # Create Some Visualizations
        with st.container():
            st.subheader("📈 Data Visualization")
            st.write("Visualize your data to identify patterns and trends:")
            if st.checkbox(f"Show a basic bar chart"):
                try:
                    st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])
                except Exception as e:
                    st.error(
                        f"❌ Could not create chart. Ensure there are at least two numerical columns in the selected data. Error: {e}")

        # Convert the File --> CSV to Excel
        with st.container():
            st.subheader("🔄 File Conversion")
            st.write("Transform your data into your preferred file format:")
            conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

            if st.button(f"Convert and Download"):
                buffer = BytesIO()
                try:
                    if conversion_type == "CSV":
                        df.to_csv(buffer, index=False)
                        file_name = file.name.replace(file_ext, ".csv")
                        mime_type = "text/csv"
                    elif conversion_type == "Excel":
                        df.to_excel(buffer, index=False, engine='openpyxl')  # ✅ Fixed
                        file_name = file.name.replace(file_ext, ".xlsx")
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    buffer.seek(0)

                    # Download the File
                    st.download_button(
                        label=f"⬇️ Download {file_name}",
                        data=buffer,
                        file_name=file_name,
                        mime=mime_type
                    )
                except Exception as e:
                    st.error(
                        f"❌ Error during file conversion: {e}.  Please ensure the 'openpyxl' library is installed if converting to Excel. You can install it with: `pip install openpyxl`")

    st.success("✅ Data processing complete!")