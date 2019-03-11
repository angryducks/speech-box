# -*- coding: utf-8 -*-
"""
Example code to call Rosette API to get entities from a piece of text.
"""
from __future__ import print_function

import argparse
import json
import os

from rosette.api import API, DocumentParameters, RosetteException


def entities(text, alt_url='https://api.rosette.com/rest/v1/'):
    """ Run the example """
    # Create an API instance
    key = 'Your rosette api key'  # Create your api key though url https://www.rosette.com/
    api = API(user_key=key, service_url=alt_url)

    params = DocumentParameters()
    params["content"] = text
    params["genre"] = "social-media"
    try:
        return api.entities(params)
    except RosetteException as exception:
        print(exception)


if __name__ == '__main__':
    RESULT = entities()
    # print(json.dumps(RESULT, indent=2, ensure_ascii=False, sort_keys=True).encode("utf8"))
    for i in range(len(RESULT['entities'])):
        print(RESULT['entities'][i]['mention'])

