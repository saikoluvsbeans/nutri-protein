import requests
import streamlit as st
from datetime import datetime

# Get today's date in the required format
current_date = datetime.today().strftime("%Y/%m/%d")
formatted_date = datetime.today().strftime("%B %d, %Y")

# Define the API URL with dynamic date
api_url = f"https://leanderisd.api.nutrislice.com/menu/api/weeks/school/glenn-high/menu-type/lunch/{current_date}/"

# Fetch the menu data from the Nutrislice API
response = requests.get(api_url)

# Function to assign appropriate emoji based on food name
def get_food_emoji(food_name):
    food_name = food_name.lower()
    emoji_dict = {
        "chicken": "🍗",
        "beef": "🥩",
        "steak": "🥩",
        "fish": "🐟",
        "salmon": "🐟",
        "pasta": "🍝",
        "burger": "🍔",
        "pizza": "🍕",
        "sandwich": "🥪",
        "salad": "🥗",
        "nugget": "🍗",
        "panini": "🥪"
    }
    for key in emoji_dict.keys():
        if key in food_name:
            return emoji_dict[key]
    return "🍽️"

# Check if the request was successful
if response.status_code == 200:
    menu_data = response.json()
    unique_entrees = {}
    archived_entrees = []

    # Iterate through each day's menu to create the food item list
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
            image_url = food.get("image_url")

            # Ensure a valid image URL and check for valid protein and calorie values
            if image_url and (calories is not None and calories > 0) and (protein is not None and protein > 0):
                unique_entrees[name] = {
                    "name": name,
                    "calories": calories,
                    "protein": protein,
                    "protein_calorie_ratio": protein / calories,
                    "image_url": image_url,
                    "emoji": get_food_emoji(name)
                }
            elif image_url:  # If there is an image but not necessarily valid nutritional values
                archived_entrees.append({
                    "name": name,
                    "calories": calories,
                    "protein": protein,
                    "image_url": image_url,
                    "emoji": get_food_emoji(name)
                })

    # Sort unique entrees by protein-to-calorie ratio and create rank
    sorted_entrees = sorted(unique_entrees.values(), key=lambda x: x["protein_calorie_ratio"], reverse=True)
    for index, entree in enumerate(sorted_entrees):
        entree["rank"] = index + 1  # Assign rank

    # Streamlit UI
    st.markdown("<h1 style='text-align: center; color: white;'>🔥 Top 3 High-Protein Entrées 🍽️</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: white;'>📅 Menu for {formatted_date}</h3>", unsafe_allow_html=True)

    # Custom CSS for dark mode and centered layout
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
            max-width: 800px; /* Set a maximum width for better appearance */
            margin: 20px auto; /* Center the container and add margin */
            padding: 20px; /* Add some padding to the container */
        }

        .entree-card {
            width: 200px;  /* Fixed width for consistent sizing */
            height: 300px; /* Fixed height for cards, maintaining uniformity */
            border-radius: 15px;
            padding: 10px;
            margin: 10px;
            background-color: #1f1f1f; /* Darker card background */
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
            height: 100px; /* Fixed height for square images */
            object-fit: cover; /* Ensure images are cropped to maintain square shape */
        }

        /* Responsive styles */
        @media (max-width: 600px) {
            .entree-card {
                width: 80%; /* Adjust width on mobile for better spacing */
                height: auto; /* Height adjusts based on content */
            }
            img {
                height: 150px; /* Square images for mobile */
            }
            h3 {
                font-size: 1.2rem; /* Smaller heading size on mobile */
            }
            p {
                font-size: 0.8rem; /* Smaller paragraph size on mobile */
            }
        }

        .archive-header {
            margin-top: 30px;
            font-size: 1.4rem;
            text-align: center;
            color: #ffffff; /* White color for clear visibility */
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
            f"<h3>{entree['rank']} - {entree['name']} {entree['emoji']}</h3>"
            f"<img src='{entree['image_url']}' alt='{entree['name']} Image'>"
            f"<p><b>💪 Protein:</b> {entree['protein']}g</p>"
            f"<p><b>🔥 Calories:</b> {entree['calories']}</p>"
            f"<p><b>⚖️ Protein-to-Calorie Ratio:</b> {entree['protein_calorie_ratio']:.4f}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)  # Close the card container

    # Search Functionality
    search_item = st.text_input("Search for another food item (e.g., 'nugget'):", "").strip()
    
    if search_item:
        # Search for entered term across the unique_entrees
        found_entrees = [entree for entree in sorted_entrees if search_item.lower() in entree['name'].lower()]

        if found_entrees:
            st.markdown(
                f"<h3 style='text-align: center; color: white;'>Search Results for: '{search_item}'</h3>", 
                unsafe_allow_html=True
            )
            # Display all found items
            for found_entree in found_entrees:
                st.markdown(
                    f"<div class='entree-card'>"
                    f"<h3>{found_entree['rank']} - {found_entree['name']} {found_entree['emoji']}</h3>"
                    f"<img src='{found_entree['image_url']}' alt='{found_entree['name']}'>"
                    f"<p><b>💪 Protein:</b> {found_entree['protein']}g</p>"
                    f"<p><b>🔥 Calories:</b> {found_entree['calories']}</p>"
                    f"<p><b>⚖️ Protein-to-Calorie Ratio:</b> {found_entree['protein_calorie_ratio']:.4f}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.error("😞 Sorry, no information found for that food item.")
    
    # Archive Section for Other Available Items
    if archived_entrees:
        st.markdown("<h3 class='archive-header'>📦 Other Available Items</h3>", unsafe_allow_html=True)
        st.markdown("<div class='card-container'>", unsafe_allow_html=True)
        for archived in archived_entrees:
            st.markdown(
                f"<div class='entree-card'>"
                f"<h3>{archived['name']} {archived['emoji']}</h3>"
                f"<img src='{archived['image_url']}' alt='{archived['name']}'>"
                f"<p><b>💪 Protein:</b> {archived['protein'] if archived['protein'] is not None else 'N/A'}g</p>"
                f"<p><b>🔥 Calories:</b> {archived['calories'] if archived['calories'] is not None else 'N/A'}</p>"
                f"</div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)  # Close the archive container
else:
    st.error("❌ Error fetching data from the API.")
