
import sys

from google.oauth2 import service_account
import setting
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types


def get_native_encoding_type():
    """Returns the encoding type that matches Python's native strings."""
    if sys.maxunicode == 65535:
        return 'UTF16'
    else:
        return 'UTF32'


def analyze_entities(text, encoding='UTF32'):
    credentials = service_account.Credentials.from_service_account_file(
    setting.GOOGLE_API)
    credentials = credentials.with_scopes(
        ['https://www.googleapis.com/auth/cloud-platform'])
    client = language.LanguageServiceClient(credentials=credentials)

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects entities in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    entities = client.analyze_entities(document).entities

    return entities


if __name__ == '__main__':
    text = "The main content of today's meeting is to determine the solution, Tom will eventually release the final version tomorrow."
    e_result = analyze_entities(text, get_native_encoding_type())
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')
    for entity in e_result:
        if entity_type[entity.type] == "PERSON" or entity_type[entity.type] == "EVENT":
            print(type(entity.name))
            print(entity.name)
        # print(entity_type[entity.type])


