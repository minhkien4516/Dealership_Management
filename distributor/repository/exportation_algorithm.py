import datetime

from dealership.models import Dealership
from repository.models import Repository, Exportation, ExportationDetail


def show_exportation_detail_form(filled_form, discount_rate):
    product = Repository.objects.get(product_name=filled_form.cleaned_data['product'])
    p_name = product.product_name.split('-')
    p_price = product.product_price + (product.product_price * 0.3) - (product.product_price * discount_rate)
    p_quantity = filled_form.cleaned_data['product_quantity']
    p_total = int(p_price) * int(p_quantity)

    filled_exportation_detail_form = {'p_name': p_name[0], 'p_importation_date': p_name[1], 'p_price': p_price,
                                      'p_quantity': p_quantity, 'p_total': p_total}

    return filled_exportation_detail_form, p_quantity <= product.product_quantity


def show_exportation_form(request, total, dealership):
    d_name = dealership.name
    d_address = f'{dealership.address}, {dealership.district}, {dealership.city}'
    d_pre_debt = dealership.debt
    d_payed = int(request.POST['payed'])
    d_debt = total - d_payed

    filled_exportation_form = {'d_name': d_name, 'd_address': d_address, 'd_pre_debt': d_pre_debt, 'd_payed': d_payed,
                               'd_debt': d_debt, 'date': datetime.datetime.now().strftime('%d/%m/%Y')}

    return filled_exportation_form, (d_pre_debt + d_debt) <= dealership.type.maximum_debt


def create_exportation_form_in_db(request, dealership):
    d_payed = int(request.POST['payed'])

    exportation = Exportation(
        payed=d_payed,
        dealership=dealership
    )
    exportation.save()

    return exportation, d_payed


def create_product_in_exportation_in_db(filled_form, exportation, discount_rate):
    product = Repository.objects.get(product_name=filled_form.cleaned_data['product'])
    p_price = product.product_price + (product.product_price * 0.3) - (product.product_price * discount_rate)
    p_quantity = filled_form.cleaned_data['product_quantity']
    p_total = int(p_price) * int(p_quantity)

    ExportationDetail(
        product=product,
        product_price=p_price,
        product_quantity=p_quantity,
        total_price=p_total,
        exportation=exportation
    ).save()

    product.product_quantity -= p_quantity
    product.save()
    return p_total


def add_information_for_exportation_form(exportation, total, d_payed, dealership):
    exportation = Exportation.objects.get(id=exportation.id)
    exportation.total = total
    exportation.debt = total - d_payed
    exportation.save()

    d_debt = total - d_payed
    dealership.debt += d_debt
    Dealership.objects.filter(id=dealership.id).update(debt=dealership.debt)
