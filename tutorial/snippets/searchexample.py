""""""
import json
import time

from flask import Blueprint, jsonify, request
from ..services import components, component_data, units
from ..helpers import cleanQueryArgs, trace

bp = Blueprint('search', __name__,
               url_prefix='/hardware/search')


def compare_values(op, value1, value2, units1, units2, debug=False):
    """ Compare two values, using the given op and provided units.
    """
    if value1 is None or value2 is None:
        trace("Value1 or Value2 are None", debug)
        return False

    try:
        u1 = units.first(name=units1)
        u2 = units.first(name=units2)

        value1 = float(value1) * (u1.conversion_to_SI if u1 else 1)
        value2 = float(value2) * (u2.conversion_to_SI if u2 else 1)
        trace("Comparing %s(%s) %s %s(%s)" %
              (value1, u1.name, op, value2, u2.name), debug)

        if op == 'gt' or op == '>':
            return value1 > value2
        elif op == 'gte' or op == '>=':
            return value1 >= value2
        elif op == 'lt' or op == '<':
            return value1 < value2
        elif op == 'lte' or op == '<=':
            return value1 <= value2
        elif op == 'ne' or op == 'neq' or op == '!=':
            return value1 != value2
        else:
            return value1 == value2
    except:
        trace("comparison error", debug)
        return False


@bp.route('/', methods=["GET", "POST"])
def search():
    """ Return list of components based upon search criteria.


    """
    start = time.clock()

    # Parse the query string
    params = cleanQueryArgs(request.args.to_dict())  \
        if request.method == 'GET' \
        else request.get_json(force=True)
    debug = params.pop('debug', False)

    trace("params = %s" % params, debug)

    ids = []        # contains ids of components garnered from component_data
    results = []    # contains components filtered by all parameters.

    # pull out the 'q' parameter.
    q = params.pop('q', "")

    # Process filters from q parameter.
    if q:

        # parse the filters using either a GET or POST request.
        filters = json.loads(
            q)['filters'] if request.method == 'GET' else q['filters']
        filter_length = len(filters)
        counter = 0

        while counter < filter_length:
            trace("counter = %s" % counter, debug)

            # find component parameters based on the name.
            comp_data = component_data.find(
                field_name=filters[counter]['name'])
            trace("found %s parameters with name '%s'" %
                  (comp_data.count(), filters[counter]['name']), debug)

            # We should do adjacent comparison if there enough filters to
            # check for and the "name" of the filter is the same as the
            # adjacent filter.
            do_adjacent_comparisons =  \
                counter + 1 < filter_length and \
                filters[counter]['name'] == filters[counter + 1]['name']

            for result in comp_data:

                # Testing a range of filters temporarily using
                # unconverted field_value. will change to
                # field_value_SI once the conversions are complete
                compare1 = compare_values(filters[counter]['op'],
                                          result.field_value,
                                          filters[counter]['value'],
                                          result.units.name if result.units else "",
                                          filters[counter]['units'])
                compare2 = compare_values(filters[counter + 1]['op'],
                                          result.field_value,
                                          filters[counter + 1]['value'],
                                          result.units.name if result.units else "",
                                          filters[counter + 1]['units']
                                          ) if do_adjacent_comparisons else True

                if compare1 and compare2:
                    ids.append(result.component_id)
                    trace("Added %s to ids from attribute id = %s" %
                          (result.component_id, result.id), debug)

            # skip to the next filter or next 2 filters.
            counter += 1
            if do_adjacent_comparisons:
                counter += 1

    # Search for components by meta parameters and by ids
    trace("ids:%s and params:%s" % (ids, params), debug)
    if len(ids) > 0 or len(params) > 0:
        query = components.find(ids=ids, **params)
        trace("sql: %s\n recordcount: %s" % (query, query.count()), debug)

        for comp in query:
            results.append(comp.to_dict({'component_type': True,
                                         'subsystem': True,
                                         'id': True,
                                         'manufacturer': True,
                                         'attributes': debug,
                                         'vendor': True}))

    return jsonify({'count':        len(results),
                    'elapsed':      time.clock() - start,
                    'searched':     results,
                    })


@bp.route('/test', methods=["GET", "POST"])
def test_search():
    """ test searching.
    """
