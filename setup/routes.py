from setup.__init__ import enterprise_wiki, db
from setup import bcrypt
from flask import render_template, request, redirect, url_for, flash, abort
from setup.forms import RegisrationForm, LoginForm, PostForm, UploadForm, SearchForm
from setup.models import Users, Post
from flask_login import login_user, login_required, current_user, logout_user
import os
import logging
from werkzeug.utils import secure_filename
from sqlalchemy import or_


@login_required
@enterprise_wiki.route('/')
@enterprise_wiki.route('/home')
def home():
    return render_template('home.html')


@enterprise_wiki.route('/get_started')
@login_required
def get_started():
    return render_template('get_started.html')


UPLOAD_FOLDER = '/Users/masoud/projects/EnterpriseWiki/setup/static/uploaded_pics'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@enterprise_wiki.route('/upload_pic', methods=['POST'])
@login_required
def upload_pic():
    logging.info("Attempting to upload picture")
    if 'pic' in request.files:
        pic = request.files['pic']
        print(pic, "where are there?")
        if pic.filename != '':
            if allowed_file(pic.filename):
                filename = secure_filename(pic.filename)
                pic.save(os.path.join(UPLOAD_FOLDER, filename))
                current_user.image_file = filename  # Update the user's image filename
                db.session.commit()

                flash('Image uploaded and saved successfully', 'success')
                logging.info("Picture uploaded and saved successfully")
            else:
                flash('Invalid file type', 'error')
                logging.error("Invalid file type")
        else:
            flash('No file selected', 'error')
            logging.error("No file selected")
    else:
        flash('File field not found in request', 'error')
        logging.error("File field not found in request")

    return redirect(url_for('account'))


@enterprise_wiki.route('/save_pic', methods=['POST'])
@login_required
def save_pic():
    logging.info("Attempting to save picture")
    if 'pic' in request.files:
        pic = request.files['pic']
        if pic.filename != '':
            if allowed_file(pic.filename):
                filename = secure_filename(pic.filename)
                pic.save(os.path.join(UPLOAD_FOLDER, filename))
                current_user.image_file = filename
                db.session.commit()
                flash('Image uploaded and changes saved successfully', 'success')
                logging.info("Picture saved successfully")
    return redirect(url_for('account'))


@enterprise_wiki.route('/account')
@login_required
def account():
    form = UploadForm()
    image_file = current_user.image_file
    return render_template('account.html', title='Account', image_file=image_file, form=form)


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


@enterprise_wiki.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('daily_posts'))
    return render_template('create_post.html', title='New Post', form=form)


@enterprise_wiki.route("/daily_posts")
@login_required
def daily_posts():
    posts = Post.query.all()
    return render_template('daily_posts.html', title='Daily Posts', posts=posts)


@enterprise_wiki.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@enterprise_wiki.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been edited!', 'success')
        return redirect(url_for('daily_posts', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('edit_post.html', title='Edit Post', legend='Edit Post', form=form)


@enterprise_wiki.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('daily_posts'))



#Pass Stuff to Navbar
@enterprise_wiki.context_processor
def layout():
    form = SearchForm()
    return dict(form=form)


@enterprise_wiki.route("/search", methods=['POST'])
@login_required
def search():
    search_query = request.form.get('searched').lower()  # Convert search query to lowercase for case-insensitive searc

    # Search for posts containing the query
    posts = Post.query.filter(or_(Post.content.ilike(f'%{search_query}%'), Post.title.ilike(f'%{search_query}%')))
    posts = posts.order_by(Post.title).all()

    return render_template('search.html', searched=search_query, posts=posts)





