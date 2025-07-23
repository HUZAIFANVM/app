import streamlit as st
import requests
from auth import get_auth_url, exchange_code_for_tokens
from property_list import list_properties

# ---------- PAGE CONFIG ---------- #
st.set_page_config(page_title="GA4 Audit App", page_icon="📊", layout="wide")

# ---------- CUSTOM CSS ---------- #
st.markdown("""
    <style>
        html, body {
            background-color: #fafafa;
        }
        .main {
            font-family: 'Segoe UI', sans-serif;
            color: #2E2E2E;
        }
        h1, h2, h3 {
            color: #2E2E2E;
        }
        .stButton>button {
            background-color: #9147ff;
            color: white;
            border-radius: 8px;
            padding: 0.6em 1.2em;
            font-size: 16px;
            font-weight: 500;
            border: none;
            box-shadow: 0 4px 14px rgba(0,0,0,0.1);
            transition: background 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #722ccf;
        }
        .selectbox-label {
            font-weight: 600;
            color: #333;
            margin-bottom: 0.2em;
        }
        .audit-container {
            background: white;
            padding: 2em;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER WITH LOGO ---------- #
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://marketlytics.com/wp-content/uploads/2023/03/logo-2-1-1024x366-1.png", width=2000)
with col2:
    st.markdown("""
        <h1 style="font-size:2em; margin-bottom:0;">GA4 Analytics Audit</h1>
        <p style="font-size:1.1em; color:#555;">MarketLytics GA4 Configuration Health Check</p>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------- AUTHENTICATION ---------- #
if "access_token" not in st.session_state:
    query_params = st.query_params
    if "code" not in query_params:
        auth_url = get_auth_url()
        st.markdown(f"""
            <div style="text-align:center; margin-top:3em;">
                <a href="{auth_url}" target="_blank">
                    <button style="
                        background-color:white; 
                        color:#444; 
                        padding:0.8em 1.6em;
                        border:1px solid #ccc; 
                        border-radius:8px; 
                        font-weight:600; 
                        font-size:16px;
                        box-shadow:0 2px 5px rgba(0,0,0,0.1);
                        display:flex; align-items:center; gap:10px;">
                        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" style="height:20px;">
                        Login with Google
                    </button>
                </a>
                <p style="color:#666;">Please authorize to access your GA4 properties.</p>
            </div>
        """, unsafe_allow_html=True)
        st.stop()
    else:
        try:
            code = query_params["code"]
            with st.spinner("🔐 Exchanging code for tokens..."):
                tokens = exchange_code_for_tokens(code)
                st.session_state["access_token"] = tokens["access_token"]
                st.query_params.clear()
                st.success("✅ Authorization successful")
        except Exception as e:
            st.error(f"Token exchange failed: {e}")
            st.stop()

# ---------- SELECT PROPERTY ---------- #
access_token = st.session_state["access_token"]

try:
    properties = list_properties(access_token)
except Exception as e:
    st.error(f"Error fetching properties: {e}")
    st.stop()

st.markdown("### 🔍 Select GA4 Property")

with st.container():
    with st.form("ga4_audit_form", border=False):
        with st.container():
        st.markdown('<div class="audit-container">', unsafe_allow_html=True)
        
        prop_names = [p[0] for p in properties]
        selected_index = st.selectbox("Choose your GA4 Property", options=range(len(prop_names)),
                                      format_func=lambda i: prop_names[i])
        
        site_type = st.selectbox(
            "Select Site Type",
            options=["ecommerce", "leadgen", "other"],
            index=0
        )
        submitted = st.form_submit_button("✨ Run Audit")
        st.markdown('</div>', unsafe_allow_html=True)


# ---------- PERFORM AUDIT ---------- #
if submitted:
    with st.status("Running GA4 Audit...", expanded=True) as status:
        try:
            st.write("📤 Submitting for full analysis...")

            payload = {
                "audit_type": "full",
                "property_id": properties[selected_index][1],
                "access_token": access_token
            }

            response = requests.post(
                "https://us-central1-marketlytics-dataware-house.cloudfunctions.net/data-analytics-tool",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            if not result:
                st.warning("⚠️ The GA4 data retrieved appears to be incomplete or not sufficiently rich for auditing. Please ensure that data is being collected properly in your GA4 property and try again later.")
                status.update(label="⚠️ Insufficient Data", state="error")
                st.stop()

            status.update(label="✅ Audit Complete", state="complete")

            # ---------- RESULTS ---------- #
            st.markdown("## 🧾 Audit Summary")
            st.success("Audit successfully completed!")

            if not result.get("ecommerce_included", False):
                st.warning("⚠️ Ecommerce data missing. Skipping ecommerce-related checks.")

            if not result.get("anomaly_included", False):
                st.warning("⚠️ Revenue anomaly check skipped due to insufficient data.")

            # ---------- Download Buttons ---------- #
            buttons_html = ""

            if result.get("pdf_url"):
                buttons_html += f"""
                    <a href="{result['pdf_url']}" target="_blank">
                        <button style="background-color:#9147ff; color:white; padding:0.8em 1.6em;
                        border:none; border-radius:6px; font-size:16px; margin-top:1em;">
                            📝Download PDF Report
                        </button>
                    </a>
                """

            if result.get("gdoc_url"):
                st.markdown(f"""
                    <a href="{result['gdoc_url']}" target="_blank">
                        <button style="background-color:#4285F4; color:white; padding:0.8em 1.6em;
                        border:none; border-radius:6px; font-size:16px; margin-top:1em;">
                            📝 Google Docs Report
                        </button>
                    </a>
                """, unsafe_allow_html=True)
            else:
                st.info("📄 PDF report is available. Google Docs version could not be generated.")

            if buttons_html:
                st.markdown(buttons_html, unsafe_allow_html=True)
                st.markdown("🔗 Click a button above to open/download your audit report.")
            else:
                st.error("❌ No report URLs received.")

        except Exception as e:
            status.update(label="❌ Audit Failed", state="error")
            st.error(f"Audit failed: {e}")




