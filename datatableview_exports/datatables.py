from datatableview.datatables import Datatable as dt
from datatableview.exceptions import SkipRecord
import six


class Datatable(dt):
    def get_all_records(self):
        """
        Calls :py:meth:`.populate_records` to apply searches and sorting to the object list, then
        extracts the applicate page of results, calling :py:meth:`.get_record_data` for each result
        in the page.

        Returns the final list of processed results.
        """
        if not hasattr(self, '_records'):
            self.populate_records()

        page_data = []
        for obj in self._records:
            try:
                record_data = self.get_all_record_data(obj)
            except SkipRecord:
                pass
            else:
                page_data.append(record_data)
        return page_data

    def get_all_record_data(self, obj):
        """
        Returns a dict of column data that will be given to the view for final serialization.  The
        key names in this dict are not finalized at this stage, but all of the data is present.

        Each column is consulted for its value (computed based on its
        :py:attr:`~datatableview.columns.Column.sources` applied against the given ``obj`` instance)
        and then sent to the column's :py:attr:`~datatableview.columns.Column.processor` function.
        """

        preloaded_kwargs = self.preload_record_data(obj)
        data = {
            # 'pk': self.get_object_pk(obj),
            # '_extra_data': self.get_extra_record_data(obj),
        }
        for i, (name, column) in enumerate(self.columns.items()):
            kwargs = dict(column.get_processor_kwargs(**preloaded_kwargs), **{
                'datatable': self,
                'view': self.view,
                'field_name': column.name,
            })
            value = self.get_column_value(obj, column, **kwargs)
            processor = self.get_processor_method(column, i)
            # if processor:
            #     value = processor(obj, default_value=value[0], rich_value=value[1], **kwargs)

            # A 2-tuple at this stage has presumably served its purpose in the processor callback,
            # so we convert it to its "rich" value for display purposes.
            if isinstance(value, (tuple, list)):
                value = value[1]

            if six.PY2 and isinstance(value, str):  # not unicode
                value = value.decode('utf-8')
            data[name] = six.text_type(value)
        return data
