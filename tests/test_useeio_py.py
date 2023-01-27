from context import Model
from pprint import pprint

model = Model('USEEIOv2.0')

iocodes = model.load_io_codes()



print(iocodes['ImportCodes'])
print(iocodes['InternationalTradeAdjustmentCodes'])