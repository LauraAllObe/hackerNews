"""
This file uses pytest to test the routes.py file
"""
from hackernews import app, db
from hackernews.models import User, Vote
from hackernews.routes import fetch_news_item, get_vote_color
from hackernews.routes import get_vote_color_two, change_votes, add_user

app.testing = True
clienttwo = app.test_client()
ctx = app.app_context()
ctx.push()


def test_home_route():
    """Tests the home route.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    response = clienttwo.get('/')
    assert response.status_code == 200

def test_fetch_news_item():
    """Tests the fetch_news_item() function.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    item_id = 38157145
    result = fetch_news_item(item_id)
    assert result != "Nothing here"

def test_newsfeed_route():
    """Tests the newsfeed route.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    response = clienttwo.get('/newsfeed')
    assert response.status_code == 200
    assert response.json is not None

def test_login_route():
    """Tests the login route.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    response = clienttwo.get('/login')
    assert response.status_code == 302

def test_logout_route():
    """Tests the logout route.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    response = clienttwo.get('/logout')
    assert response.status_code == 302

def test_account_route():
    """Tests the account route.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    with app.test_request_context():
        with app.test_client() as client:
            response = client.get('/account')
            assert response.status_code == 302

def test_admin_route():
    """Tests the admin route.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    with app.test_request_context():
        with app.test_client() as client:
            response = client.get('/admin')
            assert response.status_code == 302

def test_add_user():
    """Tests the add user function.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    with app.test_request_context():
        mock_token = {
            "userinfo": {
                "email": "duplicate_admin@example.com",
                "name": "Admin User",
                "nickname": "admin_user"
            }
        }
        add_user(mock_token)
        user = User.query.filter_by(email="duplicate_admin@example.com").first()
        assert user is not None
        assert user.email == "duplicate_admin@example.com"
        assert user.name == "Admin User"
        assert user.nickname == "admin_user"
        assert user.admin is False


def test_admin_route_two():
    """Tests the admin route.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    with app.test_request_context('/admin', method='POST'):
        with app.test_client() as client:
            db.session.rollback()
            new_email = "duplicate_admin@example.com"
            response = client.post('/admin', data={"new_email": new_email})
            assert response.status_code == 302
    with app.test_request_context('/admin', method='POST'):
        with app.test_client() as client:
            response = client.post('/admin', data={"deleteAdmin": "duplicate_admin@example.com"})
            assert response.status_code == 302
    with app.test_request_context('/admin', method='POST'):
        with app.test_client() as client:
            user_to_delete = User.query.filter_by(email="duplicate_admin@example.com").first()
            if user_to_delete:
                response = client.post('/admin', data={"deleteUser": str(user_to_delete.id)})
                assert response.status_code == 302
    with app.test_request_context('/admin'):
        with app.test_client() as client:
            response = client.get('/admin')
            assert response.json is None
            db.session.rollback()

def test_execute_fetch_route():
    """Tests the execute fetch route.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    response = clienttwo.get('/execute_fetch')
    assert response.status_code == 200
    assert response.json == {"message": "OK"}

def test_callback_route():
    """Tests the callback route.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    response = clienttwo.get('/callback')
    assert response.status_code == 400

def test_change_votes():
    """Tests the change votes function.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    with app.test_request_context():
        with app.test_client() as client:
            client.get('/login')
        news_id = 38157145
        click = True
        result = change_votes(click, news_id)
        assert result is None

def test_get_vote_color():
    """Tests the get vote color function.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    with app.test_request_context():
        with app.test_client() as client:
            client.get('/login')
        news_id = 38157145
        assert get_vote_color(news_id, True, True) == "thumbs_up.png" 
        assert get_vote_color(news_id, False, True) == "#5f4747"
        assert get_vote_color(news_id, False, False) == "#5f4747"
        assert get_vote_color(news_id, True, False) == "thumbs_down.png"
        news_id = 38221121
        existing_vote = Vote.query.filter_by(news_id=news_id).first()
        assert get_vote_color_two(existing_vote, True, True) == \
                "red_thumbs_up.png"
        assert get_vote_color_two(existing_vote, False, True) == \
                "thumbs_down.png"
        assert get_vote_color_two(existing_vote, False, False) == "#5f4747"
        assert get_vote_color_two(existing_vote, True, False) == "#652525"

def test_get_vote_color_two():
    """Tests the get vote color two function.
    Args: N/A
    Kwargs: N/A
    Returns: N/A
    Raises: N/A
    """
    existing_vote = Vote(liked=True, news_id=38157145, user_id=1)
    need_image = True
    is_like = True
    result = get_vote_color_two(existing_vote, is_like, need_image)
    assert result == "red_thumbs_up.png"

ctx.pop()
