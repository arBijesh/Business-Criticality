import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(page_title="AEP App Scorer (Refined)", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .big-font { font-size:18px !important; }
    .stRadio > label { font-size: 16px; font-weight: bold; color: #2c3e50; }
    .stSelectbox > label { font-size: 16px; font-weight: bold; color: #2c3e50; }
    div[data-testid="stForm"] { border: 2px solid #f0f2f6; padding: 25px; border-radius: 10px; }
    h3 { color: #1565C0; padding-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- REFINED LOGIC ENGINE ---
def calculate_score(a):
    # --- LEVEL 1: MISSION CRITICAL ---
    # The "Kill Switch" scenarios. If ANY of these are Yes, it is Tier 1.
    if (a['Safety'] == 'Yes' or 
        a['Grid'] == 'Yes' or 
        a['Fines'] == 'Yes' or 
        a['RestoreTime'] == 'Immediately (Within 4 hours)'):
        return {
            "Level": "1 - Mission Critical",
            "Description": "Vital for Safety, Grid, or Law. Zero downtime tolerance.",
            "Color": "#D32F2F" # Red
        }

    # --- LEVEL 2: BUSINESS CRITICAL ---
    # High Value scenarios. Revenue, Customers, or Private Data.
    if (a['Money'] == 'Yes' or 
        a['Public'] == 'Yes' or 
        a['Privacy'] == 'Yes' or 
        a['RestoreTime'] == 'Same Day (Within 24 hours)'):
        return {
            "Level": "2 - Business Critical",
            "Description": "Core business blocked. High financial risk, Customer impact, or PII data.",
            "Color": "#F57C00" # Orange
        }

    # --- LEVEL 3: OPERATIONAL ---
    # Work stops, but we can survive a day.
    # Logic: If manual work is IMPOSSIBLE ("No" backup) OR Work Stops completely.
    if (a['ManualBackup'] == 'No (We stop working)' or 
        a['RestoreTime'] == 'Next Day (24-48 hours)'):
        return {
            "Level": "3 - Operational",
            "Description": "Important tool. Work is painful or stops without it, but can wait 24h.",
            "Color": "#1976D2" # Blue
        }

    # --- LEVEL 4: NON-CRITICAL ---
    # Convenience only.
    return {
        "Level": "4 - Non-Critical",
        "Description": "Administrative or convenience tool. Work continues manually.",
        "Color": "#616161" # Grey
    }

# --- HEADER ---
st.title("⚡ AEP CSDM Business Criticality Assessment")
st.write("Please answer these **15 questions**. This determines the Business Criticality and Support level required.")

# --- INPUTS ---
with st.form("refined_form"):
    
    # 0. BASIC INFO
    col_a, col_b = st.columns(2)
    with col_a:
        app_name = st.text_input("Application Name")
    with col_b:
        dept_name = st.selectbox("Department", ["Distribution", "Transmission", "Generation", "IT/Corporate", "HR/Finance"])

    st.divider()

    # SECTION 1: CRITICALITY DRIVERS (The "Why")
    st.markdown("### 1. 🚨 Impact & Risk")
    
    q1_safety = st.radio("1. Could a failure here hurt a person or damage the Power Grid?", ["No", "Yes"], horizontal=True)
    q2_money = st.radio("2. Do we lose actual money (revenue/payments) if this breaks?", ["No", "Yes"], horizontal=True)
    q3_fines = st.radio("3. Will the government fine or sue us immediately if this is down?", ["No", "Yes"], horizontal=True)
    q4_restore = st.selectbox("4. If it breaks, how fast do you need it back?", 
                              ["Immediately (Within 4 hours)", "Same Day (Within 24 hours)", "Next Day (24-48 hours)", "3-5 Days (Low Priority)"])

    st.divider()

    # SECTION 2: USAGE (The "Who")
    st.markdown("### 2. 👥 Users & Accessibility")
    
    q5_users = st.selectbox("5. Who uses this software?", 
                            ["Just me / My small team (<10 people)", "My whole department (~50-100 people)", "The Whole Company (Everyone)"])
    q6_freq = st.radio("6. How often do people log in?", ["Rarely / Once a Month", "Weekly", "Daily / Constantly"], horizontal=True)
    q7_public = st.radio("7. Do external Customers (the public) use this directly?", ["No", "Yes"], horizontal=True)
    q8_backup = st.radio("8. Can you do your job on Paper/Excel if this breaks?", ["Yes (We can survive manually)", "No (We stop working)"], horizontal=True)

    st.divider()

    # SECTION 3: TECHNICAL DETAILS (The "How")
    st.markdown("### 3. 💻 Technical Details")
    
    q9_access = st.radio("9. How do you access it?", ["Web Browser (Chrome/Edge)", "Installed on my Laptop (.exe)", "Mobile App on Phone"], horizontal=True)
    q10_login = st.radio("10. Do you log in with your standard AEP Password (SSO)?", ["Yes (SSO)", "No (Separate Username/Password)"], horizontal=True)
    q11_vendor = st.selectbox("11. Who built this?", ["We bought it (Vendor/SaaS)", "AEP built it (In-house Custom)", "I don't know"])
    q12_network = st.radio("12. Does it work without the Internet/Network?", ["No (Needs Network)", "Yes (Works Offline)"], horizontal=True)

    st.divider()

    # SECTION 4: DATA SENSITIVITY (The "What")
    st.markdown("### 4. 🔒 Data & Integration")

    q13_privacy = st.radio("13. Does it contain private people data (SSN, Payroll, Addresses)?", ["No", "Yes"], horizontal=True)
    # REMOVED: Export question
    q14_connect = st.radio("14. Does it send data automatically to other AEP systems?", ["No (It stands alone)", "Yes (It feeds other apps)"], horizontal=True)
    q15_input = st.radio("15. Do you TYPE new data in, or just READ old data?", ["We Type/Edit Data (Active)", "Just Read/View (Read-Only)"], horizontal=True)

    st.divider()
    submitted = st.form_submit_button("Calculate Criticality")

# --- RESULTS ---
if submitted:
    if not app_name:
        st.error("⚠️ Please enter an Application Name at the top.")
    else:
        # Collect Answers
        answers = {
            "Safety": q1_safety, "Grid": q1_safety, 
            "Money": q2_money, "Fines": q3_fines, "RestoreTime": q4_restore,
            "Users": q5_users, "UsageFreq": q6_freq, "Public": q7_public, "ManualBackup": q8_backup,
            "Access": q9_access, "Login": q10_login, "Vendor": q11_vendor, "Network": q12_network,
            "Privacy": q13_privacy, "Connects": q14_connect, "Input": q15_input
        }

        # Calculate Score
        result = calculate_score(answers)

        # Show Visual Result
        st.success("Assessment Complete!")
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 15px solid {result['Color']};">
            <h2 style="color: {result['Color']}; margin:0;">{result['Level']}</h2>
            <p style="font-size: 18px; margin-top: 10px;">{result['Description']}</p>
        </div>
        """, unsafe_allow_html=True)

        # --- PREPARE EXCEL LIST (2 Columns) ---
        data_rows = [
            ["Application Name", app_name],
            ["Department", dept_name],
            ["CALCULATED CRITICALITY", result['Level']],
            ["--- IMPACT ---", ""],
            ["1. Safety/Grid Risk", q1_safety],
            ["2. Financial Loss", q2_money],
            ["3. Legal/Fines", q3_fines],
            ["4. Restore Time Needed", q4_restore],
            ["--- USAGE ---", ""],
            ["5. Who uses it?", q5_users],
            ["6. How often?", q6_freq],
            ["7. External Customers?", q7_public],
            ["8. Manual Workaround?", q8_backup],
            ["--- TECH ---", ""],
            ["9. Access Method", q9_access],
            ["10. SSO/Login", q10_login],
            ["11. Vendor/Builder", q11_vendor],
            ["12. Network Dependency", q12_network],
            ["--- DATA ---", ""],
            ["13. PII/Private Data", q13_privacy],
            ["14. Integration (Feeds others)", q14_connect],
            ["15. Active vs Read-Only", q15_input]
        ]

        # Convert to DataFrame
        df = pd.DataFrame(data_rows, columns=["Question", "Answer"])

        # Display Table
        st.markdown("### 📥 Verify & Download")
        st.dataframe(df, hide_index=True, use_container_width=True)

        # Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results (Excel/CSV)",
            data=csv,
            file_name=f"{app_name}_Assessment.csv",
            mime="text/csv"
        )

