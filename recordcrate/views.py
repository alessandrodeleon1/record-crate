from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q, Count
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from recordcrate.forms import CustomUserCreationForm, ReleaseCreationForm
from django.http import HttpResponseRedirect

from recordcrate.models import Release, Item, Owns, Order_Item, Orders, AuthUser


def index(request):
    recent_releases = Release.objects.order_by("-release_id")[:10]
    return render(
        request,
        "home.html",
        {
            "recent_releases": recent_releases,
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

    return render(
        request,
        "listings.html",
        {
            "items": items,
            "for_sale_items": for_sale_items,
            "genres": genres,
            "query": query,
            "selected_genre": genre,
        },
    )


def item_detail(request, item_id):
    item = get_object_or_404(Item.objects.select_related("release_id"), pk=item_id)
    owners = Owns.objects.filter(item_id=item)#.select_related("user_id")
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

@login_required(login_url="recordcrate:login")
def create_release(request):
    if request.method == "POST":
        form = ReleaseCreationForm(request.POST)
        if form.is_valid():
            new_release = form.save()
            # release = Release.objects.create(
            #     title = request.POST['title'],
            #     genre = request.POST['genre'],
            #     year = request.POST['year'],
            #     media_format = request.POST['media format'],
            #     artist = request.POST['artist'],
            #     label = request.POST['label'],
            # )
            return redirect("recordcrate:release_detail", release_id=new_release.release_id)
    else:
        form = ReleaseCreationForm()
    return render(request, 'create_release.html', {"form": form})

#
#         return HttpResponseRedirect
#
#     return redirect(request, "create_release.html")

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


# User Authentication ###############3
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            django_user = form.save()

            User.objects.create(
                user_id=django_user,
                city = form.cleaned_data.get('city'),
                address =form.cleaned_data.get('address'),
            )

            login(request, django_user)
            return redirect("recordcrate:user_profile", user_id=django_user.profile.user_id)
    else:
        form = CustomUserCreationForm()
    return render(request, 'authenticate/register.html', {"form": form})

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
