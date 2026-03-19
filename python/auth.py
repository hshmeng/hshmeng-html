from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from python.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password or not confirm_password:
            flash('所有字段均为必填项', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('auth.register'))

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('用户名已存在', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('注册成功，请登录！', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('登录成功！', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not check_password_hash(current_user.password, old_password):
        flash('原密码错误', 'danger')
    elif new_password != confirm_password:
        flash('两次新密码输入不一致', 'danger')
    else:
        current_user.password = generate_password_hash(new_password)
        current_user.must_change_password = False
        db.session.commit()
        flash('密码修改成功', 'success')
    return redirect(url_for('profile.profile', username=current_user.username))

@auth_bp.route('/force_change_password', methods=['GET', 'POST'])
@login_required
def force_change_password():
    if not current_user.must_change_password:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('两次新密码输入不一致', 'danger')
        elif new_password == '123456':
            flash('新密码不能与初始密码相同', 'danger')
        else:
            current_user.password = generate_password_hash(new_password)
            current_user.must_change_password = False
            db.session.commit()
            flash('密码修改成功，请继续使用！', 'success')
            return redirect(url_for('main.index'))
            
    return render_template('auth/force_change_password.html')
