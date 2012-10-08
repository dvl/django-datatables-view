def pretty_print(qs, colname='name'):
    out = qs.values_list(colname, flat=True)
    return ', '.join(out)

def datatables_sort(request, columns):
    sortdir = request.REQUEST.get('sSortDir_0', 'asc')
    i_sort_col = request.REQUEST.get('iSortCol_0', 0)

    sdir = sortdir == 'desc' and '-' or ''

    try:
        i_sort_col = int(i_sort_col)
    except Exception:
        i_sort_col = 0
    sortcol = columns[i_sort_col]
    return ['%s%s' % (sdir, sortcol)]