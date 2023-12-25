from django import forms


class LoginForm(forms.Form):
    login = forms.CharField(label="Логин", max_length=100, required=True)
    pswd = forms.CharField(
        label="Пароль",
        max_length=100,
        required=True,
        widget=forms.PasswordInput(),
    )
    next = forms.CharField(label="next", widget=forms.HiddenInput, required=False)
