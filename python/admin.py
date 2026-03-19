from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from python.models import db, User, Notification, ShopProduct, RedemptionOrder

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
    return render_template('admin/admin_users.html', users=users)

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

@admin_bp.route('/messages', methods=['GET', 'POST'])
def admin_messages():
    users = User.query.order_by(User.username.asc()).all()
    preset_user_id = request.args.get('user_id', type=int)
    if request.method == 'POST':
        target = request.form.get('target')
        content = (request.form.get('content') or '').strip()
        if not content:
            flash('请输入消息内容', 'danger')
            return redirect(url_for('admin.admin_messages'))

        if target == 'all':
            recipients = User.query.filter(User.id != current_user.id).all()
            for u in recipients:
                db.session.add(Notification(
                    user_id=u.id,
                    sender_id=current_user.id,
                    type='admin_message',
                    content=content
                ))
            db.session.commit()
            flash('已群发站内消息', 'success')
            return redirect(url_for('admin.manage_users'))

        user_ids = request.form.getlist('user_ids')
        user_ids = [int(x) for x in user_ids if str(x).isdigit()]
        user_ids = [uid for uid in user_ids if uid != current_user.id]
        if not user_ids:
            flash('请选择接收人', 'danger')
            return redirect(url_for('admin.admin_messages'))
        recipients = User.query.filter(User.id.in_(user_ids)).all()
        for u in recipients:
            db.session.add(Notification(
                user_id=u.id,
                sender_id=current_user.id,
                type='admin_message',
                content=content
            ))
        db.session.commit()
        flash(f'已发送站内消息（{len(recipients)} 人）', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/admin_messages.html', users=users, preset_user_id=preset_user_id)

@admin_bp.route('/shop/products', methods=['GET', 'POST'])
def shop_products():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        kind = request.form.get('kind')
        virtual_type = request.form.get('virtual_type') or None
        title_text = (request.form.get('title_text') or '').strip() or None
        style_key = request.form.get('style_key') or None
        description = (request.form.get('description') or '').strip() or None
        price_points = request.form.get('price_points', type=int) or 0
        stock = request.form.get('stock', type=int)
        max_per_user = request.form.get('max_per_user', type=int)
        is_active = request.form.get('is_active') == 'on'

        if not name:
            flash('请输入商品名称', 'danger')
            return redirect(url_for('admin.shop_products'))
        if kind not in ('virtual', 'physical'):
            flash('商品类型不正确', 'danger')
            return redirect(url_for('admin.shop_products'))
        if price_points < 0:
            flash('积分价格不正确', 'danger')
            return redirect(url_for('admin.shop_products'))
        if max_per_user is not None and max_per_user <= 0:
            flash('每人限购数量不正确', 'danger')
            return redirect(url_for('admin.shop_products'))
        if kind == 'virtual' and max_per_user is None:
            max_per_user = 1

        p = ShopProduct(
            name=name,
            description=description,
            kind=kind,
            virtual_type=virtual_type if kind == 'virtual' else None,
            title_text=title_text if kind == 'virtual' and virtual_type == 'title' else None,
            style_key=style_key if kind == 'virtual' and virtual_type in ('avatar_frame', 'profile_bg') else None,
            price_points=price_points,
            stock=stock,
            max_per_user=max_per_user,
            is_active=is_active,
        )
        db.session.add(p)
        db.session.commit()
        flash('已创建商品', 'success')
        return redirect(url_for('admin.shop_products'))

    products = ShopProduct.query.order_by(ShopProduct.created_at.desc()).all()
    return render_template('admin/admin_shop_products.html', products=products)

@admin_bp.route('/shop/products/<int:product_id>/toggle', methods=['POST'])
def shop_product_toggle(product_id):
    p = ShopProduct.query.get_or_404(product_id)
    p.is_active = not p.is_active
    db.session.commit()
    return redirect(url_for('admin.shop_products'))

@admin_bp.route('/shop/orders')
def shop_orders():
    orders = RedemptionOrder.query.order_by(RedemptionOrder.created_at.desc()).all()
    return render_template('admin/admin_shop_orders.html', orders=orders)

@admin_bp.route('/shop/orders/<int:order_id>/status', methods=['POST'])
def shop_order_status(order_id):
    order = RedemptionOrder.query.get_or_404(order_id)
    status = request.form.get('status')
    if status not in ('need_address', 'pending', 'processing', 'shipped', 'fulfilled', 'cancelled'):
        return redirect(url_for('admin.shop_orders'))
    order.status = status
    status_name = {
        'need_address': '待填写地址',
        'pending': '待处理',
        'processing': '处理中',
        'shipped': '已发货',
        'fulfilled': '已完成',
        'cancelled': '已取消',
    }.get(status, status)
    db.session.add(Notification(
        user_id=order.user_id,
        sender_id=current_user.id,
        type='order_status',
        content=f'你的兑换订单《{order.product.name}》状态更新为：{status_name}'
    ))
    db.session.commit()
    return redirect(url_for('admin.shop_orders'))
