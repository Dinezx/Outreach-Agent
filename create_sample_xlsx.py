from openpyxl import Workbook

workbook = Workbook()
worksheet = workbook.active
worksheet.append(["company_name"])
worksheet.append(["Umbrella Corp"])
worksheet.append(["Stark Industries"])
workbook.save(r"d:\Company Agent\sample-companies.xlsx")
print("created")
