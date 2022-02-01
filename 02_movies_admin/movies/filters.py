from django.contrib.admin.filters import (AllValuesFieldListFilter,
                                          RelatedFieldListFilter)


class DropdownFilter(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'


class RelatedDropdownFilter(RelatedFieldListFilter):
    template = 'admin/dropdown_filter.html'
