import os
import streamlit as st
import google.generativeai as genai
import io

# Page configuration
st.set_page_config(page_title="🔄 SSIS Workflow Generator", page_icon="🔄")

# Language dictionary for a user-friendly interface
language_dict = {
    "enter_description": "📝 Describe your ETL requirements in plain language:",
    "generated_workflow": "Here’s your SSIS package outline with step-by-step instructions:",
    "download_workflow": "📄 Download Workflow Outline",
    "like": "👍 Like",
    "dislike": "👎 Dislike",
    "thank_feedback": "Thank you for your feedback!",
    "improve_suggestions": "We'll work on improving our suggestions.",
    "api_key_required": "Please enter your Google Generative AI API Key in the sidebar to use this app.",
    "enter_warning": "Please enter a description to generate your SSIS workflow."
}

# Initialize session state for feedback
st.session_state.setdefault('feedback', [])

# App title and description
st.title("🔄 SSIS Workflow Generator")
st.markdown("Generate an SSIS package outline with step-by-step instructions based on your ETL requirements!")

# Sidebar for API key input and instructions
st.sidebar.header("🔑 API Configuration")
st.sidebar.markdown("""
To use the Gemini API, you need an API key. Obtain one in **[Google AI Studio](https://aistudio.google.com/)**.
""")

# Function to get API key
def get_api_key():
    api_key = os.getenv("GOOGLE_GENERATIVEAI_API_KEY") or st.secrets.get("GOOGLE_GENERATIVEAI_API_KEY")
    if not api_key:
        api_key = st.sidebar.text_input("🔑 Enter your Google Generative AI API Key", type="password")
    return api_key

api_key = get_api_key()

# Configure Google Generative AI if API key is available
if api_key:
    try:
        genai.configure(api_key=api_key)
        st.sidebar.success("Google Generative AI configured successfully 🎉")
    except Exception as e:
        st.sidebar.error(f"Configuration failed: {e} 😢")
        st.warning(language_dict['api_key_required'])
        st.stop()
else:
    st.warning(language_dict['api_key_required'])
    st.stop()

# User input for ETL description
st.markdown(f"### {language_dict['enter_description']}")
etl_description = st.text_area("Describe the ETL process you want to create in SSIS (e.g., 'Extract data from SQL Server, remove duplicates, and load to Azure SQL Database')")

# Gemini API function to generate SSIS workflow
def generate_ssis_workflow(etl_description):
    prompt = f"""
    You are an assistant generating SSIS workflows. Based on the following ETL description:
    - {etl_description}
    
    Provide a detailed SSIS package outline with step-by-step instructions for each task and data flow. Include specific components (like Data Flow Task, Execute SQL Task, Source, and Destination), explain each component briefly, and include best practices where applicable.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating SSIS workflow: {e}")
        return None

# Display generated SSIS workflow and provide download option
if etl_description:
    with st.spinner("🔄 Generating your SSIS package outline..."):
        ssis_workflow = generate_ssis_workflow(etl_description)
        if ssis_workflow:
            st.markdown(f"## 📄 {language_dict['generated_workflow']}")
            st.markdown(ssis_workflow)

            # Convert workflow to a downloadable file
            download_text = f"SSIS Workflow Outline:\n\n{ssis_workflow}"
            download_file = io.BytesIO(download_text.encode())
            
            st.download_button(
                label=language_dict['download_workflow'],
                data=download_file,
                file_name="ssis_workflow_outline.txt",
                mime="text/plain"
            )

            # Feedback buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"{language_dict['like']}"):
                    st.session_state['feedback'].append('like')
                    st.success(language_dict['thank_feedback'])
            with col2:
                if st.button(f"{language_dict['dislike']}"):
                    st.session_state['feedback'].append('dislike')
                    st.warning(language_dict['improve_suggestions'])
        else:
            st.warning("⚠️ Unable to generate SSIS workflow with the provided description.")
else:
    st.info(f"⚠️ {language_dict['enter_warning']}")
