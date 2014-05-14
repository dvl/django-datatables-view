About
=====

django-datatables-view is a base view for handling server side processing for the awesome datatables (http://datatables.net).

django-datatables-view simplifies handling of sorting, filtering and creating JSON output, as defined at: http://datatables.net/usage/server-side

Example
=======

Example project that uses django-datatables-view is available at: https://bitbucket.org/pigletto/django-datatables-view-example/

Usage
=====

### 1. Install django-datatables-view ###
  
    pip install django-datatables-view

### 2. Edit views.py ###

_django_datatables_view_ uses **GenericViews**, so your view should just inherit from base class: **BaseDatatableView**, and override few things
(there is also a DatatableMixin - pure datatables handler that can be used with the mixins of your choice)
  These are:

  * **model** - the model that should be used to populate the datatable
  * **columns** - the columns that are going to be displayed
  * **order_columns** - list of column names used for sorting (eg. if user sorts by second column then second column name from this list will be used in order by).
  * **filter_queryset** - if you want to filter your datatable then override this method
  * **linked_columns** - defines which columns should be linked using model get_absolut_url() method.

  For more advanced customisation you might want to override:

  * **get_initial_queryset** - method that should return queryset used to populate datatable
  * **prepare_results** - this method should return list of lists (rows with columns) as needed by datatables

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

### 3. Edit urls.py ###

  Add typical django's urlconf entry:

        # ...
        url(r'^my/datatable/data/$', login_required(OrderListJson.as_view()), name='order_list_json'),
        # ....

### 4. Define HTML + JavaScript ###

Example JS:

    $(document).ready(function() {
        var oTable = $('.datatable').dataTable({
            // ...
            "bProcessing": true,
            "bServerSide": true,
            "sAjaxSource": "{% url order_list_json %}"
        });
        // ...
    });


## Another example of views.py customisation ##

    from django_datatables_view.base_datatable_view import BaseDatatableView

    class OrderListJson(BaseDatatableView):
        order_columns = ['number', 'user', 'state']

        def get_initial_queryset(self):
            # return queryset used as base for futher sorting/filtering
            # these are simply objects displayed in datatable
            # You should not filter data returned here by any filter values entered by user. This is because
            # we need some base queryset to count total number of records.
            return MyModel.objects.filter(something=self.kwargs['something'])

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
