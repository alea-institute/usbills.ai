"""
Constants for the database models related to bills.
"""

# default float value to avoid nulls
DEFAULT_FLOAT_VALUE = 0.0

# bill type codes
BILL_TYPE_CODES = {
    "hjres": "House Joint Resolution",
    "hconres": "House Concurrent Resolution",
    "hr": "House Resolution",
    "hres": "House Simple Resolution",
    "s": "Senate Bill",
    "sres": "Senate Resolution",
    "sjres": "Senate Joint Resolution",
    "sconres": "Senate Concurrent Resolution",
}

# bill version codes mapping
BILL_VERSION_CODES = {
    "as": "Amendment Ordered to be Printed (Senate)",
    "ash": "Additional Sponsors House",
    "ath": "Agreed to House",
    "ats": "Agreed to Senate",
    "cdh": "Committee Discharged House",
    "cds": "Committee Discharged Senate",
    "cph": "Considered and Passed House",
    "cps": "Considered and Passed Senate",
    "eah": "Engrossed Amendment House",
    "eas": "Engrossed Amendment Senate",
    "eh": "Engrossed in House",
    "enr": "Enrolled Bill",
    "es": "Engrossed in Senate",
    "fph": "Failed Passage House",
    "fps": "Failed Passage Senate",
    "hds": "Held at Desk Senate",
    "ih": "Introduced in House",
    "iph": "Indefinitely Postponed House",
    "ips": "Indefinitely Postponed Senate",
    "is": "Introduced in Senate",
    "lth": "Laid on Table in House",
    "lts": "Laid on Table in Senate",
    "pap": "Printed as Passed",
    "pcs": "Placed on Calendar Senate",
    "pp": "Public Print",
    "pvtl": "Private Law",
    "pl": "Public Law",
    "rch": "Reference Change House",
    "rcs": "Reference Change Senate",
    "rds": "Received in Senate",
    "rfh": "Referred in House",
    "rfs": "Referred in Senate",
    "rh": "Reported in House",
    "rhuc": "Returned to the House by Unanimous Consent",
    "rih": "Referral Instructions House",
    "rs": "Reported to Senate",
    "rth": "Referred to Committee House",
    "rts": "Referred to Committee Senate",
    "sc": "Sponsor Change",
    "statpvt": "Statutes at Large (Private Law)",
    "stat": "Statute",
}
