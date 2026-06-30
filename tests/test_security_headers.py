from fastapi import status
import pytest

# --------- SECURITY TEST: Checks if essential security headers are present in responses ------- #

@pytest.mark.asyncio
async def test_security_headers_are_present(client):
    # 1. Make a simple request to the public root endpoint
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK

    # 2. Verify that your custom security middleware injected the headers
    assert "X-Frame-Options" in response.headers
    assert "X-Content-Type-Options" in response.headers
    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers
    assert "Referrer-Policy" in response.headers

    # 3. Verify their exact strict values configured in main.py
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
    
    # Use 'in' instead of '==' to allow for additional policy rules (like script-src, style-src)
    assert "default-src 'self';" in response.headers["Content-Security-Policy"]
    
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"