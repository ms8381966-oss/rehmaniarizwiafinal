from django.urls import path
from . import views

app_name = "library"

urlpatterns = [
    # 📚 Books Inventory Route Controls
    path("", views.BookListView.as_view(), name="books"),
    path("add/", views.BookCreateView.as_view(), name="book_add"),
    path("<int:pk>/edit/", views.BookUpdateView.as_view(), name="book_edit"),
    path("<int:pk>/delete/", views.BookDeleteView.as_view(), name="book_delete"),
    
    # 💰 Book Sales Tab Route Controls
    path("sales/", views.SaleListView.as_view(), name="sales_list"),
    path("sales/new/", views.SaleCreateView.as_view(), name="sale_create"),
]
