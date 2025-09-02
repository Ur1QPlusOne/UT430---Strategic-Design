import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Import my data
df = pd.read_csv("/Users/dinguid/PH Accelerator Dropbox/Dylan Ingui/Mac/Downloads/EasternMarketVendors - Sheet1.csv")

# Filter out Market Vendors and save the count
no_market_vendors = df[df['Business'].str.lower() == "market vendor"]
market_vendor_count = len(df) - len(no_market_vendors)


no_unspecified = df[(df['Business'].str.lower() == "district business") & (df['Type'].str.lower() == "unspecified")]
unspecified_count = market_vendor_count - len(no_unspecified)

filtered_df = df.drop(no_market_vendors.index).drop(no_unspecified.index)
filtered_df = filtered_df.dropna(subset=['Latitude', 'Longitude'])

# Setup Streamlit App
st.set_page_config(layout="wide")
st.title("Eastern Market Detroit Map")

# Create columns for layout
col1, col2 = st.columns([1, 3])

with col1:
    # Print how much data is being displayed
    st.write(f"Excluded **{market_vendor_count} market vendors**.")
    st.write(f"Excluded **{unspecified_count} district businesses** with unspecified type.")
    st.write(f"There are **{len(filtered_df)} district businesses** displayed on the map.")

    # Setup Multiselect for Business Types
    all_types = sorted(filtered_df["Type"].dropna().unique())
    selected_types = st.multiselect("Select business types to display:", options=all_types, default=all_types)

    # Create Legend
    st.markdown("### Legend")
    color_map = {
        "flowers": "red",
        "art": "orange",
        "baked goods": "brown",
        "dine": "blue",
        "other": "hotpink",
        "produce": "green"
    }
    
    # Generate legend HTML
    legend_items = "".join(
        f"<div style='margin-bottom:6px;'>"
        f"<span style='background:{c}; width:14px; height:14px; border-radius:50%; "
        f"display:inline-block; margin-right:8px; border:1px solid #555;'></span>{k.title()}"
        f"</div>"
        for k, c in color_map.items()
    )
    
    # Display legend and add border and padding
    st.markdown(
        f"<div style='padding:10px; border:1px solid #ccc; border-radius:8px; width:200px;'>{legend_items}</div>",
        unsafe_allow_html=True
    )

with col2:
    # Filter dataframe for only selected types
    filtered_display = filtered_df[filtered_df["Type"].isin(selected_types)]

    # Create Map
    m = folium.Map(location=[42.3467, -83.0415], zoom_start=15)

    # Eastern Market Polygon (so proud of this lowkey)
    boundary_coords = [
        [42.3403797, -83.0413600],
        [42.3526067, -83.0322425],
        [42.3564136, -83.0347309],
        [42.3513322, -83.0473038],
        [42.3456200, -83.0440393],
        [42.3403862, -83.0413557],
    ]
    # Add polygon to the map
    folium.Polygon(boundary_coords, color="black", weight=2, fill=True, fill_opacity=0.05).add_to(m)

    # Add points (for each business add a dot)
    for _, row in filtered_display.iterrows():
        t = str(row['Type']).lower()
        color = color_map.get(t, "blue")
        
        # Makes the popup formatted better
        popup_html = f"""
        <div style="width:200px;">
            <b>{row['Name']}</b><br>
            Type: {row['Type']}
        </div>
        """
        
        # Add circle marker with popup
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],  # lat, lon
            radius=6,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250)  # 👈 controls popup width
        ).add_to(m)

    # Show the map
    st_folium(m, width=900, height=600)
