from django.urls import path
from customer import views

app_name = "customer"

urlpatterns = [
    path("create", views.CreateCustomerView.as_view(), name="create"),
    path("update/<int:pk>", views.UpdateCustomerView.as_view(), name="update"),
]
