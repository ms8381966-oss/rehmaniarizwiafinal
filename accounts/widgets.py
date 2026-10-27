from django import forms


class BootstrapModelForm(forms.ModelForm):
    """ModelForm that applies Bootstrap 5 classes and HTML5 date/time inputs automatically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            w = field.widget
            if isinstance(w, forms.CheckboxInput):
                w.attrs["class"] = "form-check-input"
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                w.attrs["class"] = "form-select"
            elif isinstance(w, forms.ClearableFileInput):
                w.attrs["class"] = "form-control"
            else:
                w.attrs["class"] = "form-control"
            if isinstance(field, forms.DateField) and not isinstance(field, forms.DateTimeField):
                w.input_type = "date"
                w.format = "%Y-%m-%d"
            if isinstance(field, forms.TimeField):
                w.input_type = "time"
                w.format = "%H:%M"
