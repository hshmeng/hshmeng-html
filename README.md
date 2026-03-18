# 游戏交流社区项目说明

这是一个基于 Python Flask 框架开发的游戏交流社区。支持用户注册、登录、发帖、评论、点赞、收藏、打赏、签到等功能，并提供管理员后台管理功能。

## 目录结构及文件用途

### 根目录
- `app.py`: 项目入口文件。负责 Flask 应用的初始化、配置、蓝图注册、错误处理以及数据库表的初始化。
- `requirements.txt`: 项目依赖列表。记录了运行本项目所需的 Python 库。
- `logo.ico`: 网站图标文件（应放置在此处或 `html/` 下）。

### `python/` (后端逻辑)
- [models.py](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/python/models.py): 数据库模型定义。包含用户、帖子、评论、点赞、收藏、打赏记录等表的结构定义。
- [auth.py](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/python/auth.py): 用户认证蓝图。处理注册、登录、退出、修改密码及强制重置密码逻辑。
- [main.py](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/python/main.py): 核心业务蓝图。处理首页展示、分页加载 API、文件上传下载及网站图标路由。
- [post.py](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/python/post.py): 帖子相关蓝图。处理发帖、帖子详情、删除帖子、评论、点赞、收藏及打赏逻辑。
- [profile.py](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/python/profile.py): 个人主页蓝图。处理个人空间展示、头像上传及每日签到逻辑。
- [admin.py](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/python/admin.py): 管理员后台蓝图。处理用户管理、强制重置密码及积分增减逻辑。
- [utils.py](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/python/utils.py): 工具函数。包含头像保存等通用逻辑。
- `__init__.py`: 使 `python` 文件夹成为一个 Python 包。

### `html/` (前端模板)
- [layout.html](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/html/layout.html): 基础布局模板。包含导航栏、全局样式和 JavaScript 脚本引用。
- [index.html](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/html/index.html): 网站首页。展示社区动态（左侧）和官方新闻（右侧），支持下拉加载。
- [login.html](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/html/login.html): 登录页面。
- [register.html](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/html/register.html): 注册页面。
- [profile.html](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/html/profile.html): 个人主页页面。分类展示动态、点赞和收藏，支持修改密码。
- [post.html](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/html/post.html): 帖子详情页面。展示正文、打赏记录和评论区，包含点赞、收藏、打赏按钮。
- [create_post.html](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/html/create_post.html): 发布动态/新闻页面。
- [admin_users.html](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/html/admin_users.html): 管理员后台页面。展示用户列表并支持重置密码和积分管理。
- [force_change_password.html](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/html/force_change_password.html): 强制修改密码页面。
- [404.html](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/html/404.html): 页面未找到报错页。
- [500.html](file:///c:/Users/HSHMENG/Desktop/hshmeng-html/html/500.html): 服务器内部错误报错页。

### `database/` (数据库)
- `community.db`: SQLite 数据库文件，存储所有用户和社区数据。

### `uploads/` (上传文件)
- 存储用户上传的个性化头像文件。

## 如何运行
1. 安装依赖：`pip install -r requirements.txt`
2. 运行应用：`python app.py`
3. 访问地址：`http://127.0.0.1:5000`
