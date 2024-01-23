import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

server = 'PHANDUCTRUONG\\SQLEXPRESS'
database = 'Demo_QLKH'
username = 'truong'
password = '123456'

sql_query = """
SELECT 
    c.name_customer,
    c.phone,
    c.age,
    r.comment_review,
    r.rateStar,
    r.total_like,
    r.date_reviews,
    p.name_product,
    pt.type_products,
    p.price,
    p.cost,
    b.isbought,
    b.date_bought
FROM products_type pt
JOIN products p ON pt.type_products_id = p.type_product_id
JOIN customers c ON p.product_id = c.product_id
JOIN reviews r ON p.product_id = r.product_id AND c.customer_id = r.customer_id
JOIN bought b ON p.product_id = b.product_id AND c.customer_id = b.customer_id;
"""

connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
df = pd.read_sql_query(sql_query, connection_string)

print(df.info())

sns.histplot(df['age'], bins=20, kde=True)
plt.title('Distribution of Customer Age')
plt.xlabel('Age')
plt.ylabel('Count')
plt.show()

sns.countplot(x='rateStar', data=df)
plt.title('Distribution of Ratings')
plt.xlabel('Rating')
plt.ylabel('Count')
plt.show()

plt.figure(figsize=(10, 6))
sns.countplot(x='type_products', data=df, hue='isbought')
plt.title('Product Type Distribution by Purchase Status')
plt.xlabel('Product Type')
plt.ylabel('Count')
plt.show()

plt.figure(figsize=(10, 6))
sns.scatterplot(x='price', y='rateStar', data=df, hue='isbought', size='total_like')
plt.title('Correlation between Product Price, Rating, and Likes')
plt.xlabel('Product Price')
plt.ylabel('Rating')
plt.show()

plt.figure(figsize=(12, 8))
sns.boxplot(x='type_products', y='rateStar', data=df)
plt.title('Rating Distribution by Product Type')
plt.xlabel('Product Type')
plt.ylabel('Rating')
plt.show()

numeric_columns = df.select_dtypes(include=['number']).columns

sns.pairplot(df[numeric_columns])
plt.suptitle('Pairwise Relationships and Distributions', y=1.02)
plt.show()

import pandas as pd
import plotly.express as px

# ... (your existing code for SQL query and data preparation)

# Plotly Histogram
fig = px.histogram(df, x='age', nbins=20, title='Distribution of Customer Age')
fig.show()

# Plotly Bar Chart
fig = px.bar(df, x='rateStar', title='Distribution of Ratings')
fig.show()

# Plotly Bar Chart with Grouping
fig = px.bar(df, x='type_products', color='isbought', title='Product Type Distribution by Purchase Status')
fig.show()

# Plotly Scatter Plot
fig = px.scatter(df, x='price', y='rateStar', color='isbought', size='total_like',
                 title='Correlation between Product Price, Rating, and Likes',
                 labels={'price': 'Product Price', 'rateStar': 'Rating'})
fig.show()

# Plotly Box Plot
fig = px.box(df, x='type_products', y='rateStar', title='Rating Distribution by Product Type',
             labels={'type_products': 'Product Type', 'rateStar': 'Rating'})
fig.show()

# Plotly Pair Plot
fig = px.scatter_matrix(df[numeric_columns], title='Pairwise Relationships and Distributions')
fig.update_layout(title=dict(x=0.5, y=0.95))
fig.show()

correlation_matrix = df[numeric_columns].corr()
fig = px.imshow(correlation_matrix, color_continuous_scale='Viridis', labels=dict(color='Correlation'))
fig.update_layout(title='Correlation Matrix')
fig.show()