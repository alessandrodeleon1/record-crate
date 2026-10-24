from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.db.models import Count
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from recordcrate.forms import CustomUserCreationForm

from recordcrate.models import Release, Item, Owns, Order_Item, Orders, AuthUser
from recordcrate.forms import CustomUserCreationForm, SellItemForm

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
    for_sale_items = items.filter(for_sale=True)

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

    owned_ids = set()
    if request.user.is_authenticated:
        owned_ids = set(
            Owns.objects.filter(user_id=request.user.pk).values_list("item_id", flat=True)
        )

    return render(
        request,
        "listings.html",
        {
            "items": items,
            "for_sale_items": for_sale_items,
            "genres": genres,
            "query": query,
            "selected_genre": genre,
            "owned_ids": owned_ids,
        },
    )


def item_detail(request, item_id):
    item = get_object_or_404(Item.objects.select_related("release_id"), pk=item_id)
    owners = Owns.objects.filter(item_id=item)
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


@login_required(login_url="recordcrate:login")
def user_collection(request, user_id):
    user = get_object_or_404(AuthUser, pk=user_id)
    owned = Owns.objects.filter(user_id=user).select_related("item_id__release_id")
    return render(request, "collection.html", {"profile_user": user, "owned": owned})


@login_required(login_url="recordcrate:login")
def order_list(request, user_id):
    user = get_object_or_404(AuthUser, pk=user_id)
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


@login_required(login_url="recordcrate:login")
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

# user folder
@login_required(login_url="recordcrate:login")
def profile(request, user_id):
    profile_user = get_object_or_404(AuthUser, pk=user_id)
    return render(request, "user/profile.html", {"current_user":profile_user})

def create_release(request):
    return redirect(request, "create_release.html")

def my_collection(request, user_id):
  profile_user = get_object_or_404(AuthUser, pk=user_id)

  collection_items = (
      Owns.objects.filter(user_id=profile_user)
      .select_related(
          "item_id", "item_id__release_id"
      ) 
  )

  context = {
      "profile_user": profile_user,
      "collection_items": collection_items,
  }

  return render(request, "user/collection.html", context)


@login_required(login_url="recordcrate:login")
def sell_item(request, item_id):
    # Only the owner of this copy can list it
    ownership = get_object_or_404(Owns, item_id=item_id, user_id=request.user.pk)
    item = ownership.item_id

    if request.method == "POST":
        form = SellItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.for_sale = True
            item.save()
            return redirect("recordcrate:my_listings", user_id=request.user.pk)
    else:
        form = SellItemForm(instance=item)

    return render(request, "user/sell_item.html", {"form": form, "item": item})

def my_listings(request, user_id):
  profile_user = get_object_or_404(AuthUser, pk=user_id)

  active_listings = (
      Owns.objects.filter(user_id=profile_user, item_id__for_sale=True)
      .select_related(
          "item_id", "item_id__release_id"
      )  # Optimizes database queries
  )

  context = {
      "profile_user": profile_user,
      "active_listings": active_listings,
  }

  return render(request, "user/active_listings.html", context)


@login_required(login_url="recordcrate:login")
@require_POST
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, pk=item_id, for_sale=True)

    if Owns.objects.filter(item_id=item, user_id=request.user.pk).exists():
        messages.error(request, "You can't buy your own item.")
        return redirect("recordcrate:listings")

    order = Orders.objects.filter(
        placed_by_user_id_id=request.user.pk, shipping_status="cart"
    ).first()
    if order is None:
        order = Orders.objects.create(
            placed_by_user_id_id=request.user.pk,
            shipping_address="",
            shipping_status="cart",
        )

    Order_Item.objects.get_or_create(
        order_id=order, item_id=item, defaults={"price": item.price}
    )

    messages.success(request, "Added to cart.")
    return redirect("recordcrate:listings")


@login_required(login_url="recordcrate:login")
@require_POST
def unlist_item(request, item_id):
    get_object_or_404(Owns, item_id=item_id, user_id=request.user.pk)
    Item.objects.filter(pk=item_id).update(for_sale=False)
    messages.success(request, "Item removed from sale.")
    return redirect("recordcrate:my_listings", user_id=request.user.pk)

# User Authentication ###############3
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("recordcrate:login")
    else:
        form = CustomUserCreationForm()
    return render(request, "authenticate/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST) # just need username and pass
        if form.is_valid():
            login(request, form.get_user())
            return redirect("recordcrate:homepage")
    else:
        form = AuthenticationForm()
    return render(request, 'authenticate/login.html', {"form": form})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("recordcrate:homepage")
########################
