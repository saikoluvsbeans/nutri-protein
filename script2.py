import requests
import streamlit as st
from datetime import datetime, timedelta
import pytz  # Make sure to install pytz

# Emoji mapping for food items with specific keyword handling
FOOD_EMOJIS = {
    "chicken enchilada": "🌮",  # Emoji for chicken enchiladas
    "pepperoni pizza": "🍕",    # Emoji for pepperoni pizza
    "meat lover's pizza": "🍕",  # Emoji for meat lovers pizza
    "vegetarian pizza": "🍕",    # Emoji for vegetarian pizza
    "salad": "🥗",               # Emoji for salad
    "cheeseburger": "🍔",        # Emoji for cheeseburger
    "hamburger": "🍔",           # Emoji for hamburger
    "hot dog": "🌭",             # Emoji for hot dog
    "taco": "🌮",                # Emoji for taco
    "spaghetti": "🍝",           # Emoji for spaghetti
    "fish": "🐟",                # Emoji for fish
    "chicken": "🍗",             # Emoji for chicken
    "breakfast": "🍳",           # Emoji for breakfast
    "default": "🍽️"             # Default food emoji
}

# Function to get the emoji based on food name
def get_food_emoji(name):
    # Normalize food name to lower case
    normalized_name = name.lower()
    for food in FOOD_EMOJIS.keys():
        if food in normalized_name:
            return FOOD_EMOJIS[food]
    return FOOD_EMOJIS['default']  # Return default if no match found

# Get the current date and time in Austin, Texas
austin_tz = pytz.timezone('America/Chicago')  # Austin is in Central Time Zone
current_time = datetime.now(austin_tz)

# Ensure we are on the correct date, account properly for changes after midnight.
if current_time.hour < 6:  # Assuming services start at 6 AM
    current_date = (current_time - timedelta(days=1)).strftime("%Y/%m/%d")
else:
    current_date = current_time.strftime("%Y/%m/%d")

formatted_date = current_time.strftime("%B %d, %Y")

# Define the API URL for the lunch menu
api_url_lunch = f"https://leanderisd.api.nutrislice.com/menu/api/weeks/school/glenn-high/menu-type/lunch/{current_date}/"

# Fetch the lunch menu data from the Nutrislice API
response_lunch = requests.get(api_url_lunch)

# Check if the request was successful for lunch menu
if response_lunch.status_code == 200:
    menu_data_lunch = response_lunch.json()
    unique_entrees = {}

    # Iterate through each day's menu to build the food item list for the lunch current date
    for day in menu_data_lunch.get("days", []):
        for item in day.get("menu_items", []):
            food = item.get("food")
            if not food:
                continue

            category = food.get("food_category", "").lower()
            if category != "entree":
                continue

            name = food.get("name", "Unknown Item")

            nutrients = food.get("rounded_nutrition_info", {})
            calories = nutrients.get("calories")
            protein = nutrients.get("g_protein")
            sodium = nutrients.get("mg_sodium")  # Added sodium field

            # Use an emoji instead of an image
            emoji = get_food_emoji(name)  # Get emoji for the food item

            # Ensure valid nutritional values before adding to unique_entrees
            if calories is not None and calories > 0 and protein is not None and protein > 0:
                unique_entrees[name] = {
                    "name": name,
                    "calories": calories,
                    "protein": protein,
                    "sodium": sodium,
                    "protein_calorie_ratio": protein / calories,
                    "emoji": emoji  # Assign emoji directly
                }

    # Sort unique entrees by protein-to-calorie ratio and create rank
    sorted_entrees = sorted(unique_entrees.values(), key=lambda x: x["protein_calorie_ratio"], reverse=True)
    for index, entree in enumerate(sorted_entrees):
        entree["rank"] = index + 1  # Assign rank

    # Make sure we filter for actual available menu items
    if not sorted_entrees:
        st.error("❌ No available items for the current menu date.")
    else:
        # Streamlit Sidebar Menu (only Top 3 Rankings option)
        st.sidebar.title("Menu")
        menu_option = st.sidebar.selectbox("Navigate", options=["Top 3 Lunch Rankings", "Top 3 Breakfast Rankings"])

        # Dynamic content for Top 3 Lunch Rankings
        if menu_option == "Top 3 Lunch Rankings":
            st.markdown("<h1 style='text-align: center; color: white;'>Top 3 High-Protein Entrées</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; color: white; margin-bottom: 10px;'>📅 Menu for {formatted_date}</h3>", unsafe_allow_html=True)

            # Custom CSS for dark mode and layout adjustments
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
                    justify-content: space-around; /* Evenly space cards */
                    flex-wrap: wrap; /* Allow wrapping of cards */
                    width: 100%; /* Full width for the container */
                    margin: 10px 0; /* Reduce top margin to bring cards closer */
                    padding: 20px; /* Add some padding to the container */
                }

                .entree-card {
                    flex: 1 1 30%; /* Allow cards to grow and shrink, with a base width of 30% */
                    height: auto;   /* Set auto height for cards */
                    border-radius: 15px;
                    padding: 10px;
                    margin: 10px; /* Space around cards */
                    background-color: #1f1f1f; /* Dark card background */
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
                    color: #ffffff; /* Light text color */
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center; /* Center content vertically */
                    text-align: center;       /* Center the text */
                }

                .nutritional-info {
                    font-size: 16px;  /* Standard text size for nutrition info */
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
                    f"<p style='font-size: 72px; margin: 0;'>{entree['emoji']}</p>"  # Directly style the emoji
                    f"<p class='nutritional-info'><b>💪 Protein:</b> {entree['protein']}g</p>"
                    f"<p class='nutritional-info'><b>🔥 Calories:</b> {entree['calories']}</p>"
                    f"<p class='nutritional-info'><b>🧂 Sodium:</b> {entree['sodium'] if entree['sodium'] is not None else 'N/A'} mg</p>"
                    f"<p class='nutritional-info'><b>⚖️ Protein-to-Calorie Ratio:</b> {entree['protein_calorie_ratio']:.4f}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)  # Close the card container

        # Dynamic content for Top 3 Breakfast Rankings
        elif menu_option == "Top 3 Breakfast Rankings":
            # Fetch the breakfast menu data from the Nutrislice API
            breakfast_api_url = "https://leanderisd.api.nutrislice.com/menu/api/weeks/school/glenn-high/menu-type/breakfast/2025/04/01/"
            response_breakfast = requests.get(breakfast_api_url)

            # Check if the request was successful for breakfast menu
            if response_breakfast.status_code == 200:
                breakfast_data = response_breakfast.json()
                unique_breakfasts = {}

                # Iterate through the breakfast menu to build the food item list
                for breakfast_item in breakfast_data.get("days", []):
                    for item in breakfast_item.get("menu_items", []):
                        food = item.get("food")
                        if not food:
                            continue

                        category = food.get("food_category", "").lower()
                        if category != "breakfast":
                            continue
                        
                        name = food.get("name", "Unknown Item")
                        nutrients = food.get("rounded_nutrition_info", {})
                        calories = nutrients.get("calories")
                        sugars = nutrients.get("g_sugar")  # Added sugar field

                        # Use an emoji for breakfast
                        emoji = get_food_emoji(name)  # Get emoji for the food item

                        # Ensure valid nutritional values before adding to unique_breakfasts
                        if calories is not None and calories > 0 and sugars is not None and sugars >= 0:
                            unique_breakfasts[name] = {
                                "name": name,
                                "calories": calories,
                                "sugars": sugars,
                                "emoji": emoji  # Assign emoji directly
                            }

                # Sort unique breakfasts by calories first, and then by sugars
                sorted_breakfasts = sorted(unique_breakfasts.values(), key=lambda x: (x["calories"], x["sugars"]))
                for index, breakfast in enumerate(sorted_breakfasts):
                    breakfast["rank"] = index + 1  # Assign rank

                # Make sure we filter for actual available menu items
                if not sorted_breakfasts:
                    st.error("❌ No available breakfast items for the specified date.")
                else:
                    # Container for the top breakfasts
                    st.markdown("<h1 style='text-align: center; color: white;'>Top 3 Low-Sugar Breakfasts</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h3 style='text-align: center; color: white; margin-bottom: 10px;'>📅 Breakfast Menu</h3>", unsafe_allow_html=True)

                    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
                    for breakfast in sorted_breakfasts[:3]:  # Display the top 3
                        st.markdown(
                            f"<div class='entree-card'>"
                            f"<h3>{breakfast['rank']} - {breakfast['name']}</h3>"
                            f"<p style='font-size: 72px; margin: 0;'>{breakfast['emoji']}</p>"  # Directly style the emoji
                            f"<p class='nutritional-info'><b>🔥 Calories:</b> {breakfast['calories']}</p>"
                            f"<p class='nutritional-info'><b>🍬 Sugars:</b> {breakfast['sugars']}g</p>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    st.markdown("</div>", unsafe_allow_html=True)  # Close the card container
            else:
                st.error("❌ Error fetching data from the breakfast API.")

else:
    st.error("❌ Error fetching data from the lunch API.")
