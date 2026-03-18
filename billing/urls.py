from django.urls import path

from . import views
app_name = "billing"

urlpatterns = [
    path("", views.index, name="index"),
    path("invoices/", views.displayInvoice, name="display_invoices"),
    # path("invoices/<int:invoice_id>/", views.displayInvoiceDetail, name="invoice_detail"),
    path("invoices/<int:invoice_id>/", views.DisplayInvoiceView, name="invoice_detail")
]
