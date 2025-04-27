

def _remove_empty(d):
    if isinstance(d, dict):
        new_dict = {}
        for k, v in d.items():
            if v:
                new_val = _remove_empty(v)
                if new_val:
                    new_dict[k] = new_val
        return new_dict
    if isinstance(d, list):
        return [_remove_empty(e) for e in d]
    return d


class AirlineModel:
    def __init__(self):
        self.booking_data = None
        self.currency = None
        self.issue_place = None
        self.passport = None
        self.phone_number = None
        self.travel_agent = None
        self.visa_details = None


class AirlineModelBuilder:

    def __init__(self, response):
        self.__response = response
        self.__model = AirlineModel()

    def __get(self, key, source=None):
        response = source if source else self.__response
        for k in key.split("."):
            if response:
                response = response.get(k, {})
        return response

    def _booking_data(self):
        documents = self.__get('data.getMYBTripDetails.originalResponse.pnr.documents')
        if documents:
            self.__model.booking_data = [
                {
                    'Country Code': self.__get('documentDetails.countryCode', document),
                    'Station Location': self.__get('documentDetails.stationLocation', document),
                    'Issue Date': self.__get('documentDetails.issueDate', document),
                    'Currency Code': self.__get('documentDetails.currencyCode', document)
                } for document in documents]

    def _currency(self):
        self.__model.currency = _remove_empty(self.__get(
            'data.getMYBTripDetails.originalResponse.pnr.priceBreakdown'
        ))

    def __for_every_passenger(self, func):
        return [
            func(passenger)
            for passenger in self.__get('data.getMYBTripDetails.originalResponse.pnr.passengers') or []
        ]

    def _issue_place(self):
        self.__model.issue_place = self.__for_every_passenger(lambda passenger: {
            'Issuing Country': self.__get('visaInfo.issuingCountry', passenger),
            'Issue Date': self.__get('visaInfo.issueDate', passenger),
            'Expiry Date': self.__get('visaInfo.expiryDate', passenger),
            'Document Number': self.__get('visaInfo.documentNumber', passenger),
            'Issue Place': self.__get('visaInfo.issuePlace', passenger)
        })

    def _passport(self):
        self.__model.passport = self.__for_every_passenger(lambda passenger: {
            'Issuing Country': self.__get('documentInfo.issuingCountry', passenger),
            'Document NUmber': self.__get('documentInfo.documentNumber', passenger),
            'Document Type': self.__get('documentInfo.documentType', passenger),
            'Nationality': self.__get('documentInfo.nationality', passenger),
            'Expiration': self.__get('documentInfo.expirationDate', passenger),
            'Date Of Birth': self.__get('documentInfo.dateOfBirth', passenger)
        })

    def _phone_number(self):
        self.__model.phone_number = [
            request.get('description')
            for request in self.__get('data.getMYBTripDetails.originalResponse.pnr.specialServiceRequests') or []
            if request.get('code') == 'CTCM'
        ]

    def _travel_agent(self):
        self.__model.travel_agent = self.__get('data.getMYBTripDetails.originalResponse.pnr.otherServiceInformation')

    def _visa_details(self):
        self.__model.visa_details = self.__for_every_passenger(lambda passenger: [
            {
                'Issuing Country': self.__get('issuingCountry', all_document_infos),
                'Issue Date': self.__get('issueDate', all_document_infos),
                'Document Number': self.__get('documentNumber', all_document_infos),
                'Document Type': self.__get('documentType', all_document_infos),
                'Expiration Date': self.__get('expirationDate', all_document_infos)
            }
            for all_document_infos in self.__get('allDocumentInfos', passenger) or []])

    def build(self):
        self._booking_data()
        self._currency()
        self._issue_place()
        self._passport()
        self._phone_number()
        self._travel_agent()
        self._visa_details()
        return self.__model
