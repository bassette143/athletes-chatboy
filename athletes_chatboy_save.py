import pandas as pd
import streamlit as st
from PIL import Image
import os
from dotenv import load_dotenv
from datetime import date
import re

# Load environment variables
load_dotenv()

# Secure API and email credentials (not used in this script, but loaded for future use)
email_sender = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")

# CSV saving setup - use the absolute path!
csv_file = r'C:\Users\Grace\Downloads\athletes_data.csv'

def save_data(data):
    if os.path.exists(csv_file):
        df_existing = pd.read_csv(csv_file)
        df_new = pd.DataFrame([data])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_csv(csv_file, index=False)
    else:
        df = pd.DataFrame([data])
        df.to_csv(csv_file, index=False)

def load_data():
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)
    else:
        return pd.DataFrame()

# Set page config
st.set_page_config(page_title="Athletes ChatBoy", page_icon="🏈", layout="centered")

# Custom background color and logo
st.markdown("""
    <style>
    .stApp {
        background-color: orange;
    }
    </style>
""", unsafe_allow_html=True)

# Display the logo
logo_path = r"C:\Users\Grace\OneDrive\Documents\btw_logo.png"
try:
    logo = Image.open(logo_path)
    st.image(logo, use_container_width=True)
except FileNotFoundError:
    st.warning("Logo image not found. Please check the file path.")

st.title("Athletes ChatBoy 🧠")

# Athlete Information Entry Form in Sidebar
with st.sidebar:
    st.header("✍️ Enter New Athlete")
    with st.form("athlete_form"):
        name = st.text_input("Name")
        dob = st.date_input("Date of Birth", min_value=date(2000, 1, 1))
        age = st.number_input("Age", min_value=0)
        school = st.text_input("School")
        sport = st.text_input("Sport")
        position = st.text_input("Position")
        physical_date = st.date_input("Physical Date")
        physical_expiry = st.date_input("Physical Expiry Date")
        grad_year = st.number_input("Graduation Year", min_value=2000, max_value=2100)
        grade9_entry = st.date_input("9th Grade Entry Date")
        impact_test = st.date_input("Baseline IMPACT Test Date")
        home_phone = st.text_input("Home Phone")
        cell_phone = st.text_input("Cell Phone")
        email = st.text_input("Email")
        gpa = st.number_input("GPA", min_value=0.0, max_value=4.0, step=0.01)
        football_ins = st.text_input("Football Insurance Status")
        interscholastic_ins = st.text_input("Interscholastic Insurance Status")

        submitted = st.form_submit_button("Submit")

if submitted:
    data = {
        "Name": name,
        "Date of Birth": dob,
        "Age": age,
        "School": school,
        "Sport": sport,
        "Position": position,
        "Physical Date": physical_date,
        "Physical Expiry Date": physical_expiry,
        "Graduation Year": grad_year,
        "9th Grade Entry Date": grade9_entry,
        "Baseline IMPACT Test Date": impact_test,
        "Home Phone": home_phone,
        "Cell Phone": cell_phone,
        "Email": email,
        "GPA": gpa,
        "Football Insurance Status": football_ins,
        "Interscholastic Insurance Status": interscholastic_ins
    }

    save_data(data)
    st.success("Athlete information saved!")
    st.write("Submitted Athlete Info:")
    st.write(data)

# 🧠 Chatbot section
st.header("🧠 Ask ChatBoy About Athletes")
question = st.text_input("Ask a question about the saved athletes:")
df = load_data()
st.write("Names in database:", list(df['Name'].fillna('').str.lower().str.strip()))

def find_column(attr_query, columns):
    attr_query = attr_query.lower().strip().replace("?", "")
    # Try exact match
    for col in columns:
        if attr_query == col.lower().strip():
            return col
    # Try if all words in attr_query are in the column name
    for col in columns:
        col_lower = col.lower().strip()
        if all(word in col_lower for word in attr_query.split()):
            return col
    # Try fuzzy match (any word)
    for col in columns:
        col_lower = col.lower().strip()
        for word in attr_query.split():
            if word in col_lower:
                return col
    return None

if question:
    if df.empty:
        st.warning("No data available to answer your question.")
    else:
        question_lower = question.lower().strip()

        # How many football players?
        if "how many" in question_lower and "football" in question_lower:
            count = df[df['Sport'].fillna('').str.lower().str.strip() == "football"].shape[0]
            st.info(f"There are {count} football athletes saved.")

        # GPA above X
        elif "gpa above" in question_lower:
            try:
                match = re.search(r"gpa above\s*([0-9.]+)", question_lower)
                if match:
                    threshold = float(match.group(1))
                    filtered = df[df['GPA'] > threshold]
                    st.write(filtered)
                    st.info(f"Found {len(filtered)} athletes with GPA above {threshold}.")
                else:
                    st.warning("Couldn't understand the GPA value.")
            except Exception as e:
                st.warning(f"Error: {e}")

        # Does [name] have a physical?
        elif "have a physical" in question_lower or "physical date" in question_lower or "physical" in question_lower:
            match = re.search(r"does (.+?) have a physical", question_lower)
            if match:
                name_query = match.group(1).strip()
                matched_rows = df[df['Name'].fillna('').str.lower().str.strip().str.contains(name_query.strip())]
                if not matched_rows.empty:
                    st.write("### 📋 Physical Info for Athlete")
                    st.write(matched_rows[["Name", "Physical Date", "Physical Expiry Date"]])
                else:
                    st.info("No athlete matched that name. Try using the full name or check spelling.")
            else:
                st.info("Please ask using the format: 'Does [Name] have a physical?'")

        # Attribute question: "what is [name]'s [attribute]" or "what is [name] [attribute]"
        elif "what is" in question_lower or "birth date" in question_lower or "date of birth" in question_lower:
            # Try to extract name and attribute
            # Handles: what is jamie colins age, what is jamie colins's gpa, etc.
            match = re.search(r"what is (.+?)(?:'s|s)? ([\w\s]+)\??", question_lower)
            if not match:
                # Try to match "[name] birth date" or similar
                match = re.search(r"([a-z\s]+)\s+([\w\s]+)", question_lower)
            if match:
                name_query = match.group(1).strip()
                attr_query = match.group(2).strip()
                matched_rows = df[df['Name'].fillna('').str.lower().str.strip().str.contains(name_query.strip())]
                if not matched_rows.empty:
                    col_match = find_column(attr_query, df.columns)
                    if col_match:
                        value = matched_rows.iloc[0][col_match]
                        st.info(f"{matched_rows.iloc[0]['Name']}'s {col_match}: {value}")
                    else:
                        st.info(f"Could not find the attribute '{attr_query}'.")
                else:
                    st.info("No athlete matched that name. Try using the full name or check spelling.")
            else:
                st.info("Please ask using the format: 'What is [Name]'s [attribute]?'")

        # Name search (fallback)
        else:
            matched_rows = df[df['Name'].fillna('').str.lower().str.strip().str.contains(question_lower.strip())]
            if not matched_rows.empty:
                st.write("### 📋 Matched Athlete Info")
                st.write(matched_rows)
            else:
                st.info("No athlete matched that name. Try using the full name or check spelling.")

# 📥 Download CSV Button
st.subheader("⬇️ Download All Athlete Data")
df_all = load_data()

if not df_all.empty:
    csv = df_all.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Athlete Data as CSV",
        data=csv,
        file_name='athletes_data.csv',
        mime='text/csv',
    )
else:
    st.info("No athlete data available to download yet.")