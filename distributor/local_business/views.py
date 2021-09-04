import datetime

from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger
from django.shortcuts import render, redirect

from dealership.models import Dealership, Owner
from financial_accounting.models import Importation, ImportationDetail
from local_business.models import DealershipRegistrationQueue, DealershipCancellationQueue
from repository.models import Exportation, ExportationDetail
from user.views import get_user_fullname


def count_notifications():
    num_of_undone_regis_form = DealershipRegistrationQueue.objects.filter(is_done=False).count()
    num_of_undone_cancel_form = DealershipCancellationQueue.objects.filter(is_done=False).count()
    if num_of_undone_regis_form > 0 and num_of_undone_cancel_form > 0:
        return {'total': num_of_undone_regis_form + num_of_undone_cancel_form,
                'regis': num_of_undone_regis_form,
                'cancel': num_of_undone_cancel_form}
    if num_of_undone_regis_form > 0:
        return {'total': num_of_undone_regis_form + num_of_undone_cancel_form,
                'regis': num_of_undone_regis_form, }
    if num_of_undone_cancel_form > 0:
        return {'total': num_of_undone_regis_form + num_of_undone_cancel_form,
                'cancel': num_of_undone_cancel_form}
    return {}


def dealership_list_view(request):
    dealerships = Dealership.objects.all()

    paginator = Paginator(dealerships, 10)
    pages = request.GET.get('page', 1)
    try:
        dealerships = paginator.page(pages)
    except PageNotAnInteger:
        dealerships = paginator.page(1)

    context = {
        'dealerships': dealerships,
        'num_of_total_undone_form': count_notifications(),
        'username': get_user_fullname(request)
    }

    return render(request, 'local_business/dealership_list.html', context)


def dealership_registration_queue_view(request):
    queue_dealerships = DealershipRegistrationQueue.objects.filter(is_done=False)

    paginator = Paginator(queue_dealerships, 10)
    pages = request.GET.get('page', 1)
    try:
        queue_dealerships = paginator.page(pages)
    except PageNotAnInteger:
        queue_dealerships = paginator.page(1)

    context = {
        'queue_dealerships': queue_dealerships,
        'num_of_total_undone_form': count_notifications(),
        'username': get_user_fullname(request)
    }

    return render(request, 'local_business/dealership_in_registration_queue.html', context)


def approve_registration_form(request, dealership_in_queue_id):
    dealership_in_queue = DealershipRegistrationQueue.objects.get(id=dealership_in_queue_id)

    if request.method == 'GET':
        current_number_of_normal_dealerships = Dealership.objects \
            .filter(district=dealership_in_queue.district,
                    type=dealership_in_queue.type) \
            .count()

        max_number_of_dealerships = dealership_in_queue.type.maximum_number_of_dealerships

        if current_number_of_normal_dealerships < max_number_of_dealerships:
            dealership_in_queue.status = 'Đã duyệt đơn! Đơn đăng ký đại lý đã được chấp nhận'
            dealership_in_queue.is_done = True
            dealership_in_queue.save()

            owner = Owner(
                pk=dealership_in_queue.owner,
                name=dealership_in_queue.owner_name,
                phone_number=dealership_in_queue.owner_phone,
                email=dealership_in_queue.owner_email
            )
            owner.save()

            dealership = Dealership(
                name=dealership_in_queue.name,
                type=dealership_in_queue.type,
                city=dealership_in_queue.city,
                district=dealership_in_queue.district,
                address=dealership_in_queue.address,
                owner=owner,
            )
            dealership.save()

            message = 'Đã chấp nhận đơn đăng ký!'
            messages.success(request, message)
        else:
            message = f'Đã đủ số lượng đại lý loại {dealership_in_queue.type} ' \
                      f'trên {dealership_in_queue.district}, {dealership_in_queue.city}!'
            messages.error(request, message)
        return redirect('dealership-registration-queue')

    return render(request, 'local_business/dealership_in_registration_queue.html')


def reject_registration_form(request, dealership_in_queue_id):
    dealership_in_queue = DealershipRegistrationQueue.objects.get(id=dealership_in_queue_id)

    if request.method == 'GET':
        dealership_in_queue.status = 'Đã duyệt đơn! Đơn đăng ký đại lý đã bị từ chối'
        dealership_in_queue.is_done = True
        dealership_in_queue.save()
        return redirect('dealership-registration-queue')

    return render(request, 'local_business/dealership_in_registration_queue.html')


def dealership_cancellation_in_queue_view(request):
    queue_dealerships = DealershipCancellationQueue.objects.filter(is_done=False)

    context = {
        'queue_dealerships': queue_dealerships,
        'num_of_total_undone_form': count_notifications(),
        'username': get_user_fullname(request)
    }

    return render(request, 'local_business/dealership_in_cancellation_queue.html', context)


def approve_cancellation_form(request, dealership_id):
    dealership = Dealership.objects.get(id=dealership_id)

    exportation_forms = Exportation.objects.filter(dealership=dealership)
    for exportation_form in exportation_forms:
        exportation_detail_forms = ExportationDetail.objects.filter(exportation=exportation_form)
        for exportation_detail_form in exportation_detail_forms:
            importation_date = datetime.datetime.strptime(exportation_detail_form.product_id[:6], '%d%m%y')
            product_id = exportation_detail_form.product_id[6:]
            product_quantity = exportation_detail_form.product_quantity
            importation_forms = Importation.objects.filter(importation_date__date=importation_date)
            for importation_form in importation_forms:
                product_quantity_in_importation = ImportationDetail.objects\
                    .get(importation=importation_form, product_id=product_id)\
                    .product_quantity
                ImportationDetail.objects.filter(importation=importation_form, product_id=product_id)\
                    .update(product_quantity=product_quantity_in_importation-product_quantity)

    dealership.delete()

    message = 'Đã duyệt đơn huỷ đăng ký đại lý!'
    messages.success(request, message)
    return redirect('dealerships-in-cancellation-queue')


def reject_cancellation_form(request, dealership_id):
    dealership = Dealership.objects.get(id=dealership_id)

    cancellation_form = DealershipCancellationQueue.objects.get(dealership=dealership)
    cancellation_form.status = 'Đơn huỷ đăng ký đại lý đã bị từ chối'
    cancellation_form.is_done = True
    cancellation_form.save()

    Dealership.objects.filter(id=dealership_id).update(is_active=True)

    message = 'Đã từ chối đơn huỷ đăng ký đại lý!'
    messages.success(request, message)
    return redirect('dealerships-in-cancellation-queue')
