from django.urls import path
from .views import LinkedInProfileView

urlpatterns = [
    path('linkedin/profile/', LinkedInProfileView.as_view(), name='linkedin_profile'),
]