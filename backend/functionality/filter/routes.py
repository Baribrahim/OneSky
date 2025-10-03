from flask import render_template, Blueprint
from data_access import DataAccess

bp = Blueprint("filter", __name__, url_prefix="")

@bp.route('/filter_events', methods=['GET', 'POST'])
def filter_events():
    data_access = DataAccess()
    
    locations = data_access.get_location()
    # tags = get_tag()
    return render_template('event_page.html', locations=locations)
