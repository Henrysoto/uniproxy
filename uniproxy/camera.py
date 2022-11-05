from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from uniproxy.auth import login_required
from uniproxy.db import get_db

bp = Blueprint('camera', __name__)

@bp.route('/<int:id>/cameras')
def index(id):
    cameras = get_cameras_from_project(id)
    return render_template('home/index.html', cameras=cameras)

@bp.route('/<int:id>/create', methods=('GET', 'POST'))
@login_required
def create(id):
    if request.method == 'POST':
        ip = request.form['ipaddress'].strip()
        project_id = id
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        name = request.form['name'].strip()
        error = None

        if not ip:
            error = 'IP Address field is invalid.'
        elif not name:
            error = 'Name field is invalid.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO camera (ip, name, username, password)'
                ' VALUES (?, ?, ?, ?)',
                (ip, name, '' if not username else username, '' if not password else password)
            )
            db.commit()
            return redirect(url_for('camera.index'))
    return render_template('camera/create.html')

def get_camera(id):
    camera = get_db().execute(
        'SELECT * FROM camera WHERE id = ?',
        (id,)
    ).fetchone()

    if camera is None:
        abort(404, f"Camera id {id} not found")
    
    return camera

def get_cameras_from_project(id):
    cameras = get_db().execute(
        'SELECT * FROM camera WHERE project_id = ?', (id,)
    ).fetchall()

    if cameras is None:
        abort(404, f"No cameras found for this project")
    
    return cameras

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    camera = get_camera(id)

    if request.method == 'POST':
        ip = request.form['ipaddress'].strip()
        name = request.form['name'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        error = None

        if not ip:
            error = 'IP Address field is invalid.'
        elif not name:
            error = 'Name field is invalid.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE camera SET ip = ?, name = ?, username = ?, password = ? WHERE id = ?',
                (ip, name, '' if not username else username, '' if not password else password, id)
            )
            db.commit()
            return redirect(url_for('camera.index'))
    return render_template('camera/update.html', camera=camera)

@bp.route('/<int:id>/delete', methods=('GET',))
@login_required
def delete(id):
    get_camera(id)
    db = get_db()
    db.execute('DELETE FROM camera WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('camera.index'))