from flask import Blueprint, jsonify

from libs.lib import get_nat_types

faa_blueprint = Blueprint('faa', __name__)


@faa_blueprint.route('/data/nat/<aircraft>', methods=['GET'])
def _get_aircraft_nat(aircraft):
    nat_types = get_nat_types(aircraft)
    return jsonify(nat_types)
