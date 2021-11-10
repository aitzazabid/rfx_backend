from django.contrib import admin
from core.models import UserProfile, Publication, FollowSupplier
admin.site.register(UserProfile)
admin.site.register(Publication)
admin.site.register(FollowSupplier)