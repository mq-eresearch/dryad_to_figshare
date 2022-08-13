#!/usr/bin/env python3
"""
Harvesting of Dryad-based MQ datasets into json file
"""

__author__ = "Gerry Devine"
__version__ = "0.1.0"
__license__ = "MIT"


# Imports
import requests
import json
import re
import config


# SETTINGS
BASE_URL = "https://api.figsh.com/v2"  # Staging instance
ROR = "01sf06y89"  # from https://ror.org
LICENSE_ID = 2  # ID of the relevant license in the figshare instance
GROUP_ID = 39389  # Figshare data group
CATEGORIES = [26209]  # List of categories under which to upload dataset
ADD_CUSTOM = True  # Boolean for whether to add custom metadata fields

# API Token should be retrieved from a seperate config file (config.py)
TOKEN = config.TOKEN


def generate_search_url(page_num, per_page):
    """
    Generate a URL string for Dryad search endpoint using page number and per_page
    """

    return f"https://datadryad.org/api/v2/search?affiliation=https%3A%2F%2Fror.org%2F{ROR}&page={page_num}&per_page={per_page}"


def validate_record(dryad_record):
    """
    Validate that the record is okay for upload to the RDR
    """

    if dryad_record["license"] != "https://creativecommons.org/publicdomain/zero/1.0/":
        print(dryad_record["title"])
        print("The license type for this record is not recognised")
        return False

    if dryad_record["visibility"] != "public":
        print(dryad_record["title"])
        print("This record is not marked as public visibility")
        return False

    if dryad_record["curationStatus"] != "Published":
        print(dryad_record["title"])
        print("This record is not marked as Published")
        return False

    return True


def get_rdr_userid(email):
    """
    Return an RDR user ID (if one exists) given an mq email address
    """
    url = f"{BASE_URL}/account/institution/accounts?email={email}"

    headers = {"Authorization": f"token {TOKEN}"}

    response = requests.request("GET", url, headers=headers)

    if len(response.json()) == 0:
        return 0
    else:
        return response.json()[0]["user_id"]


def handle_authors(authors):
    """
    Returns a structured list of authors
    """
    author_list = []
    for dryad_author in authors:
        author = {}

        # Check if the author has a macquarie email
        if "email" in dryad_author and "mq.edu.au" in dryad_author["email"].lower():
            rdr_userid = get_rdr_userid(dryad_author["email"].lower())

            if rdr_userid != 0:
                author["id"] = rdr_userid
            else:
                author["first_name"] = f"{dryad_author['firstName']}"
                author["last_name"] = f"{dryad_author['lastName']}"

                # if "email" in dryad_author and dryad_author["email"] != "":
                #     author["email"] = f"{dryad_author['email'].lower()}"
                # elif "orcid" in dryad_author and dryad_author["orcid"] != "":
                #     author["orcid_id"] = f"{dryad_author['orcid']}"
        else:
            author["first_name"] = f"{dryad_author['firstName']}"
            author["last_name"] = f"{dryad_author['lastName']}"

            # if "email" in dryad_author and dryad_author["email"] != "":
            #     author["email"] = f"{dryad_author['email'].lower()}"

            # if "orcid" in dryad_author and dryad_author["orcid"] != "":
            #     author["orcid_id"] = f"{dryad_author['orcid']}"

        author_list.append(author)

    return author_list


def handle_funders(funders):
    """
    Returns a structured list of funders
    """
    funding_list = []
    for dryad_funder in funders:
        if "awardNumber" not in dryad_funder or dryad_funder["awardNumber"] == "":
            funder = {}
            funder["title"] = dryad_funder["organization"]
        else:
            funder = {}
            funder["title"] = (
                dryad_funder["organization"] + " : " + dryad_funder["awardNumber"]
            )

        funding_list.append(funder)

    funding_list_uniques = [dict(t) for t in {tuple(d.items()) for d in funding_list}]

    return funding_list_uniques


def handle_description(dryad_record):
    """
    Pulls together dryad abstract, methods and usage text into figshare description field
    """

    # Handle abstract - strip out HTML tags
    cleaned_text = re.compile("<.*?>")
    description = re.sub(cleaned_text, "", dryad_record["abstract"])

    # Handle methods if present
    if "methods" in dryad_record:
        description += (
            "\n\n"
            + "<h3>Methods</h3>\n"
            + re.sub(cleaned_text, "", dryad_record["methods"])
        )

    # Handle usage notes if present
    if "usageNotes" in dryad_record:
        description += (
            "\n\n"
            + "<h3>Usage Notes</h3>\n"
            + re.sub(cleaned_text, "", dryad_record["usageNotes"])
        )

    # Ensure that the generated description text is less than 10000 chars
    if len(description) >= 10000:
        description = description[:9950] + "....see Dryad link for full text"

    return description


def handle_references(references):
    """
    Returns a structured list of references
    """
    reference_list = []
    for reference in references:
        if (
            "identifier" in reference
            and (
                reference["identifierType"] == "URL"
                or reference["identifierType"] == "DOI"
            )
            and reference["identifier"] != ""
            and reference["identifier"].startswith("http")
        ):
            reference_list.append(reference["identifier"])

    return reference_list


def handle_doi(doi):
    """
    Returns doi format
    """

    # return doi
    return doi.replace("doi:", "")


def get_dryad_records():

    loop = True
    total = 0
    page_num = 1
    per_page = 100
    data = []

    while loop == True:

        url = generate_search_url(page_num, per_page)
        response = requests.request("GET", url)
        dryad_records = response.json()

        for dryad_record in dryad_records["_embedded"]["stash:datasets"]:
            # Check record is valid for upload to the RDR
            valid_record = validate_record(dryad_record)

            if valid_record:

                record = {}

                # Handle Identifier/DOI
                record["doi"] = handle_doi(dryad_record["identifier"])

                # Handle title
                record["title"] = dryad_record["title"]

                # Handle authors
                record["authors"] = handle_authors(dryad_record["authors"])

                # Handle references
                if "relatedWorks" in dryad_record:
                    record["references"] = handle_references(
                        dryad_record["relatedWorks"]
                    )
                else:
                    record["references"] = []

                # Handle description
                record["description"] = handle_description(dryad_record)

                # Handle funders
                if "funders" in dryad_record:
                    record["funding_list"] = handle_funders(dryad_record["funders"])
                else:
                    record["funding_list"] = []

                # Handle keywords (and fieldOfScience codes) if present
                keywords = []
                if "keywords" in dryad_record and dryad_record["keywords"] != "":
                    keywords = dryad_record["keywords"]
                if (
                    "fieldOfScience" in dryad_record
                    and dryad_record["fieldOfScience"] != ""
                ):
                    keywords.append(dryad_record["fieldOfScience"])

                if keywords:
                    record["keywords"] = list(set(keywords))
                else:
                    record["keywords"] = ["None Given"]

                # Handle associated dates
                timelines = {}
                timelines["firstOnline"] = dryad_record["publicationDate"]
                timelines["publisherPublication"] = dryad_record["publicationDate"]
                timelines["publisherAcceptance"] = dryad_record["publicationDate"]
                record["timeline"] = timelines

                # Insert license matching CC-BY
                record["license"] = LICENSE_ID

                # Insert RDR/figshare group id
                record["group_id"] = GROUP_ID

                # Insert defined type
                record["defined_type"] = "Dataset"

                # Insert category
                record["categories"] = CATEGORIES

                # Insert custom fields
                if ADD_CUSTOM:
                    record["custom_fields"] = {
                        "Data Sensitivity": ["General"],
                        "Source": "Dryad",
                    }

                data.append(record)

                total += 1
                print(f"Total = {total}")

        page_num += 1
        print("")
        print(f"Page Number = {page_num}")
        print("")

        if len(dryad_records["_embedded"]["stash:datasets"]) < per_page:
            loop = False
            print(f"Done! Total number of records = {total}")

    with open("data/dryad_records.json", "w") as outfile:
        json.dump(data, outfile)


def main():
    get_dryad_records()


if __name__ == "__main__":
    main()
