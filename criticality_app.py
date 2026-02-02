import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(page_title="AEP App Scorer (Simple)", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .big-font { font-size:18px !important; }
    .stRadio > label { font-size: 16px; font-weight: bold; color: #2c3e50; }
    div[data-testid="stForm"] { border: 2px solid #f0f2f6; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC ENGINE ---
def calculate_score(answers):
    # TIER 1: MISSION CRITICAL (Red)
    # Logic: Safety, Grid, Fines, or "Must be fixed immediately"
    if (answers['Safety'] == 'Yes' or 
        answers['Grid'] == 'Yes' or 
        answers['Fines'] == 'Yes' or 
        answers['Urgency'] == 'Immediately (Within 4 hours)'):
        return {
            "Level": "1 - Mission Critical",
            "Description": "This app keeps the lights on or people safe. It cannot go down.",
            "Color": "#D32F2F" # Red
        }

    # TIER 2: BUSINESS CRITICAL (Orange)
    # Logic: Money, Customers, Private Data, or "Must be fixed same day"
    if (answers['Money'] == 'Yes' or 
        answers['Customers'] == 'Yes' or 
        answers['Privacy'] == 'Yes' or 
        answers['Urgency'] == 'Same Day (Within 24 hours)'):
        return {
            "Level": "2 - Business Critical",
            "Description": "Important for revenue or customers. Downtime is very expensive.",
            "Color": "#F57C00" # Orange
        }

    # TIER 3: OPERATIONAL (Blue)
    # Logic: Work stops, but we can wait a day or use paper.
    if (answers['WorkStops'] == 'Yes'):
        return {
            "Level": "3 - Operational",
            "Description": "Internal work relies on this, but we can use paper/Excel for a day if needed.",
            "Color": "#1976D2" # Blue
        }

    # TIER 4: NON-CRITICAL (Grey)
    return {
        "Level": "4 - Non-Critical",
        "Description": "Convenience tool. Work continues fine without it.",
        "Color": "#616161" # Grey
    }

# --- HEADER ---
st.title("⚡ Simple App Assessment")
st.write("Answer these **8 simple questions** to tell us how important this application is to AEP.")

# --- INPUTS ---
with st.form("simple_form"):
    
    st.subheader("📝 Application Details")
    col_a, col_b = st.columns(2)
    with col_a:
        app_name = st.text_input("Application Name (e.g. OMS, SAP)")
    with col_b:
        dept_name = st.selectbox("Department", ["Distribution", "Transmission", "Generation", "IT/Corporate", "HR/Finance"])

    st.divider()

    st.subheader("❓ The Questions")

    # Q1: Safety
    q_safety = st.radio(
        "1. If this app stops working, could someone get hurt or the power grid fail?",
        ["No", "Yes"], horizontal=True
    )

    # Q2: Money
    q_money = st.radio(
        "2. If this app stops, does AEP lose money immediately (missed payments/bills)?",
        ["No", "Yes"], horizontal=True
    )

    # Q3: Fines
    q_fines = st.radio(
        "3. Will the government fine us or sue us if this app is down?",
        ["No", "Yes"], horizontal=True
    )

    # Q4: Customers
    q_customer = st.radio(
        "4. Do AEP customers (the public) use this app directly?",
        ["No", "Yes"], horizontal=True
    )

    # Q5: Privacy
    q_privacy = st.radio(
        "5. Does this app hold private customer info (SSN, Credit Cards)?",
        ["No", "Yes"], horizontal=True
    )

    # Q6: Work Stoppage
    q_work = st.radio(
        "6. If this app breaks, does your team have to STOP working completely?",
        ["No", "Yes"], horizontal=True
    )

    # Q7: Manual Backup
    q_backup = st.radio(
        "7. Can you do the work on Paper or Excel if the app is broken?",
        ["Yes (We can survive manually)", "No (We are dead in the water)"], horizontal=True
    )

    # Q8: Urgency (The most important question)
    q_urgency = st.selectbox(
        "8. If it breaks, how fast do you need it back?",
        [
            "Immediately (Within 4 hours) - It's an Emergency",
            "Same Day (Within 24 hours) - Urgent",
            "Next Day (24-48 hours) - Important but can wait",
            "Whenever (3-5 Days) - Low Priority"
        ]
    )

    st.divider()
    submitted = st.form_submit_button("Check Criticality Level")

# --- RESULTS ---
if submitted:
    if not app_name:
        st.error("⚠️ Please enter an Application Name at the top.")
    else:
        # Collect Answers into a dictionary
        user_answers = {
            "Safety": q_safety,
            "Grid": q_safety, # Grouping grid/safety for simplicity
            "Money": q_money,
            "Fines": q_fines,
            "Customers": q_customer,
            "Privacy": q_privacy,
            "WorkStops": q_work,
            "ManualBackup": q_backup,
            "Urgency": q_urgency
        }

        # Calculate Logic
        result = calculate_score(user_answers)

        # Show Visual Result
        st.success("Assessment Complete!")
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 15px solid {result['Color']};">
            <h2 style="color: {result['Color']}; margin:0;">{result['Level']}</h2>
            <p style="font-size: 18px; margin-top: 10px;">{result['Description']}</p>
        </div>
        """, unsafe_allow_html=True)

        # --- PREPARE EXCEL/CSV DATA ---
        # We create a list of lists: [ [Question, Answer], [Question, Answer] ... ]
        data_rows = [
            ["Application Name", app_name],
            ["Department", dept_name],
            ["CALCULATED CRITICALITY", result['Level']], # Put the score right at the top
            ["1. Safety / Grid Impact", q_safety],
            ["2. Financial Loss", q_money],
            ["3. Legal/Fines", q_fines],
            ["4. Customer Usage", q_customer],
            ["5. Private Data (PII)", q_privacy],
            ["6. Work Stoppage", q_work],
            ["7. Manual Workaround?", q_backup],
            ["8. Urgency to Fix", q_urgency]
        ]

        # Convert to DataFrame
        df = pd.DataFrame(data_rows, columns=["Question", "Answer"])

        # Display the Table
        st.markdown("### 📥 Download Results")
        st.table(df)

        # Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download as Excel/CSV",
            data=csv,
            file_name=f"{app_name}_Assessment.csv",
            mime="text/csv"
        )
