from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from python.models import db, ShopProduct, UserOwnedProduct, RedemptionOrder, Notification

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/shop')
@login_required
def shop_index():
    kind = request.args.get('kind')
    vt = request.args.get('vt')
    q = ShopProduct.query.filter_by(is_active=True)
    if vt in ('avatar_frame', 'title', 'profile_bg'):
        q = q.filter_by(kind='virtual', virtual_type=vt)
    else:
        if kind in ('virtual', 'physical'):
            q = q.filter_by(kind=kind)
    products = q.order_by(ShopProduct.created_at.desc()).all()
    return render_template('shop/shop.html', products=products, kind=kind, vt=vt)

@shop_bp.route('/shop/inventory')
@login_required
def inventory():
    owned = UserOwnedProduct.query.filter_by(user_id=current_user.id).join(ShopProduct).order_by(ShopProduct.created_at.desc()).all()
    titles = [o.product for o in owned if o.product.kind == 'virtual' and o.product.virtual_type == 'title']
    frames = [o.product for o in owned if o.product.kind == 'virtual' and o.product.virtual_type == 'avatar_frame']
    bgs = [o.product for o in owned if o.product.kind == 'virtual' and o.product.virtual_type == 'profile_bg']
    physical_orders = RedemptionOrder.query.join(ShopProduct).filter(
        RedemptionOrder.user_id == current_user.id,
        ShopProduct.kind == 'physical'
    ).order_by(RedemptionOrder.created_at.desc()).all()
    return render_template('shop/inventory.html', titles=titles, frames=frames, bgs=bgs, physical_orders=physical_orders)

@shop_bp.route('/shop/equip', methods=['POST'])
@login_required
def equip():
    product_id = request.form.get('product_id', type=int)
    action = request.form.get('action')
    if action not in ('title', 'avatar_frame', 'profile_bg'):
        return redirect(url_for('shop.inventory'))
    owned = UserOwnedProduct.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if not owned:
        flash('你未拥有该物品', 'danger')
        return redirect(url_for('shop.inventory'))
    p = owned.product
    if p.kind != 'virtual' or p.virtual_type != action:
        flash('物品类型不匹配', 'danger')
        return redirect(url_for('shop.inventory'))
    if action == 'title':
        current_user.title_text = p.title_text
    elif action == 'avatar_frame':
        current_user.avatar_frame = p.style_key
    else:
        current_user.profile_bg = p.style_key
    db.session.commit()
    flash('装备成功', 'success')
    return redirect(url_for('shop.inventory'))

@shop_bp.route('/shop/unequip', methods=['POST'])
@login_required
def unequip():
    action = request.form.get('action')
    if action == 'title':
        current_user.title_text = None
    elif action == 'avatar_frame':
        current_user.avatar_frame = None
    elif action == 'profile_bg':
        current_user.profile_bg = None
    else:
        return redirect(url_for('shop.inventory'))
    db.session.commit()
    flash('已卸下', 'success')
    return redirect(url_for('shop.inventory'))

@shop_bp.route('/shop/orders/<int:order_id>/address', methods=['POST'])
@login_required
def update_order_address(order_id):
    order = RedemptionOrder.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    if order.product.kind != 'physical':
        return redirect(url_for('shop.inventory'))
    shipping_name = (request.form.get('shipping_name') or '').strip()
    shipping_phone = (request.form.get('shipping_phone') or '').strip()
    shipping_address = (request.form.get('shipping_address') or '').strip()
    if not shipping_name or not shipping_phone or not shipping_address:
        flash('请填写完整收货信息', 'danger')
        return redirect(url_for('shop.inventory'))
    order.shipping_name = shipping_name
    order.shipping_phone = shipping_phone
    order.shipping_address = shipping_address
    if order.status in ('pending', 'need_address'):
        order.status = 'processing'
    db.session.commit()
    flash('收货信息已保存', 'success')
    return redirect(url_for('shop.inventory'))

@shop_bp.route('/shop/redeem/<int:product_id>', methods=['POST'])
@login_required
def redeem(product_id):
    p = ShopProduct.query.get_or_404(product_id)
    if not p.is_active:
        flash('该商品已下架', 'danger')
        return redirect(url_for('shop.shop_index'))

    qty = request.form.get('quantity', 1, type=int)
    if not qty or qty <= 0:
        flash('数量不合法', 'danger')
        return redirect(url_for('shop.shop_index'))

    if p.kind == 'virtual':
        owned = UserOwnedProduct.query.filter_by(user_id=current_user.id, product_id=p.id).first()
        if owned:
            flash('你已拥有该虚拟物品', 'warning')
            return redirect(url_for('shop.shop_index'))
        qty = 1

    if p.max_per_user is not None:
        already = db.session.query(db.func.coalesce(db.func.sum(RedemptionOrder.quantity), 0)).filter(
            RedemptionOrder.user_id == current_user.id,
            RedemptionOrder.product_id == p.id,
            RedemptionOrder.status != 'cancelled'
        ).scalar()
        if (already or 0) + qty > p.max_per_user:
            flash(f'该商品每人限购 {p.max_per_user} 件', 'danger')
            return redirect(url_for('shop.shop_index'))

    if p.stock is not None and p.stock < qty:
        flash('库存不足', 'danger')
        return redirect(url_for('shop.shop_index'))

    total_cost = p.price_points * qty
    if current_user.points < total_cost:
        flash('积分不足', 'danger')
        return redirect(url_for('shop.shop_index'))

    shipping_name = None
    shipping_phone = None
    shipping_address = None

    current_user.points -= total_cost
    if p.stock is not None:
        p.stock -= qty

    order = RedemptionOrder(
        user_id=current_user.id,
        product_id=p.id,
        quantity=qty,
        points_spent=total_cost,
        status='need_address' if p.kind == 'physical' else 'pending',
        shipping_name=shipping_name,
        shipping_phone=shipping_phone,
        shipping_address=shipping_address,
    )
    db.session.add(order)

    if p.kind == 'virtual':
        owned = UserOwnedProduct.query.filter_by(user_id=current_user.id, product_id=p.id).first()
        if not owned:
            db.session.add(UserOwnedProduct(user_id=current_user.id, product_id=p.id))
        if p.virtual_type == 'title' and p.title_text:
            current_user.title_text = p.title_text
        if p.virtual_type == 'avatar_frame' and p.style_key:
            current_user.avatar_frame = p.style_key
        if p.virtual_type == 'profile_bg' and p.style_key:
            current_user.profile_bg = p.style_key
        order.status = 'fulfilled'

    db.session.add(Notification(
        user_id=current_user.id,
        sender_id=None,
        type='redeem',
        content=f'你已兑换：{p.name}（{total_cost} 积分）'
    ))

    db.session.commit()
    flash('兑换成功', 'success')
    return redirect(url_for('shop.shop_index'))
