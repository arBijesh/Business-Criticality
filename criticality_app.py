import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="ServiceNow Business Criticality Assessor", layout="wide")

def calculate_criticality(responses):
    """
    Logic based on the provided flowchart:
    1. Mission Critical: Immediate Financial Loss/Fines/Safety.
    2. Business Critical: Work Stops + No viable workaround.
    3. Non-Critical: Inconvenient, but work continues.
    4. Archive/Admin: Rarely used / Read-only.
    """
    
    # --- TIER 1 CHECKS (Mission Critical) ---
    if (responses['financial_loss'] == 'Yes' or 
        responses['regulatory_fines'] == 'Yes' or 
        responses['safety_impact'] == 'Yes'):
        return {
            "tier": "Tier 1: MISSION CRITICAL",
            "color": "#D32F2F",  # Red
            "definition": "The business STOPS. No workaround exists.",
            "rto": "< 1 hour",
            "support": "24/7 Dedicated",
            "examples": "SAP ERP, Public Ecommerce, Electronic Health Records"
        }

    # --- TIER 2 CHECKS (Business Critical) ---
    # Logic: Outage stops work AND (No workaround OR Workaround is not sustainable)
    if (responses['stops_work'] == 'Yes' and 
       (responses['workaround_exists'] == 'No' or responses['workaround_sustainable'] == 'No')):
        return {
            "tier": "Tier 2: BUSINESS CRITICAL",
            "color": "#F57C00",  # Orange
            "definition": "Productivity drops, manual workarounds exist for a short time.",
            "rto": "< 4 hours",
            "support": "Business Hours + On-call",
            "examples": "CRM (Salesforce), Email, Payroll (Non-run days)"
        }

    # --- TIER 3 CHECKS (Non-Critical) ---
    # Logic: Outage is inconvenient OR Work continues
    if responses['inconvenient_only'] == 'Yes' or responses['stops_work'] == 'No':
        return {
            "tier": "Tier 3: NON-CRITICAL (Internal)",
            "color": "#1976D2",  # Blue
            "definition": "Low impact. Operations continue normally for most people.",
            "rto": "24-48 hours",
            "support": "Best Effort (Next Business Day)",
            "examples": "Room Booking, Intranet News, Performance Review Tool"
        }

    # --- TIER 4 CHECKS (Fallback / Archive) ---
    return {
        "tier": "Tier 4: ADMINISTRATIVE / ARCHIVE",
        "color": "#616161",  # Grey
        "definition": "Rarely used or read-only data.",
        "rto": "> 1 week",
        "support": "No SLA",
        "examples": "Legacy Archive Systems, Test/Dev Sandboxes"
    }

# --- APP UI ---

st.title("🛡️ ServiceNow Business Criticality Assessor")
st.markdown("""
This tool helps define the criticality of an application based on **Business Impact**, **Recovery Time**, and **Operational Risks**.
Answer the questions below to determine the correct Tier.
""")

st.divider()

# Input: Application Details
with st.sidebar:
    st.header("Application Details")
    app_name = st.text_input("Application Name")
    app_owner = st.text_input("Application Owner")
    business_unit = st.selectbox("Business Unit", ["IT", "HR", "Finance", "Sales", "Operations", "Other"])

# Container for the Form
with st.form("assessment_form"):
    st.subheader("1. Financial & Regulatory Impact (The 'Knockout' Questions)")
    col1, col2 = st.columns(2)
    
    with col1:
        q1 = st.radio("Does an outage cause immediate financial loss?", ("No", "Yes"), index=0, help="e.g., Customers cannot buy products")
        q2 = st.radio("Are there major regulatory fines associated with downtime?", ("No", "Yes"), index=0, help="e.g., GDPR, HIPAA violations")
    with col2:
        q3 = st.radio("Does the outage impact human safety or patient care?", ("No", "Yes"), index=0, help="e.g., Hospital cannot admit patients")

    st.subheader("2. Operational Impact")
    col3, col4 = st.columns(2)
    
    with col3:
        q4 = st.radio("Does an outage STOP work for critical teams?", ("No", "Yes"), index=0, help="e.g., Warehouse cannot ship, Call center down")
    with col4:
        q5 = st.radio("Is there a manual workaround available?", ("No", "Yes"), index=0)
        q6 = st.radio("If a workaround exists, is it sustainable for >4 hours?", ("No", "Yes", "N/A"), index=0)

    st.subheader("3. Usage & Convenience")
    q7 = st.radio("Is the outage merely 'inconvenient' (work continues)?", ("No", "Yes"), index=0, help="e.g., Internal Survey Tool, Cafeteria Menu")

    # Submit Button
    submitted = st.form_submit_button("Assess Criticality")

# --- RESULTS PROCESSING ---
if submitted:
    if not app_name:
        st.warning("Please enter an Application Name in the sidebar.")
    else:
        # Collect responses into a dictionary
        user_responses = {
            "financial_loss": q1,
            "regulatory_fines": q2,
            "safety_impact": q3,
            "stops_work": q4,
            "workaround_exists": q5,
            "workaround_sustainable": q6,
            "inconvenient_only": q7
        }
        
        # Calculate Logic
        result = calculate_criticality(user_responses)
        
        st.divider()
        st.subheader(f"Result for: {app_name}")
        
        # Display Result Card
        st.markdown(f"""
        <div style="padding: 20px; border-radius: 10px; background-color: #f0f2f6; border-left: 10px solid {result['color']};">
            <h2 style="color: {result['color']}; margin:0;">{result['tier']}</h2>
            <p style="font-size: 18px;"><strong>Definition:</strong> {result['definition']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display Details Columns
        c1, c2, c3 = st.columns(3)
        c1.metric("Recovery Time (RTO)", result['rto'])
        c2.metric("Support Level", result['support'])
        c3.info(f"**Examples:** {result['examples']}")

        # JSON Export Option
        st.divider()
        st.download_button(
            label="Download Assessment JSON",
            data=pd.Series({**{"Application": app_name, "Owner": app_owner}, **user_responses, **result}).to_json(),
            file_name=f"{app_name}_criticality_assessment.json",
            mime="application/json"
        )