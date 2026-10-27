from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title", "author", "category", "language", 
            "isbn", "copies", "shelf", "sale_status", 
            "publication_type", "price"
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "author": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Tafseer, Hadith, Fiqh"}),
            "language": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Arabic, Urdu"}),
            "isbn": forms.TextInput(attrs={"class": "form-control"}),
            "copies": forms.NumberInput(attrs={"class": "form-control"}),
            "shelf": forms.TextInput(attrs={"class": "form-control"}),
            "sale_status": forms.Select(attrs={"class": "form-select"}),
            "publication_type": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
        }


class BookChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, book):
        # FIXED: Core python condition used instead of template pipe format
        author_name = book.author if book.author else 'Unknown'
        return f"{book.title} — {author_name} ({book.copies} copies remaining)"


class SaleForm(forms.Form):
    book = BookChoiceField(
        queryset=Book.objects.none(), 
        widget=forms.Select(attrs={"class": "form-select"})
    )
    quantity = forms.IntegerField(
        min_value=1, 
        initial=1, 
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    sold_to = forms.CharField(
        max_length=255,
        required=False,
        label="Sold To (Optional)",
        widget=forms.TextInput(attrs={
            "placeholder": "Customer Name or Institution",
            "class": "form-control"
        })
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)
        
        # Inhi library books ko display karega jo active sale par hain aur stock mein hain
        self.fields["book"].queryset = Book.objects.filter(
            sale_status='FOR_SALE', copies__gt=0
        )
