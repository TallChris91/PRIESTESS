import xlrd
import os

def ConvertWorkbook(db):
    workbook = xlrd.open_workbook(db)
    worksheets = workbook.sheet_names()[0]
    legend = []
    templates = []
    # Open the excel file
    worksheet = workbook.sheet_by_name(worksheets)
    #Get all the columns
    for col in range(worksheet.ncols):
        #Append the first value to get the type of template
        legend.append(worksheet.cell_value(0, col))
        #Append the non-empty values after the first value to get the templates
        newcol = worksheet.col_values(col)
        temp = []
        for idx, val in enumerate(newcol):
            if (idx != 0) and (val != ''):
                temp.append(val)
        templates.append(temp)

    return legend, templates