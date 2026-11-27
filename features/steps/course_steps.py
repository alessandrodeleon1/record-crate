from decimal import Decimal

from behave import given, then, use_step_matcher, when
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

from recordcrate.models import Item, Order_Item, Orders, Owns, Release

use_step_matcher("parse")

User = get_user_model()
DEFAULT_PASSWORD = "test-pass-123"


# ---------------------------------------------------------------- helpers

def page_url(name):
    return {
        "home": reverse("recordcrate:homepage"),
        "login": reverse("recordcrate:login"),
        "listings": reverse("recordcrate:listings"),
        "releases": reverse("recordcrate:releases"),
    }[name]


def user_named(context, username):
    if username not in context.users:
        context.users[username] = User.objects.create_user(
            username=username, password=DEFAULT_PASSWORD
        )
    return context.users[username]


def make_copy(context, title, fmt, username, for_sale, price):
    release = Release.objects.get(title=title)
    item = Item.objects.create(
        release_id=release,
        physical_format=fmt,
        for_sale=for_sale,
        price=price,
    )
    Owns.objects.create(user_id=user_named(context, username), item_id=item)
    context.items[title] = item
    return item


# ---------------------------------------------------------------- given

@given("the catalogue is empty")
def step_empty_catalogue(context):
    # Each scenario starts with an empty database, so nothing to do.
    pass


@given('a release "{title}" by "{artist}"')
def step_release(context, title, artist):
    Release.objects.create(title=title, artist=artist, year=2000)


@given('a user named "{username}"')
def step_user(context, username):
    user_named(context, username)


@given('a copy of "{title}" in "{fmt}" format owned by "{username}"')
def step_copy(context, title, fmt, username):
    make_copy(context, title, fmt, username, for_sale=False, price=Decimal("0.00"))


@given('a copy of "{title}" in "{fmt}" format listed for sale at {price} owned by "{username}"')
def step_copy_for_sale(context, title, fmt, price, username):
    make_copy(context, title, fmt, username, for_sale=True, price=Decimal(price))


@given('I am logged in as "{username}"')
def step_logged_in(context, username):
    user = user_named(context, username)
    context.client.force_login(user)
    context.current_user = user


# ---------------------------------------------------------------- when: browsing

@when("I visit the home page")
def step_visit_home(context):
    context.response = context.client.get(page_url("home"))


@when("I visit the listings page")
def step_visit_listings(context):
    context.response = context.client.get(page_url("listings"))


@when('I search the listings for "{query}"')
def step_search_listings(context, query):
    context.response = context.client.get(page_url("listings"), {"q": query})


@when('I search the releases for "{query}"')
def step_search_releases(context, query):
    context.response = context.client.get(page_url("releases"), {"q": query})


@when('I visit the artist page for "{artist}"')
def step_visit_artist(context, artist):
    context.response = context.client.get(
        reverse("recordcrate:artist_releases", args=[artist])
    )


@when('I visit the detail page for "{title}"')
def step_visit_release(context, title):
    release = Release.objects.get(title=title)
    context.response = context.client.get(
        reverse("recordcrate:release_detail", args=[release.release_id])
    )


@when('I visit the item page for "{title}"')
def step_visit_item(context, title):
    item = context.items[title]
    context.response = context.client.get(
        reverse("recordcrate:item_detail", args=[item.item_id])
    )


@when('I visit the collection of "{username}"')
def step_visit_collection(context, username):
    user = user_named(context, username)
    context.response = context.client.get(
        reverse("recordcrate:my_collection", args=[user.pk])
    )


@when("I click the random button")
def step_click_random(context):
    context.response = context.client.get(reverse("recordcrate:random_release"))


# ---------------------------------------------------------------- when: cart and sales

@when('I add "{title}" to my cart')
def step_add_to_cart(context, title):
    item = context.items[title]
    context.response = context.client.post(
        reverse("recordcrate:add_to_cart", args=[item.item_id])
    )


@when('I try to add "{title}" to my cart with a GET request')
def step_add_to_cart_get(context, title):
    item = context.items[title]
    context.response = context.client.get(
        reverse("recordcrate:add_to_cart", args=[item.item_id])
    )


@when('I unlist "{title}"')
def step_unlist(context, title):
    item = context.items[title]
    context.response = context.client.post(
        reverse("recordcrate:unlist_item", args=[item.item_id])
    )


@when('I list "{title}" for sale at {price}')
def step_list_for_sale(context, title, price):
    item = context.items[title]
    # Field names assumed from SellItemForm; adjust if your form differs.
    context.response = context.client.post(
        reverse("recordcrate:sell_item", args=[item.item_id]),
        {"price": price, "condition": "good"},
    )


# ---------------------------------------------------------------- when: releases

@when('I create a release titled "{title}" by "{artist}"')
def step_create_release(context, title, artist):
    context.response = context.client.post(
        reverse("recordcrate:create_release"),
        {"title": title, "artist": artist},
    )


@when('I add a copy of "{title}" in "{fmt}" format')
def step_add_copy(context, title, fmt):
    release = Release.objects.get(title=title)
    context.response = context.client.post(
        reverse("recordcrate:release_detail", args=[release.release_id]),
        {"physical_format": fmt},
    )


# ---------------------------------------------------------------- when: accounts

@when('I register with username "{username}" and password "{password}"')
def step_register(context, username, password):
    context.response = context.client.post(
        reverse("recordcrate:register"),
        {"username": username, "password1": password, "password2": password},
    )


@when('I log in with username "{username}" and password "{password}"')
def step_login(context, username, password):
    context.response = context.client.post(
        reverse("recordcrate:login"),
        {"username": username, "password": password},
    )


@when("I log out")
def step_logout(context):
    context.response = context.client.post(reverse("recordcrate:logout"))


# ---------------------------------------------------------------- then: responses

@then("I should see the status code {code:d}")
def step_status_code(context, code):
    actual = context.response.status_code
    assert actual == code, f"expected status {code}, got {actual}"


@then('I should see "{text}"')
def step_see_text(context, text):
    content = context.response.content.decode()
    assert text in content, f"'{text}' not found in response"


@then('I should not see "{text}"')
def step_not_see_text(context, text):
    content = context.response.content.decode()
    assert text not in content, f"'{text}' unexpectedly found in response"


@then('I should see the message "{text}"')
def step_see_message(context, text):
    messages = [str(m) for m in get_messages(context.response.wsgi_request)]
    assert text in messages, f"message not found; got {messages}"


@then("I should be redirected to the {page} page")
def step_redirected_to_page(context, page):
    response = context.response
    assert response.status_code == 302, f"expected redirect, got {response.status_code}"
    expected = page_url(page)
    assert response.url.startswith(expected), f"redirected to {response.url}, expected {expected}"


@then('I should be redirected to the detail page for "{title}"')
def step_redirected_to_release(context, title):
    release = Release.objects.get(title=title)
    expected = reverse("recordcrate:release_detail", args=[release.release_id])
    assert context.response.status_code == 302, f"expected redirect, got {context.response.status_code}"
    assert context.response.url == expected, f"redirected to {context.response.url}, expected {expected}"


# ---------------------------------------------------------------- then: session and users

@then("I should be logged in")
def step_is_logged_in(context):
    assert "_auth_user_id" in context.client.session, "user is not logged in"


@then("I should not be logged in")
def step_is_not_logged_in(context):
    assert "_auth_user_id" not in context.client.session, "user is still logged in"


@then('a user named "{username}" should exist')
def step_user_exists(context, username):
    assert User.objects.filter(username=username).exists(), f"no user '{username}'"


# ---------------------------------------------------------------- then: database

@then("no cart should exist")
def step_no_cart(context):
    assert not Orders.objects.filter(shipping_status="cart").exists(), "a cart exists"


@then('I should have a cart containing "{title}"')
def step_cart_contains(context, title):
    item = context.items[title]
    order = Orders.objects.filter(
        placed_by_user_id=context.current_user, shipping_status="cart"
    ).first()
    assert order is not None, "no cart found for the logged-in user"
    assert Order_Item.objects.filter(order_id=order, item_id=item).exists(), (
        f"'{title}' is not in the cart"
    )


@then('the copy of "{title}" should be for sale')
def step_copy_for_sale_check(context, title):
    item = context.items[title]
    item.refresh_from_db()
    assert item.for_sale, "copy is not for sale"


@then('the copy of "{title}" should not be for sale')
def step_copy_not_for_sale_check(context, title):
    item = context.items[title]
    item.refresh_from_db()
    assert not item.for_sale, "copy is still for sale"


@then('the copy of "{title}" should be priced at {price}')
def step_copy_price_check(context, title, price):
    item = context.items[title]
    item.refresh_from_db()
    assert item.price == Decimal(price), f"price is {item.price}, expected {price}"


@then('I should own a copy of "{title}" in "{fmt}" format')
def step_owns_copy(context, title, fmt):
    exists = Owns.objects.filter(
        user_id=context.current_user,
        item_id__release_id__title=title,
        item_id__physical_format=fmt,
    ).exists()
    assert exists, f"no '{fmt}' copy of '{title}' owned by the current user"


@then('no copies of "{title}" should exist')
def step_no_copies(context, title):
    assert not Item.objects.filter(release_id__title=title).exists(), "copies exist"
