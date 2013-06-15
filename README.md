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

  * model - the model that should be used to populate the datatable
  * columns - the columns that are going to be displayed
  * order_columns - list of column names used for sorting (eg. if user sorts by second column then second column name from this list will be used in order by).
  * filter_queryset - if you want to filter your datatable then override this method

  See example below:

    :::python

        from django_datatables_view.base_datatable_view import BaseDatatableView

        class OrderListJson(BaseDatatableView):
            # The model we're going to show
            model = MyModel

            # define the columns that will be returned
            columns = ['number', 'user', 'state', 'created', 'modified']

            # define column names that will be used in sorting
            # order is important and should be same as order of columns
            # displayed by datatables. For non sortable columns use empty
            # value like ''
            order_columns = ['number', 'user', 'state']

            # set max limit of records returned, this is used to protect our site if someone tries to attack our site
            # and make it return huge amount of data
            max_display_length = 500

            def render_column(self, row, column):
                # We want to render user as a custom column
                if column == 'user':
                    return '%s %s' % (row.customer_firstname, row.customer_lastname)
                else:
                    return super(OrderListJson, self).render_column(row, column)

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
