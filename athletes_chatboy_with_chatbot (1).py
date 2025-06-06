
import streamlit as st
from PIL import Image
import openai
from docx import Document
import smtplib
from email.message import EmailMessage
import os
import csv
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Secure API and email credentials
openai.api_key = os.getenv("OPENAI_API_KEY")
email_sender = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")

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
    st.image(logo, use_column_width=True)
except:
    st.warning("Logo image not found. Please check the file path.")

st.title("Athletes ChatBoy 🧠")

# Athlete Information Entry Form in Sidebar
with st.sidebar:
    st.header("✍️ Enter New Athlete")
    with st.form("athlete_form"):
        name = st.text_input("Name")
        dob = st.date_input("Date of Birth")
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

# Display submitted data in main area and save to CSV
if submitted:
    st.success(f"Athlete {name} added successfully!")
    athlete_data = {
        "Name": name,
        "DOB": dob,
        "Age": age,
        "School": school,
        "Sport": sport,
        "Position": position,
        "Physical Date": physical_date,
        "Physical Expiry": physical_expiry,
        "Graduation Year": grad_year,
        "9th Grade Entry": grade9_entry,
        "IMPACT Test Date": impact_test,
        "Home Phone": home_phone,
        "Cell Phone": cell_phone,
        "Email": email,
        "GPA": gpa,
        "Football Insurance": football_ins,
        "Interscholastic Insurance": interscholastic_ins
    }
    st.write(athlete_data)

    # Save to CSV
    csv_file = "athletes_data.csv"
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=athlete_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(athlete_data)

    st.info("Athlete data saved to athletes_data.csv")

# Chatbot Section
st.header("🤖 Ask the ChatBot About the Athlete")
user_input = st.text_input("Ask a question:")
if user_input:
    prompt = f"""
    You are an assistant that answers questions based on the following athlete data:
    {athlete_data}

    Question: {user_input}
    Answer:
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response['choices'][0]['message']['content'].strip()
        st.success(answer)
    except Exception as e:
        st.error(f"Chatbot error: {e}")
