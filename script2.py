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
    archived_entrees_dict = {}  # Use a dictionary to prevent duplicates

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
                # Store unique archived entrees in a dictionary to ensure no duplicates
                archived_entrees_dict[name] = {
                    "name": name,
                    "calories": calories,
                    "protein": protein,
                    "sodium": sodium,
                    "image_url": image_url
                }
            elif image_url:  # If only an image exists, archive the item
                archived_entrees_dict[name] = {
                    "name": name,
                    "calories": calories,
                    "protein": protein,
                    "sodium": sodium,
                    "image_url": image_url
                }

    # Convert archived items back to a list
    archived_entrees = list(archived_entrees_dict.values())

    # Sort unique entrees by protein-to-calorie ratio and create rank
    sorted_entrees = sorted(unique_entrees.values(), key=lambda x: x["protein_calorie_ratio"], reverse=True)
    for index, entree in enumerate(sorted_entrees):
        entree["rank"] = index + 1  # Assign rank

    # Streamlit Sidebar Menu
    st.sidebar.title("Menu")
    menu_option = st.sidebar.selectbox("Navigate", options=["Top 3 Rankings", "Archive", "Search"])

    # Dynamic content based on the selected menu option
    if menu_option == "Top 3 Rankings":
        st.markdown("<h1 style='text-align: center; color: white;'>🔥 Top 3 High-Protein Entrées</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: white;'>📅 Menu for {formatted_date}</h3>", unsafe_allow_html=True)

        # Custom CSS for dark mode and full width top 3 layout
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

            /* Responsive styles */
            @media (max-width: 600px) {
                .entree-card {
                    width: 100%; /* Full width on mobile */
                    height: auto; /* Allow auto height on mobile */
                }
            }

            .archive-header {
                margin-top: 30px;
                font-size: 1.4rem;
                text-align: center;
                color: #ffffff; /* White color for clear visibility */
            }

            .archive-container {
                display: grid;
                grid-template-columns: repeat(2, 1fr); /* Two-column grid layout */
                gap: 10px; /* Space between grid items */
                margin: 20px; /* Space around grid */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Container for the top entrees
        st.markdown("<div class='card-container'>", unsafe_allow_html=True)
        for entree in sorted_entrees[:3]:  # Displaying only top 3 for the main section
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

    elif menu_option == "Archive":
        st.markdown("<h3 style='text-align: center; color: white;'>📦 All Available Items</h3>", unsafe_allow_html=True)
        st.markdown("<div class='archive-container'>", unsafe_allow_html=True)  # Use grid container
        for archived in archived_entrees:
            st.markdown(
                f"<div class='entree-card'>"
                f"<h3>{archived['name']}</h3>"  # Removed emoji
                f"<img src='{archived['image_url']}' alt='{archived['name']}'>"
                f"<p><b>💪 Protein:</b> {archived['protein'] if archived['protein'] is not None else 'N/A'}g</p>"
                f"<p><b>🔥 Calories:</b> {archived['calories'] if archived['calories'] is not None else 'N/A'}</p>"
                f"<p><b>🧂 Sodium:</b> {archived['sodium'] if archived['sodium'] is not None else 'N/A'} mg</p>"
                f"</div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)  # Close the archive container

    elif menu_option == "Search":
        search_item = st.text_input("Search for another food item (e.g., 'nugget'):", "").strip()
        if search_item:
            # Search for entered term across the unique_entrees
            found_entrees = [entree for entree in sorted_entrees if search_item.lower() in entree['name'].lower()]
            if found_entrees:
                st.markdown(
                    f"<h3 style='text-align: center; color: white;'>Search Results for: '{search_item}'</h3>", 
                    unsafe_allow_html=True
                )
                for found_entree in found_entrees:
                    st.markdown(
                        f"<div class='entree-card'>"
                        f"<h3>{found_entree['rank']} - {found_entree['name']}</h3>"  # Removed emoji
                        f"<img src='{found_entree['image_url']}' alt='{found_entree['name']}'>"
                        f"<p><b>💪 Protein:</b> {found_entree['protein']}g</p>"
                        f"<p><b>🔥 Calories:</b> {found_entree['calories']}</p>"
                        f"<p><b>🧂 Sodium:</b> {found_entree['sodium'] if found_entree['sodium'] is not None else 'N/A'} mg</p>"
                        f"<p><b>⚖️ Protein-to-Calorie Ratio:</b> {found_entree['protein_calorie_ratio']:.4f}</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
            else:
                st.error("😞 Sorry, no information found for that food item.")
else:
    st.error("❌ Error fetching data from the API.")
