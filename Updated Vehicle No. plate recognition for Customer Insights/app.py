import streamlit as st
from util import save_temp_image
from main import process_vehicle
from insights import plot_state_charts, show_recommendations
from database.db_handler import init_db, import_csv_data

st.set_page_config(page_title="Vehicle Number Recognition", layout="wide")


import streamlit as st
st.set_page_config(page_title="Vehicle Number Recognition", layout="wide")
st.title("🚗 Vehicle Number Recognition for Customer Region Insights")

st.write("🔹 App initialized successfully...")  # ✅ Debug line



st.title("🚗 Vehicle Number Recognition for Customer Region Insights")

# Initialize DB
init_db()
import_csv_data()

tab1, tab2 = st.tabs(["📸 Detection", "📊 Insights"])

with tab1:
    uploaded_file = st.file_uploader("Upload Vehicle Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_path = save_temp_image(uploaded_file)
        st.image(image_path, caption="Uploaded Image", use_container_width=True)
        with st.spinner("Processing..."):
            results = process_vehicle(image_path)
        if results:
            for plate, region in results:
                st.success(f"Detected: **{plate}** → Region: **{region}**")
        else:
            st.error("No plate detected.")

with tab2:
    st.subheader("Vehicle Distribution by State")
    pie, bar = plot_state_charts()
    if pie and bar:
        st.plotly_chart(pie, use_container_width=True)
        st.plotly_chart(bar, use_container_width=True)
    else:
        st.warning("No data yet. Upload images to generate insights.")

    st.subheader("Recommended Stock by Top States")
    recs = show_recommendations()
    if recs is not None and not recs.empty:
        st.dataframe(recs)
    else:
        st.info("No recommendations yet. Add more data.")
