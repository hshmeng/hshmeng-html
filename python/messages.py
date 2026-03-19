from flask import Blueprint, render_template, redirect, url_for, flash, request, g
from flask_login import login_required, current_user
from python.models import db, Notification

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages')
@login_required
def inbox():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('messages/messages.html', notifications=pagination.items, pagination=pagination, unread_count=getattr(g, 'unread_count', 0))

@messages_bp.route('/messages/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_read(notification_id):
    n = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    if not n.is_read:
        n.is_read = True
        db.session.commit()
    return redirect(request.referrer or url_for('messages.inbox'))

@messages_bp.route('/messages/read_all', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('已全部标记为已读', 'success')
    return redirect(url_for('messages.inbox'))
