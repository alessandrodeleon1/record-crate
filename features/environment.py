from django.test import Client


def before_scenario(context, scenario):
    context.client = Client()
    context.response = None
    context.users = {}
    context.items = {}
    context.current_user = None


def before_step(context, step):
    # Safety net: make sure the state attributes exist before any step runs.
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
