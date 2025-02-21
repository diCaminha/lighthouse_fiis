#!/usr/bin/env python
import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

# Set page configuration at the very top.
st.set_page_config(page_title="FIIs Report Generator")

# For local development, load the .env file.
load_dotenv()

# Try to load production secrets; if not found, fallback to local environment variables.
try:
    prod_config = st.secrets["postgres"]
except Exception:
    prod_config = None

if prod_config:
    DB_HOST = prod_config["host"]
    DB_PORT = prod_config["port"]
    DB_NAME = prod_config["dbname"]
    DB_USER = prod_config["user"]
    DB_PASSWORD = prod_config["password"]
else:
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

@st.cache_resource
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def validate_login(email, password):
    """Validate the provided email and password against the PostgreSQL database."""
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT 1 FROM users WHERE email = %s AND password = %s"
    cur.execute(query, (email, password))
    result = cur.fetchone()
    cur.close()
    return result is not None

def login_screen():
    st.title("Login")
    st.write("Please log in to access the FIIs Report Generator")
    
    email = st.text_input("Email", key="email")
    password = st.text_input("Password", type="password", key="password")
    
    if st.button("Login"):
        if email and password:
            if validate_login(email, password):
                st.session_state.logged_in = True
                st.success("Login successful!")
            else:
                st.error("Invalid email or password.")
        else:
            st.error("Please enter both email and password.")

def report_generator_app():
    st.title("Gerador de Relatório de FIIs")
    st.write("Você está logado.")
    
    st.header("Inserir Nomes dos FIIs")
    fii_names = st.text_area("Digite os nomes dos FIIs separados por vírgula:")
    
    if st.button("Gerar relatório"):
        if fii_names.strip():
            fii_list = [fii.strip() for fii in fii_names.split(",")]
            with st.spinner("Gerando relatório..."):
                current_date = datetime.now().strftime("%Y/%m/%d")
                report = (
                    f"Relatório gerado em {current_date} para os FIIs: {', '.join(fii_list)}\n\n"
                    "Decisão: Buy/Do Not Invest"
                )
            st.header("Relatório Gerado")
            st.markdown(report)
        else:
            st.warning("Por favor, insira pelo menos um nome de FII.")

def main():
    # Initialize the login state if not already set.
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Create a placeholder container for the login screen.
    placeholder = st.empty()

    # If the user is not logged in, render the login screen in the placeholder.
    if not st.session_state.logged_in:
        with placeholder.container():
            login_screen()
    else:
        # Clear the placeholder so the login form disappears.
        placeholder.empty()
        report_generator_app()

if __name__ == "__main__":
    main()
