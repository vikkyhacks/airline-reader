

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


def _flatten(object):
    def _to_str(collections):
        if isinstance(collections, dict):
            return "\n".join([key + ": " + value for key, value in collections.items() if value])
        elif isinstance(collections, list):
            return "\n\n".join([_flatten(item) for item in collections if item])
        else:
            return collections

    return (_to_str(object) or '').strip()


class AirlineModel:
    def __init__(self):
        self.name=None
        self.trip=None
        self.layover=None
        self.personal_details=None
        self.booking_data = None
        self.payment_details = None
        self.currency = None
        self.issue_place = None
        self.passport = None
        self.phone_number = None
        self.travel_agent = None
        self.visa_details = None
        self.email = None
    def to_dict(self):
        return {
            'Name': _flatten(self.name),	    
            'Trip': _flatten(self.trip),
            'Layover': _flatten(self.layover),
	    'Personal details': _flatten(self.personal_details),
            'Phone Number': _flatten(self.phone_number),
            'email': _flatten(self.email),
            'Payment info': _flatten(self.payment_details),
            'Currency': _flatten(self.currency),
            'Passport': _flatten(self.passport),
            'Booking Data': _flatten(self.booking_data),
            'Issue Place': _flatten(self.issue_place),
            'Travel Agent': _flatten(self.travel_agent),
            'Visa Details': _flatten(self.visa_details) 
        }


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

    def _personal_details(self):
        passenger_info = self.__get('data.getMYBTripDetails.originalResponse.pnr.passengers')
        if passenger_info:
            self.__model.personal_details = [
                {
                    'DOB': self.__get('passengerInfo.dateOfBirth', pax),
                    'Gender': self.__get('passengerInfo.gender', pax),
                    'Email': ", ".join(self.__get('passengerInfo.emails', pax)) if self.__get('passengerInfo.emails', pax) else "",
                    'Phone': ", ".join(
                        [f"{phone.get('countryCode', '')} {phone.get('number', '')}".strip()
                         for phone in self.__get('passengerInfo.phones', pax)]
                     ) if self.__get('passengerInfo.phones', pax) else ""
                } for pax in passenger_info
            ]


    def _name(self):
        passenger_name = self.__get('data.getMYBTripDetails.originalResponse.pnr.passengers')
        if passenger_name:
            self.__model.name = [
                " ".join(
                    filter(None, [
                        self.__get('passengerDetails.firstName', pax),
                        self.__get('passengerDetails.middleName', pax),
                        self.__get('passengerDetails.lastName', pax)
                    ])
                )
                for pax in passenger_name
            ]

    def _currency(self):
        currencies = set()
        def _currency_vals(node: dict):
            if isinstance(node, dict) and "currency" in node:
                currencies.add(node["currency"])
            if isinstance(node, dict):
                for k, v in node.items():
                    _currency_vals(v)
            if isinstance(node, list):
                for v in node:
                    _currency_vals(v)

        potential_currency_nodes = _remove_empty(self.__get(
            'data.getMYBTripDetails.originalResponse.pnr.priceBreakdown'
        ))
        _currency_vals(potential_currency_nodes)
        self.__model.currency = list(currencies)

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
        special_service_phones = [
            request.get('description')
            for request in self.__get('data.getMYBTripDetails.originalResponse.pnr.specialServiceRequests') or []
            if request.get('code') == 'CTCM'
        ]

        contact_phones = [
            f"+{phone.get('countryCode', '')} {phone.get('number', '')}".strip()
            for phone in self.__get('data.getMYBTripDetails.originalResponse.pnr.contact.phones') or []
        ]

        self.__model.phone_number = special_service_phones + contact_phones

    def _email(self):
        special_service_emails = [
            request.get('origin')
            for request in self.__get('data.getMYBTripDetails.originalResponse.pnr.specialServiceRequests') or []
            if request.get('code') == 'CTCE'
        ]

        contact_emails = self.__get('data.getMYBTripDetails.originalResponse.pnr.contact.emails') or []

        self.__model.email = special_service_emails + contact_emails

    def _layover(self):
        itinerary_parts = self.__get('data.getMYBTripDetails.originalResponse.pnr.itinerary.itineraryParts')
        self.__model.layover = []
        for part in itinerary_parts:
            connections = part.get('connectionInformations', [])
            for conn in connections:
                duration = conn.get('duration')
                if duration is not None:
                    hours = duration // 60
                    minutes = duration % 60
                    formatted = f"{hours}h {minutes}m"
                    self.__model.layover.append(formatted)

    def _travel_agent(self):
        self.__model.travel_agent = self.__get('data.getMYBTripDetails.originalResponse.pnr.otherServiceInformation')

    def _trip(self):
        passengers = self.__get('data.getMYBTripDetails.originalResponse.pnr.passengers')
        self.__model.trip = []
        seen_segments = set()

        for pax in passengers:
            prefs = pax.get('preferences', {}).get('specialPreferences', {})
            remarks = prefs.get('specialServiceRequestRemarks', [])

            for remark in remarks:
                for segment in remark.get("segmentKeys", []):
                    signature = (
                        segment.get("origin", ""),
                        segment.get("destination", ""),
                        segment.get("departure", "")
                    )

                    if signature not in seen_segments:
                        seen_segments.add(signature)
                        route = f"{signature[0]} → {signature[1]}"
                        time = f"{segment.get('departure', '')} → {segment.get('arrival', '')}"

                        if route and time:
                            self.__model.trip.append([route, time])


    def _payment_details(self):
        payment_details = self.__get('data.getMYBTripDetails.originalResponse.pnr.payments')
        if payment_details:
            self.__model.payment_details = []
            for price in payment_details:
                method = price.get('paymentType', '')
                code = price.get('paymentCode', '')
                card_number = price.get('identifier','')
                price_block = price.get('price', {}).get('alternatives', [[{}]])
                amount = price_block[0][0].get('amount', '')
                currency = price_block[0][0].get('currency', '')

                self.__model.payment_details.append({
                    'Payment Method': method,
                    'Payment Code': code,
                    'card_number': card_number,
                    'Amount': f"{amount} {currency}" if amount and currency else ""
                })


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
        
        self._trip()
        self._name()
        self._personal_details()
        self._booking_data()
        self._currency()
        self._issue_place()
        self._passport()
        self._phone_number()
        self._travel_agent()
        self._visa_details()
        self._email()
        self._layover()
        self._payment_details()
        return self.__model
