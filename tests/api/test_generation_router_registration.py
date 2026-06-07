from apps.api.main import app


def test_generation_routes_are_registered() -> None:
    route_paths = {
        route.path
        for route in app.routes
    }

    assert "/generation/questions/preview" in route_paths
    assert "/generation/questions/save" in route_paths