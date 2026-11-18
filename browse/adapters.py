from allauth.account.adapter import DefaultAccountAdapter


class ApprovalAccountAdapter(DefaultAccountAdapter):
    error_messages = {
        **DefaultAccountAdapter.error_messages,
        "username_password_mismatch": (
            "Login failed. The inserted credentials may be incorrect. Otherwise, if you "
            "confirmed your email, your account may still be awaiting administrator approval."
            " If this is taking too long, please contact LiteBIRD IMo team directly."
        ),
        "email_password_mismatch": (
            "Login failed. The inserted credentials may be incorrect. Otherwise, if you "
            "confirmed your email, your account may still be awaiting administrator approval."
            " If this is taking too long, please contact LiteBIRD IMo team directly."
        ),
    }
