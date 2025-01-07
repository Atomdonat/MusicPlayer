from selenium.common.exceptions import TimeoutException
from code_backend.shared_config import *
from code_backend.secondary_methods import print_error, update_env_key


# mps: 1
def request_regular_token() -> None:
    """
    Request an access token, using the Authorization Code Flow tutorial and cache it in the .env file. If Spotify credentials are found in .env file, the script runs the login automated. Else User interaction is needed.
    Official API Documentation: https://developer.spotify.com/documentation/web-api/tutorials/code-flow
    :return: caches token in .env
    """

    app = Flask(__name__)

    def generate_random_string(length):
        """Generate a random string of fixed length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @app.route('/login')
    def login():
        state = generate_random_string(16)

        query_params = {
            'response_type': 'code',
            'client_id': CLIENT_ID,
            'scope': SCOPES,
            'redirect_uri': REDIRECT_URI,
            'state': state
        }

        auth_url = 'https://accounts.spotify.com/authorize?' + urlencode(query_params)
        return redirect(auth_url)

    @app.route('/')
    def callback():
        # Extract the 'code' and 'state' parameters from the URL
        code = request.args.get('code')
        state = request.args.get('state')

        if state is None:
            error_query = urlencode({'error': 'state_mismatch'})
            return redirect(f'/#{error_query}')

        # Prepare the request for token exchange
        token_url = 'https://accounts.spotify.com/api/token'
        auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_header}'
        }
        data = {
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }

        # Exchange the authorization code for an access token
        response = requests.post(token_url, headers=headers, data=data)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return f"Error: {response.text}", response.status_code

    def run_flask_app():
        """Run Flask app in a separate thread."""
        app.run(port=8080, debug=True, use_reloader=False)

    def automated_request_handling(use_credentials=False):
        wait_timeout = 120 # seconds

        driver = webdriver.Firefox()
        driver.implicitly_wait(WAIT_TIME)
        try:
            driver.get("http://localhost:8080/login")
            if use_credentials:
                driver.find_element("id", "login-username").send_keys(SPOTIFY_USERNAME)
                driver.find_element("id", "login-password").send_keys(SPOTIFY_PASSWORD)
                driver.find_element("id", "login-button").click()


            # else: login manually while script waits up to 2 min
            WebDriverWait(driver, wait_timeout).until(
                lambda d: d.current_url.startswith("http://localhost:8080/?code=")
            )

            with open(ROOT_DIR_PATH + "/code_backend/testing/tmp.html", "w") as file:
                file.write(driver.page_source)

            raw_data_tab = driver.find_element(By.ID, 'rawdata-tab')
            raw_data_tab.click()

            # Allow time for content to load
            time.sleep(1)

            # Locate the content within the "Raw Data" panel
            token_data = json.loads(driver.find_element(By.TAG_NAME, 'pre').text)
            relevant_data = {
                'access_token': token_data['access_token'],
                'token_type': 'Bearer',
                'expires': int(time.time()) + token_data['expires_in']
            }
            update_env_key("EXTENDED_TOKEN", json.dumps(relevant_data))
            update_env_key("REFRESH_TOKEN", json.dumps({"refresh_token": token_data['refresh_token']}))

        except TimeoutException:
            print_error(
                error_message="TimeoutException: The timeout occurred while trying to login.",
                more_infos="Either the credentials are incorrect or the user has not logged in. \n  - Check your credentials in .env (if stored there)\n  - if script aborted before finishing to enter credentials increment wait_timeout",
                exit_code=1
            )

        except Exception as error:
            print_error(
                error_message=error,
                more_infos=None,
                exit_code=1
            )

        finally:
            driver.close()

    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # Give Flask a moment to start
    time.sleep(1)

    # Run Selenium in the main thread
    automated_request_handling(use_credentials=(len(SPOTIFY_USERNAME) > 0 and len(SPOTIFY_PASSWORD) > 0))


# mps: 1
def renew_regular_token():
    """"""
    print(int(time.time()))
    print(json.loads(os.getenv("REGULAR_TOKEN"))['expires'])
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body_data = {
        'grant_type': 'client_credentials',
        'refresh_token': json.loads(os.getenv("REFRESH_TOKEN"))['refresh_token'],
        'client_id': CLIENT_ID,
    }

    # response = requests.post(
    #     url=url,
    #     headers=headers,
    #     data=body_data
    # )
    # print(response.status_code)
    # update_env_key("REFRESH_TOKEN", json.dumps(response.json()))



if __name__ == "__main__":
    """"""
    request_regular_token()