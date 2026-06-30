from scripts.seed_demo_users import DEMO_USERS


def test_demo_users_match_demo_auth_design() -> None:
    users_by_username = {user["username"]: user for user in DEMO_USERS}

    assert set(users_by_username) == {"admin", "user1", "user2", "user3"}
    assert users_by_username["admin"]["role"] == "admin"
    assert users_by_username["admin"]["password"] == "Admin@123"

    for username in ["user1", "user2", "user3"]:
        assert users_by_username[username]["role"] == "user"
        assert users_by_username[username]["password"] == "User@123"

