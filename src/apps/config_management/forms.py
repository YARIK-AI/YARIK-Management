from django import forms

class CustomForm(forms.Form):
    custom = forms.CharField(initial="{}", widget=forms.Textarea(attrs={"cols":80, "rows":6,"style":"resize:none;"}), label="")