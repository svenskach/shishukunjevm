import requests
import streamlit as st
from streamlit_js_eval import streamlit_js_eval


# ============================================================
# CONFIGURATION
# ============================================================

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

BACKEND_URL = "https://evm.pythonanywhere.com"

ELECTION_ID = "school-election-2026"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title=SCHOOL_NAME,
    page_icon="🗳️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f5efe3;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    #MainMenu {
        visibility: hidden;
    }

    .school-title {
        text-align: center;
        font-size: 30px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 4px;
    }

    .school-subtitle {
        text-align: center;
        font-size: 17px;
        margin-bottom: 30px;
    }

    .success-box {
        background-color: #e9f7ed;
        border: 1px solid #8ac79a;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .success-box h3 {
        margin-top: 0;
    }

    .info-text {
        text-align: center;
        font-size: 15px;
    }

    .console-title {
        text-align: center;
        font-size: 27px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 5px;
    }

    .console-subtitle {
        text-align: center;
        margin-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# BROWSER DEVICE TOKEN
# ============================================================

device_token = streamlit_js_eval(
    js_expressions="""
    (() => {
        const key = "shishukunj_voting_device_token";

        let token = localStorage.getItem(key);

        if (!token) {
            token =
                crypto.randomUUID()
                + "-"
                + crypto.randomUUID();

            localStorage.setItem(key, token);
        }

        return token;
    })()
    """,
    want_output=True,
    key="persistent_device_token",
)


if not device_token:

    st.info("Preparing voting session...")

    st.stop()


# ============================================================
# CHECK WHETHER THIS IS /#console
# ============================================================

url_hash = streamlit_js_eval(
    js_expressions="window.location.hash",
    want_output=True,
    key="url_hash",
)


# ============================================================
# ADMIN CONSOLE
# ============================================================

if url_hash == "#console":

    st.markdown(
        f"""
        <div class="console-title">
            {SCHOOL_NAME}
        </div>

        <div class="console-subtitle">
            Voting Administration Console
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    console_password = st.text_input(
        "Console password",
        type="password",
        placeholder="Enter password",
    )

    if st.button(
        "OPEN CONSOLE",
        type="primary",
        use_container_width=True,
    ):

        if not console_password:

            st.error("Please enter the console password.")

        else:

            try:

                response = requests.post(
                    f"{BACKEND_URL}/console",
                    json={
                        "password": console_password,
                    },
                    timeout=15,
                )

                if response.status_code == 401:

                    st.error("Incorrect password.")

                elif response.status_code != 200:

                    try:
                        error_data = response.json()
                        st.error(
                            error_data.get(
                                "error",
                                "Unable to open console.",
                            )
                        )
                    except Exception:
                        st.error(
                            "Unable to open console."
                        )

                else:

                    data = response.json()

                    votes = data.get(
                        "votes",
                        [],
                    )

                    total_votes = data.get(
                        "total_votes",
                        len(votes),
                    )

                    st.success(
                        f"Console opened successfully. "
                        f"Total votes: {total_votes}"
                    )

                    if votes:

                        table_rows = []

                        for vote in votes:

                            table_rows.append(
                                {
                                    "Name":
                                        vote.get(
                                            "name",
                                            "",
                                        ),

                                    "Phone Number":
                                        vote.get(
                                            "phone_number",
                                            "",
                                        ),

                                    "Vote":
                                        vote.get(
                                            "vote",
                                            "",
                                        ),
                                }
                            )

                        st.dataframe(
                            table_rows,
                            use_container_width=True,
                            hide_index=True,
                        )

                    else:

                        st.info(
                            "No votes have been recorded yet."
                        )

            except requests.RequestException:

                st.error(
                    "Unable to contact the voting server."
                )

    st.markdown("---")

    st.caption(
        "Administrative console • "
        + ELECTION_ID
    )

    st.stop()


# ============================================================
# NORMAL VOTING PAGE
# ============================================================

st.markdown(
    f"""
    <div class="school-title">
        {SCHOOL_NAME}
    </div>

    <div class="school-subtitle">
        Voting Portal
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# BACKEND FUNCTIONS
# ============================================================

def get_vote_status():

    response = requests.post(
        f"{BACKEND_URL}/status",
        json={
            "election_id": ELECTION_ID,
            "device_token": device_token,
        },
        timeout=15,
    )

    response.raise_for_status()

    return response.json()


def submit_vote(
    name,
    phone_number,
    choice,
):

    response = requests.post(
        f"{BACKEND_URL}/vote",
        json={
            "election_id": ELECTION_ID,
            "device_token": device_token,
            "name": name,
            "phone_number": phone_number,
            "choice": choice,
        },
        timeout=15,
    )

    return response


# ============================================================
# CHECK EXISTING VOTE
# ============================================================

try:

    status_data = get_vote_status()

except requests.RequestException:

    st.error(
        "Unable to contact the voting server."
    )

    st.stop()


if status_data.get("has_voted"):

    st.markdown(
        """
        <div class="success-box">

            <h3>✓ Vote Already Recorded</h3>

            <p>
                Your vote has already been submitted
                from this browser for this election.
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
# VOTER INFORMATION
# ============================================================

st.markdown("### Voter Information")

name = st.text_input(
    "Full Name *",
    placeholder="Enter your full name",
)

phone_number = st.text_input(
    "Phone Number *",
    placeholder="Enter your phone number",
)


# ============================================================
# VOTING OPTIONS
# ============================================================

st.markdown("### Select Your Vote")

selected_option = st.radio(
    "Voting options",
    OPTIONS,
    index=None,
    label_visibility="collapsed",
)


# ============================================================
# SUBMIT
# ============================================================

if st.button(
    "SUBMIT VOTE",
    type="primary",
    use_container_width=True,
):

    # --------------------------------------------------------
    # Name validation
    # --------------------------------------------------------

    name = name.strip()

    if not name:

        st.error(
            "Please enter your name."
        )

        st.stop()


    # --------------------------------------------------------
    # Phone validation
    # --------------------------------------------------------

    phone_number = phone_number.strip()

    if not phone_number:

        st.error(
            "Please enter your phone number."
        )

        st.stop()


    # --------------------------------------------------------
    # Vote validation
    # --------------------------------------------------------

    if not selected_option:

        st.error(
            "Please select an option."
        )

        st.stop()


    if selected_option not in OPTIONS:

        st.error(
            "Invalid voting option."
        )

        st.stop()


    # --------------------------------------------------------
    # Submit to backend
    # --------------------------------------------------------

    try:

        response = submit_vote(
            name,
            phone_number,
            selected_option,
        )

        if response.status_code == 201:

            st.markdown(
                """
                <div class="success-box">

                    <h3>✓ Vote Recorded</h3>

                    <p>
                        Your vote has been successfully
                        submitted.
                    </p>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <p class="info-text">
                    A second vote from this browser
                    will not be accepted.
                </p>
                """,
                unsafe_allow_html=True,
            )

            st.stop()


        elif response.status_code == 409:

            st.error(
                "A vote has already been recorded "
                "from this browser for this election."
            )

            st.stop()


        else:

            try:

                error_data = response.json()

                error_message = error_data.get(
                    "error",
                    "The vote could not be recorded.",
                )

            except Exception:

                error_message = (
                    "The vote could not be recorded."
                )

            st.error(error_message)


    except requests.RequestException:

        st.error(
            "Unable to contact the voting server."
        )
