import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from rembg import remove
import io
import numpy as np

# --- Page Config ---
st.set_page_config(page_title="Baka Studio - Pro", layout="wide")

st.title("✂️ Baka Professional Studio Engine")
st.markdown("##### High-precision extraction with Radial Gradient Shadows (Zero API Cost)")

# --- Sidebar ---
with st.sidebar:
    st.header("Studio Controls")
    uploaded_file = st.file_uploader("Upload Product Photo", type=["png", "jpg", "jpeg", "webp"])
    
    st.divider()
    st.subheader("Shadow Engineering")
    # Professional default values for perfume bottles
    sh_opacity = st.slider("Shadow Intensity", 0, 255, 90)
    sh_blur = st.slider("Edge Softness", 10, 150, 80)
    sh_width = st.slider("Shadow Width", 0.5, 2.5, 1.4)
    sh_offset = st.slider("Grounding (Y-Axis)", -10, 40, 5)

# --- Professional Radial Shadow Function ---
def apply_pro_shadow(img, opacity, blur, width_factor, offset):
    img = img.convert("RGBA")
    w, h = img.size
    
    # Create a canvas large enough for the shadow spread
    canvas_w = int(w * 1.5)
    canvas_h = int(h * 1.5)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    
    # 1. Create a Radial Gradient Mask
    # This is the secret to a professional look
    shadow_w = int(w * width_factor)
    shadow_h = int(h * 0.2) # Flattened for floor perspective
    
    # Generate the gradient ellipse
    mask = Image.new('L', (shadow_w, shadow_h), 0)
    draw = ImageDraw.Draw(mask)
    
    # Loop to create a smooth falloff from center to edge
    for i in range(blur, 0, -1):
        alpha = int(opacity * (1 - (i / blur)))
        draw.ellipse([i, i, shadow_w - i, shadow_h - i], fill=alpha)
    
    # Soften the edges further with Gaussian blur
    mask = mask.filter(ImageFilter.GaussianBlur(radius=blur/2))
    
    # Create the actual shadow layer
    shadow_layer = Image.new("RGBA", (shadow_w, shadow_h), (0, 0, 0, 255))
    shadow_layer.putalpha(mask)
    
    # --- COMPOSITING ---
    # Position shadow at the base center
    shadow_x = (canvas_w - shadow_w) // 2
    shadow_y = h + offset - (shadow_h // 2)
    canvas.paste(shadow_layer, (shadow_x, shadow_y), shadow_layer)
    
    # Position product in the center
    product_x = (canvas_w - w) // 2
    canvas.paste(img, (product_x, 0), img)
    
    return canvas.crop(canvas.getbbox()) # Trim excess space

# --- Main Logic ---
if uploaded_file:
    col1, col2 = st.columns(2)
    input_image = Image.open(uploaded_file)
    
    with col1:
        st.subheader("Original")
        st.image(input_image, use_container_width=True)

    with st.spinner("Extracting subject and rendering shadow..."):
        # Step 1: Remove BG (Free, uses server CPU)
        no_bg = remove(input_image)
        
        # Step 2: Apply the Pro Radial Shadow
        final_result = apply_pro_shadow(no_bg, sh_opacity, sh_blur, sh_width, sh_offset)
        
    with col2:
        st.subheader("Studio Final")
        st.image(final_result, use_container_width=True)
        
        buf = io.BytesIO()
        final_result.save(buf, format="PNG")
        st.download_button("💾 Download Studio PNG", buf.getvalue(), "baka_pro.png", "image/png", type="primary", use_container_width=True)
else:
    st.info("Upload a product photo to begin.")
