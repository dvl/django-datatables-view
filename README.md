What is it?
===========

django-datatables-view is a base view for handling server side processing for the awesome datatables (http://datatables.net).

django-datatables-view simplifies handling of sorting, filtering and creating JSON output, as defined at:
http://datatables.net/usage/server-side


Usage
=====

1. pip install django-datatables-view

2. views.py:

  django_datatables_view uses GenericViews, so your view should just inherit from base class: BaseDatatableView, and override few things.
  These are:

  * order_columns - list of column names used for sorting (eg. if user sorts by second column then second column name from this list will be used in order by).
  * get_initial_queryset - method that should return queryset used to populate datatable
  * filter_queryset - if you want to filter your datatable then override this method
  * prepare_results - this method should return list of lists (rows with columns) as needed by datatables

  See example below:

    :::python

        from django_datatables_view.base_datatable_view import BaseDatatableView

        class OrderListJson(BaseDatatableView):
            # define column names that will be used in sorting
            # order is important and should be same as order of columns
            # displayed by datatables. For non sortable columns use empty
            # value like ''
            order_columns = ['number', 'user', 'state']

            def get_initial_queryset(self):
                # return queryset used as base for futher sorting/filtering
                # these are simply objects displayed in datatable
                return MyModel.objects.all()

            def filter_queryset(self, qs):
                # use request parameters to filter queryset

                # simple example:
                sSearch = self.request.POST.get('sSearch', None)
                if sSearch:
                    qs = qs.filter(name__istartswith=sSearch)

                # more advanced example
                filter_customer = self.request.POST.get('customer', None)

                if filter_customer:
                    customer_parts = filter_customer.split(' ')
                    qs_params = None
                    for part in customer_parts:
                        q = Q(customer_firstname__istartswith=part)|Q(customer_lastname__istartswith=part)
                        qs_params = qs_params | q if qs_params else q
                    qs = qs.filter(qs_params)
                return qs

            def prepare_results(self, qs):
                # prepare list with output column data
                # queryset is already paginated here
                json_data = []
                for item in qs:
                    json_data.append([
                        item.number,
                        "%s %s" % (item.customer_firstname, item.customer_lastname),
                        item.get_state_display(),
                        item.created.strftime("%Y-%m-%d %H:%M:%S"),
                        item.modified.strftime("%Y-%m-%d %H:%M:%S")
                    ])
                return json_data

3. urls.py

  Add typical django's clause:

    ::: python

        # ...
        url(r'^my/datatable/data/$', login_required(OrderListJson.as_view()), name='order_list_json'),
        # ....

4. Define HTML + JavaScript part as usual, eg:

  Example JS:

    ::: javascript

      $(document).ready(function() {
          var oTable = $('.datatable').dataTable({
              // ...
              "bProcessing": true,
              "bServerSide": true,
              "sAjaxSource": "{% url order_list_json %}"
          });
          // ...
      });
