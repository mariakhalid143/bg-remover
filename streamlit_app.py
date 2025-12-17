import streamlit as st
from PIL import Image
from rembg import remove
import io

# --- Page Config ---
st.set_page_config(page_title="Baka Professional BG Remover", layout="wide")

st.title("✂️ Professional BG Remover")
st.markdown("##### High-precision subject extraction for product photography")

# --- Sidebar ---
with st.sidebar:
    st.header("Baka Digital")
    uploaded_file = st.file_uploader("Upload Product Photo", type=["png", "jpg", "jpeg"])
    st.info("This tool runs locally on our server. No API key required!")

# --- Main Logic ---
if uploaded_file:
    col1, col2 = st.columns(2)
    
    input_image = Image.open(uploaded_file)
    
    with col1:
        st.subheader("Original")
        st.image(input_image, use_container_width=True)

    with st.spinner("Processing edges..."):
        # The actual removal logic
        # 'remove' from rembg handles transparency automatically
        output_image = remove(input_image)
        
    with col2:
        st.subheader("Transparent Result")
        st.image(output_image, use_container_width=True)
        
        # Prepare for Download
        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        
        st.download_button(
            label="💾 Download Transparent PNG",
            data=buf.getvalue(),
            file_name="baka_transparent.png",
            mime="image/png",
            type="primary",
            use_container_width=True
        )
else:
    st.info("Please upload a photo to begin.")
