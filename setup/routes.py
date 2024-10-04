from setup.__init__ import enterprise_wiki, db
from setup import bcrypt
from flask import render_template, request, redirect, url_for, flash
from setup.forms import RegisrationForm, LoginForm
from setup.models import Users, Post
from flask_login import login_user, login_required, current_user, logout_user


@login_required
@enterprise_wiki.route('/')
@enterprise_wiki.route('/home')
def home():
    # Sample data for demonstration
    wiki_items = [
        {"title": "Getting Started", "url": "/wiki/getting-started"},
        {"title": "Installation", "url": "/wiki/installation"},
        {"title": "Configuration", "url": "/wiki/configuration"},
        {"title": "FAQ", "url": "/wiki/faq"},
    ]

    return render_template('home.html', items=wiki_items)


@enterprise_wiki.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@enterprise_wiki.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@enterprise_wiki.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@enterprise_wiki.route('/account')
@login_required
def account():
    image_file = current_user.image_file
    return render_template('account.html', title='Account', image_file=image_file)




