# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write("Choose the fruits you want in your custom Smoothie!")

# Input name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit list
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()

fruit_list = my_dataframe["FRUIT_NAME"].tolist()

# Fruit selector
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Convert list to string
if ingredients_list:
    ingredients_string = ",".join(ingredients_list)
    st.write("Your ingredients:", ingredients_string)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")

# Nutrition info from SmoothieFroot API
for fruit_chosen in ingredients_list:
    st.subheader(f"{fruit_chosen} Nutrition Information")

    smoothiefroot_response = requests.get(
        "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
    )

    if smoothiefroot_response.status_code == 200:
        sf_df = pd.DataFrame([smoothiefroot_response.json()])
        st.dataframe(sf_df, use_container_width=True)
