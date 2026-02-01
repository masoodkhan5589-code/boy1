class StatusConstants:

    # =======================
    # 1️⃣ ACCOUNT STATUS
    # =======================
    ACCOUNT_LIVE = "Live"
    ACCOUNT_DISABLED = "Disabled"
    ACCOUNT_LOADED = "Account has been loaded."
    ACCOUNT_STATUS_CHECKING = "Checking account status..."
    ACCOUNT_HAS_BEEN_VERIFIED = "Account has been verified."

    # ======================
    # 2️⃣ ACCOUNT REGISTRATION
    # ======================
    GETTING_FACEBOOK_PAGE = "Opening Facebook..."
    PAGE_REDIRECTING = "Redirecting web page..."
    CONFIRMATION_CODE = "Verifying OTP code..."
    CONFIRMATION_CODE_SUCCESSFUL = "Verification successful."
    VERIFIED = "Verified"
    UNVERIFIED = "Unverified"
    RECEIVED_OTP = "Received verification code {}"
    COULD_NOT_CONFIRM_CODE = "Could not verify the code."
    COULD_NOT_RETRIEVE_CODE = "Did not receive the verification code."
    START_RECOVER_ACCOUNT = "Starting account recovery..."
    RECOVERY_SUCCESSFUL = "Password recovery request sent successfully."
    RECOVERY_FAILED = "Failed to send password recovery request."
    VERIFICATION_SENT_VIA_SMS_SUCCESSFULLY = "Verification code sent via SMS successfully."
    FAILED_TO_VERIFICATION_SENT_VIA_SMS = "Failed to send verification code."

    # ================================
    # 4️⃣ EMAIL / CONTACT INFORMATION
    # ================================
    ADD_CONTACT_FAILED = "Failed to add contact."
    ADD_CONTACT_SUCCESSFUL = "Contact added successfully."
    ADDING_NEW_CONTACT = "Adding new email..."
    COULD_NOT_GET_NEW_CONTACT = "Error: could not retrieve new contact information."
    NO_METHOD_FOR_SEND_SMS = "No method for sending messages via SMS found."


    # =================================
    # 5️⃣ IP / PROXY / DEVICE
    # =================================
    PREPARING_VIRTUAL_DEVICE_INFO = "Preparing virtual device information..."
    CHECKING_IP_ADDRESS = "Retrieving IP address..."
    COULD_NOT_GET_IP_ADDRESS = "Could not retrieve IP address."

    # =====================================
    # 6️⃣ KATANA TOKEN / ELIGIBILITY HASH
    # =====================================
    REQUIRES_FB_KATANA_TOKEN = "EAAAAU token required to perform this action."
    THE_SESSION_HAS_BEEN_INVALIDATED = "Token has expired."

    # =============================
    # 7️⃣ LOGIN / SESSION
    # =============================
    STARTING_LOGIN = "Logging in..."
    LOGIN_FAILED = "Login failed."
    LOGIN_SUCCESS = "Login successful."
    EXCEPTION_ERROR = "An exception occurred."

    # ======================
    # DONE
    # ======================
    TASK_COMPLETED = "Process completed."
    UNKNOWN = "Unknown"
