from koda_validate import *

validator = ListValidator(StringValidator())

validator(["cool"])
# > Ok(['cool'])

validator([5])
# > Err({'0': ['expected a string']})
