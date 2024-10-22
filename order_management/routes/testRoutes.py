from flask import Blueprint

testBlueprint = Blueprint("test",__name__)

@testBlueprint.route("/test")
def test():
    return "Hello world ;)"