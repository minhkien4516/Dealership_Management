from django.core.exceptions import ObjectDoesNotExist

from financial_accounting.models import ImportationRequest, Importation, ImportationDetailRequest, ImportationDetail
from repository.models import Repository


def create_product_in_importation_in_db(importation, importation_detail):
    product_id = f'{importation.importation_date.strftime("%d%m%y")}' \
                 f'{importation_detail.product_id.upper()}'

    try:
        product = Repository.objects.get(product_id=product_id)
        product.product_name = f'{importation_detail.product_name} - ' \
                               f'{importation.importation_date.strftime("%d/%m/%Y")}'
        product.product_quantity += int(importation_detail.product_quantity)
        product.product_price = importation_detail.product_price
        product.save()
    except ObjectDoesNotExist:
        product = Repository()
        product.product_id = product_id
        product.product_name = f'{importation_detail.product_name} - ' \
                               f'{importation.importation_date.strftime("%d/%m/%Y")}'
        product.product_price = importation_detail.product_price
        product.product_quantity = importation_detail.product_quantity
        product.save()


def create_importation_in_db(importation_request_id, debt=0):
    importation_request = ImportationRequest.objects.get(id=importation_request_id)
    importation = Importation(
        importation_date=importation_request.importation_date,
        total=importation_request.total,
        payed=debt,
        debt=importation_request.total - debt
    )
    importation.save()
    importation_details_requests = ImportationDetailRequest.objects \
        .filter(importation_request=importation_request)
    for importation_detail_request in importation_details_requests:
        importation_detail = ImportationDetail(
            product_id=importation_detail_request.product_id,
            product_name=importation_detail_request.product_name,
            product_price=importation_detail_request.product_price,
            product_quantity=importation_detail_request.product_quantity,
            total_price=importation_detail_request.total_price,
            importation=importation
        )
        importation_detail.save()
        create_product_in_importation_in_db(importation, importation_detail)
        importation_detail_request.delete()
    importation_request.delete()


def remove_importation_request(importation_request_id):
    ImportationRequest.objects.get(id=importation_request_id).delete()
