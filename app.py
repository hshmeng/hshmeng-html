import os
from flask import Flask, render_template
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from python.models import db, User

def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, template_folder='html')
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'community.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB 限制

    # 确保必要的目录存在
    for folder in ['database', 'uploads']:
        path = os.path.join(basedir, folder)
        if not os.path.exists(path):
            os.makedirs(path)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 注册蓝图
    from python.main import main_bp
    from python.auth import auth_bp
    from python.profile import profile_bp
    from python.post import post_bp
    from python.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(admin_bp)

    # 全局请求拦截器：强制修改密码
    from flask import request, redirect, url_for, flash
    from flask_login import current_user

    @app.before_request
    def check_password_change():
        if current_user.is_authenticated and getattr(current_user, 'must_change_password', False):
            # 允许访问的路由：强制修改密码页面、退出登录、静态文件、favicon
            allowed_endpoints = ['auth.force_change_password', 'auth.logout', 'static', 'main.favicon']
            if request.endpoint not in allowed_endpoints:
                flash('管理员已重置您的密码，请先修改密码！', 'warning')
                return redirect(url_for('auth.force_change_password'))

    # 注册错误处理程序
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # 创建数据库表
    with app.app_context():
        db.create_all()
        # 如果不存在管理员账号，则创建一个默认的
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            hashed_pw = generate_password_hash('admin123')
            admin = User(username='admin', password=hashed_pw, is_admin=True)
            db.session.add(admin)
            db.session.commit()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
