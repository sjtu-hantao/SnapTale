from http import HTTPStatus
import dashscope
import time
import os
from pathlib import Path
from dotenv import load_dotenv
import base64, uuid, io, json
from passlib.context import CryptContext
import requests
from typing import List, Dict, Any, Union

load_dotenv()

dashscope.api_key = os.environ.get("QWEN_API_KEY")


def describe_image(image_url):
    """
    Describes the content of an image using a multi-modal conversation model.

    Args:
        image_url (str): The URL of the image to be described.HHHHHHHHHH

    Returns:
        str or None: The description of the image, or None if no description is available.
    """
    messages = [
        {
            "role": "user",
            "content": [
                {"image": image_url},
                {"text": "Please describe what you see in this image."},
            ],
        }
    ]

    response = dashscope.MultiModalConversation.call(
        model="qwen-vl-plus", messages=messages
    )
    # Extracting the description
    if response["output"]["choices"][0]["message"]["content"]:
        description = response["output"]["choices"][0]["message"]["content"][0]["text"]
        return description
    else:
        return "Failed to describe image."

def hash_pwd(password: str) -> str:
    """
    Hashes a password using the sha256_crypt algorithm.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
    return pwd_context.hash(password)


# TODO: Future feature: customizable system prompts
async def generate_journal_func(entries: List[Dict[str, Any]]) -> Union[str, str]:
    """
    Generates a journal based on a list of entries.

    Args:
        entries (List[Dict[str, Any]]): A list of journal entries, sorted by creation date.
        entries[0] (Dict[str, Any]): A journal entry.
        entries[0]["time_created"] (str): The creation time of the entry.
        entries[0]["type"] (str): The type of the entry: "text" or "image".
        entries[0]["content"] (str): The content of the entry: text or image description.
        entries[0]["url"] (str): The url of the image.
    Returns:
        Union[str, str]: The generated title and content of the journal, or an error message.
    """

    message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": f"""
                I'm a 24-year-old girl who loves to write journals and diaries. I have prepared a draft of journal that I would like to rewrite. Please follow the rules below to generate the journal.

                The journal:
                - Answers some of the following questions "What happened today?", "What did I experience today?", "What did I feel today?", "What did I learn today?", "What did I think today?"
                - Start from title directly, DON'T append any additional introduction
                - Should be formatted in markdown, every detail in the draft should be referenced
                - All images should be included in the journal, in form of '![](url)'
                - Should connect all the entries in a coherent way, can be separated into less than 3 paragraphs
                - Should be written in first person and in high school level English
                - Should be at least 100 words long
                - Should reference the timestamps but do not need to include them in the final journal
                - Is allowed to be creative in wording but should not change the meaning of the entries
                - Is allowed to use emojis and other expressive elements if needed
                - Should include a title that is creative and relevant to the content

                Here are the entries:

                {entries}""",
                            }
                        ],
                    }
    messages = [message]
    response = dashscope.Generation.call(model="qwen-plus", messages=messages, temperature=0.5, top_p=0.95, top_k=50)
    if response["output"]:
        journal = response["output"]["text"]
        title, journal = get_title_from_journal(journal)
        return title, journal
    else:
        return "Failed Entry", "Failed to generate journal."
    
    
def get_title_from_journal(journal: str) -> Union[str, str]:
    title = ""
    idx = journal.find("#")
    # remove introduction before the first #
    if idx != -1:
        journal = journal[idx:]
    
    title = journal.split("\n")[0].strip("#")
    return title, journal

