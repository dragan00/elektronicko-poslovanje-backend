from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('countries', views.CountryViewSet)
router.register('cities', views.CityViewSet)
router.register('zip_codes', views.ZipCodeViewSet)


urlpatterns = [
    path('test/', views.TestApiView.as_view()),
    path('prepare/', views.PrepareApiView.as_view()),
    # path('cities/', views.CityApiView.as_view()),
    # path('zip_codes/', views.ZipCodeApiView.as_view()),
    path('get_my_cargo/', views.GetMyCargoApiView.as_view()),
    path('get_my_loading_spaces/', views.GetMyLoadingSpacesApiView.as_view()),
    path('get_my_stocks/', views.GetMyStocksApiView.as_view()),
    path('auctions/', views.AuctionApiView.as_view()),
    path('cargo/', views.CargoApiView.as_view()),
    path('cargo/<cargo_id>', views.CargoApiView.as_view()),
    path('cargo/<cargo_id>/', views.CargoApiView.as_view()),
    path('cargo/<pk>/close/', views.CloseCargoApiView.as_view()),
    path('loading_space/', views.LoadingSpaceApiView.as_view()),
    path('loading_space/<pk>', views.LoadingSpaceApiView.as_view()),
    path('loading_space/<pk>/', views.LoadingSpaceApiView.as_view()),
    path('loading_space/<pk>/close/', views.CloseLoadingSpaceApiView.as_view()),
    path('stock/', views.StockApiView.as_view()),
    path('stock/<pk>', views.StockApiView.as_view()),
    path('stock/<pk>/', views.StockApiView.as_view()),
    path('stock/<pk>/close/', views.CloseStockApiView.as_view()),
    path('stock/<pk>/images/', views.StockImageApiView.as_view()),
    path('stock/<pk>/images/<image_id>/remove/', views.RemoveStockImageApiView.as_view()),
    path('companies/', views.CompanyApiView.as_view()),
    path('companies/<pk>', views.CompanyApiView.as_view()),
    path('companies/<pk>/', views.CompanyApiView.as_view()),
    path('companies/<pk>/documents/', views.CompanyDocumentApiView.as_view()),
    path('companies/<pk>/documents/<document_id>/remove/', views.RemoveCompanyDocumentApiView.as_view()),
    path('company_avatar/', views.CompanyAvatarApiView.as_view()),
    path('block_company/', views.BlockCompanyApiView.as_view()),
    path('panes/', views.PanesApiView.as_view()),
    path('confirm_company/', views.ConfirmCompanyApiView.as_view()),
    path('companies_to_confirm/', views.CompaniesToConfirmApiView.as_view()),
    path('basic_backoffice_info/', views.BasicBackofficeInfoApiView.as_view()),
    path('first_page_data/', views.FirstPageApiView.as_view()),
    path('', include(router.urls)),
    # path('register/', views.AccountCreate.as_view()),
]
