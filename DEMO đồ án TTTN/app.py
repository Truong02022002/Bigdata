from flask import Flask, abort, flash, render_template, request, redirect, url_for, session
from flask_oauthlib.client import OAuth
import hashlib
import os
import pyodbc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, Boolean
from sqlalchemy.orm import relationship


app = Flask(__name__)
app.secret_key = os.urandom(24)
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key='644891834247-05mt48pui6t12kpncss397vl9on83ffe.apps.googleusercontent.com',
    consumer_secret='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',
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
)

google.redirect_uri = 'http://127.0.0.1:5000/google-login/authorized'

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = 'accounts'
    accounts_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String, nullable=False)

class ProductType(db.Model):
    __tablename__ = 'products_type'
    type_products_id = Column(Integer, primary_key=True, autoincrement=True)
    type_products = Column(String(50), nullable=False, unique=True)

class Product(db.Model):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name_product = Column(String(255), nullable=False, unique=True)
    price = Column(DECIMAL(18,2), nullable=False)
    cost = Column(DECIMAL(18,2), nullable=False)
    type_product_id = Column(Integer, ForeignKey('products_type.type_products_id'), nullable=False)
    type_product = relationship('ProductType', back_populates='products')
    
class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name_customer = Column(String(50), nullable=False)
    phone = Column(String(10), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    product = relationship('Product', back_populates='customers')

class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    rate_star = Column(Integer, nullable=False)
    comment_reviews = Column(Text, nullable=False)
    total_like = Column(Integer)
    date_reviews = Column(DateTime, nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False)
    product = relationship('Product', back_populates='reviews')
    customer = relationship('Customer', back_populates='reviews')

class Bought(db.Model):
    __tablename__ = 'bought'
    bought_id = Column(Integer, primary_key=True, autoincrement=True)
    isbought = Column(Boolean, nullable=False)
    date_bought = Column(DateTime)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False)
    product = relationship('Product', back_populates='bought')
    customer = relationship('Customer', back_populates='bought')

class ItemDatabase:
    def __init__(self):
        try:
            self.conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=PHANDUCTRUONG\\SQLEXPRESS; DATABASE=Demo_QLKH;')
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
    
    def insert_items(self, table_name, *args):
        query = ""
        if table_name == 'products_type':
            query = "INSERT INTO products_type (type_products) VALUES (?)"
        elif table_name == 'products':
            query = "INSERT INTO products (name_product, price, cost, type_product_id) VALUES (?, ?, ?, ?)"
        else:
            print("Invalid table name for insertion.")
            return

        try:
            self.cursor.execute(query, args)
            self.conn.commit()
            print(f"{table_name.capitalize()} added successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting into {table_name}: {e}")
    
    def get_item_by_id(self, table_name, item_id):
        query = ""
        if table_name == 'products_type':
            query = "SELECT * FROM products_type WHERE type_products_id = ?"
        elif table_name == 'products':
            query = "SELECT * FROM products WHERE product_id = ?"
        self.cursor.execute(query, (item_id,))
        return self.cursor.fetchone()

    def update_item(self, table_name, item_id, *args):
        query = ""
        if table_name == 'products_type':
            query = "UPDATE products_type SET type_products = ? WHERE type_products_id = ?"
        elif table_name == 'products':
            query = "UPDATE products SET name_product = ?, price = ?, cost = ?, type_product_id = ? WHERE product_id = ?"
        else:
            raise ValueError("Invalid table name for update.")

        try:
            self.cursor.execute(query, args + (item_id,))
            self.conn.commit()
            print(f"{table_name.capitalize()} updated successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating {table_name}: {e}")
                                                                                                                                                                                                                                                                                                                   
    # def delete_item(self, table_name, item_id):
    #     query = ""
    #     if table_name == 'products_type':
    #         query = "DELETE FROM products_type WHERE type_products_id = ?"
    #     elif table_name == 'products':
    #         query = "DELETE FROM products WHERE product_id = ?"
    #     else:
    #         print("Invalid table name for deletion.")
    #         return

    #     try:
    #         self.cursor.execute(query, (item_id,))
    #         self.conn.commit()
    #         print(f"{table_name.capitalize()} deleted successfully.")
    #     except Exception as e:
    #         self.conn.rollback()
    #         print(f"Error deleting from {table_name}: {e}")
    
db = ItemDatabase()

class NewDatabase:
    def __init__(self):
        self.conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=PHANDUCTRUONG\\SQLEXPRESS; DATABASE=Demo_QLKH;')
        self.cursor = self.conn.cursor()

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

    def execute_query_all(self,query):
        result = self.execute_query(query)
        return result

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
        elif dashboard == "avgrateStar":
            query = """
                SELECT
                    pt.type_products,
                    Round(AVG(r.rateStar),5) AS AvgStarRating
                FROM products_type pt
                JOIN products p ON pt.type_products_id = p.type_product_id
                JOIN customers c ON p.product_id = c.product_id
                JOIN reviews r ON p.product_id = r.product_id AND c.customer_id = r.customer_id
                JOIN bought b ON p.product_id = b.product_id AND c.customer_id = b.customer_id
                GROUP BY pt.type_products
                ORDER BY AvgStarRating DESC;
            """
        
        return self.execute_query(query)

class UserDatabase:
    def __init__(self):
        self.conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=PHANDUCTRUONG\\SQLEXPRESS; DATABASE=Demo_QLKH;') 
        self.cursor = self.conn.cursor()

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

@app.errorhandler(404)
def page_not_found(error):
    username = session.get('username')
    return render_template('404.html', username=username), 404


@app.route('/', methods=['GET', 'POST'])
def index():
    username = session.get('username')
    if 'username' in session:
        return render_template('index.html', username=username)
    else:
        return redirect(url_for('login'))

ITEMS_PER_PAGE = 5

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session.get('username')

    table_name = request.form.get('table_select', 'products_type') if request.method == 'POST' else request.args.get('table_select', 'products_type')
    search_term = request.form.get('search', '') if request.method == 'POST' else request.args.get('search', '')
    page = int(request.args.get('page', 1))

    if search_term:
        columns, items = db.search_items(table_name, search_term)
        num_pages = 1 
    else:
        columns, all_items = db.get_items(table_name)
        total_items = len(all_items)
        num_pages = max(1, (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)

        start_index = (page - 1) * ITEMS_PER_PAGE
        end_index = min(start_index + ITEMS_PER_PAGE, total_items)
        items = all_items[start_index:end_index]

    if not items:
        abort(404)

    current_page = page if page > 0 else 1

    print(f"Debug: current_page={current_page}")

    return render_template('manage.html', columns=columns, items=items, selected_table=table_name, username=username,
                           num_pages=num_pages, current_page=current_page)

@app.route('/add_data/<data_type>', methods=['GET', 'POST'])
def add_data(data_type):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session.get('username')

    if request.method == 'POST':
        if data_type == 'products':
            data_to_insert = (
                request.form.get('name_product'),
                float(request.form.get('price')),
                float(request.form.get('cost')),
                int(request.form.get('type_product_id'))
            )
            db.insert_items('products', *data_to_insert)
        elif data_type == 'products_type':
            data_to_insert = (
                request.form.get('type_products'),
            )
            db.insert_items('products_type', *data_to_insert)

        return redirect(url_for('manage', table_select=data_type))

    return render_template(f'add_{data_type}.html', data_type=data_type, username=username)

@app.route('/edit_data/<data_type>/<int:item_id>', methods=['GET', 'POST'])
def edit_data(data_type, item_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session.get('username')

    if request.method == 'GET':
        item_data = db.get_item_by_id(data_type, item_id)
        return render_template('edit_data.html', data_type=data_type, username=username, item_data=item_data)

    elif request.method == 'POST':
        try:
            if data_type == 'products':
                data_to_update = (
                    request.form.get('name_product'),
                    float(request.form.get('price')),
                    float(request.form.get('cost')),
                    int(request.form.get('type_product_id'))
                )
                db.update_item('products', item_id, *data_to_update)
            elif data_type == 'products_type':
                data_to_update = (
                    request.form.get('type_products'),
                )
                db.update_item('products_type', item_id, *data_to_update)

            return redirect(url_for('manage', table_select=data_type))
        except ValueError as e:
            flash(str(e), 'error')

    return render_template('edit_data.html', data_type=data_type, username=username)


# @app.route('/delete_item/<table_name>/<int:item_id>', methods=['POST'])
# def delete_item(table_name, item_id):
#     try:
#         if table_name == 'products_type':
#             item = ProductType.query.get(item_id)
#         elif table_name == 'products':
#             item = Product.query.get(item_id)
#         else:
#             print("Invalid table name for deletion.")
#             abort(400) 

#         if item:
#             db.session.delete(item)
#             db.session.commit()
#             print(f"{table_name.capitalize()} deleted successfully.")
#             return redirect('/')
#         else:
#             abort(404) 

#     except Exception as e:
#         db.session.rollback()
#         print(f"Error deleting from {table_name}: {e}")
#         abort(500) 

# @app.route('/delete_data/<table_name>/<data_type>/<int:item_id>', methods=['GET', 'POST'])
# def delete_data(data_type, item_id):
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     username = session.get('username')

#     if request.method == 'POST':
#         db.delete_item(data_type, item_id)
#         return redirect(url_for('manage', table_select=data_type))

#     return render_template('delete_data.html', data_type=data_type, item_id=item_id, username=username)

# @app.route('/edit_data/<data_type>/<int:item_id>', methods=['GET', 'POST'])
# def edit_data(data_type, item_id):
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     username = session.get('username')

#     if data_type == 'products':
#         product_data = db.get_product_by_id(item_id)

#         if request.method == 'POST':
#             updated_data = {
#                 'name_product': request.form.get('name_product'),
#                 'price': float(request.form.get('price')),
#                 'cost': float(request.form.get('cost')),
#                 'type_product_id': int(request.form.get('type_product_id'))
#             }
#             db.edit_items(item_id, updated_data)
#             return redirect(url_for('manage', table_select=data_type))

#         return render_template('edit_product.html', data_type=data_type, username=username, product_data=product_data)

#     elif data_type == 'products_type':
#         type_data = db.get_product_type_by_id(item_id)

#         if request.method == 'POST':
#             updated_data = {
#                 'type_products': request.form.get('type_products')
#             }
#             db.edit_items(item_id, updated_data)
#             return redirect(url_for('manage', table_select=data_type))

#         return render_template('edit_product_type.html', data_type=data_type, username=username, type_data=type_data)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form.get('identifier') 
        password = request.form.get('password')

        authenticated_username = user_db.authenticate_user(email_or_username, password)

        if authenticated_username:
            session['username'] = authenticated_username  
            return redirect(url_for('index'))
        else:
            error_message = "Invalid email/username or password. Please try again."
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')
        
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

def generate_random_color():
    r = 0
    g = 200  
    b = 0
    a = 1.0  

    return f"rgba({r}, {g}, {b}, {a})"

def generate_random_color1():
    r = 255  
    g = 165  
    b = 0    
    a = 1.0  

    return f"rgba({r}, {g}, {b}, {a})"

def generate_random_color2():
    r = 0    
    g = 120  
    b = 200  
    a = 1.0  

    return f"rgba({r}, {g}, {b}, {a})"

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    username = session.get('username')

    if username:
        new_db = NewDatabase()
        dashboard_type = request.form.get('dashboard_type', 'percentage_bought')

        if dashboard_type in ['none','percentage_bought', 'compare', 'compares', 'type_product', 'age', 'products', 'products_price',
                              'reviews_rateStar', 'rateStars', 'discounts', 'price', 'comment_review', 'sumtotallikes', 
                              'countrateStars', 'avgrateStar']:
            columns, items = new_db.generate_sales_dashboard(dashboard_type)

            if columns and items:
                if dashboard_type == 'percentage_bought':
                    percentage_bought = items[0]['percentage_bought']
                    percentage_not_bought = items[0]['percentage_not_bought']
                    labels = ['Đã Mua', 'Chưa Mua']
                    data = [percentage_bought, percentage_not_bought]
                    print(data)
                    colors = [generate_random_color(), generate_random_color1()]
                    chart_title = 'Biểu đồ thể hiện tỷ lệ khách hàng đã mua và chưa mua quan tâm đến sản phẩm'
                elif dashboard_type == 'compare':
                    chart_title = 'Biểu đồ thể hiện doanh thu theo tháng'
                    labels = [f"{item['month']}/{item['year']}" for item in items]
                    data = [item['total_revenue'] for item in items]
                    colors = [generate_random_color()]
                elif dashboard_type == 'compares':
                    chart_title = 'Biểu đồ thể hiện lượng sản phẩm bán được theo tháng'
                    labels = [f"{item['month']}/{item['year']}" for item in items]
                    data = [item['Bought'] for item in items]
                    colors = [generate_random_color()]
                elif dashboard_type == 'avgrateStar':
                    chart_title = 'Biểu đồ thể hiện điểm đánh giá trung bình theo loại sản phẩm'
                    labels = [item['type_products'] for item in items]
                    data = [item['AvgStarRating'] for item in items]
                    colors = [generate_random_color()]
                elif dashboard_type == 'type_product':
                    chart_title = 'Biểu đồ thể hiện lượng sản phẩm bán được theo loại sản phẩm'
                    labels = [item['Type'] for item in items]
                    data = [item['Bought'] for item in items]
                    colors = [generate_random_color()]
                elif dashboard_type == 'age':
                    chart_title = 'Biểu đồ thể hiện lượng khách hàng đã mua hàng theo từng độ tuổi'
                    labels = [item['AgeRange'] for item in items]
                    data = [item['BoughtCount'] for item in items]
                    colors = [generate_random_color()]
                elif dashboard_type == 'products':
                    chart_title = 'Biểu đồ thể hiện top 10 sản phẩm bán chạy nhất'
                    labels = [item['short_name'] for item in items]
                    labels_1 = [item['name_product'] for item in items]
                    data = [item['bought'] for item in items]
                    colors = [generate_random_color()]
                elif dashboard_type == 'products_price':
                    chart_title = 'Biểu đồ thể hiện top 10 sản phẩm có doanh thu cao nhất'
                    labels = [item['short_name'] for item in items]
                    labels_1 = [item['name_product'] for item in items]
                    data = [item['total_revenue'] for item in items]
                    colors = [generate_random_color()]
                elif dashboard_type == 'reviews_rateStar':
                    chart_title = 'Biểu đồ thể hiện top 10 sản phẩm có lượt đánh giá 5 sao cao nhất'
                    labels = [item['short_name'] for item in items]
                    labels_1 = [item['name_product'] for item in items]
                    data = [item['NumberOf5StarReviews'] for item in items]
                    colors = [generate_random_color()]
                elif dashboard_type == 'rateStars':
                    chart_title = 'Biểu đồ thể hiện lượt đánh giá sao của khách hàng'
                    labels = [item['rateStar'] for item in items]
                    data = [item['TotalNumberOfReviews'] for item in items]
                    data_1 = [item['NumberOfReviews_Bought'] for item in items]
                    data_2 = [item['NumberOfReviews_NotBought'] for item in items]
                    colors = [generate_random_color()]
                    colors_1 = [generate_random_color1()]
                    colors_2 = [generate_random_color2()]
                elif dashboard_type == 'price':
                    chart_title = 'Biểu đồ thể hiện giá bán, giá gốc, giảm giá và lượt mua theo sản phẩm'
                    labels = [item['short_name'] for item in items]
                    labels_1 = [item['name_product'] for item in items]
                    data = [item['price'] for item in items]
                    data_1 = [item['bought_count'] for item in items]
                    data_2 = [item['cost'] for item in items]
                    data_3 = [item['discount'] for item in items]
                    colors = [generate_random_color()]
                    colors_1 = [generate_random_color1()]
                    colors_2 = [generate_random_color2()]
                elif dashboard_type == 'comment_review':
                    chart_title = 'Biểu đồ thể hiện lượt bình luận đánh giá của khách chưa mua hàng'
                    labels = [item['short_name'] for item in items]
                    labels_1 = [item['name_product'] for item in items]
                    data = [item['count_comment'] for item in items]
                    colors = [generate_random_color()]
                elif dashboard_type == 'sumtotallikes':
                    chart_title = 'Biểu đồ thể hiện tổng lượt thích theo từng sản phẩm'
                    labels = [item['short_name'] for item in items]
                    labels_1 = [item['name_product'] for item in items]
                    data = [item['sumtotallike'] for item in items]
                    colors = [generate_random_color()]
                elif dashboard_type == 'countrateStars':
                    chart_title = 'Biểu đồ thể hiện lượt đánh giá 5 sao theo sản phẩm'
                    labels = [item['short_name'] for item in items]
                    labels_1 = [item['name_product'] for item in items]
                    data = [item['NumberOfReviews'] for item in items]
                    colors = [generate_random_color()]
                else:
                    return render_template('dashboard.html', message='Invalid dashboard type', username=username)
            else:
                return render_template('dashboard.html', message='No data available', username=username)

            return render_template('dashboard.html', username=username, labels=labels, data=data, 
                                   **({'data_1': data_1} if 'data_1' in locals() else {}), colors=colors,
                                   **({'colors_1': colors_1} if 'colors_1' in locals() else {}), **({'labels_1': labels_1} if 'labels_1' in locals() else {}),
                                   **({'colors_2': colors_2} if 'colors_2' in locals() else {}), **({'data_2': data_2} if 'data_2' in locals() else {}), 
                                   **({'data_3': data_3} if 'data_3' in locals() else {}), chart_title=chart_title, selected_dashboard_type=dashboard_type, sub_dashboard_type = dashboard_type)
        else:
            return render_template('dashboard.html', message='Invalid dashboard type', username=username)
    else:
        return redirect(url_for('login'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/google-login')
def google_login():
    return google.authorize(callback=url_for('google_authorized', _external=True))

@app.route('/google-login/authorized')
def google_authorized():
    response = google.authorized_response()

    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')

    if user_info is not None and 'email' in user_info.data:
        email = user_info.data['email']
        username = email.split('@')[0]
        session['username'] = username
    else:
        return 'Failed to retrieve user information from Google'

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
