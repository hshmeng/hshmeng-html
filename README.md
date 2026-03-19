# 游戏交流社区项目说明

这是一个基于 Python Flask 框架开发的游戏交流社区。支持用户注册、登录、发帖、评论、点赞、收藏、打赏、签到等功能，并提供管理员后台管理功能。

## 目录结构及文件用途

### 根目录
- `app.py`: 项目入口文件。负责 Flask 应用的初始化、配置、蓝图注册、错误处理以及数据库表的初始化。
- `requirements.txt`: 项目依赖列表。记录了运行本项目所需的 Python 库。

### `python/` (后端逻辑)
- `models.py`: 数据库模型定义。包含用户、帖子、评论、点赞、收藏、打赏记录等表的结构定义。
- `auth.py`: 用户认证蓝图。处理注册、登录、退出、修改密码及强制重置密码逻辑。
- `main.py`: 核心业务蓝图。处理首页展示、分页加载 API、文件上传下载及网站图标路由。
- `post.py`: 帖子相关蓝图。处理发帖、帖子详情、删除帖子、评论、点赞、收藏及打赏逻辑。
- `profile.py`: 个人主页蓝图。处理个人空间展示、头像上传及每日签到逻辑。
- `admin.py`: 管理员后台蓝图。处理用户管理、强制重置密码及积分增减逻辑。
- `utils.py`: 工具函数。重构了文件保存逻辑，通过 UUID 和提取真实扩展名确保文件名唯一且正确，解决了部分图片触发下载的问题。
- `__init__.py`: 使 `python` 文件夹成为一个 Python 包。

### `html/` (前端模板)
- `base/layout.html`: 基础布局模板。包含导航栏、全局样式和自定义 Lightbox（帖子图片居中全屏预览）功能。
- `main/index.html`: 网站首页。展示社区动态（左侧）和官方新闻（右侧），支持下拉加载。
- `auth/login.html` / `auth/register.html` / `auth/force_change_password.html`: 登录/注册/强制修改密码页面。
- `profile/profile.html`: 个人主页页面。展示用户资料、称号/头像框/背景效果，以及动态/点赞/收藏。
- `post/create_post.html` / `post/post.html`: 发帖页面与帖子详情页（含图片展示与互动）。
- `messages/messages.html`: 站内信息收件箱页面。
- `shop/shop.html` / `shop/inventory.html`: 积分商店与我的物品（装备/卸下、实物订单补充收货地址）。
- `admin/*`: 管理员后台页面（用户管理、站内消息、商品管理、订单管理）。
- `errors/404.html` / `errors/500.html`: 错误页面。
- `logo.ico`: 网站图标文件。

### `database/` (数据库)
- `community.db`: SQLite 数据库文件，存储所有用户和社区数据。

### `uploads/` (上传文件)
- 存储用户上传的个性化头像文件及帖子附带的图片。

## 功能特性
- **用户系统**：注册、登录、个人主页、每日签到领积分。
- **动态交流**：
    - 发布动态（支持同时上传最多5张图片）。
    - **发帖时图片实时预览**：在选择图片后，页面会显示缩略图，并支持单独移除不满意的图片。
    - **帖子图片全屏预览**：在帖子详情页，点击图片会触发一个定制的、无依赖的 Lightbox 效果，实现带遮罩的全屏预览。
    - 评论、点赞、收藏。
- **打赏机制**：支持使用积分打赏喜欢的帖子。
- **安全检查与健壮性**：
    - 对上传的头像及帖子图片进行真实性分析，防止非图片文件上传。
    - **文件名安全重构**：重写了文件上传逻辑，确保所有保存的图片都拥有唯一且正确的带点扩展名，从根本上解决了部分浏览器将图片识别为下载项的问题。
- **管理员后台**：管理用户、重置密码、手动增减用户积分。

## 如何运行
1. 安装依赖：`pip install -r requirements.txt`
2. 运行应用：`python app.py`
3. 访问地址：`http://127.0.0.1:5000`

## 数据库表结构与字段说明（community.db）

数据库使用 SQLite，核心模型定义在 [models.py](file:///d:/Data/BianCheng_WORD/Python/hshmeng-html/python/models.py)。

### 1) 用户：`user`（User）

| 字段 | 类型 | 允许为空 | 默认值 | 说明 |
|---|---|---:|---|---|
| id | Integer | 否 | - | 用户主键 |
| username | String(50) | 否 | - | 用户名（唯一） |
| password | String(100) | 否 | - | 密码哈希（不是明文） |
| avatar | String(200) | 是 | default.png | 头像文件名（位于 `uploads/`） |
| points | Integer | 是 | 0 | 当前积分余额 |
| last_signin | Date | 是 | NULL | 上次签到日期（用于限制每日签到一次） |
| is_admin | Boolean | 是 | False | 是否管理员 |
| must_change_password | Boolean | 是 | False | 是否强制修改密码（管理员重置后触发） |
| title_text | String(50) | 是 | NULL | 当前装备的称号文本（展示在主页/帖子） |
| avatar_frame | String(30) | 是 | NULL | 当前装备的头像框样式 key（如 `red`/`blue`） |
| profile_bg | String(30) | 是 | NULL | 当前装备的主页背景样式 key（如 `red`/`purple`） |

说明：
- `title_text/avatar_frame/profile_bg` 用于虚拟物品“装备效果”，样式在 [base/layout.html](file:///d:/Data/BianCheng_WORD/Python/hshmeng-html/html/base/layout.html) 中定义。

### 2) 帖子：`post`（Post）

| 字段 | 类型 | 允许为空 | 默认值 | 说明 |
|---|---|---:|---|---|
| id | Integer | 否 | - | 帖子主键 |
| title | String(100) | 否 | - | 标题 |
| content | Text | 否 | - | 内容 |
| date_posted | DateTime | 否 | 当前时间 | 发布时间 |
| user_id | Integer(FK) | 否 | - | 作者用户 ID（关联 `user.id`） |
| is_news | Boolean | 是 | False | 是否官方新闻（首页右侧展示） |

### 3) 帖子图片：`post_image`（PostImage）

| 字段 | 类型 | 允许为空 | 默认值 | 说明 |
|---|---|---:|---|---|
| id | Integer | 否 | - | 主键 |
| filename | String(200) | 否 | - | 图片文件名（位于 `uploads/`） |
| post_id | Integer(FK) | 否 | - | 所属帖子（关联 `post.id`） |
| date_uploaded | DateTime | 否 | 当前时间 | 上传时间 |

### 4) 评论：`comment`（Comment）

| 字段 | 类型 | 允许为空 | 默认值 | 说明 |
|---|---|---:|---|---|
| id | Integer | 否 | - | 主键 |
| content | Text | 否 | - | 评论内容 |
| date_posted | DateTime | 否 | 当前时间 | 评论时间 |
| user_id | Integer(FK) | 否 | - | 评论人（关联 `user.id`） |
| post_id | Integer(FK) | 否 | - | 被评论帖子（关联 `post.id`） |

### 5) 点赞：`like`（Like）

| 字段 | 类型 | 允许为空 | 默认值 | 说明 |
|---|---|---:|---|---|
| id | Integer | 否 | - | 主键 |
| user_id | Integer(FK) | 否 | - | 点赞用户（关联 `user.id`） |
| post_id | Integer(FK) | 否 | - | 被点赞帖子（关联 `post.id`） |
| date_liked | DateTime | 否 | 当前时间 | 点赞时间 |

### 6) 收藏：`favorite`（Favorite）

| 字段 | 类型 | 允许为空 | 默认值 | 说明 |
|---|---|---:|---|---|
| id | Integer | 否 | - | 主键 |
| user_id | Integer(FK) | 否 | - | 收藏用户（关联 `user.id`） |
| post_id | Integer(FK) | 否 | - | 被收藏帖子（关联 `post.id`） |
| date_favorited | DateTime | 否 | 当前时间 | 收藏时间 |

### 7) 打赏：`tip`（Tip）

| 字段 | 类型 | 允许为空 | 默认值 | 说明 |
|---|---|---:|---|---|
| id | Integer | 否 | - | 主键 |
| amount | Integer | 否 | - | 打赏积分数量 |
| sender_id | Integer(FK) | 否 | - | 打赏人（关联 `user.id`） |
| receiver_id | Integer(FK) | 否 | - | 收款人（帖子作者，关联 `user.id`） |
| post_id | Integer(FK) | 否 | - | 被打赏帖子（关联 `post.id`） |
| date_tipped | DateTime | 否 | 当前时间 | 打赏时间 |

### 8) 站内信息/通知：`notification`（Notification）

| 字段 | 类型 | 允许为空 | 默认值 | 说明 |
|---|---|---:|---|---|
| id | Integer | 否 | - | 主键 |
| user_id | Integer(FK) | 否 | - | 接收人（关联 `user.id`） |
| sender_id | Integer(FK) | 是 | NULL | 发送人（管理员/其他用户；系统通知可为空） |
| post_id | Integer(FK) | 是 | NULL | 关联帖子（可为空） |
| type | String(30) | 否 | system | 通知类型（如 `like`/`favorite`/`tip`/`admin_message`/`redeem`/`order_status`） |
| content | Text | 否 | - | 文案内容 |
| link | String(200) | 是 | NULL | 可点击跳转链接（可为空） |
| is_read | Boolean | 是 | False | 是否已读 |
| created_at | DateTime | 否 | 当前时间 | 生成时间 |

### 9) 积分商店商品：`shop_product`（ShopProduct）

| 字段 | 类型 | 允许为空 | 默认值 | 说明 |
|---|---|---:|---|---|
| id | Integer | 否 | - | 商品主键 |
| name | String(100) | 否 | - | 商品名称（展示用） |
| description | Text | 是 | NULL | 商品说明文案 |
| kind | String(20) | 否 | virtual | 商品大类：`virtual` 虚拟 / `physical` 实物 |
| virtual_type | String(30) | 是 | NULL | 虚拟细分：`title`/`avatar_frame`/`profile_bg`（实物为空） |
| title_text | String(50) | 是 | NULL | 称号内容（仅 `virtual_type=title` 使用） |
| style_key | String(30) | 是 | NULL | 样式 key（头像框/背景使用：如 `red`/`purple`） |
| price_points | Integer | 否 | 0 | 单价（积分） |
| stock | Integer | 是 | NULL | 库存；NULL 表示不限库存 |
| max_per_user | Integer | 是 | NULL | 每人限购数量；NULL 表示不限（虚拟商品通常为 1） |
| is_active | Boolean | 是 | True | 是否上架 |
| created_at | DateTime | 否 | 当前时间 | 创建时间 |

### 10) 用户已拥有物品：`user_owned_product`（UserOwnedProduct）

| 字段 | 类型 | 允许为空 | 默认值 | 说明 |
|---|---|---:|---|---|
| id | Integer | 否 | - | 主键 |
| user_id | Integer(FK) | 否 | - | 所属用户（关联 `user.id`） |
| product_id | Integer(FK) | 否 | - | 拥有的商品（关联 `shop_product.id`） |
| acquired_at | DateTime | 否 | 当前时间 | 获得时间 |

### 11) 兑换订单：`redemption_order`（RedemptionOrder）

| 字段 | 类型 | 允许为空 | 默认值 | 说明 |
|---|---|---:|---|---|
| id | Integer | 否 | - | 订单主键 |
| user_id | Integer(FK) | 否 | - | 下单用户（关联 `user.id`） |
| product_id | Integer(FK) | 否 | - | 兑换商品（关联 `shop_product.id`） |
| quantity | Integer | 否 | 1 | 数量 |
| points_spent | Integer | 否 | 0 | 实际消耗积分（= 单价 × 数量） |
| status | String(30) | 否 | pending | 订单状态：`need_address/pending/processing/shipped/fulfilled/cancelled` |
| shipping_name | String(50) | 是 | NULL | 收货人（实物订单） |
| shipping_phone | String(30) | 是 | NULL | 手机号（实物订单） |
| shipping_address | String(200) | 是 | NULL | 收货地址（实物订单） |
| created_at | DateTime | 否 | 当前时间 | 创建时间 |
| updated_at | DateTime | 否 | 当前时间 | 更新时间（自动更新） |
