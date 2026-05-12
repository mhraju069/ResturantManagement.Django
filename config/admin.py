from django.db.models import Sum, Count, F
from authentication.models import User
from order.models import Order, OrderItem
from product.models import FoodItem, FoodImage
from payment.models import Payments
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import json


def _get_revenue_by_period(paid_orders, days):
    """Return list of {label, value} dicts for the given number of past days."""
    now = timezone.now()
    data = []
    if days == 7:
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            total = paid_orders.filter(
                created_at__date=day.date()
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            data.append({"label": day.strftime("%a"), "value": float(total)})
    elif days == 30:
        # Weekly buckets over 4 weeks
        for i in range(3, -1, -1):
            week_start = now - timedelta(days=(i + 1) * 7)
            week_end   = now - timedelta(days=i * 7)
            total = paid_orders.filter(
                created_at__gte=week_start, created_at__lt=week_end
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            data.append({"label": f"W{4 - i}", "value": float(total)})
    else:
        # 12 months
        current_year = now.year
        current_month = now.month
        for i in range(11, -1, -1):
            target_month = current_month - i
            target_year = current_year
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            month_start = now.replace(year=target_year, month=target_month, day=1,
                                      hour=0, minute=0, second=0, microsecond=0)
            next_month_num = target_month + 1
            next_year_num = target_year
            if next_month_num > 12:
                next_month_num = 1
                next_year_num += 1
            next_month = now.replace(year=next_year_num, month=next_month_num, day=1,
                                     hour=0, minute=0, second=0, microsecond=0)
            total = paid_orders.filter(
                created_at__gte=month_start, created_at__lt=next_month
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            data.append({"label": month_start.strftime("%b"), "value": float(total)})
    return data


def _add_heights(data):
    max_val = max((d['value'] for d in data), default=1) or 1
    for item in data:
        item['height'] = max((item['value'] / max_val) * 100, 2)
    return data


def _get_top_foods(days=None):
    """Return top 10 most ordered food items by quantity for the given period."""
    qs = OrderItem.objects.filter(order__status='paid')
    if days:
        now = timezone.now()
        start_date = now - timedelta(days=days)
        qs = qs.filter(order__created_at__gte=start_date)
        
    top_items = qs.values(
        'food_item__id',
        'food_item__name',
        'food_item__category'
    ).annotate(
        total_qty=Sum('quantity'),
        total_rev=Sum(F('quantity') * F('price'))
    ).order_by('-total_qty')[:10]
    
    result = []
    max_qty = top_items[0]['total_qty'] if top_items else 1
    for item in top_items:
        image_obj = FoodImage.objects.filter(food_id=item['food_item__id']).first()
        image_url = image_obj.image.url if image_obj and image_obj.image else None

        result.append({
            'id': str(item['food_item__id']),
            'name': item['food_item__name'],
            'category': item['food_item__category'],
            'qty': item['total_qty'],
            'rev': float(item['total_rev'] or 0),
            'percent': (item['total_qty'] / max_qty) * 100 if max_qty > 0 else 0,
            'image_url': image_url,
        })
    return result


def dashboard_callback(request, context):
    """Professional Dashboard Callback for Unfold."""
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    # ── Stats ──────────────────────────────────────────────
    paid_orders = Order.objects.filter(status='paid')
    total_revenue = paid_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders  = Order.objects.count()
    active_users  = User.objects.filter(is_active=True).count()
    pending_count = Order.objects.filter(status='pending').count()

    # ── Chart data for all three periods ──────────────────
    chart_7d  = _add_heights(_get_revenue_by_period(paid_orders, 7))
    chart_1m  = _add_heights(_get_revenue_by_period(paid_orders, 30))
    chart_1y  = _add_heights(_get_revenue_by_period(paid_orders, 365))

    # ── Upcoming orders ────────────────────────────────────
    upcoming_orders = (
        Order.objects.filter(status__in=['preparing', 'paid', ])
        .order_by('-created_at')[:5]
    )

    # ── Recent invoices WITH Stripe link ──────────────────
    recent_payments = (
        Payments.objects
        .filter(status='paid', order__isnull=False)
        .select_related('order', 'user')
        .order_by('-created_at')[:5]
    )

    # ── Recent user activity ───────────────────────────────
    recent_users = User.objects.order_by('-created_at')[:3]
    recent_activity = [
        {
            "id": str(u.id),
            "name": f"{u.first_name or ''} {u.last_name or ''}".strip() or u.email,
            "action": "New signup",
            "status": "ACTIVE" if u.is_active else "INACTIVE",
            "color": "vd-avatar-green" if u.is_active else "vd-avatar-gray",
            "image_url": u.image.url if u.image else None,
        }
        for u in recent_users
    ]

    # ── Leaderboard data ──────────────────────────────────
    leaderboard_7d = _get_top_foods(7)
    leaderboard_1m = _get_top_foods(30)
    leaderboard_1y = _get_top_foods(365)

    context.update({
        "custom_stats": [
            {"title": "Total Orders",   "value": total_orders,        "change": "+12% this month",   "icon": "shopping_cart", "color": "text-yellow-500"},
            {"title": "Total Revenue",  "value": f"${total_revenue:,.0f}", "change": "+8% vs last month", "icon": "payments",      "color": "text-green-500"},
            {"title": "Active Users",   "value": active_users,        "change": "Live count",         "icon": "group",         "color": "text-purple-500"},
            {"title": "Pending Orders", "value": pending_count,       "change": "Needs attention",    "icon": "pending",       "color": "text-orange-500"},
        ],
        # Pass all chart data as JSON for JavaScript to pick up
        "chart_7d_json":  json.dumps(chart_7d),
        "chart_1m_json":  json.dumps(chart_1m),
        "chart_1y_json":  json.dumps(chart_1y),
        "revenue_chart":  chart_1y,   # default view
        "leaderboard_7d_json": json.dumps(leaderboard_7d),
        "leaderboard_1m_json": json.dumps(leaderboard_1m),
        "leaderboard_1y_json": json.dumps(leaderboard_1y),
        "leaderboard_1y": leaderboard_1y, # default view
        "upcoming_orders":  upcoming_orders,
        "recent_activity":  recent_activity,
        "recent_payments":  recent_payments,
    })
    return context
