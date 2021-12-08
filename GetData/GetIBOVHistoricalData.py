
from GetData.Alpha_Vantage_Get_Data import Alpha_Vantage_Get_Data as avgd

#Get Data
symbol_list = []
with open('./Indice/ibov.txt') as f:
    symbol_list = f.read().splitlines()

# print(symbol_list)

#Get Data
# symbol_list = ['BOVA11','SMAL11']
av = avgd(debug = True, data_dir = './GetData/Data/')
print(av.DATA_DIR)
data_list = av.get_stock_data(
                symbol_list)
del av