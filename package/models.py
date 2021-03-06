from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from package import db, login_manager
from flask import current_app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_pic = db.Column(db.String(20), unique=False, nullable=False, default='default.jpg')
    password = db.Column(db.String(60), unique=False, nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    fav_list = db.relationship('Atable_fav', back_populates='liker', lazy=True)
    comment_list = db.relationship('Comment', back_populates='under_user')
    notif_list = db.relationship('Atable_notif', back_populates='recipient')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except KeyError:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.profile_pic}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)
    picture = db.Column(db.String(50), unique=False, nullable=False)
    picture_w = db.Column(db.Integer, nullable=False)
    picture_h = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    edit_tags = db.Column(db.String, nullable=False)
    tag_list = db.relationship('Atable_tag', back_populates='post')
    likers_list = db.relationship('Atable_fav', back_populates='fav')
    comment_list = db.relationship('Comment', back_populates='under_post')

    def __repr__(self):
        return f"Post('{self.id}', '{self.date_posted}')"


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    post_list = db.relationship('Atable_tag', back_populates='tag')

    def __repr__(self):
        return f"{self.name}"


class Atable_tag(db.Model):
    __tablename__ = 'atable_tag'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    tag = db.relationship('Tag', back_populates='post_list')
    post = db.relationship('Post', back_populates='tag_list')


class Atable_fav(db.Model):
    __tablename__ = 'atable_fav'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fav_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    fav = db.relationship('Post', back_populates='likers_list')
    liker = db.relationship('User', back_populates='fav_list')


class Atable_subs(db.Model):
    __tablename__ = 'atable_subs'
    cmaker_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    sub_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, unique=False, nullable=False)
    date_posted = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, unique=False, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.String, db.ForeignKey('user.username'))
    under_post = db.relationship('Post', back_populates='comment_list')
    under_user = db.relationship('User', back_populates='comment_list')


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, nullable=True)
    username = db.Column(db.String, nullable=True)
    type = db.Column(db.String, unique=False, nullable=False)
    content = db.Column(db.String, unique=False, nullable=False)
    date = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)
    recip_list = db.relationship('Atable_notif', back_populates='notification')

class Atable_notif(db.Model):
    __tablename__ = 'atable_notif'
    notif_id = db.Column(db.Integer, db.ForeignKey('notification.id'), primary_key=True)
    recip_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    notification = db.relationship('Notification', back_populates='recip_list')
    recipient = db.relationship('User', back_populates='notif_list')
