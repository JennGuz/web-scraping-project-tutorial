from bs4 import BeautifulSoup
import requests
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

url = "https://www.macrotrends.net/stocks/charts/TSLA/tesla/revenue"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
response = requests.get(url, headers=headers)

if response.status_code == 200: 
    html_content = response.text
else:
    print("Error al acceder a la pagina", response.status_code)

soup = BeautifulSoup(html_content, 'html.parser')

all_tables = soup.find_all("table")
table_evolution = None

for idx, table in enumerate(all_tables):
    if "Tesla Quarterly Revenue" in str(table):
        table_evolution = table
        break

if table_evolution:
    tesla_revenue = pd.DataFrame(columns=["date", "revenue"])
    
    for row in table_evolution.find_all("tr")[1:]:
        cols = row.find_all("td")
        if cols:
            date = cols[0].text.strip()
            revenue = cols[1].text.strip().replace("$", "").replace(",", "")
            tesla_revenue = pd.concat([tesla_revenue, pd.DataFrame({
                "date": [date],
                "revenue": [revenue]
            })], ignore_index=True)

    # Convertir la columna 'revenue' a tipo numérico
    tesla_revenue['revenue'] = pd.to_numeric(tesla_revenue['revenue'], errors='coerce')
    
    # Extraer el año
    tesla_revenue['year'] = pd.to_datetime(tesla_revenue['date']).dt.year

    print(tesla_revenue.head())

    # Guardar en la base de datos
    conn = sqlite3.connect('Tesla.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS REVENUE (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            revenue REAL
        )
    ''')

    for index, row in tesla_revenue.iterrows():
        cursor.execute("INSERT INTO REVENUE (date, revenue) VALUES (?, ?)", (row['date'], row['revenue']))

    conn.commit()
    
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='year', y='revenue', data=tesla_revenue)
    plt.title("Tesla's Revenue Over Time")
    plt.xticks(rotation=45)
    plt.ylabel('Revenue')
    plt.xlabel('Year')
    plt.ylim(0, tesla_revenue['revenue'].max())
    plt.show()

    plt.figure(figsize=(10, 6))
    sns.boxplot(x='year', y='revenue', data=tesla_revenue)
    plt.title('Boxplot Tesla revenue', fontsize=16)
    plt.xticks(rotation=45) 
    plt.ylabel('Revenue (in millions)')
    plt.xlabel('Year')
    plt.show()

    plt.figure(figsize=(12, 6))
    sns.barplot(x='year', y='revenue', data=tesla_revenue, palette='coolwarm')
    plt.title('Tesla revenue', fontsize=16)
    plt.xticks(rotation=45)
    plt.ylabel('Revenue (in millions)')
    plt.xlabel('Year')
    plt.show()

else:
    print("Table not found Tesla Quarterly Revenue.")