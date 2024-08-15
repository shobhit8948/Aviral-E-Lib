# create virtual environment 
python -m venv .env
# Activate virtual environment(for windows only)
.env/Scripts/activate
# To install requirements 
pip install -r requirements.txt
# After downloading the requirements, write below cammand to start the server 
python app.py


# file structure
├── application/
│   └──__pycahe__
│   └── __init__.py
│   └── database.py
│   └── models.py
│   └── routes.py
│
├── static/
│   ├── css/
│   │   └── styles.css
│   │   └── auth.css
│   ├── images/
│   │   └── logo1.jpg
│   │   └── background.jpg
│   └── uploads/
│       └── images/
│       └── pdfs/
├── instance/
│   └── database.sqlite3

├── templates/
│   ├── basefor_admin.html
│   ├── basefor_user.htm
│   ├── baseforauth.html
│   ├── login.html
│   ├── register.html
│   ├── librarianlogin.html
│   ├── librarian_dashboard.html
│   ├── search_results.html
│   ├── edit_section.html
│   ├── edit_book.html
│   ├── error.html
│   ├── handle_requests.html
│   ├── my_books.html
│   ├── purchase_confirmation.html
│   ├── section_books.html
│   ├── stats.html
│   ├── user_profile.html
│   ├── user_search_result.html
│   ├── user_section_results.html
│   ├── user_section_books.html
│   └── user_dashboard.html
│
├── app.py
└── requirements.txt