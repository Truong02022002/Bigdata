import hashlib
import os
from flask import Flask, session
import app
import pyodbc
from config import SQL_SERVER, SQL_DATABASE, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

class ItemDatabase:
    def __init__(self):
        try:
            connection_string = f'DRIVER={{SQL Server}}; SERVER={SQL_SERVER}; DATABASE={SQL_DATABASE};'
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print("Error connecting to the database:", e)
            
    def get_items(self, table_name):
        query = ""
        if table_name == 'products_type':
            query = "SELECT * FROM products_type"
        elif table_name == 'products':
            query = """
                SELECT p.product_id, p.name_product, p.price, p.cost, pt.type_products
                FROM products p
                INNER JOIN products_type pt ON p.type_product_id = pt.type_products_id
            """
        elif table_name == 'reviews':
            query = """
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
        
        try:
            self.cursor.execute(query)
            columns = [column[0] for column in self.cursor.description]
            items = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            
            return columns, items
        except Exception as e:
            print("Error executing query:", e)
            return [], []

    def search_items(self, table_name, search_term):
        columns, items = [], []
        if search_term:
            query = ""
            params = ()
            
            if table_name == 'products_type':
                query = """
                    SELECT * 
                    FROM products_type 
                    WHERE type_products LIKE ?
                """
                params = ('%' + search_term + '%',)
            elif table_name == 'products':
                query = """
                    SELECT 
                        p.product_id, 
                        p.name_product, 
                        p.price, 
                        p.cost, 
                        pt.type_products 
                    FROM products p 
                    INNER JOIN products_type pt ON p.type_product_id = pt.type_products_id 
                    WHERE 
                        p.name_product LIKE ? OR 
                        p.price LIKE ? OR 
                        p.cost LIKE ? OR 
                        pt.type_products LIKE ?
                """
                params = ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%')
            elif table_name == 'reviews':
                query = """
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
                    JOIN bought b ON p.product_id = b.product_id AND c.customer_id = b.customer_id
                    WHERE 
                        c.name_customer LIKE ? OR
                        c.phone LIKE ? OR
                        c.age LIKE ? OR
                        r.comment_review LIKE ? OR
                        r.rateStar LIKE ? OR
                        r.total_like LIKE ? OR
                        r.date_reviews LIKE ? OR
                        p.name_product LIKE ? OR
                        pt.type_products LIKE ? OR
                        p.price LIKE ? OR
                        p.cost LIKE ? OR
                        b.isbought LIKE ? OR
                        b.date_bought LIKE ?
                """
                params = tuple(['%' + search_term + '%'] * 13)

            try:
                self.cursor.execute(query, params)
                columns = [column[0] for column in self.cursor.description]
                items = [dict(zip(columns, row)) for row in self.cursor.fetchall()]

            except Exception as e:
                print("Error executing query:", e)

        return columns, items
    def insert_items(self, table_name):
        query = ""
        if table_name == 'products_type':
            query = """
                INSERT INTO products_type (type_products)
                VALUE (?)
            """
        elif table_name == 'products':
            query = """
                INSERT INTO products (name_product, price, cost, type_product_id)
                VALUE (?,?,?,?)
            """
        elif table_name == 'reviews':
            if table_name == 'customers':
                query = """
                    INSERT INTO products (name_customer, phone, age, product_id)
                    VALUE (?,?,?,?)
                """
            elif table_name == 'review':
                query = """
                    INSERT INTO products (rate_star, comment_reviews, total_like, date_reviews, product_id, customer_id)
                    VALUE (?,?,?,?,?,?)
                """
            elif table_name == 'bought':
                query = """
                    INSERT INTO products (isbought, date_bought, product_id, customer_id)
                    VALUE (?,?,?,?)
                """
        
        try:
            self.cursor.execute(query)
            columns = [column[0] for column in self.cursor.description]
            items = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            
            return columns, items
        except Exception as e:
            print("Error executing query:", e)
            return [], []
    
db = ItemDatabase()

class NewDatabase:
    def __init__(self):
        try:
            connection_string = f'DRIVER={{SQL Server}}; SERVER={SQL_SERVER}; DATABASE={SQL_DATABASE};'
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print("Error connecting to the database:", e)

    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            columns = [column[0] for column in self.cursor.description]
            items = [dict(zip(columns, row)) for row in self.cursor.fetchall()]

            return columns, items

        except Exception as e:
            print("Error executing query:", e)
            return [], []

    def generate_sales_dashboard(self, dashboard):
        query = ""
        
        if dashboard == 'none':
            query = """"""
        elif dashboard == "percentage_bought":
            query = """
                SELECT
                    cast(round((num_bought * 100.0 / total),2) as decimal(5,2)) AS percentage_bought,
                    cast(round((num_not_bought * 100.0 / total),2) as decimal(5,2)) AS percentage_not_bought
                FROM
                    (
                        SELECT
                            COUNT(DISTINCT R.customer_id) AS total,
                            COUNT(DISTINCT CASE WHEN B.isbought = 1 THEN C.customer_id END) AS num_bought,
                            COUNT(DISTINCT CASE WHEN B.isbought = 0 THEN C.customer_id END) AS num_not_bought
                        FROM
                            customers C
                        JOIN
                            bought B ON C.customer_id = B.customer_id
                        JOIN
                            reviews R ON C.customer_id = R.customer_id
                    ) AS subquery;
            """
        elif dashboard == "compare":
            query = """
                SELECT
                    YEAR(b.date_bought) AS year,
                    MONTH(b.date_bought) AS month,
                    SUM(p.price) AS total_revenue
                FROM
                    bought b
                JOIN
                    products p ON b.product_id = p.product_id
                WHERE
                    (YEAR(date_bought) = 2021 OR YEAR(date_bought) = 2022 OR YEAR(date_bought) = 2023)
                GROUP BY
                    YEAR(b.date_bought),
                    MONTH(b.date_bought)
                ORDER BY
                    year, month;
            """
        elif dashboard == "compares":
            query = """
                SELECT 
                    YEAR(date_bought) AS year,
                    MONTH(date_bought) AS month,
                    COUNT(isbought) AS Bought
                FROM bought
                WHERE
                    (YEAR(date_bought) = 2021 OR YEAR(date_bought) = 2022 OR YEAR(date_bought) = 2023)
                GROUP BY YEAR(date_bought), MONTH(date_bought)
                ORDER BY year, month;
            """
        elif dashboard == "type_product":
            query = """
                SELECT 
                    pt.type_products AS Type,
                    COUNT(b.isbought) AS Bought
                FROM products_type pt
                JOIN products p ON p.type_product_id = pt.type_products_id
                JOIN bought b ON b.product_id = p.product_id
                Where b.isbought = 'True'
                GROUP BY pt.type_products;
            """
        elif dashboard == "age":
            query = """
                SELECT 
                    CASE 
                        WHEN c.age BETWEEN 18 AND 20 THEN '18-20'
                        WHEN c.age BETWEEN 21 AND 25 THEN '21-25'
                        WHEN c.age BETWEEN 26 AND 30 THEN '26-30'
                        WHEN c.age BETWEEN 31 AND 35 THEN '31-35'
                        WHEN c.age BETWEEN 36 AND 40 THEN '36-40'
                        WHEN c.age BETWEEN 41 AND 45 THEN '41-45'
                        WHEN c.age BETWEEN 46 AND 50 THEN '46-50'
                        WHEN c.age BETWEEN 51 AND 55 THEN '51-55'
                        WHEN c.age BETWEEN 56 AND 60 THEN '56-60'
                        ELSE 'Unknown'
                    END AS AgeRange,
                    COUNT(b.isBought) AS BoughtCount
                FROM 
                    products p
                JOIN 
                    customers c ON p.product_id = c.product_id
                JOIN 
                    bought b ON b.customer_id = c.customer_id
                WHERE 
                    b.isBought = 'True'
                GROUP BY 
                    CASE 
                        WHEN c.age BETWEEN 18 AND 20 THEN '18-20'
                        WHEN c.age BETWEEN 21 AND 25 THEN '21-25'
                        WHEN c.age BETWEEN 26 AND 30 THEN '26-30'
                        WHEN c.age BETWEEN 31 AND 35 THEN '31-35'
                        WHEN c.age BETWEEN 36 AND 40 THEN '36-40'
                        WHEN c.age BETWEEN 41 AND 45 THEN '41-45'
                        WHEN c.age BETWEEN 46 AND 50 THEN '46-50'
                        WHEN c.age BETWEEN 51 AND 55 THEN '51-55'
                        WHEN c.age BETWEEN 56 AND 60 THEN '56-60'
                        ELSE 'Unknown'
                    END
                ORDER BY 
                    AgeRange;
            """
        elif dashboard == "products":
            query = """
                SELECT TOP 10
                    COUNT(b.isBought) AS bought,
                    SUBSTRING(p.name_product, 1, 26) AS short_name,
                    p.name_product
                FROM products p
                JOIN bought b ON p.product_id = b.product_id
                GROUP BY p.name_product
                ORDER BY bought DESC;
            """
        elif dashboard == "products_price":
            query = """
                SELECT TOP 10
                    SUM(p.price) AS total_revenue,
                    SUBSTRING(p.name_product, 1, 26) AS short_name,
                    p.name_product
                FROM products p
                JOIN bought b ON p.product_id = b.product_id
                GROUP BY p.name_product
                ORDER BY total_revenue DESC;
            """
        elif dashboard == "reviews_rateStar":
            query = """
                SELECT TOP 10
                    COUNT(r.rateStar) AS NumberOf5StarReviews,
                    SUBSTRING(p.name_product, 1, 26) AS short_name,
                    p.name_product
                FROM products p
                JOIN reviews r ON r.product_id = p.product_id
                WHERE r.rateStar = 5
                GROUP BY p.name_product
                ORDER BY NumberOf5StarReviews DESC;
            """
        elif dashboard == "rateStars":
            query = """
                    SELECT
                        r.rateStar,
                        SUM(CASE WHEN b.isbought = 1 THEN 1 ELSE 0 END) AS NumberOfReviews_Bought,
                        SUM(CASE WHEN b.isbought = 0 OR b.isbought IS NULL THEN 1 ELSE 0 END) AS NumberOfReviews_NotBought,
                        COUNT(r.rateStar) AS TotalNumberOfReviews
                    FROM products p
                    JOIN reviews r ON r.product_id = p.product_id
                    JOIN customers c ON c.customer_id = r.customer_id
                    LEFT JOIN bought b ON b.product_id = p.product_id AND b.customer_id = c.customer_id
                    GROUP BY r.rateStar
                    ORDER BY TotalNumberOfReviews DESC;
            """
        elif dashboard == "discounts":
            query = """
                SELECT
                    (p.cost - p.price) AS discount,
                    SUBSTRING(p.name_product, 1, 26) AS short_name,
                    p.name_product,
                    COUNT(b.isBought) AS bought_count
                FROM products p
                JOIN bought b ON p.product_id = b.product_id
                WHERE b.isBought = 'True'
                GROUP BY p.name_product, p.cost, p.price
                ORDER BY discount DESC;
            """
        elif dashboard == "price":
            query = """
                SELECT
                    p.cost,
                    p.price,
                    (p.cost - p.price) AS discount,
                    SUBSTRING(p.name_product, 1, 26) AS short_name,
                    p.name_product,
                    COUNT(b.isBought) AS bought_count
                FROM products p
                JOIN bought b ON p.product_id = b.product_id
                WHERE b.isBought = 'True'
                GROUP BY p.name_product, p.price, p.cost
                ORDER BY p.price DESC;
            """
        elif dashboard == "comment_review":
            query = """
                SELECT
                    SUBSTRING(p.name_product, 1, 26) AS short_name,
                    p.name_product,
                    COUNT(r.comment_review) AS count_comment
                FROM products p
                JOIN reviews r ON r.product_id = p.product_id
                JOIN customers c ON c.customer_id = r.customer_id
                LEFT JOIN bought b ON b.product_id = p.product_id AND b.customer_id = c.customer_id
                WHERE b.isbought IS NULL OR b.isbought = 'False'
                GROUP BY p.name_product
                ORDER BY count_comment DESC;
            """
        elif dashboard == "sumtotallikes":
            query = """
                SELECT
                    SUBSTRING(p.name_product, 1, 26) AS short_name,
                    p.name_product,
                    SUM(r.total_like) AS sumtotallike
                FROM products p
                JOIN reviews r ON r.product_id = p.product_id
                JOIN customers c ON c.customer_id = r.customer_id
                LEFT JOIN bought b ON b.product_id = p.product_id AND b.customer_id = c.customer_id
                GROUP BY p.name_product
                ORDER BY sumtotallike DESC;
            """
        elif dashboard == "countrateStars":
            query = """
                SELECT
                    SUBSTRING(p.name_product, 1, 26) AS short_name,
                    p.name_product,
                    COUNT(r.rateStar) AS NumberOfReviews
                FROM products p
                JOIN reviews r ON r.product_id = p.product_id
                JOIN customers c ON c.customer_id = r.customer_id
                LEFT JOIN bought b ON b.product_id = p.product_id AND b.customer_id = c.customer_id
                WHERE r.rateStar = 5.0
                GROUP BY p.name_product, r.rateStar
                ORDER BY NumberOfReviews DESC;
            """
        
        return self.execute_query(query)

class UserDatabase:
    def __init__(self):
        try:
            connection_string = f'DRIVER={{SQL Server}}; SERVER={SQL_SERVER}; DATABASE={SQL_DATABASE};'
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print("Error connecting to the database:", e)

    def authenticate_user(self, identifier, password):
        query = "SELECT username, email FROM accounts WHERE (username = ? OR email = ?) AND password_hash = ?"
        params = (identifier, identifier, hashlib.sha256(password.encode()).hexdigest())

        try:
            self.cursor.execute(query, params)
            user_info = self.cursor.fetchone()

            if user_info:
                username, email = user_info
                session['username'] = username
                return username  
            else:
                return None
        except Exception as e:
            print("Error authenticating user:", e)
            return None

user_db = UserDatabase()