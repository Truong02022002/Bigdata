from flask import Flask, abort, render_template, redirect, request, url_for, session
from flask_oauthlib.client import OAuth
from io import BytesIO
import random
import matplotlib.pyplot as plt
import base64
from app.controllers import NewDatabase, ItemDatabase, UserDatabase
from config import SECRET_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

app = Flask(__name__, template_folder='/app/templates')
app.secret_key = SECRET_KEY
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=GOOGLE_CLIENT_ID,
    consumer_secret=GOOGLE_CLIENT_SECRET,
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

@app.errorhandler(404)
def page_not_found(error):
    return render_template('templates/404.html'), 404

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
    db = ItemDatabase()

    table_name = request.form.get('table_select', 'products') if request.method == 'POST' else request.args.get('table_select', 'products')
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

    return render_template('templates/manage.html', columns=columns, items=items, selected_table=table_name, username=username, num_pages=num_pages, current_page=current_page)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form.get('identifier') 
        password = request.form.get('password')

        print(f"Debug: Received login request with email/username: {email_or_username}, password: {password}")

        user_db = UserDatabase()
        
        authenticated_username = user_db.authenticate_user(email_or_username, password)

        if authenticated_username:
            session['username'] = authenticated_username  
            print(f"Debug: User {authenticated_username} successfully authenticated.")
            return redirect(url_for('index'))
        else:
            error_message = "Invalid email/username or password. Please try again."
            print(f"Debug: Authentication failed. {error_message}")
            return render_template('templates/login.html', error_message=error_message)

    return render_template('templates/login.html')
        
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

def generate_random_color():
    r = random.randint(50, 255)
    g = random.randint(50, 255)
    b = random.randint(50, 255)
    a = random.uniform(0.0, 1.0)

    return f"rgba({r}, {g}, {b}, {a})"

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    username = session.get('username')

    if username:
        new_db = NewDatabase()
        dashboard_type = request.form.get('dashboard_type', 'percentage_bought')

        if dashboard_type in ['none','percentage_bought', 'compare', 'compares', 'type_product', 'age', 'products', 'products_price',
                              'reviews_rateStar', 'rateStars', 'discounts', 'price', 
                              'comment_review', 'sumtotallikes', 'countrateStars']:
            columns, items = new_db.generate_sales_dashboard(dashboard_type)

            if columns and items:
                if dashboard_type == 'none':
                    chart_title = 0
                    labels = 0
                    data = 0
                    colors = 0
                elif dashboard_type == 'percentage_bought':
                    percentage_bought = items[0]['percentage_bought']
                    percentage_not_bought = items[0]['percentage_not_bought']
                    labels = ['Đã Mua', 'Chưa Mua']
                    data = [percentage_bought, percentage_not_bought]
                    colors = [generate_random_color() for _ in labels]
                    chart_title = 'Biểu đồ thể hiện tỷ lệ khách hàng đã mua và chưa mua quan tâm đến sản phẩm'
                elif dashboard_type == 'compare':
                    chart_title = 'Biểu đồ doanh thu theo tháng'
                    labels = [f"{item['month']}/{item['year']}" for item in items]
                    data = [item['total_revenue'] for item in items]
                    colors = [generate_random_color()]
                elif dashboard_type == 'compares':
                    chart_title = 'Biểu đồ thể hiện lượng sản phẩm bán được theo tháng'
                    labels = [f"{item['month']}/{item['year']}" for item in items]
                    data = [item['Bought'] for item in items]
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
                    colors_1 = [generate_random_color()]
                    colors_2 = [generate_random_color()]
                elif dashboard_type == 'discounts':
                    chart_title = 'Biểu đồ thể hiện lượt mua và giảm giá theo sản phẩm'
                    labels = [item['short_name'] for item in items]
                    labels_1 = [item['name_product'] for item in items]
                    data = [item['discount'] for item in items]
                    data_1 = [item['bought_count'] for item in items]
                    colors = [generate_random_color()]
                    colors_1 = [generate_random_color()]
                elif dashboard_type == 'price':
                    chart_title = 'Biểu đồ thể hiện lượt mua và giá bán theo sản phẩm'
                    labels = [item['short_name'] for item in items]
                    labels_1 = [item['name_product'] for item in items]
                    data = [item['price'] for item in items]
                    data_1 = [item['bought_count'] for item in items]
                    data_2 = [item['cost'] for item in items]
                    data_3 = [item['discount'] for item in items]
                    colors = [generate_random_color()]
                    colors_1 = [generate_random_color()]
                    colors_2 = [generate_random_color()]
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
                    return render_template('templates/dashboard.html', message='Invalid dashboard type', username=username)
            else:
                return render_template('templates/dashboard.html', message='No data available', username=username)

            return render_template('templates/dashboard.html', username=username, labels=labels, data=data, 
                                   **({'data_1': data_1} if 'data_1' in locals() else {}), colors=colors,
                                   **({'colors_1': colors_1} if 'colors_1' in locals() else {}), **({'labels_1': labels_1} if 'labels_1' in locals() else {}),
                                   **({'colors_2': colors_2} if 'colors_2' in locals() else {}), **({'data_2': data_2} if 'data_2' in locals() else {}), 
                                   **({'data_3': data_3} if 'data_3' in locals() else {}), chart_title=chart_title, selected_dashboard_type=dashboard_type, sub_dashboard_type = dashboard_type)
        else:
            return render_template('templates/dashboard.html', message='Invalid dashboard type', username=username)
    else:
        return redirect(url_for('login'))

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    username = session.get('username')
    if 'username' in session:
        labels = ['Product 1', 'Product 2', 'Product 3', 'Product 4', 'Product 5']
        discount_data = [10, 15, 8, 20, 12]
        bought_count_data = [50, 30, 40, 10, 25]

        fig, ax1 = plt.subplots()

        ax1.bar(labels, bought_count_data, color='red', alpha=0.7, label='Bought Count')

        ax2 = ax1.twinx()
        ax2.plot(labels, discount_data, color='blue', marker='o', label='Discount')

        ax1.set_ylabel('Bought Count', color='red')
        ax2.set_ylabel('Discount', color='blue')

        plt.title('Combined Chart')

        img_buf = BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        img_str = base64.b64encode(img_buf.read()).decode('utf-8')

        plt.close()

        return render_template('templates/analysis.html', img_str=img_str, username=username)
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
