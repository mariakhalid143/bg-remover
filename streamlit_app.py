import streamlit as st
from PIL import Image
import io
from google import genai
from google.genai import types

# --- Page Configuration ---
st.set_page_config(page_title="Baka AI Studio Re-Renderer", layout="wide")

st.title("📸 Baka AI Studio Re-Renderer")
st.markdown("##### Transform raw photos into high-end luxury ads with natural AI lighting.")

# --- Sidebar ---
with st.sidebar:
    st.header("Baka Digital")
    # Using your secret key
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = st.text_input("Enter Gemini API Key", type="password")
        
    st.divider()
    uploaded_file = st.file_uploader("Upload Product Photo", type=["png", "jpg", "jpeg", "webp"])
    
    st.divider()
    st.subheader("Studio Style")
    surface_type = st.selectbox("Surface Material", 
                                ["Polished Black Marble", "Frosted Glass", "Soft Satin Fabric", "Natural Light Wood", "Minimalist Concrete"])
    lighting_style = st.selectbox("Lighting Style", 
                                  ["Softbox Side Lighting", "Moody Rim Light", "Bright Direct Sunlight", "Under-lit Glow"])

# --- AI Studio Logic ---
if uploaded_file:
    col1, col2 = st.columns(2)
    img = Image.open(uploaded_file)
    
    with col1:
        st.subheader("Raw Photo")
        st.image(img, use_container_width=True)

    if st.button("🚀 Render Studio Scene", type="primary", use_container_width=True):
        if not api_key:
            st.error("API Key missing.")
        else:
            with st.spinner("Re-rendering product in professional studio..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    # AI-driven instruction for natural shadows
                    prompt = (
                        f"Place this exact product on a {surface_type} surface. "
                        f"Apply {lighting_style} to create realistic, soft, natural shadows at the base. "
                        "The background should be a clean, slightly out-of-focus studio wall. "
                        "Keep the product labels perfectly readable. Professional commercial photography quality."
                    )
                    
                    # Re-rendering logic
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-image",
                        contents=[prompt, img.convert("RGB")],
                        config=types.GenerateContentConfig(response_modalities=["IMAGE"])
                    )

                    if response.candidates and response.candidates[0].content.parts:
                        for part in response.candidates[0].content.parts:
                            if part.inline_data:
                                result_img = Image.open(io.BytesIO(part.inline_data.data))
                                with col2:
                                    st.subheader("AI Studio Result")
                                    st.image(result_img, use_container_width=True)
                                    
                                    # Download
                                    buf = io.BytesIO()
                                    result_img.save(buf, format="PNG")
                                    st.download_button("💾 Download Studio Render", buf.getvalue(), "baka_studio.png", "image/png")
                                    break
                except Exception as e:
                    st.error(f"Studio Error: {str(e)}")
else:
    st.info("Upload your product photo to generate a luxury studio render.")
