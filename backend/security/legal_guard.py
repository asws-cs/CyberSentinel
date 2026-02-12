from fastapi import Header, HTTPException, status

LEGAL_DISCLAIMER = """
**IMPORTANT: LEGAL & ETHICAL USE POLICY**

CyberSentinel is a powerful security tool intended for authorized and ethical use only. 
By using the 'offensive' scanning features of this tool, you acknowledge and agree to the following:

1.  **Authorization**: You have explicit, written permission from the owner of the target system to perform these tests.
2.  **Responsibility**: You are solely responsible for your actions and any consequences that may arise from the use of this tool. The creators and distributors of CyberSentinel are not liable for any damages or legal issues.
3.  **Compliance**: You will comply with all applicable local, state, national, and international laws regarding cybersecurity and penetration testing.
4.  **No Harm**: You will not use this tool to cause harm, disrupt services, or access data without authorization.

Running offensive scans without proper authorization is illegal and unethical. 
"""

def get_legal_disclaimer_text() -> str:
    """
    Returns the official legal disclaimer text.
    """
    return LEGAL_DISCLAIMER

class LegalAcceptance:
    """
    FastAPI dependency to check for the 'X-Legal-Accepted' header.
    
    This header must be present and set to 'true' to proceed with an
    operation that requires legal and ethical consent.
    """
    def __init__(self, required: bool = True):
        self.required = required

    async def __call__(self, x_legal_accepted: str | None = Header(None)):
        if self.required:
            if not x_legal_accepted or x_legal_accepted.lower() != "true":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "message": "Offensive scanning requires legal acceptance. "
                                   "Set the 'X-Legal-Accepted' header to 'true'.",
                        "disclaimer": LEGAL_DISCLAIMER,
                    },
                )

# Pre-configured dependency instances for ease of use
require_legal_acceptance = LegalAcceptance(required=True)
optional_legal_acceptance = LegalAcceptance(required=False)
