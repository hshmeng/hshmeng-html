from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from python.models import db, User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        flash('无权限访问', 'danger')
        return redirect(url_for('main.index'))

@admin_bp.route('/users')
def manage_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/user/<int:user_id>/reset_password', methods=['POST'])
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    user.password = generate_password_hash('123456')
    user.must_change_password = True
    db.session.commit()
    flash(f'已将用户 {user.username} 的密码重置为 123456', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/user/<int:user_id>/adjust_points', methods=['POST'])
def adjust_points(user_id):
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')
    amount = request.form.get('amount', type=int)
    
    if not amount or amount <= 0:
        flash('请输入有效的积分数量', 'danger')
        return redirect(url_for('admin.manage_users'))
        
    if action == 'add':
        user.points += amount
        flash(f'已为用户 {user.username} 增加 {amount} 积分', 'success')
    elif action == 'sub':
        user.points -= amount
        flash(f'已扣除用户 {user.username} {amount} 积分', 'success')
        
    db.session.commit()
    return redirect(url_for('admin.manage_users'))
