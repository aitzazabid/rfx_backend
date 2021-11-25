from django.contrib import admin
from core.models import UserProfile, Publication, FollowSupplier, AddProducts, MultipleImages

admin.site.register(UserProfile)
admin.site.register(Publication)
admin.site.register(FollowSupplier)
admin.site.register(AddProducts)


class MultipleImagesAdmin(admin.ModelAdmin):
    list_display = ["product"]


admin.site.register(MultipleImages, MultipleImagesAdmin)
