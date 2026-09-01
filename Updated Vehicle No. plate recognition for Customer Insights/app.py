import streamlit as st
import cv2
from PIL import Image
from util import save_temp_image
from main import process_vehicle
from insights import plot_state_charts, show_recommendations, get_summary_metrics
from database.db_handler import init_db, import_csv_data, fetch_recent_vehicles

# Set page config ONCE at the very top
st.set_page_config(
    page_title="Vehicle Recognition & Customer Insights",
    page_icon="🚗",
    layout="wide"
)

# Initialize database idempotently
@st.cache_resource
def setup_database():
    init_db()
    import_csv_data()
    return True

setup_database()

# Header
st.title("🚗 Vehicle Plate Recognition & Customer Insights")
st.caption("AI-Powered Automatic Number Plate Recognition (ANPR) & Regional Customer Behavior Analytics")

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📸 Vehicle Detection", "📊 Customer Insights", "📋 Visit Logs"])

# ----------------- TAB 1: DETECTION -----------------
with tab1:
    st.subheader("Upload Vehicle Image")
    col_upload, col_preview = st.columns([1, 2])
    
    with col_upload:
        uploaded_file = st.file_uploader(
            "Choose a vehicle image (JPG, PNG, JPEG)",
            type=["jpg", "jpeg", "png"]
        )
        conf_threshold = st.slider("Detection Confidence Threshold", 0.15, 0.90, 0.35, 0.05)
    
    if uploaded_file:
        image_path = save_temp_image(uploaded_file)
        
        with col_preview:
            st.write("### Detection Results")
            with st.spinner("Detecting license plate & extracting state region..."):
                results, annotated_img = process_vehicle(image_path, conf_threshold=conf_threshold)
            
            # Show original/annotated image
            if annotated_img is not None:
                st.image(
                    cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB),
                    caption="Detection Bounding Box",
                    use_container_width=True
                )
            
            # Show Extracted Details
            if results:
                st.success(f"Successfully detected {len(results)} plate(s)!")
                for idx, item in enumerate(results, 1):
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            if item["roi"] is not None and item["roi"].size > 0:
                                st.image(
                                    cv2.cvtColor(item["roi"], cv2.COLOR_BGR2RGB),
                                    caption="Cropped Plate ROI",
                                    width=180
                                )
                        with c2:
                            st.markdown(f"### 🏷️ `{item['plate']}`")
                            st.markdown(f"**State / Region:** :green[{item['state_name']}] (`{item['state_code']}`)")
                            st.markdown(f"**Confidence:** `{item['confidence'] * 100:.1f}%`")
            else:
                st.warning("⚠️ No license plate detected. Try adjusting confidence threshold or uploading a clearer image.")

# ----------------- TAB 2: INSIGHTS -----------------
with tab2:
    st.subheader("Customer Regional Insights & Analytics")
    
    total_veh, total_states, top_state = get_summary_metrics()
    
    # Top KPI metric cards
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Vehicles Logged", total_veh)
    m2.metric("Unique States Represented", total_states)
    m3.metric("Top Customer Region", top_state)
    
    st.divider()
    
    # State Distribution Visualizations
    chart_col1, chart_col2 = st.columns(2)
    pie, bar = plot_state_charts()
    
    if pie and bar:
        with chart_col1:
            st.plotly_chart(pie, use_container_width=True)
        with chart_col2:
            st.plotly_chart(bar, use_container_width=True)
            
        st.divider()
        
        # Recommendations
        st.subheader("📦 Recommended Inventory Stock & Preferences for Top Visiting Regions")
        recs = show_recommendations()
        if recs is not None and not recs.empty:
            st.dataframe(recs, use_container_width=True)
        else:
            st.info("No recommendations found for current visiting states.")
    else:
        st.info("ℹ️ No vehicle visits recorded yet. Upload vehicle images in the Detection tab to view analytics.")

# ----------------- TAB 3: VISIT LOGS -----------------
with tab3:
    st.subheader("Recent Vehicle Visit Logs")
    logs = fetch_recent_vehicles(limit=100)
    
    if not logs.empty:
        st.dataframe(logs, use_container_width=True)
        
        csv_data = logs.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Export Logs to CSV",
            data=csv_data,
            file_name="vehicle_visit_logs.csv",
            mime="text/csv"
        )
    else:
        st.info("No records in database.")
