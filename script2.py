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

# Define the API URL for the menu
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
        menu_option = st.sidebar.selectbox("Navigate", options=["Top 3 Rankings"])

        # Dynamic content for Top 3 Rankings
        if menu_option == "Top 3 Rankings":
            st.markdown("<h1 style='text-align: center; color: white;'>Top 3 High-Protein Entrées</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; color: white; margin-bottom: 1px;'>📅 Menu for {formatted_date}</h3>", unsafe_allow_html=True)

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

else:
    st.error("❌ Error fetching data from the API.")
