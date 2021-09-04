import datetime

from financial_accounting.models import Importation
from repository.models import Exportation


def load_exportation_forms_by_month(dealerships, month=datetime.datetime.now().month):
    exportation_forms = []
    total = 0
    income = 0
    debt = 0
    total_of_exportation_forms = 0

    for dealership in dealerships:
        financial_total_of_each = 0
        each_payed = 0
        debt_of_each = 0
        exportation_forms_of_dealership = Exportation.objects.filter(dealership=dealership.id,
                                                                     exportation_date__month=month)
        total_of_each_exportation_forms_of_dealership = exportation_forms_of_dealership.count()

        for form in exportation_forms_of_dealership:
            financial_total_of_each += form.total
            each_payed += form.payed
            debt_of_each += form.debt

        total_of_exportation_forms += total_of_each_exportation_forms_of_dealership
        total += financial_total_of_each
        income += each_payed
        debt += debt_of_each

        if total_of_each_exportation_forms_of_dealership > 0:
            exportation_forms.append({
                'dealership_id': dealership.id,
                'dealership_name': dealership.name,
                'dealership_address': dealership.address,
                'dealership_district': dealership.district.name,
                'dealership_city': dealership.city.name,
                'total_of_each_exportation_forms_of_dealership': total_of_each_exportation_forms_of_dealership,
                'financial_total_of_each': f'{financial_total_of_each:,}',
                'each_payed': f'{each_payed:,}',
                'debt_of_each': f'{debt_of_each:,}',

            })
    return exportation_forms, total_of_exportation_forms, total, income, debt


def load_importation_forms_by_month(month=datetime.datetime.now().month):
    total = 0
    payed = 0
    debt = 0

    importation_forms = Importation.objects.filter(importation_date__month=month)

    for form in importation_forms:
        total += form.total
        payed += form.payed
        debt += form.debt

    return importation_forms, total, payed, debt
