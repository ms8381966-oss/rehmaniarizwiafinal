from datetime import datetime, time, timedelta
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q

from accounts.decorators import role_required
from accounts.mixins import RoleRequiredMixin, MANAGEMENT_ROLES, STAFF_ROLES
from .forms import BookForm, SaleForm
from .models import Book, Sale

LIBRARY_ROLES = MANAGEMENT_ROLES + ["LIBRARIAN"]


class BookListView(RoleRequiredMixin, ListView):
    model = Book
    template_name = "library/book_list.html"
    context_object_name = "books"
    paginate_by = 20
    allowed_roles = STAFF_ROLES

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        sale_status = self.request.GET.get("sale_status")
        publication_type = self.request.GET.get("publication_type")
        stock_status = self.request.GET.get('stock_status', '') # Naya parameter fetch kiya

        # Correct Indentation for Stock Logic Checks
        if stock_status == 'out_of_stock':
            qs = qs.filter(copies=0)
        elif stock_status == 'low_stock':
            qs = qs.filter(copies__gt=0, copies__lte=5)

        # Existing Search Text Filter
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | 
                Q(author__icontains=q) | 
                Q(category__icontains=q) | 
                Q(isbn__icontains=q)
            )
            
        # Existing Dropdowns Filter
        if sale_status:
            qs = qs.filter(sale_status=sale_status)
            
        if publication_type:
            # Agar HTML se 'EXTERNAL' aata hai jabki backend model par name 'NORMAL' hai
            if publication_type == 'EXTERNAL':
                qs = qs.filter(publication_type='NORMAL')
            else:
                qs = qs.filter(publication_type=publication_type)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Dropdown input persistence data state carry mapping
        ctx["q"] = self.request.GET.get("q", "")
        ctx["sale_status"] = self.request.GET.get("sale_status", "")
        ctx["publication_type"] = self.request.GET.get("publication_type", "")
        ctx["stock_status"] = self.request.GET.get("stock_status", "") # <-- Custom Context Added
        return ctx



class BookCreateView(RoleRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "partials/form.html"
    success_url = reverse_lazy("library:books")
    extra_context = {"title": "Add Book"}
    allowed_roles = LIBRARY_ROLES


class BookUpdateView(RoleRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = "partials/form.html"
    success_url = reverse_lazy("library:books")
    extra_context = {"title": "Edit Book"}
    allowed_roles = LIBRARY_ROLES


class BookDeleteView(RoleRequiredMixin, DeleteView):
    model = Book
    template_name = "partials/confirm_delete.html"
    success_url = reverse_lazy("library:books")
    allowed_roles = LIBRARY_ROLES


# ==========================================
# 💰 NEW INTREGATED SALES MANAGEMENT VIEWS
# ==========================================

class SaleListView(RoleRequiredMixin, ListView):
    model = Sale
    template_name = "library/sale_list.html"
    context_object_name = "sales"
    allowed_roles = STAFF_ROLES

    def get_queryset(self):
        queryset = Sale.objects.select_related("book").order_by('-sold_at')
        book_id = self.request.GET.get('book_id', '').strip()
        if book_id and book_id != 'all':
            queryset = queryset.filter(book_id=book_id)

        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()
        if date_from:
            queryset = queryset.filter(sold_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(sold_at__date__lte=date_to)

        sort_by = self.request.GET.get('sort_by', '').strip()
        if sort_by == 'most_revenue':
            queryset = queryset.order_by('-total_amount')
        elif sort_by == 'least_revenue':
            queryset = queryset.order_by('total_amount')
        elif sort_by == 'most_qty':
            queryset = queryset.order_by('-quantity')
        elif sort_by == 'least_qty':
            queryset = queryset.order_by('quantity')
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['all_books'] = Book.objects.filter(sale_status='FOR_SALE').order_by('title')
        ctx['selected_book'] = self.request.GET.get('book_id', 'all')
        ctx['date_from'] = self.request.GET.get('date_from', '')
        ctx['date_to'] = self.request.GET.get('date_to', '')
        ctx['selected_sort'] = self.request.GET.get('sort_by', '')
        return ctx


class SaleCreateView(RoleRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = "library/form.html"
    success_url = reverse_lazy("library:sales_list")
    allowed_roles = LIBRARY_ROLES

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["heading_key"] = "record_sale"
        return ctx

    def form_valid(self, form):
        selected_book = form.cleaned_data["book"]
        qty = form.cleaned_data["quantity"]
        customer = form.cleaned_data.get("sold_to", "").strip()

        if selected_book.copies < qty:
            form.add_error("quantity", f"Insufficient Stock! Only {selected_book.copies} copies remaining.")
            return self.form_invalid(form)

        calculated_total = selected_book.price * qty
        Sale.objects.create(
            book=selected_book,
            quantity=qty,
            unit_price=selected_book.price,
            total_amount=calculated_total,
            sold_to=customer if customer else None
        )
        
        selected_book.copies -= qty
        selected_book.save()
        
        messages.success(self.request, "Sale recorded successfully!")
        return redirect(self.success_url)
