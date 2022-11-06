from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from uniproxy.auth import login_required
from uniproxy.db import get_db

bp = Blueprint('project', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    projects = db.execute(
        'SELECT * FROM project'
    ).fetchall()

    if projects is None:
        abort(404, f"No projects yet.")
    
    return render_template('project/index.html', projects=projects)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name'].strip()
        location = request.form['location'].strip().capitalize()
        error = None

        if not name:
            error = 'Name must be valid.'
        elif not location:
            error = 'Location must be valid.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO project (name, location, created)'
                " VALUES (?, ?, datetime(CURRENT_TIMESTAMP, 'localtime'))",
                (name, location)
            )
            db.commit()
            return redirect(url_for('project.index'))
    return render_template('project/create.html')
