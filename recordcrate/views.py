from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.db.models import Count
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout

from recordcrate.models import Release, Item, Owns, Order_Item, Orders, User


# Create your views here.
def index(request):
    recent_items = Item.objects.select_related("release_id").order_by("-item_id")[:10]
    return render(
        request,
        "home.html",
        {
            "recent_items": recent_items,
        },
    )


def listings(request):
    query = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "").strip()

    items = Item.objects.select_related("release_id").order_by("-item_id")
    if query:
        items = items.filter(
            Q(release_id__title__icontains=query)
            | Q(release_id__artist__icontains=query)
            | Q(release_id__label__icontains=query)
        )
    if genre:
        items = items.filter(release_id__genre__iexact=genre)

    genres = (
        Release.objects.exclude(genre__isnull=True)
        .exclude(genre="")
        .values_list("genre", flat=True)
        .distinct()
        .order_by("genre")
    )

    return render(
        request,
        "listings.html",
        {
            "items": items,
            "genres": genres,
            "query": query,
            "selected_genre": genre,
        },
    )


def item_detail(request, item_id):
    item = get_object_or_404(Item.objects.select_related("release_id"), pk=item_id)
    owners = Owns.objects.filter(item_id=item).select_related("user_id")
    return render(request, "item_detail.html", {"item": item, "owners": owners})


def release_detail(request, release_id):
    release = get_object_or_404(Release, pk=release_id)
    copies = Item.objects.filter(release_id=release).order_by("physical_format")
    return render(
        request, "release_detail.html", {"release": release, "copies": copies}
    )


def artist_releases(request, artist):
    releases = Release.objects.filter(artist__iexact=artist).order_by("year", "title")
    return render(request, "artist.html", {"artist": artist, "releases": releases})


@login_required
def user_collection(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    owned = Owns.objects.filter(user_id=user).select_related("item_id__release_id")
    return render(request, "collection.html", {"profile_user": user, "owned": owned})


@login_required
def order_list(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    placed = Orders.objects.filter(placed_by_user_id=user).prefetch_related(
        "order_item_set__item_id__release_id"
    )
    received = Orders.objects.filter(received_by_user_id=user).prefetch_related(
        "order_item_set__item_id__release_id"
    )
    return render(
        request,
        "orders.html",
        {
            "profile_user": user,
            "placed_orders": placed,
            "received_orders": received,
        },
    )


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Orders, pk=order_id)
    line_items = Order_Item.objects.filter(order_id=order).select_related(
        "item_id__release_id"
    )
    total = sum(li.price for li in line_items)
    return render(
        request,
        "order_detail.html",
        {
            "order": order,
            "line_items": line_items,
            "total": total,
        },
    )


def random_release(request):
    release = Release.objects.order_by("?").first()
    if release is None:
        return redirect("recordcrate:listings")
    return redirect("recordcrate:release_detail", release_id=release.release_id)

@login_required(login_url="recordcrate:login")
def profile(request):
    return render(request, "user/profile.html")


# User Authentication
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect("recordcrate:user_profile")
    else:
        form = UserCreationForm()
    return render(request, 'authenticate/register.html', {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("recordcrate:login")
    else:
        form = AuthenticationForm()
    return render(request, 'authenticate/login.html', {"form": form})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("recordcrate:homepage")
