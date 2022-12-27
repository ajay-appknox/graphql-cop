"""Constants for grapql-cop."""
from version import VERSION

HEADERS = {
    'User-Agent':'graphql-cop/{}'.format(VERSION),
}
SAVE_RESULTS = False


def save_result(file_name, file_content):
    with open("/tmp/graphql_cop/" + file_name, "w") as fd:
        fd.write(file_content)