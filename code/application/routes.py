from application import app
from flask import redirect, render_template, request, session, url_for, flash
from application.database import db
from application.models import Book, PurchaseRequest, Section, User ,book_buyers
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import uuid 
from decimal import Decimal
from sqlalchemy import func
from collections import defaultdict

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user'] = user.to_dict()
            print("Login success and logged in user:", user)
            return redirect(url_for('user_dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        user = User(name, phone, email, password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/librarianlogin', methods=['GET', 'POST'])
def librarian_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user'] = user.to_dict()
            print("Login success and logged in user:", user)
            return redirect(url_for('librarian_dashboard')) 
    return render_template('librarianlogin.html')

@app.route('/librarian_dashboard')
def librarian_dashboard():
    if 'user' in session and session['user']['role'] == 'librarian':
        sections = Section.query.all()
        return render_template('librarian_dashboard.html', sections=sections)
    else:
        return redirect(url_for('librarian_login'))
@app.route('/librarian_profile')
def librarian_profile():
    if 'user' in session:
        user_id = session['user']['id']
        user = User.query.get(user_id)
        if user:
            return render_template('librarian_profile.html', user=user)
    flash('User not found or not logged in', 'error')
    return redirect(url_for('login'))

@app.route('/update_librarian_profile', methods=['POST'])
def update_librarian_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        user_id = session['user']['id']
        user = User.query.get(user_id)
        if user:
            user.name = name
            user.phone = phone
            user.password = password
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('librarian_profile'))
    user = User.query.first()
    return render_template('librarian_profile.html', user=user)

IMAGE_UPLOAD_PATH = os.path.join(app.root_path, '..', 'static', 'uploads', 'images')
PDF_UPLOAD_PATH = os.path.join(app.root_path,'..', 'static', 'uploads', 'pdfs')
for directory in [IMAGE_UPLOAD_PATH, PDF_UPLOAD_PATH]:
    if not os.path.exists(directory):
        os.makedirs(directory)

@app.route('/add_section', methods=['POST'])
def add_section():
    if 'user' in session and session['user']['role'] == 'librarian':
        section_name = request.form['section_name']
        description = request.form['description']
        if 'image' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filename = str(uuid.uuid4()) + '-' + filename
            file_path = os.path.join(IMAGE_UPLOAD_PATH, filename)
            file.save(file_path)
            image = os.path.join('uploads', 'images', filename)

        new_section = Section(section_name=section_name, description=description, image=image, date_created=datetime.utcnow())
        db.session.add(new_section)
        db.session.commit()
        flash('Section added successfully', 'success')
        return redirect(url_for('librarian_dashboard'))
    else:
        return redirect(url_for('librarian_login'))

@app.route('/edit_section/<int:section_id>', methods=['GET', 'POST'])
def edit_section(section_id):
    section = Section.query.get_or_404(section_id)    
    if request.method == 'POST':
        section.section_name = request.form['section_name']
        section.description = request.form['description']

        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                filename = secure_filename(image_file.filename)
                filename = str(uuid.uuid4()) + '-' + filename
                file_path = os.path.join(IMAGE_UPLOAD_PATH, filename)
                image_file.save(file_path)
                section.image = os.path.join('uploads', 'images', filename)
        
        db.session.commit()        
        flash('Section updated successfully', 'success')
        return redirect(url_for('librarian_dashboard'))    
    return render_template('edit_section.html', section=section)

@app.route('/delete_section/<int:section_id>', methods=['POST'])
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)
    db.session.delete(section)
    db.session.commit()
    flash('Section deleted successfully', 'success')
    return redirect(url_for('librarian_dashboard'))

@app.route('/add_book', methods=['POST'])
def add_book():
    if 'user' in session and session['user']['role'] == 'librarian':
        title = request.form['title']
        author = request.form['author']
        content = request.form['content']
        section_id = request.form['section']
        price_per_day = float(request.form['price_per_day'])        
        if 'image' not in request.files:
            flash('No image file part', 'error')
            return redirect(request.url)
        image_file = request.files['image']
        if image_file.filename == '':
            flash('No image selected', 'error')
            return redirect(request.url)
        image_filename = secure_filename(image_file.filename)
        image_filename = str(uuid.uuid4()) + '-' + image_filename
        image_path = os.path.join(IMAGE_UPLOAD_PATH, image_filename)
        image_file.save(image_path)
        image = os.path.join('uploads', 'images', image_filename)
        pdf_file = request.files.get('pdf')
        if pdf_file:
            if pdf_file.filename != '':
                pdf_filename = secure_filename(pdf_file.filename)
                pdf_filename = str(uuid.uuid4()) + '-' + pdf_filename
                pdf_path = os.path.join(PDF_UPLOAD_PATH, pdf_filename)
                pdf_file.save(pdf_path)
                pdf = os.path.join('uploads', 'pdfs', pdf_filename)
            else:
                flash('Please upload a PDF file', 'error')
                return redirect(url_for('librarian_dashboard'))
        else:
            flash('No PDF file uploaded', 'error')
            return redirect(url_for('librarian_dashboard'))
        
        new_book = Book(title=title, author=author, content=content, image=image, pdf=pdf, section_id=section_id, price_per_day=price_per_day)  # Include rate when creating a new book
        db.session.add(new_book)
        db.session.commit()        
        flash('Book added successfully', 'success')
        return redirect(url_for('librarian_dashboard'))
    else:
        return redirect(url_for('librarian_login'))

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    section_id = book.section_id
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.content = request.form['content']
        book.price_per_day = request.form['price_per_day']
        
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            image_filename = secure_filename(image_file.filename)
            image_filename = str(uuid.uuid4()) + '-' + image_filename
            image_path = os.path.join(IMAGE_UPLOAD_PATH, image_filename)
            image_file.save(image_path)
            book.image = os.path.join('uploads', 'images', image_filename)

        pdf_file = request.files.get('pdf')
        if pdf_file and pdf_file.filename != '':
            pdf_filename = secure_filename(pdf_file.filename)
            pdf_filename = str(uuid.uuid4()) + '-' + pdf_filename
            pdf_path = os.path.join(PDF_UPLOAD_PATH, pdf_filename)
            pdf_file.save(pdf_path)
            book.pdf = os.path.join('uploads', 'pdfs', pdf_filename)
        
        db.session.commit()
        flash('Book updated successfully', 'success')
        return redirect(url_for('section_books', section_id=section_id))
    return render_template('edit_book.html', book=book, section_id=section_id)

@app.route('/section_books/<int:section_id>')
def section_books(section_id):
    if 'user' in session:
        section = Section.query.get(section_id)
        if section:
            books = section.books
            return render_template('section_books.html', books=books, section=section)
        else:
            flash('Section not found', 'error')
            return redirect(url_for('librarian_dashboard'))
    else:
        return redirect(url_for('librarian_login'))

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if 'user' in session and session['user']['role'] == 'librarian':
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully', 'success')
    else:
        flash('You are not authorized to delete this book', 'error')
    return redirect(url_for('librarian_dashboard'))

@app.route('/search_books', methods=['POST'])
def search_books():
    search_value = request.form.get('search_value', '')
    search_criteria = request.form.get('search_criteria', '')
    books = []
    if search_criteria == 'section':
            sections = Section.query.filter(Section.section_name.ilike(f'%{search_value}%')).all()
            if sections:
                return redirect(url_for('section_books', section_id=sections[0].id))
            else:
                flash('Section not found', 'error')
    elif search_criteria == 'author':
        books = Book.query.filter(func.lower(Book.author).like(f'%{search_value.lower()}%')).all()
    elif search_criteria == 'title':
        books = Book.query.filter(func.lower(Book.title).like(f'%{search_value.lower()}%')).all()
    return render_template('search_results.html', search_value=search_value, search_criteria=search_criteria, books=books)

@app.route('/book_details/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    section = book.section
    purchase_requests = PurchaseRequest.query.filter_by(book_id=book_id).all()
    return render_template('book_details.html', book=book, section=section, purchase_requests=purchase_requests)


@app.route('/revoke_access/<int:user_id>', methods=['POST'])
def revoke_access(user_id):
    user = User.query.get_or_404(user_id)
    book_id = request.form.get('book_id')
    if book_id:
        book = Book.query.get_or_404(book_id)
        if book in user.purchased_books:
            user.purchased_books.remove(book)
            db.session.commit()
            flash('Access revoked successfully', 'success')
        else:
            flash('User does not have access to this book', 'error')
    else:
        flash('Book ID not provided', 'error')
    return redirect(url_for('book_details', book_id=book_id))

@app.route('/handle_requests')
def handle_requests():
    if 'user' in session and session['user']['role'] == 'librarian':
        purchase_requests = PurchaseRequest.query.all()
        return render_template('handle_requests.html', purchase_requests=purchase_requests)
    else:
        return redirect(url_for('librarian_login'))

@app.route('/handle_requests/<int:request_id>', methods=['POST'])
def handle_purchase_request(request_id):
    purchase_request = PurchaseRequest.query.get_or_404(request_id)
    action = request.form.get('action')
    
    if action == 'grant':
        user = purchase_request.user
        book = purchase_request.book
        access_start_datetime = datetime.utcnow()
        access_end_datetime = access_start_datetime + timedelta(days=purchase_request.duration)
        price = book.price_per_day * purchase_request.duration
        user.purchased_books.append(book)
        purchase_request.access_start_datetime = access_start_datetime
        purchase_request.access_end_datetime = access_end_datetime
        db.session.execute(
            book_buyers.insert(),
            {
                'user_id': user.id,
                'book_id': book.id,
                'access_start_datetime': access_start_datetime,
                'access_end_datetime': access_end_datetime,
                'price': price,
                'access_duration': purchase_request.duration
            }
        )
    elif action == 'reject':
        db.session.delete(purchase_request)
        db.session.commit()
        flash('Purchase request rejected', 'warning')
    else:
        flash('Invalid action', 'error')
    return redirect(url_for('handle_requests'))

@app.route('/stats')
def stats():
    sections = Section.query.all()
    section_names = [section.section_name for section in sections]
    book_counts = [len(section.books) for section in sections]
    plt.figure(figsize=(10, 6))
    plt.bar(section_names, book_counts, color='skyblue')
    plt.xlabel('Section')
    plt.ylabel('Number of Books')
    plt.title('Number of Books in Each Section')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    chart_filename = 'static/images/book_counts_chart.png'
    plt.savefig(chart_filename)
    # Books added per day-----------------------
    books_added_per_day = defaultdict(int)
    today = datetime.now().date()
    ten_days_ago = today - timedelta(days=10)
    books_added_query = db.session.query(func.date(Book.date_created), func.count(Book.id)).filter(Book.date_created >= ten_days_ago).group_by(func.date(Book.date_created)).all()
    for date, count in books_added_query:
        books_added_per_day[date] = count
    sorted_books_added_per_day = dict(sorted(books_added_per_day.items()))
    dates = list(sorted_books_added_per_day.keys())
    counts = list(sorted_books_added_per_day.values())
    plt.figure(figsize=(10, 6))
    plt.plot(dates, counts, marker='o', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel('Number of Books Added')
    plt.title('Number of Books Added Per Day')
    plt.xticks(rotation=45)
    plt.tight_layout()
    time_series_chart_filename = 'static/images/books_added_time_series_chart.png'
    plt.savefig(time_series_chart_filename)

    return render_template('stats.html', chart_filename=chart_filename, time_series_chart_filename=time_series_chart_filename)


# <-------------------------------------user Side Routes-------------------------------------------------->

@app.route('/user_dashboard')
def user_dashboard():
    if 'user' in session and session['user']['role'] == 'customer':
        sections = Section.query.all()
        latest_books = Book.query.order_by(Book.date_created.desc()).limit(10).all()      
        return render_template('user_dashboard.html', sections=sections, latest_books=latest_books)
    else:
        return redirect(url_for('login'))

@app.route('/user_profile')
def user_profile():
    if 'user' in session:
        user_id = session['user']['id']
        user = User.query.get(user_id)
        if user:
            return render_template('user_profile.html', user=user)
    flash('User not found or not logged in', 'error')
    return redirect(url_for('login'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        user_id = session['user']['id']

        user = User.query.get(user_id)

        if user:
            user.name = name
            user.phone = phone
            user.password = password
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('user_profile'))
    user = User.query.first()
    return render_template('user_profile.html', user=user)

@app.route('/user_search', methods=['POST'])
def user_search():
    search_value = request.form.get('search_value', '')
    search_criteria = request.form.get('search_criteria', '')
    books = []
    if search_criteria == 'section':
            sections = Section.query.filter(Section.section_name.ilike(f'%{search_value}%')).all()
            if sections:
                return redirect(url_for('user_section_books', section_id=sections[0].id))
            else:
                flash('Section not found', 'error')
    elif search_criteria == 'author':
        books = Book.query.filter(func.lower(Book.author).like(f'%{search_value.lower()}%')).all()
    elif search_criteria == 'title':
        books = Book.query.filter(func.lower(Book.title).like(f'%{search_value.lower()}%')).all()
    return render_template('user_search_results.html', search_value=search_value, search_criteria=search_criteria, books=books)
@app.route('/user_section_books/<int:section_id>')
def user_section_books(section_id):
    section = Section.query.get(section_id)
    if section:
        books = Book.query.filter_by(section_id=section_id).order_by(Book.date_created.desc()).all()
        return render_template('user_section_books.html', section=section, books=books)
    else:
        return redirect(url_for('user_dashboard'))

@app.route('/my_books')
def my_books():
    if 'user' in session:
        user_id = session['user']['id']
        user = User.query.get(user_id)
        return render_template('my_books.html', user=user)
    else:
        flash('You must be logged in to view your books', 'error')
        return redirect(url_for('login'))
@app.route('/purchase', methods=['POST'])
def purchase():
    if request.method == 'POST':
        if 'user' not in session:
            flash('Please login to purchase books', 'error')
            return redirect(url_for('login'))
        book_id = request.form.get('book_id')
        if not book_id:
            flash('Book ID is missing', 'error')
            return redirect(url_for('user_dashboard'))
        book = Book.query.get(book_id)
        if book:
            return render_template('purchase_confirmation.html', book=book)
        else:
            flash('Book not found', 'error')
            return redirect(url_for('user_dashboard'))


@app.route('/send_request_to_librarian', methods=['GET', 'POST'])
def send_request_to_librarian():
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        duration = request.form.get('duration')
        user_id = session['user']['id']
        if duration is None or duration == '':
            return render_template('error.html', message='Duration is missing')
        book = Book.query.get(book_id)        
        price = book.price_per_day * int(duration)
        purchase_request = PurchaseRequest(user_id=user_id, book_id=book_id, duration=duration, price=price)
        db.session.add(purchase_request)
        db.session.commit()
        return redirect(url_for('user_dashboard'))
    elif request.method == 'GET':
        return render_template('purchase_confirmation.html')
