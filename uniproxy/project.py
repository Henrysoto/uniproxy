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

def get_project(id):
    project = get_db().execute(
        'SELECT * FROM project WHERE id = ?', (id,)
    ).fetchone()

    if project is None:
        abort(404, f"No project found with id: {id}")

    return project

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
            id = db.execute(
                'SELECT MAX(id) FROM project'
            ).fetchone()
            return redirect(url_for('camera.index', id=id[0]))
    return render_template('project/create.html')

@bp.route('/<int:id>/delete', methods=('GET',))
@login_required
def delete(id):
    get_project(id)
    db = get_db()
    db.execute('DELETE FROM project WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('project.index'))