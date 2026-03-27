# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')

st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options from Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert to pandas for Streamlit
fruit_df = my_dataframe.to_pandas()

# Extract list of fruits
fruit_list = fruit_df["FRUIT_NAME"].tolist()

# Multiselect for fruits
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# If user selects fruits
if ingredients_list:

    ingredients_string = ",".join(ingredients_list)

    st.write("Your ingredients:", ingredients_string)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")

# -------------------------------
# SmoothieFroot Nutrition Section
# -------------------------------

for fruit_chosen in ingredients_list:

    st.subheader(fruit_chosen + " Nutrition Information")

    smoothiefroot_response = requests.get(
        "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
    )

    if smoothiefroot_response.status_code == 200:

        # Convert JSON → DataFrame
        sf_df = pd.DataFrame([smoothiefroot_response.json()])

        # Display dataframe
        st.dataframe(sf_df, use_container_width=True)

    else:
        st.error("Failed to retrieve nutrition data.")
