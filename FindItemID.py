import pandas as pd

pd_1 = pd.read_excel(r"C:\Users\DiDi\Documents\Upload Merchants Menu\menus\Animals.xlsx", sheet_name=0)
pd_2 = pd.read_excel(r"C:\Users\DiDi\Downloads\item_library.xlsx", sheet_name=0)

pd_2 = pd_2[pd_2.SKU_UPC.str.startswith(('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'), na=False)].reset_index()

print("Process started")
skus = {
    'Library_SKU_ID': [],
    'SKU_Name': [],
    'If_Standard': [],
    'SKU_UPC': [],
    'Picture_url': [],
    'Attr_Category_ID': []
}
for i in range(0, len(pd_1.EAN)):
    for j in range(0, len(pd_2.SKU_UPC)):
        if str(pd_1.EAN[i]) == str(pd_2.SKU_UPC[j]):
            skus['Library_SKU_ID'].append(str(pd_2.Library_SKU_ID[j]))
            skus['SKU_Name'].append(str(pd_1.PRODUCT_NAME[i]))
            skus['If_Standard'].append('y')
            skus['SKU_UPC'].append(str(pd_2.SKU_UPC[j]))
            skus['Picture_url'].append(str(pd_1.IMAGE[i]))
            skus['Attr_Category_ID'].append(str(pd_2.Attr_Category_Name[j]))
skus = pd.DataFrame(skus).to_excel('skus.xlsx')
print("Process finished")
