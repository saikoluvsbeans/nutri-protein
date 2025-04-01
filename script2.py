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
        "salad": "🥗"
    }
    for key in emoji_dict.keys():
        if key in food_name:
            return emoji_dict[key]
    return "🍽️"

# Check if the request was successful
if response.status_code == 200:
    menu_data = response.json()
    unique_entrees = {}

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
            calories = nutrients.get("calories", 0)
            protein = nutrients.get("g_protein", 0)
            image_url = food.get("image_url")

            # Ensure a valid image URL
            if not image_url or not image_url.strip():
                image_url = "https://via.placeholder.com/150"  # Placeholder image

            # Only add unique entrees from the API
            if name not in unique_entrees:
                unique_entrees[name] = {
                    "name": name,
                    "calories": calories,
                    "protein": protein,
                    "protein_calorie_ratio": protein / calories if calories > 0 else 0,
                    "image_url": image_url,
                    "emoji": get_food_emoji(name)
                }

    # Sort by protein-to-calorie ratio in descending order and create rank
    sorted_entrees = sorted(unique_entrees.values(), key=lambda x: x["protein_calorie_ratio"], reverse=True)
    for index, entree in enumerate(sorted_entrees):
        entree["rank"] = index + 1  # Assign rank

    # Streamlit UI
    st.markdown("<h1 style='text-align: center;'>🔥 Top 3 High-Protein Entrées 🍽️</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>📅 Menu for {formatted_date}</h3>", unsafe_allow_html=True)

    # Custom CSS for centered layout and square images
    st.markdown(
        """
        <style>
        body {
            display: flex;
            flex-direction: column;
            align-items: center; /* Center align all elements */
        }

        .card-container {
            display: flex;
            justify-content: center; /* Center the card layout */
            flex-wrap: wrap; /* Allow wrapping of cards */
            max-width: 800px; /* Set a maximum width for better appearance */
            margin: 0 auto; /* Center the container */
            padding: 20px; /* Add some padding to the container */
        }

        .entree-card {
            width: 200px;  /* Fixed width for consistent sizing */
            height: 300px; /* Fixed height for cards, maintaining uniformity */
            border-radius: 15px;
            padding: 10px;
            margin: 10px;
            background-color: #ffffff;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            color: #333;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center; /* Center content vertically */
            text-align: center;       /* Center the text */
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
        </style>
        """,
        unsafe_allow_html=True
    )

    # Container for the cards
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
    search_item = st.text_input("Search for another food item:", "")
    
    if search_item:
        # Search the entered item in the unique_entrees dictionary
        search_item = search_item.lower()
        found_entree = next((entree for entree in sorted_entrees if entree['name'].lower() == search_item), None)

        if found_entree:
            st.markdown(
                f"<h3 style='text-align: center;'>Search Result for: {found_entree['name']}</h3>", 
                unsafe_allow_html=True
            )
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
else:
    st.info("Please enter a food item to see its protein-to-calorie ratio and rank.")
