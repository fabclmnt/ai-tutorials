"""Streamlit app for interacting with Databricks SQL using OpenAI-powered assistant."""
import os

import streamlit as st
from functions.catalog_connector import set_connection, get_catalog_metadata

# Constants
REQUIRED_KEYS = ["openai_api_key", "databricks_host", "http_path", "databricks_token", "catalog_name"]

# Page configuration
st.set_page_config(page_title="Databricks SQL Assistant", layout="wide")

# Initialize session state keys
for key in REQUIRED_KEYS + ["schema_metadata", "messages"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "messages" else []

#------- SIDEBAR CONFIGURATION -------
def configure_app():
    with st.sidebar:
        st.header("App Configuration")

        st.subheader("🔐 OpenAI API Settings")
        st.text_input("OpenAI API Key", type="password", key="openai_api_key")

        st.subheader("🧱 Databricks Connection Settings")
        st.text_input("Databricks Workspace Host", key="databricks_host", placeholder="e.g., dbc-1234.cloud.databricks.com")
        st.text_input("Databricks SQL HTTP Path", key="http_path")
        st.text_input("Databricks Access Token", type="password", key="databricks_token")
        st.text_input("Catalog name", key='catalog_name')

        if st.button("Save Configuration"):
            if all([st.session_state.get("openai_api_key"),
                    st.session_state.get("databricks_host"),
                    st.session_state.get("http_path"),
                    st.session_state.get("databricks_token")]):

                os.environ['OPENAI_API_KEY'] = st.session_state.get("openai_api_key")

                try:
                    #Here create the connector?
                    connection = set_connection(server_hostname=st.session_state['databricks_host'],
                                                http_path=st.session_state['http_path'],
                                                access_token=st.session_state['databricks_token'])

                    schema_metadata = get_catalog_metadata(catalog_name=st.session_state['catalog_name'],
                                                           connection=connection)

                    st.session_state['schema_metadata'] = schema_metadata
                except Exception as e:
                    st.error(f"❌ Failed to connect or fetch metadata: {e}")

                st.success("✅ Configuration saved!")
            else:
                st.error("❌ Please fill in all fields.")

configure_app()

#------- MAIN PAGE -------
st.title("💬 Databricks SQL Chat Assistant")

# Ensure required configuration is present
missing_keys = [key for key in REQUIRED_KEYS if not st.session_state.get(key)]
if missing_keys or not st.session_state["schema_metadata"]:
    st.warning("⚠️ Please configure your environment in the 'Configuration' tab.")
else:
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you with your data?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        import asyncio
        from functions.query_assistant import system_prompt, assistant_prompt, catalog_metadata_agent

        agent = catalog_metadata_agent(system_prompt.format(summary=st.session_state['schema_metadata']))

        st.session_state.messages.append({"role": "user", "content": prompt})

        async def run_agent(prompt):
            msg = await agent.run(prompt)
            return msg.output

        st.chat_message("user").write(prompt)
        try:
            content = asyncio.run(run_agent(assistant_prompt.format(question=prompt)))

            if content and content.code:
                st.chat_message("assistant").write(f"```sql\n{content.code}\n```")
                st.session_state["messages"].append({"role": "assistant", "content": content.code})
            else:
                st.chat_message("assistant").write("❓ Something went wrong. Please try rephrasing your question.")
        except Exception as e:
            st.chat_message("assistant").write(f"❌ Error generating response: {e}")
