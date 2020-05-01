from flask import Blueprint, redirect, flash, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required

from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestRestForm, ResetPasswordForm
from flaskblog.users.utils import save_profile, send_reset_email

users = Blueprint("users", __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('home')
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully!. Now you can do login.", 'success')
        return redirect('home')
    return render_template('registration.html', title="Registration", form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('home')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Login successfully", 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash("Invalid username and password", 'danger')
    return render_template('login.html', title="Login", form=form)


@users.route('/logout')
def logout():
    logout_user()
    flash("Logout successfully", 'success')
    return redirect('login')


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.image_file.data:
            current_user.image_file = save_profile(form.image_file.data)
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Account details updated!", 'success')
        return redirect('account')
    elif request.method == "GET":
        form.email.data = current_user.email
        form.username.data = current_user.username
    image = url_for('static', filename="profile_img/" + current_user.image_file)
    return render_template('account.html', title="Account", image=image, form=form)


@users.route('/post/user_post/<string:username>')
def user_post(username):
    user = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=3, page=page)
    return render_template('user_post.html', posts=posts, user=user)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('users.home'))
    form = RequestRestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password", 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title="Reset Password", form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('users.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is invalid or expired token", 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hash_password
        db.session.commit()
        flash("Your password has been updated!. Now you can do login.", 'success')
        return redirect('login')
    return render_template('reset_token.html', title="Reset Password", form=form)


