from typing import Optional


class ValidationError(Exception):
    message: Optional[str]

    def __init__(self, message=None):
        Exception.__init__(self, message)
        self.message = message


COMMAND_SYNTAX_ERROR = ValidationError(
    r"""*[ERROR]*
The correct syntax is
`/track <contract_address> <token_id>`
or
`/track <contract_address>/<token_id>`""")

ADDRESS_SYNTAX_ERROR = ValidationError(
    r"""*[ERROR]* Incorrect contract address argument\.
The contract address should have `0x` prefix\.""")

ADDRESS_LENGTH_ERROR = ValidationError(
    r"""*[ERROR]* Incorrect contract address argument\.""")

TOKEN_ERROR = ValidationError(
    r"""*[ERROR]* Incorrect token id argument\.
The token id should be integer\.""")

NOT_IN_WHITELIST_ERROR = ValidationError("*[ERROR]* Not allowed")

EXISTED_IN_TRACKING_LIST_ERROR = ValidationError("*[ERROR]* Already in tracking list")
