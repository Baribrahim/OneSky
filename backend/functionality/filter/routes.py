from flask import render_template
from application import app
from functionality.filter.data_access import get_location

@app.route('/filter_events', methods=['GET', 'POST'])
def filter_events():
    locations = get_location()
    # tags = get_tag()
    return render_template('event_page.html', locations=locations)