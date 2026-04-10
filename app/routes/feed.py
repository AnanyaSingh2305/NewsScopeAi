from flask import Blueprint, jsonify, request

feed_bp = Blueprint('feed', __name__)

@feed_bp.route('/trending', methods=['GET'])
def get_trending():
    # Phase 6 stub
    return jsonify({"status": "success", "articles": []}), 200

@feed_bp.route('/feed', methods=['GET'])
def get_personal_feed():
    bias = request.args.get('bias', 'CENTER')
    return jsonify({"status": "success", "bias_filter": bias, "articles": []}), 200
