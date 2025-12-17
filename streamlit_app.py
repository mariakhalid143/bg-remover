import streamlit as st
from PIL import Image, ImageOps, ImageFilter
from rembg import remove
import io
import numpy as np

# --- Page Config ---
st.set_page_config(page_title="Baka Pro BG Remover + Shadow", layout="wide")

st.title("✂️ Professional BG Remover & Shadow Engine")
st.markdown("##### High-precision extraction with realistic floor shadows")

# --- Sidebar ---
with st.sidebar:
    st.header("Baka Digital")
    uploaded_file = st.file_uploader("Upload Product Photo", type=["png", "jpg", "jpeg"])
    
    st.divider()
    st.subheader("Shadow Settings")
    shadow_strength = st.slider("Shadow Opacity", 0, 255, 120, help="Higher = Darker shadow")
    blur_radius = st.slider("Shadow Softness", 0, 50, 20, help="Higher = Softer edges")
    offset_y = st.slider("Vertical Offset", -50, 50, 10, help="Adjust shadow distance from object")

# --- Helper Function for Shadow ---
def add_floor_shadow(image, opacity, blur, offset):
    # Ensure image has alpha channel
    image = image.convert("RGBA")
    width, height = image.size
    
    # Create the shadow layer
    # We take the alpha channel (the shape) and fill it with black
    alpha = image.getchannel('A')
    shadow = Image.new("RGBA", (width, height), (0, 0, 0, opacity))
    shadow.putalpha(alpha)
    
    # 1. Distort the shadow to look like it's on the floor (perspective)
    # This stretches and flattens the shadow shape
    shadow = shadow.resize((width, int(height * 0.4)))
    
    # 2. Blur the shadow for realism
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
    
    # 3. Composite the shadow and the original image onto a white background
    # (Or transparent if preferred)
    canvas = Image.new("RGBA", (width, int(height * 1.3)), (255, 255, 255, 0))
    
    # Place shadow first
    canvas.paste(shadow, (0, height - int(height*0.2) + offset), shadow)
    
    # Place original image on top
    canvas.paste(image, (0, 0), image)
    
    return canvas

# --- Main Logic ---
if uploaded_file:
    col1, col2 = st.columns(2)
    input_image = Image.open(uploaded_file)
    
    with col1:
        st.subheader("Original")
        st.image(input_image, use_container_width=True)

    with st.spinner("Processing subject and shadow..."):
        # 1. Remove background
        no_bg_img = remove(input_image)
        
        # 2. Apply the shadow logic
        final_output = add_floor_shadow(no_bg_img, shadow_strength, blur_radius, offset_y)
        
    with col2:
        st.subheader("Professional Result")
        st.image(final_output, use_container_width=True)
        
        # Prepare for Download
        buf = io.BytesIO()
        final_output.save(buf, format="PNG")
        
        st.download_button(
            label="💾 Download PNG with Shadow",
            data=buf.getvalue(),
            file_name="baka_product_shadow.png",
            mime="image/png",
            type="primary",
            use_container_width=True
        )
else:
    st.info("Upload a product photo to see the shadow engine in action.")
