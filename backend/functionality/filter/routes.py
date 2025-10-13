from flask import render_template, Blueprint, request
from data_access import DataAccess

bp = Blueprint("filter", __name__, url_prefix="")

@bp.route('/filter_events', methods=['GET', 'POST'])
def filter_events():
    data_access = DataAccess()
    locations = data_access.get_location()
    return render_template('event_page.html', locations=locations, events=[])

@bp.route('/events', methods=['GET'])
def get_events():
    location = request.args.get('location')
    data_access = DataAccess()
    events = data_access.get_all_events(location)
    locations = data_access.get_location()
    return render_template('event_page.html', events=events, locations=locations)

@bp.route('/search', methods=['GET'])
def search_events():
    keyword = request.args.get('keyword')
    location = request.args.get('location')
    date = request.args.get('date')

    data_access = DataAccess()
    events = data_access.search_events(keyword, location, date)
    locations = data_access.get_location()
    return render_template('event_page.html', events=events, locations=locations)

