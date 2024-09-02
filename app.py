import streamlit as st
import requests
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Function to get list of US states
def get_us_states():
    response = requests.get("https://api.census.gov/data/2010/dec/sf1?get=NAME&for=state:*")
    states = [item[0] for item in response.json()[1:]]
    return sorted(states)

# Function to get cities in a state
def get_cities(state):
    response = requests.get(f"https://api.census.gov/data/2019/pep/population?get=NAME,POP&for=place:*&in=state:{state_codes[state]}")
    data = response.json()[1:]  # Skip the header row
    
    # Create a dictionary of cleaned city names to their full names and place IDs
    city_dict = {}
    for item in data:
        full_name, pop, state, place = item
        city_name = full_name.split(',')[0].strip()
        # Remove 'city', 'town', 'CDP', etc. from the end of the name
        city_name = ' '.join(word for word in city_name.split() if word.lower() not in ['city', 'town', 'cdp', 'village'])
        city_dict[city_name] = {'full_name': full_name, 'place_id': place}
    
    # Debug: Print the first few entries of city_dict
    # st.write("Debug - First few entries of city_dict:")
    # st.write(dict(list(city_dict.items())[:5]))
    
    return city_dict

# Function to get median home value and household income
def get_city_data(state, city_info):
    state_code = state_codes[state]
    place_id = city_info['place_id']
    
    # Get median home value
    home_value_url = f"https://api.census.gov/data/2019/acs/acs5?get=B25077_001E&for=place:{place_id}&in=state:{state_code}"
    home_value_response = requests.get(home_value_url)
    home_value_data = home_value_response.json()[1][0]  # Get the actual value
    
    # Get median household income
    income_url = f"https://api.census.gov/data/2019/acs/acs5?get=B19013_001E&for=place:{place_id}&in=state:{state_code}"
    income_response = requests.get(income_url)
    income_data = income_response.json()[1][0]  # Get the actual value
    
    # Debug: Print API responses
    # st.write("Debug - Home Value API Response:", home_value_response.json())
    # st.write("Debug - Income API Response:", income_response.json())
    
    return int(home_value_data), int(income_data)

# Function to calculate home buying score
def calculate_score(home_value, income):
    if home_value is None or income is None or income == 0:
        return None
    
    price_to_income_ratio = home_value / income
    st.write(f"P to I Ratio: {price_to_income_ratio:,}")
    # Scale the ratio to a score between 1 and 5
    scaler = MinMaxScaler(feature_range=(1, 5))
    score = scaler.fit_transform([[price_to_income_ratio]])[0][0]
    st.write(f"Score: {score:,}")
    # Invert the score (lower ratio is better)
    return 6 - score

# Dictionary to map state names to their codes
state_codes = {
    "Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05", "California": "06",
    "Colorado": "08", "Connecticut": "09", "Delaware": "10", "Florida": "12", "Georgia": "13",
    "Hawaii": "15", "Idaho": "16", "Illinois": "17", "Indiana": "18", "Iowa": "19",
    "Kansas": "20", "Kentucky": "21", "Louisiana": "22", "Maine": "23", "Maryland": "24",
    "Massachusetts": "25", "Michigan": "26", "Minnesota": "27", "Mississippi": "28", "Missouri": "29",
    "Montana": "30", "Nebraska": "31", "Nevada": "32", "New Hampshire": "33", "New Jersey": "34",
    "New Mexico": "35", "New York": "36", "North Carolina": "37", "North Dakota": "38", "Ohio": "39",
    "Oklahoma": "40", "Oregon": "41", "Pennsylvania": "42", "Rhode Island": "44", "South Carolina": "45",
    "South Dakota": "46", "Tennessee": "47", "Texas": "48", "Utah": "49", "Vermont": "50",
    "Virginia": "51", "Washington": "53", "West Virginia": "54", "Wisconsin": "55", "Wyoming": "56"
}

st.title("Home Buying Score App")

# Get list of states
states = get_us_states()

# Create a dropdown for state selection
selected_state = st.selectbox("Select a State", states)

# Get cities for the selected state
cities_dict = get_cities(selected_state)
city_names = list(cities_dict.keys())

# Create a dropdown for city selection
selected_city = st.selectbox("Select a City", city_names)

# Debug: Print selected city and its info
# st.write("Debug - Selected City:", selected_city)
# st.write("Debug - Selected City Info:", cities_dict.get(selected_city, "Not found"))

if st.button("Calculate Score"):
    st.write(f"Calculating score for {selected_city}, {selected_state}...")
    
    # Get city data
    city_info = cities_dict[selected_city]
    home_value, income = get_city_data(selected_state, city_info)
    
    if home_value is not None and income is not None:
        # Calculate score
        score = calculate_score(home_value, income)
        
        if score is not None:
            st.write(f"Median Home Value: ${home_value:,}")
            st.write(f"Median Household Income: ${income:,}")
            st.write(f"Home Buying Score: {score:.2f} / 5.00")
            
            # Interpretation of the score
            if score >= 4:
                st.write("Interpretation: Excellent time to buy!")
            elif score >= 3:
                st.write("Interpretation: Good time to buy.")
            elif score >= 2:
                st.write("Interpretation: Moderate buying conditions.")
            else:
                st.write("Interpretation: May be challenging to buy. Consider saving more or exploring other areas.")
        else:
            st.write("Unable to calculate score. There might be an issue with the data.")
    else:
        st.write("Unable to retrieve data for this city. It may not be available in our dataset.")