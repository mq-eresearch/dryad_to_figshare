[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7183386.svg)](https://doi.org/10.5281/zenodo.7183386)

# Dryad to Figshare harvest

Python script to harvest metadata from a selected organisation's Dryad data records and generate matching metadata-only records in an institutional Figshare repository.

## Notes

- This script only harvests metadata, not the data itself - It is intended as a mechanism to catalog the existance of dryad-based datasets from an institution into the institution's institutional Figshare repository.
- The existing (dryad-generated) dataset doi is reused on the Figshare side. A new DOI is not generated for the generated Figshare record.
- The 'link file' option is used on the figshare side to allow for the reuse of an existing doi
- This is 'one-time only' script - that is, it will harvest all dryad records associated with an institution. To adapt this script to be an ongoing harverster, it would need to be updated to harvest against a date filter etc.

## Prerequisites

To use this script, you will need to create a file called config.py and use it to set the API key/token of the institutional repository
account under which records will be generated. For example:

```python
# SET TOKEN
TOKEN = "set your token here"
```

You will also need the pandas and mqrdr libraries installed:

- pip install pandas
- pip install mqrdr

## Usage

You will need to run two scripts sequentially:

- get_dryad_records.py - this script harvests Dryad and creates a json file containing all metadata associated with the dryad records
- json_to_repo.py - this script will loop through the generated json file and create a new figshare metadata record.

Settings are applied at the top of get_dryad_records.py and allow you to set:

- BASE_URL - Base figshare URL (staging or production etc), e.g. "https://api.figsh.com/v2" for Staging instance
- ROR - Set the Research organisation ID (from https://ror.org)
- LICENSE_ID - ID of the relevant license in the figshare instance
- GROUP_ID - Figshare data group
- CATEGORIES - List of category IDs under which to upload dataset
- ADD_CUSTOM - whether to add custom metadata fields to the json file

## Authors

Gerry Devine
[gerry.devine@mq.edu.au](mailto:gerry.devine@mq.edu.au)

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
