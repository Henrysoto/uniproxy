import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from uniproxy.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        utilisateur = request.form['username'].strip()
        phrase = request.form['password'].strip()
        db = get_db()
        error = None

        if not utilisateur:
            error = 'Username is required.'
        elif not phrase:
            error = 'Password is required.'
        elif len(utilisateur) < 3:
            error = 'Username is too short.'
        elif len(phrase) < 8:
            error = 'Password must be at least 8 characters long.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO util (utilisateur, phrase, connected) VALUES (?, ?, datetime(CURRENT_TIMESTAMP, 'localtime'))",
                    (utilisateur, generate_password_hash(phrase))
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {utilisateur} is already registered"
            else:
                return redirect(url_for("auth.login"))
        
        flash(error)
    
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        utilisateur = request.form['username']
        phrase = request.form['password']
        db = get_db()
        error = None
        util = db.execute(
            'SELECT * FROM util WHERE utilisateur = ?', (utilisateur,)
        ).fetchone()

        if util is None:
            error = 'Incorrect username.'
        elif not check_password_hash(util['phrase'], phrase):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()
            session['util_id'] = util['id']
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    util_id = session.get('util_id')

    if util_id is None:
        g.util = None
    else:
        g.util = get_db().execute(
            'SELECT * FROM util WHERE id = ?', (util_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.util is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    return wrapped_view