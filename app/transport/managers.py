from django.db import models

class CompanyDetailsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()\
            .prefetch_related(
                'company_numbers'
            )