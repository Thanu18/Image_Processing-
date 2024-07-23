import streamlit as st
from PIL import Image
from remover import process_image # Import the processing function from remover.py
import io

# Streamlit app interface
st.title ("Image Background Removal and Resizing")

# File upload widget
uploaded_file = st.file_uploader("Choose and image file", type=["jpg", "jpeg", "png"])


if uploaded_file:
    """Read the images from the uploaded file"""
    image = Image.open(uploaded_file).convert("RGBA")

    # Parameters for the processing
    new_width = st.slider("Canvas Width", min_value=100, max_value=3000, value=1024, step=10)
    new_height = st.slider("Canvas Height", min_value=100, max_value=3000, value=1024, step=10)
    fixed_margin = st.slider("Margin (pixels)", min_value=0, max_value=200, value=20, step=1)

    # Process the image
    processed_image = process_image(image, new_height, new_width, fixed_margin)

    if processed_image:
        # Display the processed image
        st.image(processed_image, caption="Processed Image", use_column_width=True)

        # Provide download link for the processed image
        buffered = io.BytesIO()
        processed_image.save(buffered, format="PNG")
        st.download_button(
            label="Download Processed Image",
            data=buffered.getvalue(),
            file_name="processed_image.png",
            mime="image/png"
        )
    else:
        st.error("Failed to process the image. Please try again")