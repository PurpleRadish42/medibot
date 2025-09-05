import pandas as pd

df = pd.read_csv('Web_Scraping/practo_scraper/data/bangalore_doctors_complete.csv')
print("Shape:", df.shape)
print("Columns:", list(df.columns))
