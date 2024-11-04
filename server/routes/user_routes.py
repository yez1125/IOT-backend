from flask import Blueprint, request, jsonify
from ..models.User import User

user_routes = Blueprint('user_routes', __name__)

@user_routes.route("/register", method=['POST'])
def register():
    # 存取client的request
    data = request.get_json()
    user =  User(data['username'], data['email'], data['password'])
    if user.save():
        return jsonify({"message": })