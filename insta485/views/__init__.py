"""Views, one for each Insta485 page."""
from insta485.views.index import show_index, file_url
from insta485.views.accounts import is_logged, logout, create_account, post_accounts