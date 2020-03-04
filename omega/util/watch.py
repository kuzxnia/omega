from stringcase import snakecase
import logging

log = logging.getLogger(__name__)


def extract_watch_offer_data(page):
    def unify_title(section_title):
        return snakecase(section_title.find('p').text.strip().lower())

    data = {}
    watch_price = page.find("div", {"class": "detail-page-price"})

    for section in page.find("section", {"class": "specifications"}).find_all("tbody"):
        section_title, *section_data = section.find_all('tr')
        section_title = unify_title(section_title)

        data[section_title] = extract_data_from_section(section_title, section_data)

    return data


def extract_data_from_section(section_title, section_data):
    def parse_data_dict_format(rows):
        data = {}
        for row in rows:
            key, val = row.find_all('td')

            new_val = val.findChildren()
            if new_val:
                val = new_val[0] if isinstance(new_val, list) else new_val

            data[key.text] = val.text.replace('\n', '').replace('\t', '').strip()

        return data 


    def parse_data_list_format(rows):
        return [
            attr.replace('\n', '').strip()
            for row in rows
            for attr in row.text.split(',')
        ]

    def parse_description(row):
        return row[0].find('span', {'id': 'watchNotes'}).text

    parse_data_by_section_type = {
        'functions': parse_data_list_format,
        'description': parse_description,
        'others': parse_data_list_format,
    }
    return parse_data_by_section_type.get(section_title, parse_data_dict_format)(section_data)
