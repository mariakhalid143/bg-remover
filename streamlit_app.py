import streamlit as st
from PIL import Image, ImageFilter, ImageDraw, ImageOps
from rembg import remove
import io

# --- Page Configuration ---
st.set_page_config(page_title="Baka Luxury Studio", layout="wide")

st.title("💎 Baka Luxury Reflection Engine")
st.markdown("##### Polished Glass Surface & Linear Gradient Falloff")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Surface Controls")
    uploaded_file = st.file_uploader("Upload Product Photo", type=["png", "jpg", "jpeg", "webp"])
    
    st.divider()
    st.subheader("Reflection Properties")
    reflect_opacity = st.slider("Reflection Strength", 0.0, 1.0, 0.30, 0.05)
    reflect_length = st.slider("Reflection Length", 0.1, 0.9, 0.5, 0.1, help="How far the reflection extends down")
    reflect_blur = st.slider("Surface Softness", 0, 30, 5, help="Simulates frosted vs polished glass")
    
    st.divider()
    bg_color = st.color_picker("Studio Floor Color", "#111111")

# --- Luxury Reflection Logic ---
def create_luxury_reflection(image, opacity, length, blur):
    image = image.convert("RGBA")
    width, height = image.size
    
    # 1. Create the Reflection (Mirror Image)
    reflection = ImageOps.flip(image)
    reflection = reflection.resize((width, int(height * length)))
    
    # 2. Create the Linear Gradient Mask (Fades to zero at the bottom)
    # This is the secret to the "Professional" look
    gradient = Image.new('L', (width, reflection.height), 0)
    draw = ImageDraw.Draw(gradient)
    for y in range(reflection.height):
        # Calculate fade: Darker at the contact point, transparent at the end
        level = int((1 - (y / reflection.height)) * (opacity * 255))
        draw.line([(0, y), (width, y)], fill=level)
    
    reflection.putalpha(gradient)
    
    # 3. Apply Softness (Blur) to the surface
    if blur > 0:
        reflection = reflection.filter(ImageFilter.GaussianBlur(radius=blur))
    
    # 4. Composite onto a new canvas
    canvas_h = height + reflection.height
    canvas = Image.new("RGBA", (width, canvas_h), (0,0,0,0))
    
    # Paste Reflection first (bottom)
    canvas.paste(reflection, (0, height), reflection)
    
    # Paste Product on top (Contact point is seamless)
    canvas.paste(image, (0, 0), image)
    
    return canvas

# --- App Logic ---
if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Source")
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)

    with st.spinner("Polishing Surface..."):
        # Remove BG
        no_bg = remove(img)
        
        # Apply Luxury Reflection
        final_output = create_luxury_reflection(no_bg, reflect_opacity, reflect_length, reflect_blur)
        
    with col2:
        st.subheader("Luxury Final")
        # Preview Background
        bg = Image.new("RGBA", final_output.size, bg_color)
        combined = Image.alpha_composite(bg, final_output)
        st.image(combined, use_container_width=True)
        
        # Download
        buf = io.BytesIO()
        final_output.save(buf, format="PNG")
        st.download_button("💾 Download Luxury PNG", buf.getvalue(), "baka_luxury.png", "image/png", type="primary", use_container_width=True)
else:
    st.info("Upload your perfume bottle to create a luxury ad.")
