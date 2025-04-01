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

    # Iterate through each day's menu
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

    # Sort by protein-to-calorie ratio in descending order
    sorted_entrees = sorted(unique_entrees.values(), key=lambda x: x["protein_calorie_ratio"], reverse=True)[:3]

    # Streamlit UI
    st.title("🔥 Top 3 High-Protein Entrées 🍽️")
    st.markdown(f"### 📅 Menu for {formatted_date}")

    # Custom CSS for cards with square images
    st.markdown(
        """
        <style>
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
            height: 100px; /* Fixed height for square-like appearance */
            object-fit: cover; /* Ensures images fill the space without distortion */
        }

        /* Responsive styles */
        @media (max-width: 600px) {
            .entree-card {
                width: 80%; /* Adjust width on mobile for better spacing */
                height: auto; /* Height adjusts based on content */
            }
            img {
                height: 100px; /* Fixed height for square images */
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

    for rank, entree in enumerate(sorted_entrees, start=1):
        with st.container():
            st.markdown(
                f"<div class='entree-card'>"
                f"<h3>{rank} - {entree['name']} {entree['emoji']}</h3>"
                f"<img src='{entree['image_url']}' alt='{entree['name']} Image'>"
                f"<p><b>💪 Protein:</b> {entree['protein']}g</p>"
                f"<p><b>🔥 Calories:</b> {entree['calories']}</p>"
                f"<p><b>⚖️ Protein-to-Calorie Ratio:</b> {entree['protein_calorie_ratio']:.4f}</p>"
                f"</div>",
                unsafe_allow_html=True
            )
else:
    st.error("❌ Error fetching data from the API.")
