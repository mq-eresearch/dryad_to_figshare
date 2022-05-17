#!/usr/bin/env python3
"""
Dryad record ingest to Macquarie University Research Data Repository
"""

__author__ = "Gerry Devine"
__version__ = "0.1.0"
__license__ = "MIT"


# Imports
import json
import mqrdr
import config


token = config.TOKEN
base_url = config.BASE_URL

json_file = "data/dryad_records.json"


def upload_dryad_records():
    """Create Dryad records in the repository"""

    # Capture the figshare record IDs generated
    figshare_ids = []

    # Open JSON file
    with open(json_file) as f:

        # returns JSON object as a dictionary
        records = json.load(f)

        # Iterate through the records and upload to the RDR
        for record in records:
            article = mqrdr.articles.create_article(base_url, token, record)

            if not article.ok:
                print(article.json())
                break
            else:
                article_id = article.json()["location"].split("/")[-1]
                print("-----------------------")
                print(f"Metadata article {article_id} created")
                figshare_ids.append(article_id)

                # Run an update to remove the uploading author
                metadata = {
                    "authors": record["authors"],
                }
                mqrdr.articles.update_article(base_url, token, article_id, metadata)

                # Publish the article
                published_article = mqrdr.articles.publish_article(
                    base_url, token, article_id
                )
                print(published_article.text)


def main():
    upload_dryad_records()


if __name__ == "__main__":
    main()
