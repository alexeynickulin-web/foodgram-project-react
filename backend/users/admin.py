from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'role',
        'first_name',
        'last_name',
    )

    search_fields = ('username',)
    list_filter = ('email', 'username')


admin.site.register(Follow)
