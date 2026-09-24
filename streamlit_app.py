import requests
import streamlit as st
from streamlit_js_eval import streamlit_js_eval


# ============================================================
#                    ELECTION CONFIGURATION
# ============================================================
#
# CHANGE THESE FOUR VALUES ONLY when changing the choices.
#
# You can use candidate names, houses, parties, options, etc.
#

OPTION_1 = "Option A"
OPTION_2 = "Option B"
OPTION_3 = "Option C"
OPTION_4 = "Option D"

OPTIONS = [
    OPTION_1,
    OPTION_2,
    OPTION_3,
    OPTION_4,
]

SCHOOL_NAME = "THE SHISHUKUNJ INTERNATIONAL SCHOOL"

# PythonAnywhere backend
BACKEND_URL = "https://evm.pythonanywhere.com"

# Give every election/poll its own ID.
# Change this when starting a completely new election.
ELECTION_ID = "school-election-2026"


# ============================================================
#                        PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title=SCHOOL_NAME,
    page_icon="🗳️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
#                         STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* Main beige background */
    [data-testid="stAppViewContainer"] {
        background-color: #F3EBDD;
    }

    [data-testid="stHeader"] {
        background-color: #F3EBDD;
    }

    /* Remove normal Streamlit decoration */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    /* Keep the voting application relatively narrow */
    .block-container {
        max-width: 760px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* School name */
    .school-title {
        text-align: center;
        color: #302820;
        font-family: Georgia, "Times New Roman", serif;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        line-height: 1.25;
        margin-bottom: 0.5rem;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #75695D;
        font-family: Arial, sans-serif;
        font-size: 1rem;
        margin-bottom: 2.5rem;
    }

    /* Information text */
    .info-text {
        text-align: center;
        color: #75695D;
        font-size: 0.9rem;
    }

    /* Success message */
    .success-box {
        background-color: #E8F3E8;
        border: 1px solid #B9D5B9;
        color: #315A31;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
#                    PERSISTENT BROWSER TOKEN
# ============================================================
#
# This is NOT an HWID.
#
# It creates a random identifier and stores it in the
# browser's localStorage.
#
# Normal browser:
#     token persists
#
# Incognito:
#     normally gets a different storage context
#
# Clear site data:
#     token is removed
#
# Different browser:
#     different token
#
# The backend never stores the raw token. It stores a hash.
# ============================================================

DEVICE_TOKEN_JS = """
(() => {

    const key = "shishukunj_voting_device_token";

    let token = localStorage.getItem(key);

    if (!token) {

        token =
            crypto.randomUUID() +
            "-" +
            crypto.randomUUID();

        localStorage.setItem(key, token);
    }

    return token;

})()
"""


device_token = streamlit_js_eval(
    js_expressions=DEVICE_TOKEN_JS,
    want_output=True,
    key="persistent_device_token",
)


# The JavaScript component may require a short moment to
# return the token.

if not device_token:

    st.markdown(
        """
        <p class="info-text">
            Preparing voting session...
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


# ============================================================
#                     BACKEND FUNCTIONS
# ============================================================

def get_vote_status():
    """
    Ask the PythonAnywhere backend whether this browser
    has already voted in this election.
    """

    try:

        response = requests.post(
            f"{BACKEND_URL}/status",

            json={
                "election_id": ELECTION_ID,
                "device_token": device_token,
            },

            timeout=10,
        )

        if response.status_code != 200:

            return None, "Unable to contact the voting server."

        data = response.json()

        return data.get("has_voted", False), None

    except requests.RequestException:

        return None, "Unable to contact the voting server."


def submit_vote(choice):
    """
    Submit the selected option to the backend.
    """

    try:

        response = requests.post(
            f"{BACKEND_URL}/vote",

            json={
                "election_id": ELECTION_ID,
                "device_token": device_token,
                "choice": choice,
            },

            timeout=15,
        )

        try:
            data = response.json()

        except ValueError:
            return False, "The server returned an invalid response."

        if response.status_code == 201:

            return (
                True,
                data.get(
                    "message",
                    "Vote recorded successfully."
                ),
            )

        return (
            False,
            data.get(
                "error",
                "Vote could not be recorded."
            ),
        )

    except requests.RequestException:

        return False, "Unable to contact the voting server."


# ============================================================
#                          HEADER
# ============================================================

st.markdown(
    f"""
    <div class="school-title">
        {SCHOOL_NAME}
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        Voting Portal
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
#                    CHECK WHETHER ALREADY VOTED
# ============================================================

has_voted, status_error = get_vote_status()


if status_error:

    st.error(status_error)

    st.stop()


if has_voted:

    st.markdown(
        """
        <div class="success-box">

            <h3>Vote Already Recorded</h3>

            <p>
                A vote has already been submitted from
                this browser for this election.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p class="info-text">
            Thank you for participating.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


# ============================================================
#                         VOTING UI
# ============================================================

st.subheader("Cast your vote")

st.write("Select one option:")


selected_option = st.radio(
    "Voting options",
    OPTIONS,
    index=None,
    label_visibility="collapsed",
)


st.write("")


# ============================================================
#                       SUBMIT BUTTON
# ============================================================

vote_button = st.button(
    "SUBMIT VOTE",
    type="primary",
    use_container_width=True,
)


if vote_button:

    # --------------------------------------------------------
    # Make sure an option was selected
    # --------------------------------------------------------

    if selected_option is None:

        st.warning(
            "Please select an option before voting."
        )

        st.stop()


    # --------------------------------------------------------
    # Make sure the selected option actually belongs to the
    # configured list.
    # --------------------------------------------------------

    if selected_option not in OPTIONS:

        st.error("Invalid option.")

        st.stop()


    # --------------------------------------------------------
    # Send vote to backend
    # --------------------------------------------------------

    with st.spinner("Submitting your vote..."):

        success, message = submit_vote(
            selected_option
        )


    # --------------------------------------------------------
    # Successful vote
    # --------------------------------------------------------

    if success:

        st.markdown(
            """
            <div class="success-box">

                <h3>✓ Vote Recorded</h3>

                <p>
                    Your vote has been successfully submitted.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <p class="info-text">
                A second vote cannot be submitted from
                this browser for this election.
            </p>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # Failed vote
    # --------------------------------------------------------

    else:

        st.error(message)
