from django.contrib import admin
from core.models import UserProfile, Publication, FollowSupplier, AddProducts, MultipleImages, SocialLinks,  \
    AddServices, Category

admin.site.register(UserProfile)
admin.site.register(Publication)
admin.site.register(FollowSupplier)
admin.site.register(AddProducts)


class MultipleImagesAdmin(admin.ModelAdmin):
    list_display = ["product"]


admin.site.register(MultipleImages, MultipleImagesAdmin)
admin.site.register(SocialLinks)
admin.site.register(AddServices)
admin.site.register(Category)