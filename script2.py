import requests
import streamlit as st
from datetime import datetime

# Get today's date in the required format
current_date = datetime.today().strftime("%Y/%m/%d")
formatted_date = datetime.today().strftime("%B %d, %Y")

# Define the API URL
api_url = f"https://leanderisd.api.nutrislice.com/menu/api/weeks/school/glenn-high/menu-type/lunch/{current_date}/"

# Fetch the menu data from the Nutrislice API
response = requests.get(api_url)

# Check if the request was successful
if response.status_code == 200:
    menu_data = response.json()
    unique_entrees = {}

    # Iterate through each day's menu to build the food item list for the current date
    for day in menu_data.get("days", []):
        for item in day.get("menu_items", []):
            food = item.get("food")
            if not food:
                continue

            category = food.get("food_category", "").lower()
            if category != "entree":
                continue

            name = food.get("name", "Unknown Item")
            if "enchilada" in name.lower():  # Skip enchiladas due to too many nulls
                continue

            nutrients = food.get("rounded_nutrition_info", {})
            calories = nutrients.get("calories")
            protein = nutrients.get("g_protein")
            sodium = nutrients.get("mg_sodium")  # Added sodium field
            image_url = food.get("image_url")

            # Ensure valid image URL and nutritional values
            if image_url and (calories is not None and calories > 0) and (protein is not None and protein > 0):
                unique_entrees[name] = {
                    "name": name,
                    "calories": calories,
                    "protein": protein,
                    "sodium": sodium,
                    "protein_calorie_ratio": protein / calories,
                    "image_url": image_url
                }

    # Sort unique entrees by protein-to-calorie ratio and create rank
    sorted_entrees = sorted(unique_entrees.values(), key=lambda x: x["protein_calorie_ratio"], reverse=True)
    for index, entree in enumerate(sorted_entrees):
        entree["rank"] = index + 1  # Assign rank

    # Streamlit Sidebar Menu (only Top 3 Rankings option)
    st.sidebar.title("Menu")
    menu_option = st.sidebar.selectbox("Navigate", options=["Top 3 Rankings"])

    # Dynamic content for Top 3 Rankings
    if menu_option == "Top 3 Rankings":
        st.markdown("<h1 style='text-align: center; color: white;'>🔥 Top 3 High-Protein Entrées</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: white;'>📅 Menu for {formatted_date}</h3>", unsafe_allow_html=True)

        # Custom CSS for dark mode and layout
        st.markdown(
            """
            <style>
            body {
                background-color: #121212; /* Dark background */
                color: #ffffff; /* Light text for readability */
                display: flex;
                flex-direction: column;
                align-items: center; /* Center align all elements */
            }

            .card-container {
                display: flex;
                justify-content: center; /* Center the card layout */
                flex-wrap: wrap; /* Allow wrapping of cards */
                max-width: 100%; /* Set to full width for top items */
                margin: 20px auto; /* Center the container and add margin */
                padding: 20px; /* Add some padding to the container */
            }

            .entree-card {
                width: 150px;  /* Set fixed width for square cards */
                height: 150px; /* Set fixed height for square cards */
                border-radius: 15px;
                padding: 10px;
                margin: 10px;
                background-color: #1f1f1f; /* Dark card background */
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
                color: #ffffff; /* Light text color */
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center; /* Center content vertically */
                text-align: center;       /* Center the text */
                transition: transform 0.2s, box-shadow 0.2s; /* Smooth transition */
            }

            .entree-card:hover {
                transform: scale(1.05); /* Scale effect on hover */
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.7); /* Enhanced shadow on hover */
            }

            img {
                border-radius: 10px;
                width: 100%;
                height: 100%; /* Fill the card height */
                object-fit: cover; /* Maintain aspect ratio */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Container for the top entrees
        st.markdown("<div class='card-container'>", unsafe_allow_html=True)
        for entree in sorted_entrees[:3]:  # Display the top 3
            st.markdown(
                f"<div class='entree-card'>"
                f"<h3>{entree['rank']} - {entree['name']}</h3>"
                f"<img src='{entree['image_url']}' alt='{entree['name']} Image'>"
                f"<p><b>💪 Protein:</b> {entree['protein']}g</p>"
                f"<p><b>🔥 Calories:</b> {entree['calories']}</p>"
                f"<p><b>🧂 Sodium:</b> {entree['sodium'] if entree['sodium'] is not None else 'N/A'} mg</p>"
                f"<p><b>⚖️ Protein-to-Calorie Ratio:</b> {entree['protein_calorie_ratio']:.4f}</p>"
                f"</div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)  # Close the card container

else:
    st.error("❌ Error fetching data from the API.")
