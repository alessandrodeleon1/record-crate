# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Orders(models.Model):
    order_id = models.AutoField(primary_key=True, blank=False)
    shipping_address = models.CharField(max_length=50)
    shipping_status = models.CharField(max_length=50)
    placed_by_user_id = models.ForeignKey(
        "AuthUser",
        related_name="placed_order",
        db_column="placed_by_user_id",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    received_by_user_id = models.ForeignKey(
        "AuthUser",
        related_name="received_order",
        db_column="received_by_user_id",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        managed = True
        db_table = "Orders"


class Order_Item(models.Model):
    order_id = models.ForeignKey(
        "Orders",
        db_column="order_id",
        on_delete=models.CASCADE,  # delete order item if order no longer exists
        blank=False,
    )
    item_id = models.ForeignKey(
        "Item",
        db_column="item_id",
        on_delete=models.CASCADE,  # no longer exists in database, can't be sold
        blank=False,
    )

    class Meta:
        managed = True
        db_table = "Order_Item"


class Owns(models.Model):
    user_id = models.ForeignKey(
        "AuthUser",
        db_column="user.id",
        on_delete=models.CASCADE,  # no users exists to own
        blank=True,
        null=True,
    )
    item_id = models.ForeignKey(
        "Item", db_column="item_id", on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        managed = True
        db_table = "Owns"


class Release(models.Model):
    release_id = models.AutoField(primary_key=True, blank=False)
    title = models.CharField(max_length=50, blank=False)
    genre = models.CharField(
        max_length=50, blank=True, null=True
    )  # genre may be unkown - niche release
    year = models.PositiveIntegerField(blank=True, null=True)  # year may be unkown
    media_format = models.CharField(
        max_length=20, blank=True, null=True
    )  # format may not be certain
    artist = models.CharField(
        max_length=50, blank=True, null=True
    )  # artist may be unknown
    label = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "Release"


class Item(models.Model):
    CONDITION_CHOICES = [
        ("mint", "Mint"),
        ("near_mint", "Near mint"),
        ("very_good", "Very good"),
        ("good", "Good"),
        ("fair", "Fair"),
        ("poor", "Poor"),
    ]


    item_id = models.AutoField(primary_key=True, blank=False)
    physical_format = models.CharField(max_length=20, blank=False)
    for_sale = models.BooleanField(default=False, blank=False)
    price = models.DecimalField(default=0.00, max_digits=5, decimal_places=2, blank=True, null=True)
    condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES, blank=True, null=True
    )
    release_id = models.ForeignKey(
        "Release",
        db_column="release_id",
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )

    class Meta:
        managed = True
        db_table = "Item"

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = "auth_group"


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey("AuthPermission", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_group_permissions"
        unique_together = (("group", "permission"),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    content_type = models.ForeignKey("DjangoContentType", models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "auth_permission"
        unique_together = (("content_type", "codename"),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "auth_user"


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_groups"
        unique_together = (("user", "group"),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_user_permissions"
        unique_together = (("user", "permission"),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey(
        "DjangoContentType", models.DO_NOTHING, blank=True, null=True
    )
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "django_admin_log"


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "django_content_type"
        unique_together = (("app_label", "model"),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_migrations"


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_session"
