import streamlit as st
import pandas as pd
import os
from io import BytesIO
import openpyxl  # Ensure this is imported
import plotly.express as px  # For improved visualizations
from sklearn.preprocessing import MinMaxScaler, StandardScaler  # For Scaling
import sweetviz as sv  # For EDA Report
import datetime  # For the footer

# Set up our app - THIS MUST BE FIRST
st.set_page_config(
    page_title="Data Insights Toolkit", layout="wide"
)  # Maximize screen use

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


# === File Uploader ===
with st.container():
    uploaded_files = st.file_uploader(
        "📂 Upload your CSV or Excel files:", type=["csv", "xlsx"], accept_multiple_files=True
    )


if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # === Read File ===
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine="openpyxl")  # 🛠 Fix for Excel
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
            continue

        # === Display File Details ===
        with st.container():
            st.write(
                f"📄 **File Name:** `{file.name}` | 📏 **Size:** `{file.size / 1024:.2f} KB` | 🔢 **Rows:** `{df.shape[0]}` | 🔢 **Columns:** `{df.shape[1]}`"
            )

        # === Show 5 rows of our df ===
        with st.container():
            st.subheader("📊 Data Preview")
            st.write("Get a quick glimpse of your data:")
            st.dataframe(df.head())

        # === Data Cleaning Options ===
        with st.container():
            st.subheader("✨ Data Cleaning & Preparation")
            st.write(
                """
                Enhance data quality with our cleaning tools. Remove redundancies, handle missing values,
                and standardize data for accurate analysis and modeling.
                """
            )
            if st.checkbox(f"Enable Data Cleaning for {file.name}"):
                col1, col2, col3 = st.columns(3)  # Added a column for Scaling

                with col1:
                    with st.container():  # Wrap the button
                        if st.button(f"Eliminate Duplicate Rows"):
                            initial_rows = len(df)
                            df.drop_duplicates(inplace=True)
                            final_rows = len(df)
                            duplicates_removed = initial_rows - final_rows
                            st.success(
                                f"✅ **{duplicates_removed} duplicate rows successfully removed!**"
                            )

                with col2:
                    with st.container():  # Wrap the button
                        if st.button(f"Impute Missing Values"):
                            numeric_cols = df.select_dtypes(include=["number"]).columns
                            missing_before = df[numeric_cols].isnull().sum().sum()  # Count missing values before
                            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                            missing_after = df[numeric_cols].isnull().sum().sum()  # Count after
                            filled_values = missing_before - missing_after
                            st.success(
                                f"✅ **Successfully imputed {filled_values} missing values with the mean.**"
                            )

                with col3:
                    with st.container():
                        if st.button("Scale Numeric Data"):
                            scaler_type = st.selectbox(
                                "Choose Scaling Method",
                                ["MinMaxScaler", "StandardScaler"],
                                key=f"scaler_{file.name}",  # Unique key for each file
                            )
                            numeric_cols = df.select_dtypes(include=["number"]).columns

                            if numeric_cols.empty:
                                st.warning("No numeric columns to scale.")
                            else:
                                try:
                                    if scaler_type == "MinMaxScaler":
                                        scaler = MinMaxScaler()
                                    else:
                                        scaler = StandardScaler()

                                    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
                                    st.success(
                                        f"✅ **Successfully scaled numeric columns using {scaler_type}!**"
                                    )
                                except Exception as e:
                                    st.error(f"❌ Error during scaling: {e}")

        # === Column Selection ===
        with st.container():
            st.subheader("✂️ Column Selection")
            st.write("Select the relevant columns for your analysis:")
            columns = st.multiselect(f"Select columns for {file.name}", df.columns, default=df.columns)
            df = df[columns]

        # === Data Visualization Options ===
        with st.container():
            st.subheader("📈 Data Visualization")
            st.write("Visualize your data to identify patterns and trends:")

            visualization_type = st.selectbox(
                "Choose Visualization Type",
                ["Bar Chart", "Scatter Plot", "Line Chart", "Histogram"],
                key=f"viz_type_{file.name}",
            )

            try:
                numeric_cols = df.select_dtypes(include=["number"]).columns
                if len(numeric_cols) < 2 and visualization_type in ["Scatter Plot", "Line Chart"]:
                    st.warning(
                        "Scatter Plot and Line Chart require at least two numeric columns. Select more columns or choose a different visualization."
                    )
                else:
                    if visualization_type == "Bar Chart":
                        if len(numeric_cols) >= 2:
                            x_axis = st.selectbox("X-axis", numeric_cols, key=f"bar_x_{file.name}")
                            y_axis = st.selectbox("Y-axis", numeric_cols, key=f"bar_y_{file.name}")
                            fig = px.bar(df, x=x_axis, y=y_axis, title=f"Bar Chart of {file.name}")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Bar Chart requires at least two numeric columns.")
                    elif visualization_type == "Scatter Plot":
                        x_axis = st.selectbox("X-axis", numeric_cols, key=f"scatter_x_{file.name}")
                        y_axis = st.selectbox("Y-axis", numeric_cols, key=f"scatter_y_{file.name}")
                        fig = px.scatter(df, x=x_axis, y=y_axis, title=f"Scatter Plot of {file.name}")
                        st.plotly_chart(fig, use_container_width=True)
                    elif visualization_type == "Line Chart":
                        x_axis = st.selectbox("X-axis", numeric_cols, key=f"line_x_{file.name}")
                        y_axis = st.selectbox("Y-axis", numeric_cols, key=f"line_y_{file.name}")
                        fig = px.line(df, x=x_axis, y=y_axis, title=f"Line Chart of {file.name}")
                        st.plotly_chart(fig, use_container_width=True)
                    elif visualization_type == "Histogram":
                        if numeric_cols.empty:
                            st.warning("Histogram requires at least one numeric column.")
                        else:
                            x_axis = st.selectbox("Column for Histogram", numeric_cols, key=f"hist_x_{file.name}")
                            fig = px.histogram(df, x=x_axis, title=f"Histogram of {file.name}")
                            st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"❌ Could not create chart. Error: {e}")

        # === Download EDA Report ===
        with st.container():
            st.subheader("🔍 Exploratory Data Analysis (EDA) Report")
            st.write("Generate an interactive EDA report to gain deeper insights into your data.")
            if st.button(f"Generate EDA Report"):
                try:
                    report = sv.analyze(df)  # Generate the Sweetviz report
                    report.show_html(f"{file.name}_report.html")  # Save as HTML

                    # Read the HTML content
                    with open(f"{file.name}_report.html", "r", encoding="utf-8") as f:
                        html_data = f.read()

                    st.components.v1.html(html_data, height=800, scrolling=True)  # Embed the HTML
                    os.remove(f"{file.name}_report.html")  # Clean up

                except Exception as e:
                    st.error(f"❌ Error generating EDA report: {e}")

        # === File Conversion ===
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
                        df.to_excel(buffer, index=False, engine="openpyxl")  # ✅ Fixed
                        file_name = file.name.replace(file_ext, ".xlsx")
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    buffer.seek(0)

                    # Download the File
                    st.download_button(
                        label=f"⬇️ Download {file_name}", data=buffer, file_name=file_name, mime=mime_type
                    )
                except Exception as e:
                    st.error(
                        f"❌ Error during file conversion: {e}.  Please ensure the 'openpyxl' library is installed if converting to Excel. You can install it with: `pip install openpyxl`"
                    )

    st.success("✅ Data processing complete!")

# Add information to the sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("About the Developer")
    st.image("./hamza.jpg", width=150)  # Replace with your image URL or local path
    st.markdown("**Muhammad Hamza**")
    st.markdown("Full-stack developer proficient in Next.js, Tailwind CSS, TypeScript, and Python.")  # Add your description here
    st.markdown("[GitHub](https://github.com/MuhammadHamzaSheikh6)")  # Replace with your GitHub username
    st.markdown("[LinkedIn](www.linkedin.com/in/muhammadhamzafed)")  # Replace with your LinkedIn profile  # Replace with your LinkedIn profile

# Add a footer to the main content area
st.markdown("---")  # Separator
current_year = datetime.datetime.now().year
st.markdown(f"© {current_year} Muhammad Hamza. All rights reserved.")