from dataclasses import dataclass, field

@dataclass
class Gateway:
  country_code: str
  language_code: str
  thinq1_uri: str
  thinq2_uri: str
  emp_uri: str
  emp_spx_uri: str

@dataclass
class ClientConfig:
  gateway: Gateway
