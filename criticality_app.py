import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="AEP Application Assessment (CSDM)", layout="wide")

# --- CUSTOM CSS FOR AEP BRANDING ---
st.markdown("""
    <style>
    .big-font { font-size:20px !important; }
    .stRadio > label { font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def calculate_criticality(r):
    """
    Logic maps simple business answers to Technical CSDM Criticality Tiers.
    """
    
    # --- TIER 1: MISSION CRITICAL ---
    # Logic: Any direct impact on Grid, Safety, or Immediate Government Fines
    if (r['q_safety'] == 'Yes' or 
        r['q_grid'] == 'Yes' or 
        r['q_storm'] == 'Yes' or 
        r['q_fines'] == 'Yes'):
        return {
            "tier": "1 - Mission Critical",
            "desc": "The company cannot operate without this. Immediate impact on safety, grid, or law.",
            "sla": "Platinum (24/7 Response)",
            "color": "#D32F2F" # Red
        }

    # --- TIER 2: BUSINESS CRITICAL ---
    # Logic: Direct money loss, Customer impact, or work stops with no easy backup
    if (r['q_money'] == 'Yes' or 
        r['q_customer'] == 'Yes' or 
        (r['q_stop_work'] == 'Yes' and r['q_manual_backup'] == 'No')):
        return {
            "tier": "2 - Business Critical",
            "desc": "Core business is blocked. Revenue or Customer trust is damaged.",
            "sla": "Gold (Business Hours + On Call)",
            "color": "#F57C00" # Orange
        }

    # --- TIER 3: BUSINESS OPERATIONAL (Non-Critical) ---
    # Logic: Inconvenient, or good manual backups exist
    if (r['q_stop_work'] == 'Yes' and r['q_manual_backup'] == 'Yes'):
         return {
            "tier": "3 - Business Operational",
            "desc": "Important, but we can use manual workarounds (paper/Excel) for a day or two.",
            "sla": "Silver (Next Business Day)",
            "color": "#1976D2" # Blue
        }

    # --- TIER 3 (Low Impact) ---
    if r['q_productivity'] == 'Yes':
        return {
            "tier": "3 - Non-Critical (Productivity)",
            "desc": "Internal efficiency tool. Work is slower, but continues.",
            "sla": "Bronze (Best Effort)",
            "color": "#1976D2" # Blue
        }

    # --- TIER 4: ARCHIVE / READ-ONLY ---
    if r['q_active'] == 'No':
        return {
            "tier": "4 - Archive / Read-Only",
            "desc": "Historical data only. Not used for daily work.",
            "sla": "No SLA",
            "color": "#616161" # Grey
        }

    # Default Fallback
    return {
        "tier": "3 - Non-Critical",
        "desc": "Standard internal application.",
        "sla": "Bronze",
        "color": "#1976D2"
    }

# --- APP HEADER ---
st.title("⚡ AEP Application Assessment")
st.markdown("### CSDM Business Criticality Intake")
st.markdown("Answer these **15 questions** to help us categorize this application in ServiceNow. Please answer based on a *worst-case scenario* (e.g., the app is down completely).")
st.divider()

# --- SIDEBAR: METADATA ---
with st.sidebar:
    st.header("Application Info")
    app_name = st.text_input("Application Name")
    owner = st.text_input("Business Owner")
    dept = st.selectbox("Department", ["Transmission", "Distribution", "Generation", "Customer Ops", "Corporate/IT", "HR/Finance"])

# --- MAIN QUESTIONNAIRE ---
with st.form("csdm_form"):
    
    # SECTION 1: SAFETY & POWER (The "Lights On" Questions)
    st.subheader("1. Safety & Power Grid")
    c1, c2 = st.columns(2)
    with c1:
        q_grid = st.radio("1. Does this software directly control the flow of electricity or monitor power lines?", ["No", "Yes"], index=0)
        q_safety = st.radio("2. If this system fails, could it physically hurt an employee or the public?", ["No", "Yes"], index=0)
    with c2:
        q_storm = st.radio("3. Is this system absolutely necessary during a storm restoration event?", ["No", "Yes"], index=0)
        q_env = st.radio("4. Would a failure cause an immediate environmental violation (spill, emission)?", ["No", "Yes"], index=0)

    st.divider()

    # SECTION 2: MONEY & LAWS
    st.subheader("2. Money & Regulations")
    c3, c4 = st.columns(2)
    with c3:
        q_fines = st.radio("5. Would the government fine AEP *immediately* if this system goes down?", ["No", "Yes"], index=0)
        q_money = st.radio("6. Does this system process payments or generate direct revenue?", ["No", "Yes"], index=0)
    with c4:
        q_legal = st.radio("7. Is this system required for legal evidence or audit trails (e.g., SOX)?", ["No", "Yes"], index=0)
        q_vendor = st.radio("8. Is this system hosted by an external vendor (SaaS)?", ["No", "Yes"], index=0)

    st.divider()

    # SECTION 3: DAILY OPERATIONS
    st.subheader("3. Daily Work & Customers")
    c5, c6 = st.columns(2)
    with c5:
        q_customer = st.radio("9. Do AEP customers (public) use this app directly?", ["No", "Yes"], index=0)
        q_stop_work = st.radio("10. If this app is down, does your team's work STOP completely?", ["No", "Yes"], index=0)
    with c6:
        q_manual_backup = st.radio("11. Can you do your job using paper, Excel, or phone calls if this app is down?", ["Yes", "No"], index=0)
        q_productivity = st.radio("12. Is this mostly for convenience (e.g., booking rooms, ordering lunch)?", ["No", "Yes"], index=0)

    st.divider()

    # SECTION 4: USAGE PATTERNS
    st.subheader("4. Usage & Data")
    c7, c8 = st.columns(2)
    with c7:
        q_users = st.radio("13. Who uses this?", ["A specific team", "The whole company"], index=0)
        q_time = st.radio("14. When is this system needed?", ["Business Hours (8-5)", "24/7/365"], index=0)
    with c8:
        q_active = st.radio("15. Do you actively add new data to this system, or is it just for looking up old records?", ["Yes (Active)", "No (Archive/Read-Only)"], index=0)

    st.divider()
    
    # SUBMIT
    submitted = st.form_submit_button("Calculated Criticality Level")

# --- LOGIC & OUTPUT ---
if submitted:
    if not app_name:
        st.warning("⚠️ Please enter an Application Name in the sidebar.")
    else:
        # MAP RESPONSES
        responses = {
            "q_grid": q_grid, "q_safety": q_safety, "q_storm": q_storm, "q_env": q_env,
            "q_fines": q_fines, "q_money": q_money, "q_legal": q_legal, "q_vendor": q_vendor,
            "q_customer": q_customer, "q_stop_work": q_stop_work, "q_manual_backup": q_manual_backup,
            "q_productivity": q_productivity, "q_users": q_users, "q_time": q_time,
            "q_active": "Yes" if q_active == "Yes (Active)" else "No"
        }

        # GET RESULT
        result = calculate_criticality(responses)

        # DISPLAY RESULT
        st.success("Assessment Complete!")
        
        # Big Result Card
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 15px solid {result['color']}; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
            <h3 style="color: #555; margin: 0;">Suggested ServiceNow Criticality:</h3>
            <h1 style="color: {result['color']}; font-size: 45px; margin: 10px 0;">{result['tier']}</h1>
            <p style="font-size: 18px;"><strong>Definition:</strong> {result['desc']}</p>
            <hr>
            <p><strong>Recommended Support SLA:</strong> {result['sla']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Detailed Breakdown for the Analyst
        st.markdown("### 📋 Summary for CSDM Data Entry")
        col_A, col_B = st.columns(2)
        with col_A:
            st.text(f"App Name: {app_name}")
            st.text(f"Owner: {owner}")
            st.text(f"Department: {dept}")
        with col_B:
            st.text(f"User Base: {q_users}")
            st.text(f"Operating Hours: {q_time}")
            st.text(f"Data State: {q_active}")

        # Download Button
        csv_data = pd.DataFrame([responses]).T
        csv_data.columns = ["Answer"]
        st.download_button(
            label="Download Results for ServiceNow Import",
            data=pd.Series({**{"Application": app_name}, **responses, **result}).to_json(),
            file_name=f"{app_name}_CSDM_Assessment.json",
            mime="application/json"
        )
