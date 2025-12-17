import streamlit as st
from PIL import Image, ImageFilter, ImageColor
from rembg import remove
import io

# --- Page Configuration ---
st.set_page_config(page_title="Baka Pro Studio BG Remover", layout="wide")

st.title("✂️ Baka Professional Studio Engine")
st.markdown("##### Subject extraction with dual-layer occlusion and ambient shadows")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Baka Digital")
    uploaded_file = st.file_uploader("Upload Product Photo", type=["png", "jpg", "jpeg", "webp"])
    
    st.divider()
    st.subheader("Shadow Customization")
    shadow_opacity = st.slider("Shadow Density", 0.1, 1.0, 0.45, 0.05, help="Controls how dark the shadow appears.")
    shadow_blur = st.slider("Shadow Softness", 5, 80, 40, help="Higher values create a wider, softer spread.")
    shadow_offset = st.slider("Shadow Position", -20, 40, 5, help="Adjusts vertical placement under the object.")
    
    st.divider()
    st.subheader("Canvas Style")
    bg_color = st.color_picker("Background Color Preview", "#FFFFFF")

# --- Professional Shadow Engine ---
def create_studio_shadow(image, opacity_factor, blur_val, offset_y):
    """
    Creates a dual-layer realistic shadow: 
    1. Occlusion Shadow (Dark, sharp, close to base)
    2. Ambient Shadow (Light, soft, wide spread)
    """
    #
    image = image.convert("RGBA")
    width, height = image.size
    
    # Create a larger canvas to allow shadow spread without clipping
    canvas_height = int(height * 1.4)
    canvas = Image.new("RGBA", (width, canvas_height), (0,0,0,0))
    
    # Extract alpha mask of the object
    alpha = image.getchannel('A')
    
    # --- LAYER 1: AMBIENT SHADOW (The soft spread) ---
    #
    ambient_opacity = int(255 * opacity_factor * 0.5)
    ambient_shadow = Image.new("RGBA", (width, height), (0, 0, 0, ambient_opacity))
    ambient_shadow.putalpha(alpha)
    # Squish it horizontally and vertically for floor perspective
    ambient_shadow = ambient_shadow.resize((int(width * 1.1), int(height * 0.25)))
    ambient_shadow = ambient_shadow.filter(ImageFilter.GaussianBlur(radius=blur_val))
    
    # --- LAYER 2: OCCLUSION SHADOW (The dark contact point) ---
    #
    occlusion_opacity = int(255 * opacity_factor)
    occlusion_shadow = Image.new("RGBA", (width, height), (0, 0, 0, occlusion_opacity))
    occlusion_shadow.putalpha(alpha)
    # Very thin sliver at the very bottom
    occlusion_shadow = occlusion_shadow.resize((width, int(height * 0.08)))
    occlusion_shadow = occlusion_shadow.filter(ImageFilter.GaussianBlur(radius=blur_val // 5))

    # --- COMPOSITING ---
    #
    # Position ambient shadow (centered)
    canvas.paste(ambient_shadow, (int(-width * 0.05), height - int(height*0.12) + offset_y), ambient_shadow)
    
    # Position occlusion shadow (exactly at base)
    canvas.paste(occlusion_shadow, (0, height - int(height*0.06) + offset_y), occlusion_shadow)
    
    # Position original product on top
    canvas.paste(image, (0, 0), image)
    
    return canvas

# --- Main App Logic ---
if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Image")
        input_image = Image.open(uploaded_file)
        st.image(input_image, use_container_width=True)

    with st.spinner("Calculating Studio Shadows..."):
        # Step 1: Remove Background
        no_bg_img = remove(input_image)
        
        # Step 2: Generate Dual-Shadow
        final_result = create_studio_shadow(no_bg_img, shadow_opacity, shadow_blur, shadow_offset)
        
    with col2:
        st.subheader("Studio Output")
        # Preview with selected background color
        preview_bg = Image.new("RGBA", final_result.size, ImageColor.getrgb(bg_color))
        preview_combined = Image.alpha_composite(preview_bg, final_result)
        st.image(preview_combined, use_container_width=True)
        
        # Prepare Transparent Download
        buf = io.BytesIO()
        final_result.save(buf, format="PNG")
        
        st.download_button(
            label="💾 Download Transparent PNG",
            data=buf.getvalue(),
            file_name="baka_studio_product.png",
            mime="image/png",
            type="primary",
            use_container_width=True
        )
else:
    st.info("Please upload a product photo to activate the Studio Engine.")
