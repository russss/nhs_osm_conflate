# What will be put into "source" tags. Lower case please
source = 'www.nhs.uk'
# A fairly unique id of the dataset to query OSM, used for "ref:mos_parking" tags
# If you omit it, set explicitly "no_dataset_id = True"
dataset_id = 'GB:ENG:nhs_organisation'
# Tags for querying with overpass api
query = [('amenity', 'hospital')]
# Use bbox from dataset points (default). False = query whole world, [minlat, minlon, maxlat, maxlon]
bbox = True
# How close OSM point should be to register a match, in meters. Default is 100
max_distance = 250
# Delete objects that match query tags but not dataset? False is the default
delete_unmatched = False
# If set, and delete_unmatched is False, modify tags on unmatched objects instead
# Always used for area features, since these are not deleted
# tag_unmatched = {
#     'fixme': "Is this a hospital? It isn't listed in the NHS dataset of hospitals",
# }
# Actually, after the initial upload we should not touch any existing non-matched objects
tag_unmatched = None
# A set of authoritative tags to replace on matched objects
master_tags = ('name', 'operator')

download_url = 'http://media.nhschoices.nhs.uk/data/foi/Hospital.csv'


# A list of SourcePoint objects. Initialize with (id, lat, lon, {tags}).
def dataset(fileobj):
    import csv
    import io
    import logging
    import phonenumbers
    reader = csv.DictReader(io.TextIOWrapper(fileobj, encoding='iso-8859-1'), delimiter='\xac')
    data = []
    for row in reader:
        if row['Sector'] == 'Independent Sector':
            continue
        try:
            lat = float(row['Latitude'])
            lon = float(row['Longitude'])
        except ValueError:
            logging.warning("Failed to parse lat/lon for object ID %s", row['OrganisationID'])

        try:
            phone = phonenumbers.parse(row['Phone'], 'GB')
            phone_formatted = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except phonenumbers.phonenumberutil.NumberParseException:
            phone_formatted = None

        if ' - ' in row['OrganisationName'] and row['OrganisationName'].endswith('Trust'):
            name = row['OrganisationName'].split(' - ')[0]
        elif ', ' in row['OrganisationName'] and row['OrganisationName'].endswith('Trust'):
            name = row['OrganisationName'].split(', ')[0]
        else:
            name = row['OrganisationName']

        tags = {
            'amenity': 'hospital',
            'operator': row['ParentName'],
            'name': name,
            'addr:street': row.get('Address2'),
            'addr:city': row['City'],
            'addr:postcode': row['Postcode'],
            'website': row['Website'],
            'phone': phone_formatted
        }
        data.append(SourcePoint(row['OrganisationID'], lat, lon, tags))
    return data
