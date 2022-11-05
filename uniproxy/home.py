from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from uniproxy.auth import login_required
from uniproxy.db import get_db

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    db = get_db()
    items = db.execute(
        'SELECT i.id, camera_id, author_id, created, body'
        ' FROM item i JOIN camera c ON i.camera_id = c.id'
        ' JOIN util u ON i.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('home/index.html', items=items)