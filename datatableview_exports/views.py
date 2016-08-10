from django.views.generic import ListView, TemplateView
from django.views.generic.list import MultipleObjectMixin
from django.http import HttpResponse
from django.conf import settings
from datatableview.views import DatatableMixin as dt_mixin
from .datatables import Datatable
import csv


class DatatableCSVResponseMixin(object):
    def get(self, request, *args, **kwargs):
        """
        Detects CSV in get params access and returns appropriate serialized data.  Normal access to the view is
        unmodified.
        """
        if request.GET.get('format') == 'csv':
            return self.get_csv(request, *args, **kwargs)
        return super(DatatableCSVResponseMixin, self).get(request, *args, **kwargs)

    # Response generation
    def get_csv_response_object(self, datatable):
        """
        Returns the JSON-compatible dictionary that will be serialized for an AJAX response.

        The value names are in the form "s~" for strings, "i~" for integers, and "a~" for arrays,
        if you're unfamiliar with the old C-style jargon used in dataTables.js.  "aa~" means
        "array of arrays".  In some instances, the author uses "ao~" for "array of objects", an
        object being a javascript dictionary.
        """
        datatable.populate_records()
        response_data = datatable.get_all_records()
        return response_data


class DatatableMixin(DatatableCSVResponseMixin, dt_mixin):
    datatable_class = Datatable

    # CSV response handler
    def get_csv(self, request, *args, **kwargs):
        """ Called in place of normal ``get()`` when accessed via GET. """

        datatable = self.get_datatable()
        datatable.configure()
        response_data = self.get_csv_response_object(datatable)
        response = HttpResponse(content_type='text/plain')

        writer = csv.DictWriter(response, response_data[0].keys(), quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(response_data)

        return response


class DatatableView(DatatableMixin, ListView):
    """ Implements :py:class:`DatatableMixin` and the standard Django ``ListView``. """
