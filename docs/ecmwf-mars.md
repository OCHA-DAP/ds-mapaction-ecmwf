# ECMWF MARS

* [Configure MARS API](#configure-mars-api)
* [Download ECMWF MARS data](#download-ecmwf-mars-data)
* [Supported countries](#supported-countries)
* [Reference material](#reference-material)
* [Troubleshooting](#troubleshooting)

### Configure MARS API

Get your user API key i.e. `123456789abcdefg123456789abcdefg`  
registered to your e-mail address i.e. `your.name@company.com`

and write it into the configuration file, so it looks like:

```bash
$ cat ~/.ecmwfapirc
{
    "url"   : "https://api.ecmwf.int/v1",
    "key"   : "123456789abcdefg123456789abcdefg",
    "email" : "your.name@company.com"
}
```

### Download ECMWF MARS data

To retrieve ECMWF MARS data set, navigate to the root directory

```bash
cd ds-mapaction-ecmwf/
```

and run

```bash
poetry run python src/data_retrieval mars [country-iso]
```

for example to download the data for Ethiopia, run

```bash
poetry run python src/data_retrieval mars ETH
```

### Supported countries

| iso   | name_en                                      |
|:------|:---------------------------------------------|
| AFG   | Afghanistan                                  |
| AGO   | Angola                                       |
| AIA   | Anguilla                                     |
| ALB   | Albania                                      |
| AND   | Andorra                                      |
| ARE   | United Arab Emirates                         |
| ARG   | Argentina                                    |
| ARM   | Armenia                                      |
| ATG   | Antigua and Barbuda                          |
| AUS   | Australia                                    |
| AUT   | Austria                                      |
| AZE   | Azerbaijan                                   |
| BDI   | Burundi                                      |
| BEL   | Belgium                                      |
| BEN   | Benin                                        |
| BFA   | Burkina Faso                                 |
| BGD   | Bangladesh                                   |
| BGR   | Bulgaria                                     |
| BHR   | Bahrain                                      |
| BHS   | The Bahamas                                  |
| BIH   | Bosnia and Herzegovina                       |
| BLR   | Belarus                                      |
| BLZ   | Belize                                       |
| BMU   | Bermuda                                      |
| BOL   | Bolivia                                      |
| BRA   | Brazil                                       |
| BRB   | Barbados                                     |
| BRN   | Brunei                                       |
| BTN   | Bhutan                                       |
| BWA   | Botswana                                     |
| CAF   | Central African Republic                     |
| CAN   | Canada                                       |
| CHE   | Switzerland                                  |
| CHL   | Chile                                        |
| CHN   | China                                        |
| CIV   | Côte d'Ivoire                                |
| CMR   | Cameroon                                     |
| COD   | Democratic Republic of the Congo             |
| COG   | Congo-Brazzaville                            |
| COK   | Cook Islands                                 |
| COL   | Colombia                                     |
| COM   | Comoros                                      |
| CPV   | Cape Verde                                   |
| CRI   | Costa Rica                                   |
| CUB   | Cuba                                         |
| CYM   | Cayman Islands                               |
| CYP   | Cyprus                                       |
| CZE   | Czechia                                      |
| DEU   | Germany                                      |
| DJI   | Djibouti                                     |
| DMA   | Dominica                                     |
| DNK   | Denmark                                      |
| DOM   | Dominican Republic                           |
| DZA   | Algeria                                      |
| ECU   | Ecuador                                      |
| EGY   | Egypt                                        |
| ERI   | Eritrea                                      |
| ESP   | Spain                                        |
| EST   | Estonia                                      |
| ETH   | Ethiopia                                     |
| FIN   | Finland                                      |
| FJI   | Fiji                                         |
| FLK   | Falkland Islands                             |
| FRA   | France                                       |
| FRO   | Faroe Islands                                |
| FSM   | Federated States of Micronesia               |
| GAB   | Gabon                                        |
| GBR   | United Kingdom                               |
| GEO   | Georgia                                      |
| GGY   | Guernsey                                     |
| GHA   | Ghana                                        |
| GIB   | Gibraltar                                    |
| GIN   | Guinea                                       |
| GMB   | The Gambia                                   |
| GNB   | Guinea-Bissau                                |
| GNQ   | Equatorial Guinea                            |
| GRC   | Greece                                       |
| GRD   | Grenada                                      |
| GRL   | Greenland                                    |
| GTM   | Guatemala                                    |
| GUY   | Guyana                                       |
| HND   | Honduras                                     |
| HRV   | Croatia                                      |
| HTI   | Haiti                                        |
| HUN   | Hungary                                      |
| IDN   | Indonesia                                    |
| IMN   | Isle of Man                                  |
| IND   | India                                        |
| IOT   | British Indian Ocean Territory               |
| IRL   | Ireland                                      |
| IRN   | Iran                                         |
| IRQ   | Iraq                                         |
| ISL   | Iceland                                      |
| ISR   | Israel                                       |
| ITA   | Italy                                        |
| JAM   | Jamaica                                      |
| JEY   | Jersey                                       |
| JOR   | Jordan                                       |
| JPN   | Japan                                        |
| KAZ   | Kazakhstan                                   |
| KEN   | Kenya                                        |
| KGZ   | Kyrgyzstan                                   |
| KHM   | Cambodia                                     |
| KIR   | Kiribati                                     |
| KNA   | Saint Kitts and Nevis                        |
| KOR   | South Korea                                  |
| KWT   | Kuwait                                       |
| LAO   | Laos                                         |
| LBN   | Lebanon                                      |
| LBR   | Liberia                                      |
| LBY   | Libya                                        |
| LCA   | Saint Lucia                                  |
| LIE   | Liechtenstein                                |
| LKA   | Sri Lanka                                    |
| LSO   | Lesotho                                      |
| LTU   | Lithuania                                    |
| LUX   | Luxembourg                                   |
| LVA   | Latvia                                       |
| MAR   | Morocco                                      |
| MCO   | Monaco                                       |
| MDA   | Moldova                                      |
| MDG   | Madagascar                                   |
| MDV   | Maldives                                     |
| MEX   | Mexico                                       |
| MHL   | Marshall Islands                             |
| MKD   | North Macedonia                              |
| MLI   | Mali                                         |
| MLT   | Malta                                        |
| MMR   | Myanmar                                      |
| MNE   | Montenegro                                   |
| MNG   | Mongolia                                     |
| MOZ   | Mozambique                                   |
| MRT   | Mauritania                                   |
| MSR   | Montserrat                                   |
| MUS   | Mauritius                                    |
| MWI   | Malawi                                       |
| MYS   | Malaysia                                     |
| NAM   | Namibia                                      |
| NER   | Niger                                        |
| NGA   | Nigeria                                      |
| NIC   | Nicaragua                                    |
| NIU   | Niue                                         |
| NLD   | Netherlands                                  |
| NOR   | Norway                                       |
| NPL   | Nepal                                        |
| NRU   | Nauru                                        |
| NZL   | New Zealand                                  |
| OMN   | Oman                                         |
| PAK   | Pakistan                                     |
| PAN   | Panama                                       |
| PCN   | Pitcairn Islands                             |
| PER   | Peru                                         |
| PHL   | Philippines                                  |
| PLW   | Palau                                        |
| PNG   | Papua New Guinea                             |
| POL   | Poland                                       |
| PRK   | North Korea                                  |
| PRT   | Portugal                                     |
| PRY   | Paraguay                                     |
| QAT   | Qatar                                        |
| ROU   | Romania                                      |
| RUS   | Russia                                       |
| RWA   | Rwanda                                       |
| SAU   | Saudi Arabia                                 |
| SDN   | Sudan                                        |
| SEN   | Senegal                                      |
| SGP   | Singapore                                    |
| SGS   | South Georgia and the South Sandwich Islands |
| SHN   | Saint Helena, Ascension and Tristan da Cunha |
| SLB   | Solomon Islands                              |
| SLE   | Sierra Leone                                 |
| SLV   | El Salvador                                  |
| SMR   | San Marino                                   |
| SOM   | Somalia                                      |
| SRB   | Serbia                                       |
| SSD   | South Sudan                                  |
| STP   | São Tomé and Príncipe                        |
| SUR   | Suriname                                     |
| SVK   | Slovakia                                     |
| SVN   | Slovenia                                     |
| SWE   | Sweden                                       |
| SWZ   | Eswatini                                     |
| SYC   | Seychelles                                   |
| SYR   | Syria                                        |
| TCA   | Turks and Caicos Islands                     |
| TCD   | Chad                                         |
| TGO   | Togo                                         |
| THA   | Thailand                                     |
| TJK   | Tajikistan                                   |
| TKL   | Tokelau                                      |
| TKM   | Turkmenistan                                 |
| TLS   | East Timor                                   |
| TON   | Tonga                                        |
| TTO   | Trinidad and Tobago                          |
| TUN   | Tunisia                                      |
| TUR   | Turkey                                       |
| TUV   | Tuvalu                                       |
| TWN   | Taiwan                                       |
| TZA   | Tanzania                                     |
| UGA   | Uganda                                       |
| UKR   | Ukraine                                      |
| URY   | Uruguay                                      |
| USA   | United States                                |
| UZB   | Uzbekistan                                   |
| VAT   | Vatican City                                 |
| VCT   | Saint Vincent and the Grenadines             |
| VEN   | Venezuela                                    |
| VGB   | British Virgin Islands                       |
| VNM   | Vietnam                                      |
| VUT   | Vanuatu                                      |
| WSM   | Samoa                                        |
| XKX   | Kosovo                                       |
| YEM   | Yemen                                        |
| ZAF   | South Africa                                 |
| ZMB   | Zambia                                       |
| ZWE   | Zimbabwe                                     |

### Reference material

:book: [MARS user documentation](https://confluence.ecmwf.int/display/UDOC/MARS+user+documentation)

:book: [MARS server activity](https://apps.ecmwf.int/mars-activity/)

:book: [ECMWF Service status](https://www.ecmwf.int/en/service-status)

### Troubleshooting
