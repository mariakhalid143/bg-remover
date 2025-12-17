import streamlit as st
from PIL import Image, ImageFilter, ImageDraw, ImageOps
from rembg import remove
import io

# --- Page Config ---
st.set_page_config(page_title="Baka Studio - Zero Cost", layout="wide")

st.title("💎 Baka High-End Studio Engine")
st.markdown("##### High-precision subject grounding with multi-stage contact shadows")

# --- Sidebar ---
with st.sidebar:
    st.header("Studio Controls")
    uploaded_file = st.file_uploader("Upload Product Photo", type=["png", "jpg", "jpeg", "webp"])
    
    st.divider()
    st.subheader("Shadow Engineering")
    sh_intensity = st.slider("Shadow Depth", 0.0, 1.0, 0.5, 0.05, help="Darkness of the contact point")
    sh_spread = st.slider("Shadow Spread", 10, 200, 100, help="How far the soft shadow travels")
    sh_grounding = st.slider("Grounding Position", -20, 20, 2, help="Fine-tune the bottle's touch point")

# --- Multi-Stage Shadow Function ---
def create_pro_grounding(img, intensity, spread, offset):
    img = img.convert("RGBA")
    w, h = img.size
    
    # 1. Create a canvas large enough for a spreading shadow
    canvas_w = int(w * 1.8)
    canvas_h = int(h * 1.4)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    
    # 2. Create the Contact Shadow (Occlusion)
    # This is the dark sliver that 'grounds' the bottle
    occ_w = int(w * 0.95)
    occ_h = int(h * 0.04)
    occlusion = Image.new('L', (occ_w, occ_h), 0)
    draw_occ = ImageDraw.Draw(occlusion)
    draw_occ.ellipse([0, 0, occ_w, occ_h], fill=int(255 * intensity))
    occlusion = occlusion.filter(ImageFilter.GaussianBlur(radius=2))
    
    # 3. Create the Soft Ambient Shadow (The natural fade)
    amb_w = int(w * 1.3)
    amb_h = int(h * 0.15)
    ambient = Image.new('L', (amb_w, amb_h), 0)
    draw_amb = ImageDraw.Draw(ambient)
    
    # Draw a multi-layered gradient
    for i in range(spread, 0, -2):
        alpha = int((intensity * 120) * (1 - (i / spread)))
        draw_amb.ellipse([i, i//4, amb_w - i, amb_h - i//4], fill=alpha)
    
    ambient = ambient.filter(ImageFilter.GaussianBlur(radius=spread/4))
    
    # --- COMPOSITING ---
    # Center points
    center_x = canvas_w // 2
    
    # Paste Ambient Shadow
    amb_layer = Image.new("RGBA", (amb_w, amb_h), (0,0,0,255))
    amb_layer.putalpha(ambient)
    canvas.paste(amb_layer, (center_x - amb_w//2, h + offset - amb_h//3), amb_layer)
    
    # Paste Occlusion Shadow (The 'Dark Anchor')
    occ_layer = Image.new("RGBA", (occ_w, occ_h), (0,0,0,255))
    occ_layer.putalpha(occlusion)
    canvas.paste(occ_layer, (center_x - occ_w//2, h + offset - occ_h//2), occ_layer)
    
    # Paste Product on top
    canvas.paste(img, (center_x - w//2, 0), img)
    
    return canvas.crop(canvas.getbbox())

# --- Main App Logic ---
if uploaded_file:
    col1, col2 = st.columns(2)
    input_image = Image.open(uploaded_file)
    
    with col1:
        st.subheader("Original")
        st.image(input_image, use_container_width=True)

    with st.spinner("Rendering studio environment..."):
        # Step 1: High-precision removal
        no_bg = remove(input_image)
        
        # Step 2: Multi-stage grounding shadow
        final_result = create_pro_grounding(no_bg, sh_intensity, sh_spread, sh_grounding)
        
    with col2:
        st.subheader("Studio Quality Output")
        st.image(final_result, use_container_width=True)
        
        buf = io.BytesIO()
        final_result.save(buf, format="PNG")
        st.download_button("💾 Download Studio PNG", buf.getvalue(), "baka_pro_studio.png", "image/png", type="primary", use_container_width=True)
else:
    st.info("Upload your product photo to activate the High-End Shadow Engine.")
