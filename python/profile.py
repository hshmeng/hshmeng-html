from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from python.models import db, User, Post, Like, Favorite
from python.utils import save_avatar

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/signin', methods=['POST'])
@login_required
def signin():
    today = date.today()
    if current_user.last_signin == today:
        flash('您今天已经签到过了！', 'warning')
    else:
        current_user.points += 10 # 签到获得10积分
        current_user.last_signin = today
        db.session.commit()
        flash('签到成功！获得10积分。', 'success')
    return redirect(request.referrer or url_for('main.index'))

@profile_bp.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.date_posted.desc()).all()
    
    # 获取点赞和收藏的帖子
    liked_posts = Post.query.join(Like).filter(Like.user_id == user.id).order_by(Like.date_liked.desc()).all()
    fav_posts = Post.query.join(Favorite).filter(Favorite.user_id == user.id).order_by(Favorite.date_favorited.desc()).all()
    
    # 计算用户所有帖子获得的总赞数
    total_likes_received = sum(len(post.likes) for post in posts)
    
    return render_template('profile.html', user=user, posts=posts, liked_posts=liked_posts, fav_posts=fav_posts, total_likes_received=total_likes_received)

@profile_bp.route('/profile/update_avatar', methods=['POST'])
@login_required
def update_avatar():
    if 'avatar' not in request.files:
        flash('未选择文件', 'danger')
        return redirect(url_for('profile.profile', username=current_user.username))
    
    file = request.files['avatar']
    if file.filename == '':
        flash('未选择文件', 'danger')
        return redirect(url_for('profile.profile', username=current_user.username))
    
    if file:
        filename = save_avatar(file)
        if filename:
            current_user.avatar = filename
            db.session.commit()
            flash('头像更新成功！', 'success')
        else:
            flash('无效的图片文件，请上传真实的图片', 'danger')
    
    return redirect(url_for('profile.profile', username=current_user.username))
