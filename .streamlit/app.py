import streamlit as st
import requests
import time
from auth import get_auth_url, exchange_code_for_tokens
from property_list import list_properties

@@ -67,7 +66,7 @@
        auth_url = get_auth_url()
        st.markdown(f"""
            <div style="text-align:center; margin-top:3em;">
                <a href="{auth_url}" target="_self">
                <a href="{auth_url}" target="_blank">
                    <button style="
                        background-color:white; 
                        color:#444; 
@@ -98,9 +97,9 @@
            st.error(f"Token exchange failed: {e}")
            st.stop()

# ---------- SELECT PROPERTY ---------- #
access_token = st.session_state["access_token"]

# ---------- SELECT PROPERTY ---------- #
try:
    properties = list_properties(access_token)
except Exception as e:
@@ -132,9 +131,9 @@
            }

            response = requests.post(
                            "https://us-central1-marketlytics-dataware-house.cloudfunctions.net/data-analytics-tool",
                             json=payload
                            )
                "https://us-central1-marketlytics-dataware-house.cloudfunctions.net/data-analytics-tool",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            status.update(label="✅ Audit Complete", state="complete")
@@ -174,7 +173,6 @@
            else:
                st.info("📄 PDF report is available. Google Docs version could not be generated.")


            if buttons_html:
                st.markdown(buttons_html, unsafe_allow_html=True)
                st.markdown("🔗 Click a button above to open/download your audit report.")
@@ -184,3 +182,4 @@
        except Exception as e:
            status.update(label="❌ Audit Failed", state="error")
            st.error(f"Audit failed: {e}")




