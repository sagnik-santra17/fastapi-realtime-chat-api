from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app


def test_lifespan_starts_redis_worker():

    # Creating a fake version of the background worker function
    with patch("app.main.live_messages") as mock_live_messages:

        # Using 'with TestClient' automatically triggers the startup lifespan lines
        with TestClient(app):
            # The moment we enter this block, the server 'starts up'
            pass
            # The moment we exit the block, the server 'shuts down'

    # This proves that FastAPI actually called the worker task during startup
    mock_live_messages.assert_called_once()