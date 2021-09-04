import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger
from django.db.models import Sum
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect

from dealership.models import Dealership, DealershipType, City, District
from user.views import get_user_fullname
from financial_accounting.models import Importation, ImportationDetail
from .exportation_algorithm import show_exportation_detail_form, show_exportation_form, create_exportation_form_in_db, \
    create_product_in_exportation_in_db, add_information_for_exportation_form
from .forms import ImportationDetailForm, MultipleImportationDetailForm, \
    ExportationForm, ExportationDetailForm, MultipleExportationDetailForm
from .importation_algorithm import send_importation_request, \
    show_importation_detail_request
from .models import Repository, Exportation, ExportationDetail


@login_required(login_url='user_login')
def product_importation_view(request):
    importation_detail_form = ImportationDetailForm()
    multiple_importation_detail_form = MultipleImportationDetailForm()
    number_of_importation = Importation.objects.count()
    number_of_exportation = Exportation.objects.count()

    debt = 0
    income = 0

    if number_of_importation > 0 and number_of_exportation > 0:
        debt = Importation.objects.aggregate(Sum('debt'))['debt__sum']
        income = Exportation.objects.aggregate(Sum('payed'))['payed__sum']
    elif number_of_importation == 0 and number_of_exportation > 0:
        income = Exportation.objects.aggregate(Sum('payed'))['payed__sum']
    elif number_of_importation > 0 and number_of_exportation == 0:
        debt = Importation.objects.aggregate(Sum('debt'))['debt__sum']

    context = {
        'importation_detail_form': importation_detail_form,
        'multiple_importation_detail_form': multiple_importation_detail_form,
        'username': get_user_fullname(request),
        'debt': debt - income
    }

    if request.method == 'POST':
        filled_detail_importation_form = context['importation_detail_form'] = ImportationDetailForm(request.POST)
        if filled_detail_importation_form.is_valid():
            if 'show' in request.POST:
                context['forms'] = [show_importation_detail_request(filled_detail_importation_form)]
                context['total'] = context['forms'][0]['p_total']
            if 'save' in request.POST:
                send_importation_request(
                    filled_form=filled_detail_importation_form,
                    request=request,
                    total=int(filled_detail_importation_form.cleaned_data["product_price"]) * int(
                        filled_detail_importation_form.cleaned_data["product_quantity"]))
                messages.success(request, 'Gửi yêu cầu nhập hàng thành công')
                return redirect('product-importation')

    return render(request, 'repository/importation_form.html', context)


@login_required(login_url='user_login')
def products_importation_view(request):
    number_of_products = 2
    filled_multiple_detail_importation_form = MultipleImportationDetailForm(request.GET)
    context = {
        'username': get_user_fullname(request),
        'importation_detail_forms': []
    }

    if filled_multiple_detail_importation_form.is_valid():
        number_of_products = filled_multiple_detail_importation_form.cleaned_data['number']

    ImportationFormSet = formset_factory(ImportationDetailForm, extra=number_of_products)
    formset = ImportationFormSet()
    context['formset'] = formset

    if request.method == 'POST':
        filled_formset = context['formset'] = ImportationFormSet(request.POST)
        total = 0
        if filled_formset.is_valid():
            if 'show' in request.POST:
                for form in filled_formset:
                    try:
                        filled_importation_detail_form = context[
                            'importation_detail_form'] = show_importation_detail_request(
                            form)
                        total += filled_importation_detail_form['p_total']
                        context['importation_detail_forms'].append(filled_importation_detail_form)
                    except KeyError:
                        pass
                context['filled_importation_form'] = total
                context['total'] = total
            if 'save' in request.POST:
                for form in filled_formset:
                    total += form.cleaned_data["product_price"] * form.cleaned_data["product_quantity"]

                send_importation_request(
                    filled_form=filled_formset,
                    request=request,
                    total=total,
                    number_of_products=number_of_products
                )
                messages.success(request, 'Gửi yêu cầu nhập hàng thành công')
                return redirect('products-importation')

    return render(request, 'repository/importation_forms.html', context)


@login_required(login_url='user_login')
def product_exportation_view(request):
    cities = City.objects.all()
    districts = District.objects.all()
    exportation_form = ExportationForm()
    exportation_detail_form = ExportationDetailForm()
    multiple_exportation_detail_form = MultipleExportationDetailForm()
    context = {
        'cities': cities,
        'districts': districts,
        'exportation_form': exportation_form,
        'exportation_detail_form': exportation_detail_form,
        'forms': [],
        'multiple_exportation_detail_form': multiple_exportation_detail_form,
        'username': get_user_fullname(request),
        'is_qualified': False,
        'is_enough': False
    }

    if request.method == 'POST':
        filled_form = context['exportation_detail_form'] = ExportationDetailForm(request.POST)
        context['exportation_form'] = ExportationForm(request.POST)
        if filled_form.is_valid():
            dealership = Dealership.objects.get(id=request.POST['dealership'])
            dealership_type = Dealership.objects.get(id=request.POST['dealership']).type
            discount_rate = DealershipType.objects.get(id=dealership_type.id).discount_rate

            if 'show' in request.POST:
                filled_exportation_detail_form, is_enough = show_exportation_detail_form(filled_form, discount_rate)
                context['forms'].append(filled_exportation_detail_form)
                context['filled_exportation_form'], is_qualified = \
                    show_exportation_form(request, context['forms'][0]['p_total'], dealership)
                context['p_total'] = context['forms'][0]['p_total']
                context['is_qualified'] = is_qualified
                context['is_enough'] = is_enough
                if not is_qualified:
                    messages.error(request, 'Vượt quá công nợ cho phép')
                    return render(request, 'repository/exportation_form.html', context)
                if not is_enough:
                    messages.error(request, 'Không đủ số lượng hàng hoá')
                    return render(request, 'repository/exportation_form.html', context)

            if 'save' in request.POST:
                exportation, d_payed = create_exportation_form_in_db(request, dealership)
                total = create_product_in_exportation_in_db(filled_form, exportation, discount_rate)
                add_information_for_exportation_form(
                    exportation=exportation,
                    total=total,
                    d_payed=d_payed,
                    dealership=dealership
                )
                messages.success(request, 'Xuất hàng thành công')
                return redirect('product-exportation')

    return render(request, 'repository/exportation_form.html', context)


@login_required(login_url='user_login')
def products_exportation_view(request):
    number_of_products = 2
    exportation_form = ExportationForm()
    filled_multiple_detail_exportation_form = MultipleExportationDetailForm(request.GET)
    is_enough = False
    context = {
        'exportation_form': exportation_form,
        'username': get_user_fullname(request),
        'exportation_detail_forms': [],
        'is_qualified': False,
        'is_enough': is_enough
    }

    if filled_multiple_detail_exportation_form.is_valid():
        number_of_products = filled_multiple_detail_exportation_form.cleaned_data['number']

    ExportationDetailFormSet = formset_factory(ExportationDetailForm, extra=number_of_products)
    formset = ExportationDetailFormSet()
    context['formset'] = formset

    if request.method == 'POST':
        filled_formset = context['formset'] = ExportationDetailFormSet(request.POST)
        context['exportation_form'] = ExportationForm(request.POST)
        total = 0
        if filled_formset.is_valid():
            dealership = Dealership.objects.get(id=request.POST['dealership'])
            dealership_type = Dealership.objects.get(id=request.POST['dealership']).type
            discount_rate = DealershipType.objects.get(id=dealership_type.id).discount_rate
            if 'show' in request.POST:
                for form in filled_formset:
                    filled_exportation_detail_form, is_enough = show_exportation_detail_form(form, discount_rate)
                    total += filled_exportation_detail_form['p_total']
                    context['exportation_detail_forms'].append(filled_exportation_detail_form)
                context['filled_exportation_form'], is_qualified = show_exportation_form(request, total, dealership)
                context['p_total'] = total
                context['is_qualified'] = is_qualified
                context['is_enough'] = is_enough
                if not is_qualified:
                    messages.error(request, 'Vượt quá công nợ cho phép')
                    return render(request, 'repository/exportation_forms.html', context)
                if not is_enough:
                    messages.error(request, 'Không đủ số lượng hàng hoá')
                    return render(request, 'repository/exportation_form.html', context)
            if 'save' in request.POST:
                exportation, d_payed = create_exportation_form_in_db(request, dealership)
                for form in filled_formset:
                    total += create_product_in_exportation_in_db(form, exportation, discount_rate)

                add_information_for_exportation_form(
                    exportation=exportation,
                    total=total,
                    d_payed=d_payed,
                    dealership=dealership
                )
                messages.success(request, 'Xuất hàng thành công')
                return redirect('products-exportation')

    return render(request, 'repository/exportation_forms.html', context)


def products_report(month, products):
    importation_forms = Importation.objects.filter(importation_date__month=month)
    exportation_forms = Exportation.objects.filter(exportation_date__month=month)
    repository = Repository.objects

    report = {}
    for importation_form in importation_forms:
        date = importation_form.importation_date
        importation_detail_forms = ImportationDetail.objects.filter(importation=importation_form.id)
        for importation_detail_form in importation_detail_forms:
            product_id = f'{date.strftime("%d%m%y")}{importation_detail_form.product_id}'
            product_quantity = repository.get(product_id=product_id).product_quantity
            if importation_detail_form.product_id in report:
                report[importation_detail_form.product_id][1] += importation_detail_form.product_quantity
                report[importation_detail_form.product_id][3] += product_quantity
            else:
                report[importation_detail_form.product_id] = [f'{importation_detail_form.product_name} - '
                                                              f'{date.strftime("%d/%m/%Y")}',
                                                              importation_detail_form.product_quantity,
                                                              0,
                                                              product_quantity,
                                                              importation_form.importation_date.strftime('%d/%m/%Y')]

    export_quantity = {}
    for exportation_form in exportation_forms:
        exportation_detail_forms = ExportationDetail.objects.filter(exportation=exportation_form.id)
        for exportation_detail_form in exportation_detail_forms:
            product_id = exportation_detail_form.product_id
            if product_id in export_quantity:
                export_quantity[product_id] += exportation_detail_form.product_quantity
            else:
                export_quantity[product_id] = exportation_detail_form.product_quantity

    for product_id in export_quantity:
        import_product_id = product_id[6:]
        if import_product_id in report:
            report[import_product_id][2] += export_quantity[product_id]
            report[import_product_id][3] = Repository.objects.get(product_id=product_id).product_quantity
        else:
            report[import_product_id] = [
                repository.get(product_id=product_id).product_name,
                0,
                export_quantity[product_id],
                Repository.objects.get(product_id=product_id).product_quantity
            ]

    for product_id in report:
        products.append(report[product_id])

    return products


def pagination(request, chosen_month, products):
    products = products_report(chosen_month, products)
    paginator = Paginator(products, 10)
    pages = request.GET.get('page', 1)
    try:
        products = paginator.page(pages)
    except PageNotAnInteger:
        products = paginator.page(1)
    return products


def products_report_view(request):
    current_month = datetime.datetime.now().month
    products = []

    context = {
        'products': products,
        'current_month': current_month,
        'username': get_user_fullname(request),
        'months': [i for i in range(1, current_month + 1)],
    }

    if request.is_ajax():
        current_month = request.GET.get('month')
        products = products_report(current_month, products)
        return JsonResponse({'month': current_month, 'products': products}, status=200)

    products = pagination(request, current_month, products)
    context['products'] = products
    return render(request, 'repository/products_report.html', context)
