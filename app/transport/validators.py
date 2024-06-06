import os


def validate_company_documents(files):
    allowed_ext = ('jpeg', 'pdf', 'png')
    for file in files:
        if not file.name.lower().endswith(allowed_ext):
            print("Nedozvoljena vrsta dokumenta")
            return False
    return True

def validate_stock_images(files):
    allowed_ext = ('jpeg', 'png')
    for file in files:
        if not file.name.lower().endswith(allowed_ext):
            print("Nedozvoljena vrsta dokumenta")
            return False
    return True