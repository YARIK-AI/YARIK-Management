from django import forms


class LoginForm(forms.Form):
    login = forms.CharField(label="Username", max_length=100, required=True)
    pswd = forms.CharField(
        label="Password",
        max_length=100,
        required=True,
        widget=forms.PasswordInput(),
    )
    next = forms.CharField(label="next", widget=forms.HiddenInput, required=False)
