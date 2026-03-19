import os
from flask import Blueprint, render_template, request, jsonify, url_for, send_from_directory, current_app
from python.models import db, Post, Comment

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # 首页左侧显示所有用户发布的帖子 (前5条)
    all_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()
    # 首页右侧显示管理员发布的公开新闻 (前5条)
    news_posts = Post.query.filter_by(is_news=True).order_by(Post.date_posted.desc()).limit(5).all()
    return render_template('main/index.html', all_posts=all_posts, news_posts=news_posts)

@main_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@main_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'html'), 'logo.ico', mimetype='image/vnd.microsoft.icon')

# API 接口用于下拉加载更多所有帖子
@main_bp.route('/api/posts')
def get_more_posts():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    post_list = []
    for post in posts.items:
        post_list.append({
            'id': post.id,
            'title': post.title,
            'content': post.content[:300] + ('...' if len(post.content) > 300 else ''),
            'author': post.author.username,
            'is_admin': post.author.is_admin,
            'avatar': url_for('main.uploaded_file', filename=post.author.avatar) if post.author.avatar != 'default.png' else 'https://ui-avatars.com/api/?name=' + post.author.username,
            'date': post.date_posted.strftime('%Y-%m-%d %H:%M'),
            'comments_count': len(post.comments)
        })
    return jsonify({'posts': post_list, 'has_next': posts.has_next})

# API 接口用于下拉加载更多新闻
@main_bp.route('/api/news')
def get_more_news():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    posts = Post.query.filter_by(is_news=True).order_by(Post.date_posted.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    news_list = []
    for post in posts.items:
        news_list.append({
            'id': post.id,
            'title': post.title,
            'content': post.content[:300] + ('...' if len(post.content) > 300 else ''),
            'author': post.author.username,
            'avatar': url_for('main.uploaded_file', filename=post.author.avatar) if post.author.avatar != 'default.png' else 'https://ui-avatars.com/api/?name=' + post.author.username,
            'date': post.date_posted.strftime('%Y-%m-%d %H:%M'),
            'comments_count': len(post.comments)
        })
    return jsonify({'news': news_list, 'has_next': posts.has_next})

# API 接口用于下拉加载更多评论
@main_bp.route('/api/comments')
def get_more_comments():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    comments = Comment.query.order_by(Comment.date_posted.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    comment_list = []
    for comment in comments.items:
        comment_list.append({
            'id': comment.id,
            'content': comment.content,
            'author': comment.author.username,
            'is_admin': comment.author.is_admin,
            'avatar': url_for('main.uploaded_file', filename=comment.author.avatar) if comment.author.avatar != 'default.png' else 'https://ui-avatars.com/api/?name=' + comment.author.username,
            'date': comment.date_posted.strftime('%Y-%m-%d %H:%M'),
            'post_id': comment.post_id,
            'post_title': comment.post.title
        })
    return jsonify({'comments': comment_list, 'has_next': comments.has_next})
