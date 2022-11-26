import logging
import requests

from typing import Any, Dict, List, Optional

from config import gettext as _


_API_URL = 'https://api.github.com/repos/<user>/<repo>/commits?path=<path>'
_RAW_FILE_URL = 'https://raw.githubusercontent.com/<user>/<repo>/<path>'


def get_file_commits(user: str, repo: str, path: str) -> List[Dict[Any, Any]]:
    """
    Get commits data from GitHub API for specific file.

    :param user: GitHub user or organization
    :param repo: GitHub repository name
    :param path: filepath from root in the repository
    :return: list of commits data or empty list if any error
    """
    try:
        url = _API_URL\
            .replace('<user>', user) \
            .replace('<repo>', repo) \
            .replace('<path>', path)
        return requests.get(url).json()

    except (IOError, requests.JSONDecodeError):
        logging.exception(_('Error with downloading data from GitHub API!'))
        return []


def get_latest_commit_date(commits_data: List[Dict[Any, Any]]) -> str:
    """
    :return: date (as GitHub date str format) or empty string if no data
    """
    try:
        return commits_data[0]['commit']['committer']['date']
    except (IndexError, KeyError):
        logging.exception(_('Error with parsing data from GitHub API!'))
        return ''


def download_file(user: str, repo: str, path: str) -> Optional[str]:
    try:
        url = _RAW_FILE_URL\
            .replace('<user>', user) \
            .replace('<repo>', repo) \
            .replace('<path>', path)
        print(url)
        response = requests.get(url)
        if response.status_code != 200:
            logging.exception(_(
                'Incorrect status code at downloading github file: {}'.format(
                    response.status_code
                ))
            )

            return None

        return response.text

    except IOError:
        logging.exception(_('Error with downloading raw data from GitHub!'))
        return None
