import re
import uuid
import base64


class ThinQMessageID(object):
    """Object that returns a new random ThinQ message ID each time it's referenced as a string"""

    def __str__(self):
        return re.sub(
            "=*$", "", base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("UTF-8")
        )
