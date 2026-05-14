from django.db.models import Sum, Count, F, Q
from django.core.paginator import Paginator
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

def get_activity_data(limit=None, search_query=None, activity_type=None):
    from django.contrib.admin.models import LogEntry
    activity_items = []

    # 1. Recent Signups
    if not activity_type or activity_type == 'signup':
        users_qs = User.objects.order_by('-created_at')
        if search_query:
            users_qs = users_qs.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) | 
                Q(email__icontains=search_query)
            )
        for u in users_qs[:100]:
            activity_items.append({
                "type": "signup",
                "id": str(u.id),
                "date": u.created_at,
                "name": f"{u.first_name or ''} {u.last_name or ''}".strip() or u.email,
                "action": "Joined the platform",
                "status": "Signup",
                "badge_class": "vd-badge-green",
                "color": "vd-avatar-green",
                "image_url": u.image.url if u.image else None,
                "link": f"/admin/authentication/user/{u.id}/change/"
            })

    # 2. Recent Orders
    if not activity_type or activity_type == 'order':
        orders_qs = Order.objects.order_by('-created_at')
        if search_query:
            orders_qs = orders_qs.filter(
                Q(order_id__icontains=search_query) | 
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        for o in orders_qs[:100]:
            activity_items.append({
                "type": "order",
                "id": str(o.id),
                "date": o.created_at,
                "name": f"{o.first_name} {o.last_name}".strip() or o.user.email,
                "action": f"Placed order {o.order_id}",
                "status": o.status.upper(),
                "badge_class": "vd-badge-yellow" if o.status == 'pending' else "vd-badge-green",
                "color": "vd-avatar-blue",
                "image_url": o.user.image.url if o.user and o.user.image else None,
                "link": f"/admin/order/order/{o.id}/change/"
            })

    # 3. Admin Changes (LogEntry)
    if not activity_type or activity_type == 'admin':
        logs_qs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')
        if search_query:
            logs_qs = logs_qs.filter(
                Q(user__first_name__icontains=search_query) | 
                Q(user__last_name__icontains=search_query) | 
                Q(user__email__icontains=search_query) |
                Q(object_repr__icontains=search_query) |
                Q(change_message__icontains=search_query)
            )
        for log in logs_qs[:100]:
            if log.is_change():
                action_desc = f"Updated {log.content_type.name}: {log.object_repr}"
            elif log.is_addition():
                action_desc = f"Added {log.content_type.name}: {log.object_repr}"
            else:
                action_desc = f"Deleted {log.content_type.name}: {log.object_repr}"

            activity_items.append({
                "type": "admin",
                "id": str(log.user.id),
                "date": log.action_time,
                "name": f"{log.user.first_name or ''} {log.user.last_name or ''}".strip() or log.user.email,
                "action": action_desc,
                "status": "Admin",
                "badge_class": "vd-badge-red",
                "color": "vd-avatar-gray",
                "image_url": log.user.image.url if hasattr(log.user, 'image') and log.user.image else None,
                "link": f"/admin/authentication/user/{log.user.id}/change/"
            })

    activity_items.sort(key=lambda x: x['date'], reverse=True)
    return activity_items[:limit] if limit else activity_items


def dashboard_callback(request, context):
    """Professional Dashboard Callback for Unfold."""
    now = timezone.now()

    # ── Time Windows & Helpers ────────────────────────────
    def get_percent_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return ((current - previous) / previous) * 100

    def format_change(change, period_text):
        prefix = "+" if change >= 0 else ""
        return f"{prefix}{change:.1f}% vs {period_text}"

    # 1. Total Orders (Last 30 Days vs Prev 30)
    last_30_days_start = now - timedelta(days=30)
    prev_30_days_start = now - timedelta(days=60)
    orders_last_30 = Order.objects.filter(created_at__gte=last_30_days_start).count()
    orders_prev_30 = Order.objects.filter(created_at__gte=prev_30_days_start, created_at__lt=last_30_days_start).count()
    orders_change = get_percent_change(orders_last_30, orders_prev_30)

    # 2. Total Revenue (This Month vs Last Month)
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    rev_this_month = Order.objects.filter(status='paid', created_at__gte=this_month_start).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    rev_last_month = Order.objects.filter(status='paid', created_at__gte=last_month_start, created_at__lt=this_month_start).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    rev_change = get_percent_change(rev_this_month, rev_last_month)

    # 3. Active Users (Last 24H vs Prev 24H)
    users_24h = User.objects.filter(last_login__gte=now - timedelta(hours=24)).count()
    users_prev_24h = User.objects.filter(last_login__gte=now - timedelta(hours=48), last_login__lt=now - timedelta(hours=24)).count()
    users_change = get_percent_change(users_24h, users_prev_24h)

    # 4. New Orders (Paid in last 24H vs Prev 24H)
    new_orders_24h = Order.objects.filter(status='paid', created_at__gte=now - timedelta(hours=24)).count()
    new_orders_prev_24h = Order.objects.filter(status='paid', created_at__gte=now - timedelta(hours=48), created_at__lt=now - timedelta(hours=24)).count()
    new_orders_change = get_percent_change(new_orders_24h, new_orders_prev_24h)

    # ── Chart data ────────────────────────────────────────
    paid_orders = Order.objects.filter(status='paid')
    chart_7d  = _add_heights(_get_revenue_by_period(paid_orders, 7))
    chart_1m  = _add_heights(_get_revenue_by_period(paid_orders, 30))
    chart_1y  = _add_heights(_get_revenue_by_period(paid_orders, 365))

    # ── Lists ─────────────────────────────────────────────
    upcoming_orders = Order.objects.filter(status__in=['preparing', 'paid']).order_by('-created_at')[:5]
    recent_payments = Payments.objects.filter(status='paid', order__isnull=False).select_related('order', 'user').order_by('-created_at')[:5]
    recent_activity = get_activity_data(limit=8)

    # ── Leaderboard ───────────────────────────────────────
    leaderboard_7d = _get_top_foods(7)
    leaderboard_1m = _get_top_foods(30)
    leaderboard_1y = _get_top_foods(365)

    context.update({
        "custom_stats": [
            {
                "title": "Total Orders",
                "value": orders_last_30,
                "change": format_change(orders_change, "last month"),
                "color": "vd-trend-up" if orders_change >= 0 else "vd-trend-down"
            },
            {
                "title": "Total Revenue",
                "value": f"${rev_this_month:,.0f}",
                "change": format_change(rev_change, "last month"),
                "color": "vd-trend-up" if rev_change >= 0 else "vd-trend-down"
            },
            {
                "title": "Active Users",
                "value": users_24h,
                "change": format_change(users_change, "last 24H"),
                "color": "vd-trend-up" if users_change >= 0 else "vd-trend-down"
            },
            {
                "title": "New Orders",
                "value": new_orders_24h,
                "change": format_change(new_orders_change, "last 24H"),
                "color": "vd-trend-up" if new_orders_change >= 0 else "vd-trend-down"
            },
        ],
        "chart_7d_json": json.dumps(chart_7d),
        "chart_1m_json": json.dumps(chart_1m),
        "chart_1y_json": json.dumps(chart_1y),
        "revenue_chart": chart_1y,
        "leaderboard_7d_json": json.dumps(leaderboard_7d),
        "leaderboard_1m_json": json.dumps(leaderboard_1m),
        "leaderboard_1y_json": json.dumps(leaderboard_1y),
        "leaderboard_1y": leaderboard_1y,
        "upcoming_orders": upcoming_orders,
        "recent_activity": recent_activity,
        "recent_payments": recent_payments,
    })
    return context


from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_activity_log(request):
    """View to show the full activity history with filtering, search, and pagination."""
    from django.contrib import admin
    search_query = request.GET.get('q', '')
    activity_type = request.GET.get('type', '')
    
    all_data = get_activity_data(search_query=search_query, activity_type=activity_type)
    
    paginator = Paginator(all_data, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = admin.site.each_context(request)
    context.update({
        "page_obj": page_obj,
        "search_query": search_query,
        "activity_type": activity_type,
        "title": "Activity History"
    })
    
    return render(request, "admin/activity_log.html", context)
