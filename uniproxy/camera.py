import requests
import os
import urllib.request
from pathlib import Path

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Response
)
from werkzeug.exceptions import abort
from uniproxy.auth import login_required
from uniproxy.db import get_db

bp = Blueprint('camera', __name__)

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
        abort(404, f"No cameras found for project with id: {id}")
    
    return cameras

def get_project(id):
    project = get_db().execute(
        'SELECT * FROM project WHERE id = ?', (id,)
    ).fetchone()

    if project is None:
        abort(404, f"No project found with id: {id}")

    return project

def authenticate(camera):
    url = f"http://{camera['ip']}/api/1.1/login"
    payload = {"username": camera['username'], "password": camera['password']}
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    cookie = response.headers['Set-Cookie']

    if cookie is not None:
        db = get_db()
        db.execute(
            'UPDATE camera SET cookie = ? WHERE id = ?', (cookie, camera['id'],)
        )
        db.commit()
        return True
    return False

@bp.route('/c/<int:id>/image', methods=('GET',))
@login_required
def get_image(id, secondtry=False):
    db = get_db()
    camera = db.execute(
        'SELECT * FROM camera WHERE id = ?', (id,)
    ).fetchone()

    if camera['cookie'] is not None:
        url = f"http://{camera['ip']}/snap.jpeg"
        headers = {"Cookie": camera['cookie']}
        try:
            response = requests.request("GET", url, headers=headers, stream=True)
            response = Response(response.raw)
            response.headers['Content-Type'] = 'image/jpeg'
            return response
        except:
            abort(404, f"Something went wrong with camera id: {camera['id']}")
    else:
        if not secondtry:
            authenticate(camera)
            get_image(camera['id'], True)
        else:
            abort(404, 'Could not retrieve camera image')


@bp.route('/p/<int:id>', methods=('GET',))
def index(id):
    cameras = get_cameras_from_project(id)
    project = get_project(id)
    return render_template('camera/index.html', cameras=cameras, project=project)

@bp.route('/p/<int:id>/create', methods=('GET', 'POST'))
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
                'INSERT INTO camera (project_id, ip, name, username, password)'
                ' VALUES (?, ?, ?, ?, ?)',
                (project_id, ip, name, '' if not username else username, '' if not password else password)
            )
            db.commit()
            return redirect(url_for('camera.index', id=project_id))
    return render_template('camera/create.html', id=id)

@bp.route('/p/<int:id>/update/<int:cid>', methods=('GET', 'POST'))
@login_required
def update(id, cid):
    camera = get_camera(cid)

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
            return redirect(url_for('camera.index', id=id))
    return render_template('camera/update.html', id=id, camera=camera)

@bp.route('/p/<int:id>/delete/<int:cid>', methods=('GET',))
@login_required
def delete(id, cid):
    get_camera(cid)
    db = get_db()
    db.execute('DELETE FROM camera WHERE id = ?', (cid,))
    db.commit()
    return redirect(url_for('camera.index', id=id))

@bp.route('/p/<int:id>/refresh', methods=('GET',))
@login_required
def refresh_all(id):
    db = get_db()
    cameras = db.execute(
        'SELECT * FROM camera WHERE project_id = ?', (id,)
    ).fetchall()

    if cameras is None:
        abort(404, f"No cameras found for project with id: {id}")
    
    for camera in cameras:
        if camera['cookie'] is None:
            if camera['username'] is not None:
                if camera['password'] is not None:
                    authenticate(camera)   
        try:
            urllib.request.urlopen(f"http://{camera['ip']}", timeout=2)
            db.execute(
                'UPDATE camera SET online = 1 WHERE id = ?',
                (camera['id'],)
            )
            db.commit()
        except:
            db.execute(
                'UPDATE camera SET online = 0 WHERE id = ?',
                (camera['id'],)
            )
            db.commit()
    return redirect(url_for('camera.index', id=id))


