from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kudos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"


class Kudos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_visible = db.Column(db.Boolean, default=True)
    moderated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    moderated_at = db.Column(db.DateTime, nullable=True)
    reason_for_moderation = db.Column(db.Text, nullable=True)

    sender = db.relationship('User', foreign_keys=[sender_id], lazy='joined')
    recipient = db.relationship('User', foreign_keys=[recipient_id], lazy='joined')


def init_db():
    if not os.path.exists('kudos.db'):
        db.create_all()
        # seed sample users
        alice = User(name='Alice (admin)')
        bob = User(name='Bob')
        carol = User(name='Carol')
        db.session.add_all([alice, bob, carol])
        db.session.commit()
        print('Initialized database and seeded users.')


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@app.route('/')
def index():
    kudos = Kudos.query.filter_by(is_visible=True).order_by(Kudos.created_at.desc()).limit(50).all()
    return render_template('index.html', kudos=kudos, user=current_user())


@app.route('/kudos/new', methods=['GET', 'POST'])
def new_kudos():
    user = current_user()
    if not user:
        flash('Please login first (use /login?user_id=<id>)')
        return redirect(url_for('index'))

    users = User.query.order_by(User.name).all()
    if request.method == 'POST':
        recipient_id = request.form.get('recipient_id')
        message = request.form.get('message', '').strip()
        if not recipient_id or not message:
            flash('Recipient and message are required.')
            return redirect(url_for('new_kudos'))
        if len(message) > 500:
            flash('Message must be 500 characters or fewer.')
            return redirect(url_for('new_kudos'))

        try:
            kudos = Kudos(sender_id=user.id, recipient_id=int(recipient_id), message=message)
            db.session.add(kudos)
            db.session.commit()
            flash('Kudos sent!')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error saving kudos: ' + str(e))
            return redirect(url_for('new_kudos'))

    return render_template('kudos_form.html', users=users, user=user)


@app.route('/login')
def login():
    user_id = request.args.get('user_id')
    if not user_id:
        users = User.query.order_by(User.name).all()
        return render_template('login.html', users=users)
    session['user_id'] = int(user_id)
    flash('Logged in.')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out.')
    return redirect(url_for('index'))


def is_admin(user):
    return user and user.id == 1


@app.route('/admin/moderate/<int:kudos_id>', methods=['POST'])
def moderate(kudos_id):
    user = current_user()
    if not is_admin(user):
        flash('Unauthorized')
        return redirect(url_for('index'))

    action = request.form.get('action')
    reason = request.form.get('reason', '').strip() or None
    k = Kudos.query.get_or_404(kudos_id)
    if action == 'hide':
        k.is_visible = False
        k.moderated_by = user.id
        k.moderated_at = datetime.utcnow()
        k.reason_for_moderation = reason
        db.session.commit()
        flash('Kudos hidden.')
    elif action == 'show':
        k.is_visible = True
        k.moderated_by = user.id
        k.moderated_at = datetime.utcnow()
        k.reason_for_moderation = reason
        db.session.commit()
        flash('Kudos made visible.')
    elif action == 'delete':
        db.session.delete(k)
        db.session.commit()
        flash('Kudos deleted.')
    else:
        flash('Unknown action')

    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
