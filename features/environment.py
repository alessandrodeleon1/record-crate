from django.test import Client
from recordcrate.models import AuthUser, Item, Order_Item, Orders, Owns, Release


def clear_database():
    Order_Item.objects.all().delete()
    Orders.objects.all().delete()
    Owns.objects.all().delete()
    Item.objects.all().delete()
    Release.objects.all().delete()
    AuthUser.objects.all().delete()


def before_scenario(context, scenario):
    clear_database()
    context.client = Client()
    context.response = None
    context.users = {}
    context.items = {}
    context.current_user = None


def before_step(context, step):
    if not hasattr(context, "users"):
        context.users = {}
    if not hasattr(context, "items"):
        context.items = {}
    if not hasattr(context, "current_user"):
        context.current_user = None
    if not hasattr(context, "response"):
        context.response = None
    if not hasattr(context, "client"):
        context.client = Client()
