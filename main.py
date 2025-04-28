from fastapi import FastAPI
from pydantic import BaseModel
from playwright.sync_api import sync_playwright

# Create FastAPI app
app = FastAPI()

# Request model
class PostcodeRequest(BaseModel):
    postcode: str

# Function to check broadband using Playwright
def check_broadband_availability(postcode: str) -> dict:
    with sync_playwright() as p:
        # Important: use --no-sandbox for Render deployment
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        try:
            page.goto("https://poptelecom.co.uk")

            # Enter postcode
            page.fill('input[name="postcode"]', postcode)
            page.click("text=Check Availability")
            page.wait_for_timeout(5000)  # wait 5 seconds

            # Capture details
            expected_speed = page.inner_text(".speed-value")
            upload_speed = page.inner_text(".upload-speed-value")
            price = page.inner_text(".price")

            browser.close()

            return {
                "postcode": postcode,
                "expected_speed": expected_speed,
                "upload_speed": upload_speed,
                "price": price
            }
        except Exception as e:
            browser.close()
            return {"error": str(e)}

# FastAPI Endpoint
@app.post("/check_broadband")
def check_broadband(request: PostcodeRequest):
    return check_broadband_availability(request.postcode)
