from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from python.models import db, Post, Comment, Like, Favorite, Tip, User, PostImage, Notification
from python.utils import save_post_images

post_bp = Blueprint('post', __name__)

@post_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_news = request.form.get('is_news') == 'on' if current_user.is_admin else False
        
        if not title or not content:
            flash('标题和内容不能为空', 'danger')
            return redirect(url_for('post.create_post'))
        
        post = Post(title=title, content=content, author=current_user, is_news=is_news)
        db.session.add(post)
        
        # 处理图片上传
        files = request.files.getlist('images')
        if files:
            filenames = save_post_images(files)
            for filename in filenames:
                post_image = PostImage(filename=filename, post=post)
                db.session.add(post_image)
        
        db.session.commit()
        flash('发布成功！', 'success')
        return redirect(url_for('main.index') if is_news else url_for('profile.profile', username=current_user.username))
    return render_template('post/create_post.html')

@post_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    # 检查当前用户是否已点赞或收藏
    user_liked = False
    user_favorited = False
    if current_user.is_authenticated:
        user_liked = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first() is not None
        user_favorited = Favorite.query.filter_by(user_id=current_user.id, post_id=post.id).first() is not None
    
    return render_template('post/post.html', post=post, user_liked=user_liked, user_favorited=user_favorited)

@post_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content')
    if not content:
        flash('评论内容不能为空', 'danger')
        return redirect(url_for('post.post_detail', post_id=post.id))
    
    comment = Comment(content=content, author=current_user, post=post)
    db.session.add(comment)
    db.session.commit()
    flash('评论发表成功！', 'success')
    return redirect(url_for('post.post_detail', post_id=post.id))

@post_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if like:
        db.session.delete(like)
        flash('已取消点赞', 'info')
    else:
        new_like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(new_like)
        if post.user_id != current_user.id:
            db.session.add(Notification(
                user_id=post.user_id,
                sender_id=current_user.id,
                post_id=post.id,
                type='like',
                content=f'{current_user.username} 点赞了你的帖子《{post.title}》',
                link=url_for('post.post_detail', post_id=post.id)
            ))
        flash('点赞成功！', 'success')
    db.session.commit()
    return redirect(url_for('post.post_detail', post_id=post.id))

@post_bp.route('/post/<int:post_id>/favorite', methods=['POST'])
@login_required
def favorite_post(post_id):
    post = Post.query.get_or_404(post_id)
    fav = Favorite.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if fav:
        db.session.delete(fav)
        flash('已从收藏夹移除', 'info')
    else:
        new_fav = Favorite(user_id=current_user.id, post_id=post.id)
        db.session.add(new_fav)
        if post.user_id != current_user.id:
            db.session.add(Notification(
                user_id=post.user_id,
                sender_id=current_user.id,
                post_id=post.id,
                type='favorite',
                content=f'{current_user.username} 收藏了你的帖子《{post.title}》',
                link=url_for('post.post_detail', post_id=post.id)
            ))
        flash('收藏成功！', 'success')
    db.session.commit()
    return redirect(url_for('post.post_detail', post_id=post.id))

@post_bp.route('/post/<int:post_id>/tip', methods=['POST'])
@login_required
def tip_post(post_id):
    post = Post.query.get_or_404(post_id)
    amount = request.form.get('amount', type=int)
    
    if not amount or amount <= 0:
        flash('打赏金额必须大于0', 'danger')
        return redirect(url_for('post.post_detail', post_id=post.id))
    
    if current_user.points < amount:
        flash('积分不足，快去签到领积分吧！', 'danger')
        return redirect(url_for('post.post_detail', post_id=post.id))
    
    if current_user.id == post.user_id:
        flash('不能打赏自己的作品哦', 'warning')
        return redirect(url_for('post.post_detail', post_id=post.id))

    # 执行打赏逻辑
    current_user.points -= amount
    post.author.points += amount
    
    new_tip = Tip(amount=amount, sender_id=current_user.id, receiver_id=post.user_id, post_id=post.id)
    db.session.add(new_tip)
    db.session.add(Notification(
        user_id=post.user_id,
        sender_id=current_user.id,
        post_id=post.id,
        type='tip',
        content=f'{current_user.username} 打赏了你 {amount} 积分（帖子《{post.title}》）',
        link=url_for('post.post_detail', post_id=post.id)
    ))
    db.session.commit()
    
    flash(f'打赏成功！打赏了 {amount} 积分', 'success')
    return redirect(url_for('post.post_detail', post_id=post.id))

@post_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # 只有帖子作者或管理员可以删除
    if post.author != current_user and not current_user.is_admin:
        flash('您没有权限删除此帖子', 'danger')
        return redirect(url_for('post.post_detail', post_id=post.id))
    
    # 删除相关的评论、点赞、收藏和打赏记录
    Comment.query.filter_by(post_id=post.id).delete()
    Like.query.filter_by(post_id=post.id).delete()
    Favorite.query.filter_by(post_id=post.id).delete()
    Tip.query.filter_by(post_id=post.id).delete()
    
    db.session.delete(post)
    db.session.commit()
    
    flash('帖子已成功删除', 'success')
    return redirect(url_for('main.index'))
