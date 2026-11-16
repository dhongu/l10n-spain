Loads the Spanish localities (localidades) with their postal code and region, and fills in the
city and the region of Spanish addresses from the postal code.

- Ships the list of Spanish localities with their postal code, linked to the regions of Spain. The data
  comes from [GeoNames](https://www.geonames.org) (Creative Commons Attribution 4.0).
- Spain is set to *enforce cities*: the city of a Spanish address is chosen from the list.
- On the contact form, typing the postal code (código postal) of a Spanish address sets the city and the
  region. A postal code shared by several localities sets only the region; the city name, when it matches
  one of them (without accents and case), picks the locality.
- The action *Spain: set city from ZIP* on contacts links the Spanish contacts to the city of their postal
  code and fills in the region.
- At install, the Spanish contacts are linked: directly on a small database, by the scheduled action
  *Spain: link contacts to the city of their ZIP* in batches on a large one (it deactivates itself when done).
- Every form that runs the postal code rules of the contact (for example the delivery details of an AWB)
  gets the region filled in, so the shipment can be sent to Spain without looking it up by hand.
