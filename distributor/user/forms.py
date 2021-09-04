from django import forms

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from dealership.models import District, Dealership


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Xác nhận mật khẩu', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            'username',
            'last_name',
            'first_name',
            'email',
            'password1',
            'password2'
        )
        help_texts = {
            'username': None,
        }
        labels = {
            'username': 'Tên tài khoản',
            'first_name': 'Tên',
            'last_name': 'Họ',
        }

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class UserLoginForm(forms.ModelForm):
    username = forms.CharField(max_length=100, label='Tên đăng nhập')
    password = forms.CharField(max_length=100, label='Mât khẩu', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            'username',
            'password'
        )


class DealershipRegistrationForm(forms.ModelForm):

    owner_phone = forms.CharField(max_length=15, label='Số điện thoại người đăng ký')

    class Meta:
        model = Dealership
        fields = (
            'name',
            'type',
            'city',
            'district',
            'address',
            'owner_phone'
        )
        labels = {
            'name': 'Tên đại lý',
            'type': 'Loại đại lý',
            'city': 'Thành phố / Tỉnh',
            'district': 'Quận / Phường',
            'address': 'Địa chỉ',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['district'].queryset = District.objects.none()

        if 'city' in self.data:
            try:
                city_id = self.data.get('city')
                print(city_id)
                self.fields['district'].queryset = \
                    District.objects.filter(city_id=city_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['district'].queryset = self.instance.city\
                .district_set.order_by('name')
