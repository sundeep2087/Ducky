import streamlit as st
import helpers.sidebar
import asyncio
from services.images import generate_image, delete_image, get_all_images
from PIL import Image
import pandas as pd

st.set_page_config(
    page_title="Images",
    page_icon="🏞️",
    layout="wide"
)

helpers.sidebar.show()

st.header("Image Generation")


# ============================================================================================ #
# =================================== IMPLEMENTATION  ======================================== #
# ============================================================================================ #

tab1, tab2 = st.tabs(["Image Generation", "Image List"])

# Tab 1: Image Generation
with tab1:
    prompt = st.text_input("Prompt", placeholder="Enter a prompt for the image generation model")
    generate_button = st.button("Generate Image")

    if generate_button and prompt:
        try:
            prompt_response, image_path = generate_image(prompt)
            image = Image.open(image_path)
            st.image(image, caption=prompt_response)
        except Exception as e:
            st.error(f"Failed to generate image: {str(e)}")


with tab2:
    df = get_all_images()
    df['Date Created'] = pd.to_datetime(df['Date Created'], errors='coerce')
    df['Date Created'] = df['Date Created'].dt.strftime('%Y-%m-%d %H:%M:%S')

    if not df.empty:
        st.markdown(
            """
            <div style='display: flex; justify-content: space-between; align-items: center; font-size: 20px;'>
                <div style='flex: 0; text-align: center;'><strong>Image</strong></div>
                <div style='flex: 1.5; text-align: center;'><strong>Description</strong></div>
                <div style='flex: 1; text-align: left;'><strong>Date Created</strong></div>
                <div style='flex: 2; text-align: left;'><strong>Actions</strong></div>
            </div>
            """,
            unsafe_allow_html=True
        )
        for index, row in df.iterrows():
            cols = st.columns([2, 2, 2, 3, 2])  # Adjusted for expander

            image = Image.open(row['Image'])
            cols[0].image(image, width=100)
            cols[1].write(row['Description'])
            cols[2].write(row['Date Created'])

            with cols[3]:
                with st.expander("View"):
                    st.image(image, caption=row['Description'], use_column_width=True)

            # Delete button
            if cols[4].button('🗑️ Delete', key=f'delete_{index}'):  # Fixed key uniqueness
                delete_image(row['Image'])
                df = df.drop(index)
                st.rerun()
    else:
        st.write("No images found.")
