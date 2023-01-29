"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.accounts import login_page, logout, create_page, edit_page, delete_page, password_page, post_accounts
from insta485.views.posts import post_page
from insta485.views.followers import show_followers
from insta485.views.following import show_following