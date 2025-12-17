import streamlit as st
from PIL import Image, ImageFilter, ImageDraw, ImageOps
from rembg import remove
import io
import numpy as np

# --- Page Configuration ---
st.set_page_config(page_title="Baka Ultra-Studio BG Remover", layout="wide")

st.title("💎 Baka Ultra-Studio Shadow Engine")
st.markdown("##### Precision extraction with Elliptical Gradient Falloff shadows")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Studio Controls")
    uploaded_file = st.file_uploader("Upload Product Photo", type=["png", "jpg", "jpeg", "webp"])
    
    st.divider()
    st.subheader("Shadow Refinement")
    shadow_opacity = st.slider("Shadow Intensity", 0.0, 1.0, 0.40, 0.05)
    shadow_spread = st.slider("Horizontal Spread", 0.5, 3.0, 1.8, 0.1, help="How wide the shadow stretches")
    shadow_blur = st.slider("Edge Softness", 10, 150, 60)
    shadow_offset = st.slider("Grounding", -10, 30, 2)
    
    st.divider()
    bg_color = st.color_picker("Preview Background", "#F2F2F2")

# --- Advanced Gradient Shadow Engine ---
def create_ultra_studio_shadow(image, opacity, spread, blur, offset):
    image = image.convert("RGBA")
    width, height = image.size
    
    # 1. Create a large canvas to prevent shadow clipping
    canvas_w = int(width * 2)
    canvas_h = int(height * 1.5)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0,0,0,0))
    
    # 2. Create the Gradient Shadow Mask
    # We generate a large ellipse mask instead of just blurring the subject shape
    mask_w = int(width * spread)
    mask_h = int(height * 0.25)
    shadow_mask = Image.new("L", (mask_w, mask_h), 0)
    draw = ImageDraw.Draw(shadow_mask)
    
    # Draw a series of ellipses to create a natural manual gradient falloff
    for i in range(blur, 0, -1):
        alpha = int((opacity * 255) * (1 - (i / blur)))
        draw.ellipse([i, i, mask_w - i, mask_h - i], fill=alpha)
    
    # Apply Gaussian blur for the final smooth transition
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(radius=blur/2))
    
    # Create the actual shadow layer
    shadow_layer = Image.new("RGBA", (mask_w, mask_h), (0,0,0,255))
    shadow_layer.putalpha(shadow_mask)

    # --- COMPOSITING ---
    # Position shadow at the bottom center of the canvas
    shadow_x = (canvas_w - mask_w) // 2
    shadow_y = height + offset - (mask_h // 2)
    canvas.paste(shadow_layer, (shadow_x, shadow_y), shadow_layer)
    
    # Position product in the center
    product_x = (canvas_w - width) // 2
    canvas.paste(image, (product_x, 0), image)
    
    # Auto-crop the final result to remove excess whitespace
    return canvas.crop(canvas.getbbox())

# --- App Logic ---
if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Source")
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)

    with st.spinner("Generating Studio Environment..."):
        # Remove BG
        no_bg = remove(img)
        
        # Apply Ultra Shadow
        final_output = create_ultra_studio_shadow(no_bg, shadow_opacity, shadow_spread, shadow_blur, shadow_offset)
        
    with col2:
        st.subheader("Studio Final")
        # Preview Background
        bg = Image.new("RGBA", final_output.size, bg_color)
        combined = Image.alpha_composite(bg, final_output)
        st.image(combined, use_container_width=True)
        
        # Download
        buf = io.BytesIO()
        final_output.save(buf, format="PNG")
        st.download_button("💾 Download Studio PNG", buf.getvalue(), "baka_studio.png", "image/png", type="primary", use_container_width=True)
else:
    st.info("Upload your product image to start.")
