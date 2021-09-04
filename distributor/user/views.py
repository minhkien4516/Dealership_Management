from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from user.forms import DealershipRegistrationForm
from dealership.models import Dealership, District
from local_business.models import DealershipRegistrationQueue, DealershipCancellationQueue


def user_logout_view(request):
    logout(request)
    return redirect('/')


def get_user_fullname(request):
    return f'{request.user.first_name} {request.user.last_name}'


@login_required(login_url='homepage')
def dealership_registration_view(request):
    dealership_registration_form = DealershipRegistrationForm()
    context = {
        'form': dealership_registration_form,
        'username': f'{request.user.first_name} {request.user.last_name}',
    }

    if request.method == 'POST':
        filled_form = DealershipRegistrationForm(request.POST)

        if filled_form.is_valid():
            """
            Check the number of existing dealerships
            which are corresponding type
            of which user entered
            """

            dealership_type = filled_form.cleaned_data['type']
            dealership_type_id = filled_form.cleaned_data['type'].id

            dealership_district = filled_form.cleaned_data['district']

            current_number_of_dealerships_in_queue = DealershipRegistrationQueue.objects \
                .filter(district=dealership_district,
                        type=dealership_type_id,
                        is_done=False) \
                .count()
            current_number_of_dealerships = Dealership.objects \
                .filter(district=dealership_district,
                        type=dealership_type_id) \
                .count()

            """
            Check type of dealership which user entered
            Assign a maximum number of dealership in a variable
            based on dealership type user's form
            """
            max_number_of_dealerships = dealership_type.maximum_number_of_dealerships

            """
            Check whether if the number of existing dealership
            is greater than the maximum number or not
            If not generate dealership id for user
            """
            if current_number_of_dealerships_in_queue >= max_number_of_dealerships:
                new_form = filled_form
                message = f'Đã đủ số lượng đơn đăng ký đại lý loại {filled_form.cleaned_data["type"]} ' \
                          f'trên {filled_form.cleaned_data["district"]}, {filled_form.cleaned_data["city"]}!'

                messages.error(request, message)
                context['form'] = new_form
                return redirect('dealership-registration')
            elif current_number_of_dealerships >= max_number_of_dealerships:
                new_form = filled_form
                message = f'Đã đủ số lượng đại lý loại {filled_form.cleaned_data["type"]} ' \
                          f'trên {filled_form.cleaned_data["district"]}, {filled_form.cleaned_data["city"]}!'

                messages.error(request, message)
                context['form'] = new_form
                return redirect('dealership-registration')

            """
            Create new owner based on the current user logged in
            """
            dealership_type = filled_form.cleaned_data['type']
            dealership_name = filled_form.cleaned_data['name']
            dealership_city = filled_form.cleaned_data['city']
            dealership_address = filled_form.cleaned_data['address']
            dealership = DealershipRegistrationQueue(
                name=dealership_name,
                type=dealership_type,
                city=dealership_city,
                district=dealership_district,
                address=dealership_address,
                owner_name=f'{request.user.first_name} {request.user.last_name}',
                owner=request.user.pk,
                owner_phone=filled_form.cleaned_data['owner_phone'],
                owner_email=request.user.email
            )
            dealership.save()
            message = 'Đã gửi đơn đăng ký đến nhà phân phối!'

            messages.success(request, message)
            return redirect('dealership-registration')

    return render(request, 'user/dealership_registration_form.html', context)


def load_districts(request):
    city_id = request.GET['city']
    districts = District.objects.filter(city_id=city_id).all()
    return render(request, 'user/district_dropdown_list_options.html',
                  {'districts': districts})


def dealerships_of_current_user(request):
    current_user_id = request.user.pk
    dealerships_of_current_owner = Dealership.objects.filter(
        owner_id=current_user_id
    )
    context = {
        'dealerships': dealerships_of_current_owner,
        'username': get_user_fullname(request)
    }

    return render(request, 'user/dealerships_of_current_user.html', context)


def dealerships_in_queue_of_current_user(request):
    current_user_id = request.user.pk
    dealerships_in_registration_queue_of_current_owner = DealershipRegistrationQueue.objects.filter(
        owner=current_user_id, is_done=False
    )

    dealerships_in_cancellation_queue_of_current_owner = {}
    dealerships = Dealership.objects.filter(owner=current_user_id)
    for dealership in dealerships:
        dealerships_in_cancellation_queue = DealershipCancellationQueue.objects.filter(
            dealership=dealership
        )
        for each in dealerships_in_cancellation_queue:
            dealerships_in_cancellation_queue_of_current_owner[each.pk] = []
            dealerships_in_cancellation_queue_of_current_owner[each.pk] += [
                each.dealership.name,
                each.dealership.type.name,
                each.dealership.address,
                each.dealership.district.name,
                each.dealership.city.name,
                each.dealership.registration_date.strftime('%d/%m/%Y'),
                each.status,
            ]

    context = {
        'dealerships_in_registration_queue': dealerships_in_registration_queue_of_current_owner,
        'dealerships_in_cancellation_queue': dealerships_in_cancellation_queue_of_current_owner,
        'username': get_user_fullname(request)
    }

    return render(request, 'user/dealerships_in_queue_of_current_owner.html', context)


def update_delete_dealership_information_view(request, dealership_id):
    is_done = False
    try:
        dealership_id = int(dealership_id)
        dealership = DealershipRegistrationQueue.objects.get(id=dealership_id)
        update = DealershipRegistrationQueue.objects.filter(id=dealership_id)
    except ValueError:
        dealership = Dealership.objects.get(id=dealership_id)
        update = Dealership.objects.filter(id=dealership_id)
        is_done = True

    context = {
        'dealership': dealership,
        'is_done': is_done,
        'username': get_user_fullname(request)
    }

    if request.method == 'POST':
        if 'update' in request.POST:
            new_dealership_name = request.POST.get('dealership_name')
            new_dealership_address = request.POST.get('dealership_address')
            update.update(name=new_dealership_name, address=new_dealership_address)
            messages.success(request, 'Cập nhật thông tin đại lý thành công')
            return redirect('update-dealership-information', dealership_id)
        if 'cancel' in request.POST:
            if is_done:
                if dealership.debt == 0:
                    try:
                        DealershipCancellationQueue.objects.get(dealership=dealership, is_done=False)
                        messages.warning(request, 'Đơn huỷ đăng ký đại lý đã được gửi! '
                                                  'Vui lòng chờ bộ phân kinh doanh duyệt đơn')
                        return redirect('update-dealership-information', dealership_id)
                    except DealershipCancellationQueue.DoesNotExist:
                        DealershipCancellationQueue(dealership=dealership, message=request.POST.get('message')).save()
                        Dealership.objects.filter(id=dealership_id).update(is_active=False)
                        messages.success(request, 'Đã gửi đơn huỷ đăng ký đại lý cho nhà phân phối')
                        return redirect('update-dealership-information', dealership_id)
                else:
                    messages.error(request, 'Vui lòng thanh toán công nợ trước khi thực hiện huỷ đăng ký đại lý, '
                                            f'công nợ còn lại: {dealership.debt:,} VNĐ')
                    return redirect('update-dealership-information', dealership_id)

            DealershipRegistrationQueue.objects.get(id=dealership_id).delete()
            messages.success(request, 'Đã huỷ đơn đăng ký đại lý')
            return redirect('dealerships-in-queue-of-current-user')

    return render(request, 'user/edit_dealership_information.html', context)
