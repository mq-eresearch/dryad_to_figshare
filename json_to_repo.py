#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" json_to_repo.py

Upload of dryad metadata from json file to data repository

"""

import json
import mqrdr
import config
import requests


token = config.TOKEN
base_url = config.BASE_URL

json_file = "data/dryad_records.json"


def create_rdr_records():
    """Create Data records in the repository"""

    # Open JSON file
    with open(
        json_file,
    ) as f:

        # returns JSON object as a dictionary
        records = json.load(f)

        # Iterate through the records
        for record in records:
            print("")
            print("----------")
            print(record["title"])
            print("----------")
            metadata = {
                "doi": record["doi"],
                "title": record["title"],
                "description": record["description"],
                "keywords": record["keywords"],
                "categories": record["categories"],
                "authors": record["authors"],
                "custom_fields": {
                    "Data Sensitivity": record["custom_fields"]["Data Sensitivity"],
                    "Source": record["custom_fields"]["Source"],
                },
                "defined_type": "dataset",
                "license": record["license"],
                "funding_list": record["funding_list"],
                "references": record["references"],
                "timeline": record["timeline"],
                "group_id": record["group_id"],
            }

            # Create the metadata record
            article = mqrdr.articles.create_article(base_url, token, metadata)

            if not article.ok:
                print(article.json())
                break
            else:
                article_id = article.json()["location"].split("/")[-1]
                print("-----------------------")
                print(f"Dryad article {article_id} created")
                # figshare_ids.append(article_id)

                # Run an update to remove the uploading author
                metadata = {
                    "authors": record["authors"],
                }
                mqrdr.articles.update_article(base_url, token, article_id, metadata)

                # Create a linked file to the doi record
                url = f"{base_url}/account/articles/{article_id}/files"

                doi_url = f"https://doi.org/{record['doi']}"

                payload = {}
                payload["link"] = doi_url

                headers = {
                    "Authorization": f"token {token}",
                    "Content-Type": "text/plain",
                }

                response = requests.request(
                    "POST", url, headers=headers, data=json.dumps(payload)
                )

                print(response.text)

                # Publish the record
                published_article = mqrdr.articles.publish_article(
                    base_url, token, article_id
                )


def main():
    # Read in migrated CSV file to dataframe
    create_rdr_records()


if __name__ == "__main__":
    main()
