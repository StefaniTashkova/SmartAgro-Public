import pytest
from app.models import OwnerType

TEST_OWNER_EGN = '1112129854'


@pytest.fixture
def owner_data():
    return {'owner_type': OwnerType.PERSON.name,
            'name': 'Тесто Тести Тестов',
            'egn': TEST_OWNER_EGN,
            'phone': '+359879837264',
            'nationalID_number': '698523021',
            'nationalID_issued_by': 'МВР Тест',
            'nationalID_issue_date': '2014-03-07 00:00:00',
            'IBAN': 'BG70BNPA94409235382943',
            'BIC': 'BNPABGSX',
            'email': 'testi@abv.bg',
            'address': '69 Testi Street',
            'payment_location': 'Чарган',
            'notes': 'Тест'}
