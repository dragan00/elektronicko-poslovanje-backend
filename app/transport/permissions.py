from helpers.global_helper.exceptions import api_exc
from .models import Company, Stock, StockImage, Cargo, LoadingSpace
from .constants import ACTIVE, NEED_CONFIRM, REJECTED, CLOSED
from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, NotFound

def can_view_company_details(company_id, user):
    if user.company_id == company_id:
        return True
    try:
        company = Company.objects.get(id=company_id)
    except Exception as e:
        print(str(e))
        raise api_exc(str(e), 404)

    if company.status in [NEED_CONFIRM, REJECTED] and not user.is_admin:
        raise api_exc("Permission Denied!", 403)

    return True

def can_upload_stock_images(stock_id, user):
    stock = get_object_or_404(Stock, id=stock_id)
    print(stock.created_by.company_id)
    print(user.company_id)
    if stock.company_id != user.company_id:
        raise PermissionDenied()
    return True

def can_remove_stock_image(image_id, stock_id, user):
    image = get_object_or_404(StockImage, id=image_id, is_active=True)
    if image.stock_id != int(stock_id):
        raise NotFound
    if image.stock.company_id != user.company_id:
        raise PermissionDenied()
    return True

def can_view_cargo_details(cargo_id, user):
    cargo = get_object_or_404(Cargo, id=cargo_id)
    if cargo.status == CLOSED:
        if cargo.company_id != user.company_id:
            raise PermissionDenied()
    return True

def can_view_loading_space_details(ls_id, user):
    ls = get_object_or_404(LoadingSpace, id=ls_id)
    if ls.status == CLOSED:
        if ls.company_id != user.company_id:
            raise PermissionDenied()
    return True

def can_view_stock_details(stock_id, user):
    stock = get_object_or_404(Stock, id=stock_id)
    if stock.status == CLOSED:
        if stock.company_id != user.company_id:
            raise PermissionDenied()
    return True