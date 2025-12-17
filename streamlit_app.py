import streamlit as st
from PIL import Image, ImageFilter, ImageDraw, ImageOps
from rembg import remove
import io

# --- Page Configuration ---
st.set_page_config(page_title="Baka Executive Studio", layout="wide")

st.title("🖤 Baka Executive Studio Engine")
st.markdown("##### Luxury Surface Reflection & Grounding for Premium Products")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Studio Settings")
    uploaded_file = st.file_uploader("Upload Product Photo", type=["png", "jpg", "jpeg", "webp"])
    
    st.divider()
    st.subheader("Surface Physics")
    reflect_strength = st.slider("Reflection Intensity", 0.0, 0.8, 0.25)
    reflect_fade = st.slider("Fade Speed", 0.1, 1.0, 0.4, help="Higher = shorter, more professional reflection")
    surface_blur = st.slider("Surface Polish", 0, 20, 2, help="0 is pure mirror, higher is brushed metal/satin")
    
    st.divider()
    bg_color = st.color_picker("Floor & Background", "#080808")

# --- Executive Reflection Logic ---
def create_executive_reflection(image, strength, fade, blur):
    image = image.convert("RGBA")
    w, h = image.size
    
    # 1. Prepare the Reflection Layer
    reflection = ImageOps.flip(image)
    # We only need the bottom portion for a professional look
    reflect_h = int(h * fade)
    reflection = reflection.crop((0, 0, w, reflect_h))
    
    # 2. Apply exponential fade mask
    # This ensures the reflection 'dies out' naturally
    mask = Image.new('L', (w, reflect_h), 0)
    for y in range(reflect_h):
        # Professional falloff math
        alpha = int((strength * 255) * ((1 - y / reflect_h) ** 2))
        ImageDraw.Draw(mask).line([(0, y), (w, y)], fill=alpha)
    
    reflection.putalpha(mask)
    
    # 3. Apply surface blur
    if blur > 0:
        reflection = reflection.filter(ImageFilter.GaussianBlur(radius=blur))
    
    # 4. Composite onto a luxury canvas
    # We add extra height at the bottom for the floor
    canvas = Image.new("RGBA", (w, h + reflect_h), (0,0,0,0))
    canvas.paste(reflection, (0, h), reflection)
    canvas.paste(image, (0, 0), image)
    
    return canvas

# --- App Logic ---
if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Source Image")
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)

    with st.spinner("Rendering Studio Environment..."):
        # Precise Background Removal
        no_bg = remove(img)
        
        # Apply Executive Reflection
        final_output = create_executive_reflection(no_bg, reflect_strength, reflect_fade, surface_blur)
        
    with col2:
        st.subheader("Executive Render")
        # Create the studio background
        # We use a solid dark color to provide the 'Luxury' contrast
        bg = Image.new("RGBA", final_output.size, bg_color)
        combined = Image.alpha_composite(bg, final_output)
        
        st.image(combined, use_container_width=True)
        
        # Download
        buf = io.BytesIO()
        final_output.save(buf, format="PNG")
        st.download_button("💾 Download Studio PNG", buf.getvalue(), "baka_executive.png", "image/png", type="primary", use_container_width=True)
else:
    st.info("Upload your product to generate a high-end luxury render.")
