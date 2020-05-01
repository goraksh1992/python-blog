import os
import secrets
from PIL import Image
from flask_mail import Message
from flaskblog import app, mail
from flask import url_for


def save_profile(form_picture):
    random_hex = secrets.token_hex(8)
    fn, fext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + fext
    picture_path = os.path.join(app.root_path, 'static/profile_img/', picture_fn)
    form_picture.save(picture_path)

    # resize image
    size_125 = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(size_125)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender="gaurav@augdeck.com", recipients=[user.email])
    msg.body = f'''
        To reset your password, visit the following link:
        {url_for('reset_token', token=token, _external=True)}
        If you did not make this request then simply ignore this email.
    '''
    mail.send(msg)
