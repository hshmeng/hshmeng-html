import os
from flask import Flask, render_template, g
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from python.models import db, User, Notification, ShopProduct, UserOwnedProduct
from sqlalchemy import text

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
    from python.messages import messages_bp
    from python.shop import shop_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(shop_bp)

    # 全局请求拦截器：强制修改密码
    from flask import request, redirect, url_for, flash
    from flask_login import current_user

    @app.before_request
    def load_unread_count():
        if current_user.is_authenticated:
            g.unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        else:
            g.unread_count = 0

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
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # 创建数据库表
    with app.app_context():
        db.create_all()
        with db.engine.connect() as conn:
            cols = [r[1] for r in conn.execute(text("PRAGMA table_info(user)")).fetchall()]
            if 'title_text' not in cols:
                conn.execute(text("ALTER TABLE user ADD COLUMN title_text VARCHAR(50)"))
            if 'avatar_frame' not in cols:
                conn.execute(text("ALTER TABLE user ADD COLUMN avatar_frame VARCHAR(30)"))
            if 'profile_bg' not in cols:
                conn.execute(text("ALTER TABLE user ADD COLUMN profile_bg VARCHAR(30)"))
            sp_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(shop_product)")).fetchall()]
            if sp_cols and 'max_per_user' not in sp_cols:
                conn.execute(text("ALTER TABLE shop_product ADD COLUMN max_per_user INTEGER"))
            conn.commit()
        # 如果不存在管理员账号，则创建一个默认的
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            hashed_pw = generate_password_hash('admin123')
            admin = User(username='admin', password=hashed_pw, is_admin=True)
            db.session.add(admin)
            db.session.commit()
        if ShopProduct.query.count() == 0:
            db.session.add_all([
                ShopProduct(name='称号：新人冒险者', kind='virtual', virtual_type='title', title_text='新人冒险者', price_points=30, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='称号：勇者', kind='virtual', virtual_type='title', title_text='勇者', price_points=60, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='称号：传奇', kind='virtual', virtual_type='title', title_text='传奇', price_points=120, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='称号：大师', kind='virtual', virtual_type='title', title_text='大师', price_points=200, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='称号：王者', kind='virtual', virtual_type='title', title_text='王者', price_points=300, stock=None, max_per_user=1, is_active=True),

                ShopProduct(name='头像框：红', kind='virtual', virtual_type='avatar_frame', style_key='red', price_points=50, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='头像框：橙', kind='virtual', virtual_type='avatar_frame', style_key='orange', price_points=50, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='头像框：黄', kind='virtual', virtual_type='avatar_frame', style_key='yellow', price_points=50, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='头像框：绿', kind='virtual', virtual_type='avatar_frame', style_key='green', price_points=50, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='头像框：青', kind='virtual', virtual_type='avatar_frame', style_key='cyan', price_points=50, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='头像框：蓝', kind='virtual', virtual_type='avatar_frame', style_key='blue', price_points=50, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='头像框：紫', kind='virtual', virtual_type='avatar_frame', style_key='purple', price_points=50, stock=None, max_per_user=1, is_active=True),

                ShopProduct(name='背景：红', kind='virtual', virtual_type='profile_bg', style_key='red', price_points=60, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='背景：橙', kind='virtual', virtual_type='profile_bg', style_key='orange', price_points=60, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='背景：黄', kind='virtual', virtual_type='profile_bg', style_key='yellow', price_points=60, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='背景：绿', kind='virtual', virtual_type='profile_bg', style_key='green', price_points=60, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='背景：青', kind='virtual', virtual_type='profile_bg', style_key='cyan', price_points=60, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='背景：蓝', kind='virtual', virtual_type='profile_bg', style_key='blue', price_points=60, stock=None, max_per_user=1, is_active=True),
                ShopProduct(name='背景：紫', kind='virtual', virtual_type='profile_bg', style_key='purple', price_points=60, stock=None, max_per_user=1, is_active=True),

                ShopProduct(name='实物：纪念贴纸', kind='physical', description='随机一张游戏主题贴纸', price_points=15, stock=None, max_per_user=None, is_active=True),
                ShopProduct(name='实物：周边徽章', kind='physical', description='金属徽章一枚', price_points=200, stock=30, max_per_user=1, is_active=True),
                ShopProduct(name='实物：鼠标垫', kind='physical', description='大号游戏鼠标垫', price_points=500, stock=10, max_per_user=1, is_active=True),
                ShopProduct(name='实物：T恤', kind='physical', description='游戏主题T恤（尺码随机）', price_points=800, stock=5, max_per_user=1, is_active=True),
            ])
            db.session.commit()
        else:
            colors = ['red','orange','yellow','green','cyan','blue','purple']
            keep_keys = set(colors)

            old_products = ShopProduct.query.filter(
                ShopProduct.kind == 'virtual',
                ShopProduct.virtual_type.in_(['avatar_frame','profile_bg']),
                ~ShopProduct.style_key.in_(list(keep_keys))
            ).all()
            if old_products:
                old_ids = [p.id for p in old_products]
                UserOwnedProduct.query.filter(UserOwnedProduct.product_id.in_(old_ids)).delete(synchronize_session=False)
                ShopProduct.query.filter(ShopProduct.id.in_(old_ids)).delete(synchronize_session=False)
                db.session.commit()

            title_defs = [
                ('新人冒险者', 30),
                ('勇者', 60),
                ('传奇', 120),
                ('大师', 200),
                ('王者', 300),
            ]
            title_texts = [t[0] for t in title_defs]

            for text_value, price in title_defs:
                p = ShopProduct.query.filter_by(kind='virtual', virtual_type='title', title_text=text_value).first()
                if not p:
                    db.session.add(ShopProduct(
                        name=f'称号：{text_value}',
                        kind='virtual',
                        virtual_type='title',
                        title_text=text_value,
                        price_points=price,
                        stock=None,
                        max_per_user=1,
                        is_active=True
                    ))
                else:
                    p.is_active = True
                    p.max_per_user = 1
                    p.stock = None

            ShopProduct.query.filter(
                ShopProduct.kind == 'virtual',
                ShopProduct.virtual_type == 'title',
                ~ShopProduct.title_text.in_(title_texts)
            ).update({'is_active': False}, synchronize_session=False)

            frame_names = {'red':'红','orange':'橙','yellow':'黄','green':'绿','cyan':'青','blue':'蓝','purple':'紫'}
            for k in colors:
                p = ShopProduct.query.filter_by(kind='virtual', virtual_type='avatar_frame', style_key=k).first()
                if not p:
                    db.session.add(ShopProduct(
                        name=f'头像框：{frame_names[k]}',
                        kind='virtual',
                        virtual_type='avatar_frame',
                        style_key=k,
                        price_points=50,
                        stock=None,
                        max_per_user=1,
                        is_active=True
                    ))
                else:
                    p.is_active = True
                    p.max_per_user = 1
                    p.stock = None

            for k in colors:
                p = ShopProduct.query.filter_by(kind='virtual', virtual_type='profile_bg', style_key=k).first()
                if not p:
                    db.session.add(ShopProduct(
                        name=f'背景：{frame_names[k]}',
                        kind='virtual',
                        virtual_type='profile_bg',
                        style_key=k,
                        price_points=60,
                        stock=None,
                        max_per_user=1,
                        is_active=True
                    ))
                else:
                    p.is_active = True
                    p.max_per_user = 1
                    p.stock = None

            if User.query.filter(User.avatar_frame.isnot(None), ~User.avatar_frame.in_(colors)).count() > 0:
                User.query.filter(User.avatar_frame.isnot(None), ~User.avatar_frame.in_(colors)).update({'avatar_frame': None}, synchronize_session=False)
            if User.query.filter(User.profile_bg.isnot(None), ~User.profile_bg.in_(colors)).count() > 0:
                User.query.filter(User.profile_bg.isnot(None), ~User.profile_bg.in_(colors)).update({'profile_bg': None}, synchronize_session=False)
            db.session.commit()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)
