import datetime
from django.db.models import F, Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from accounts.mixins import RoleRequiredMixin, MANAGEMENT_ROLES
from .forms import ItemForm, MovementForm
from .models import Item, StockMovement

INVENTORY_ROLES = MANAGEMENT_ROLES + ["STAFF", "LIBRARIAN"]


class ItemListView(RoleRequiredMixin, ListView):
    model = Item
    template_name = "inventory/item_list.html"
    context_object_name = "items"
    paginate_by = 25
    allowed_roles = INVENTORY_ROLES

    def get_queryset(self):
        qs = super().get_queryset()
        q, cat = self.request.GET.get("q"), self.request.GET.get("category")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(location__icontains=q))
        if cat:
            qs = qs.filter(category=cat)
        if self.request.GET.get("low"):
            qs = qs.filter(quantity__lte=F("min_quantity"))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Item.Category.choices
        ctx["low_count"] = Item.objects.filter(quantity__lte=F("min_quantity")).count()
        return ctx


class ItemCreateView(RoleRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = "partials/form.html"
    success_url = reverse_lazy("inventory:list")
    extra_context = {"title": "Add Inventory Item"}
    allowed_roles = INVENTORY_ROLES


class ItemUpdateView(RoleRequiredMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = "partials/form.html"
    success_url = reverse_lazy("inventory:list")
    extra_context = {"title": "Edit Item"}
    allowed_roles = INVENTORY_ROLES


class ItemDeleteView(RoleRequiredMixin, DeleteView):
    model = Item
    template_name = "partials/confirm_delete.html"
    success_url = reverse_lazy("inventory:list")
    allowed_roles = MANAGEMENT_ROLES


class MovementListView(RoleRequiredMixin, ListView):
    model = StockMovement
    template_name = "inventory/movement_list.html"
    context_object_name = "movements"
    paginate_by = 25
    allowed_roles = INVENTORY_ROLES

    def get_queryset(self):
        return StockMovement.objects.select_related("item", "by")


class MovementCreateView(RoleRequiredMixin, CreateView):
    model = StockMovement
    form_class = MovementForm
    template_name = "partials/form.html"
    success_url = reverse_lazy("inventory:movements")
    extra_context = {"title": "Record Stock In / Out"}
    allowed_roles = INVENTORY_ROLES

    def get_initial(self):
        initial = {"date": datetime.date.today()}
        if self.request.GET.get("item"):
            initial["item"] = self.request.GET["item"]
        return initial

    def form_valid(self, form):
        form.instance.by = self.request.user
        return super().form_valid(form)
