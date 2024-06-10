from django.urls import path
from company import views


app_name = "company"

urlpatterns = [
    path("create-company", views.CreateCompanyView.as_view(), name="create_company"),
    path("update-company/<int:pk>", views.UpdateCompanyView.as_view(), name="update_company"),
]