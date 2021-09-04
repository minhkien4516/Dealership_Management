from financial_accounting.models import ImportationDetailRequest, ImportationRequest


def show_importation_detail_request(filled_form):
    filled_importation_detail_form = {'p_id': filled_form.cleaned_data['product_id'].upper(),
                                      'p_name': filled_form.cleaned_data['product_name'],
                                      'p_price': filled_form.cleaned_data['product_price'],
                                      'p_quantity': filled_form.cleaned_data['product_quantity'],
                                      'p_total': int(filled_form.cleaned_data['product_price']) *
                                                 int(filled_form.cleaned_data['product_quantity'])}

    return filled_importation_detail_form


def send_importation_request(filled_form, request, total, number_of_products=1):
    importation = ImportationRequest()
    importation.total = total
    importation.save()

    if number_of_products == 1:
        detail_importation = ImportationDetailRequest()
        detail_importation.importation_request = importation
        detail_importation.product_id = request.POST["product_id"].upper()
        detail_importation.product_name = request.POST["product_name"]
        detail_importation.product_price = request.POST["product_price"]
        detail_importation.product_quantity = request.POST["product_quantity"]
        detail_importation.total_price = filled_form.cleaned_data["product_price"] * \
                                         filled_form.cleaned_data["product_quantity"]
        detail_importation.save()
    else:
        for product in range(0, number_of_products):
            detail_importation = ImportationDetailRequest()
            detail_importation.importation_request = importation
            detail_importation.product_id = filled_form[product].cleaned_data["product_id"].upper()
            detail_importation.product_name = filled_form[product].cleaned_data["product_name"]
            detail_importation.product_price = filled_form[product].cleaned_data["product_price"]
            detail_importation.product_quantity = filled_form[product].cleaned_data["product_quantity"]
            detail_importation.total_price = filled_form[product].cleaned_data["product_price"] * \
                                             filled_form[product].cleaned_data["product_quantity"]
            detail_importation.save()
