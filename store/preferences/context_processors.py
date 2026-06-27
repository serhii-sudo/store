from orders.models import Order


def navbar_history(request):
    if request.user.is_authenticated:
        return {"navbar_orders": Order.objects.filter(initiator=request.user).order_by("-id")[:5]}
    return {}
