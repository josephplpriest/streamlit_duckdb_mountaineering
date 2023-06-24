import streamlit as st
import duckdb
import os
from PIL import Image
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Mountaineering: 1905 - 2019")

image = Image.open("./images/mount.jpg")
st.image(image, use_column_width=True)


files = [f"data/{file}" for file in os.listdir("./data")]
table_names = [file.split("/")[1].split(".")[0] for file in files]

for table_name, file in zip(table_names, files):
    try:
        duckdb.sql(
            f"""
                CREATE TABLE {table_name} as (SELECT * FROM '{file}')
                """
        )
    except duckdb.CatalogException:
        # Don't reload tables on a continuing session
        break


start_year, end_year = st.sidebar.slider("Select Date Range", 1900, 2020, (1900, 2020))


ascents = duckdb.sql(
    f"""
SELECT CAST(first_ascent_year as INT) as first_ascent, 
CAST(height_metres as INT) as height,
peak_name
FROM peaks
WHERE first_ascent_year != 'NA' AND 
CAST(first_ascent_year as INT) > {start_year}
AND
CAST(first_ascent_year as INT) < {end_year}
"""
).to_df()

ascents["peak_name"] = ascents["peak_name"].str.title()

fig = px.scatter(
    data_frame=ascents,
    x="first_ascent",
    y="height",
    hover_name="peak_name",
    symbol_sequence=["triangle-up"],
    title="First Ascent by Year, Peak Height"
)

st.plotly_chart(fig)

# Percentage of deaths by year
deaths = duckdb.sql(
f"""
SELECT m.year as year, 
SUM(CAST(died as INT)) / COUNT(1) as pct_deaths, 
COUNT(1) as 'Total Climbers' 
FROM members m 
WHERE m.year > {start_year}
AND m.year < {end_year}
GROUP BY m.year;
"""
).to_df()

fig = px.bar(
    data_frame=deaths,
    x="year",
    y="pct_deaths",
    hover_data={"Total Climbers":True, "pct_deaths":True, "year": True},
    title="Percentage of deaths vs total climbers by year"
)

st.plotly_chart(fig)

expedition_cnt = duckdb.sql(
    f"""
    SELECT COUNT(1) FROM expeditions e
    WHERE e.year > {start_year}
    AND e.year < {end_year}
    """
).fetchall()[0][0]

n_deaths = duckdb.sql(
    f"""
    SELECT COUNT(1) FROM members m
    WHERE m.year > {start_year}
    AND m.year < {end_year}
    AND died
"""
).fetchall()[0][0]

st.sidebar.metric("Expedition Count", expedition_cnt)
st.sidebar.metric("Total Deaths", n_deaths)


