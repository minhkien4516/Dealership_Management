import datetime

from django.contrib import messages
from django.shortcuts import render, redirect

from dealership.models import Dealership
from financial_accounting.forms import ImportationForm
from financial_accounting.handle_request_algorithm import create_importation_in_db, remove_importation_request
from financial_accounting.models import ImportationRequest, ImportationDetailRequest, Importation, ImportationDetail
from financial_accounting.report_algorithm import load_exportation_forms_by_month, load_importation_forms_by_month
from repository.models import Exportation, ExportationDetail
from user.views import get_user_fullname


def count_importation_request():
    number_of_importation_request = ImportationRequest.objects.all().count()
    if number_of_importation_request == 0:
        return {}
    return {'number_of_importation_request': number_of_importation_request}


def exportation_report_view(request):
    dealerships = Dealership.objects.all()
    current_month = datetime.datetime.now().month

    context = {
        'exportation_forms': [],
        'months': [i for i in range(1, current_month + 1)],
        'current_month': current_month,
        'number_of_importation_request': count_importation_request(),
        'username': get_user_fullname(request)
    }

    if request.method == 'GET' and 'choose_month' in request.GET:
        context['exportation_forms'], context['total_of_exportation_forms'], context['total'], \
            context['income'], context['debt'] = \
            load_exportation_forms_by_month(dealerships, request.GET.get('month'))

        context['current_month'] = request.GET.get('month')
        return render(request, 'financial_accounting/report/exportation_report.html', context)

    context['exportation_forms'], context['total_of_exportation_forms'], \
        context['total'], context['income'], context['debt'] = \
        load_exportation_forms_by_month(dealerships)
    return render(request, 'financial_accounting/report/exportation_report.html', context)


def load_exportation_detail_reports_by_month_view(request, dealership_id, month=datetime.datetime.now().month):
    exportation_forms = Exportation.objects.filter(dealership=dealership_id, exportation_date__month=month)
    dealership = Dealership.objects.get(id=dealership_id)
    context = {
        'dealership_name': dealership.name.upper(),
        'number_of_importation_request': count_importation_request(),
        'username': get_user_fullname(request),
        'exportation_detail_forms': {}
    }

    if request.method == 'GET':
        exportation_forms_container = {}
        for exportation_form in exportation_forms:
            exportation_detail_forms = ExportationDetail.objects.filter(exportation=exportation_form.id)
            for exportation_detail_form in exportation_detail_forms:
                if exportation_form.id in exportation_forms_container:
                    exportation_forms_container[exportation_form.id].append({
                        'product': exportation_detail_form.product,
                        'product_quantity': exportation_detail_form.product_quantity,
                        'product_price': exportation_detail_form.product_price,
                        'total_price': exportation_detail_form.total_price,
                        'exportation_date': exportation_form.exportation_date.strftime('%d/%m/%Y'),
                    })
                else:
                    exportation_forms_container[exportation_form.id] = [{
                        'product': exportation_detail_form.product,
                        'product_quantity': exportation_detail_form.product_quantity,
                        'product_price': exportation_detail_form.product_price,
                        'total_price': exportation_detail_form.total_price,
                        'exportation_date': exportation_form.exportation_date.strftime('%d/%m/%Y'),
                    }]

        for each in exportation_forms_container:
            context['exportation_detail_forms'][each] = []
            for i in range(0, len(exportation_forms_container[each])):
                context['exportation_detail_forms'][each].append({
                    'product': exportation_forms_container[each][i]['product'],
                    'product_quantity': exportation_forms_container[each][i]['product_quantity'],
                    'product_price': f'{exportation_forms_container[each][i]["product_price"]:,}',
                    'total_price': f'{exportation_forms_container[each][i]["total_price"]:,}',
                    'exportation_date': exportation_forms_container[each][i]['exportation_date'],
                })

        return render(request, 'financial_accounting/report/exportation_detail_report.html', context)


def importation_report_view(request):
    current_month = datetime.datetime.now().month

    context = {
        'importation_forms': [],
        'months': [i for i in range(1, current_month + 1)],
        'current_month': current_month,
        'number_of_importation_request': count_importation_request(),
        'username': get_user_fullname(request)
    }

    if request.method == 'GET' and 'choose_month' in request.GET:
        context['importation_forms'], context['total'], context['payed'], context['debt'] = \
            load_importation_forms_by_month(request.GET.get('month'))
        context['current_month'] = request.GET.get('month')
        return render(request, 'financial_accounting/report/importation_report.html', context)

    context['importation_forms'], context['total'], context['payed'], context['debt'] = \
        load_importation_forms_by_month()
    return render(request, 'financial_accounting/report/importation_report.html', context)


def load_importation_detail_reports_by_month(request, importation_id):
    context = {
        'importation_detail_forms': [],
        'id': importation_id,
        'number_of_importation_request': count_importation_request(),
        'username': get_user_fullname(request)
    }

    if request.method == 'GET':
        importation_forms = Importation.objects.filter(id=importation_id)
        for importation_form in importation_forms:
            importation_detail_forms = ImportationDetail.objects.filter(importation=importation_form)
            for importation_detail_form in importation_detail_forms:
                context['importation_detail_forms'] += [importation_detail_form]

        return render(request, 'financial_accounting/report/importation_detail_report.html', context)


def importation_request_view(request):
    importation_requests = ImportationRequest.objects.all()

    context = {
        'importation_requests': importation_requests,
        'number_of_importation_request': count_importation_request(),
        'username': get_user_fullname(request)
    }

    return render(request, 'financial_accounting/request/imporation_request.html', context)


def load_importation_detail_request(request, importation_request_id):
    importation_form = ImportationForm()
    importation_request = ImportationRequest.objects.get(id=importation_request_id)
    importation_details_request = ImportationDetailRequest.objects \
        .filter(importation_request=importation_request)

    context = {
        'importation_details_request': importation_details_request,
        'importation_request_id': importation_request.id,
        'importation_form': importation_form,
        'number_of_importation_request': count_importation_request(),
        'username': get_user_fullname(request)
    }

    if request.method == 'POST':
        filled_form = ImportationForm(request.POST)
        if filled_form.is_valid():
            create_importation_in_db(importation_request_id, filled_form.cleaned_data['payed'])
            messages.success(request, 'Đã duyệt đơn thành công')
            return redirect('importation-request')

    return render(request, 'financial_accounting/request/importation_detail_request.html', context)


def approve_importation_detail_request(request, importation_request_id):
    if request.method == 'GET':
        create_importation_in_db(importation_request_id)
        messages.success(request, 'Đã duyệt đơn thành công')
        return redirect('importation-request')

    return redirect('importation-request')


def reject_importation_detail_request(request, importation_request_id):
    remove_importation_request(importation_request_id)
    messages.success(request, 'Đã từ chối đơn xin nhập hàng hoá')
    return redirect('importation-request')
