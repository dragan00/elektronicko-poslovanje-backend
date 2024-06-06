def fields_to_string(tbl, fields):
    res = ''
    if not fields: return 'null'
    for field in fields:
        res += f'{tbl}."{field}",'
    res = res[:-1]
    print(res)
    return res


def SqlCompanyBasicInfo(tbl):
    fields = [
        'id',
        'name',
        'OIB',
        'web',
        'year',
        'avatar',
        'address',
        'status',
        'created_at',
        'number',
    ]
    return fields_to_string(tbl, fields)

def SqlCargoDetailInfo(tbl):
    fields = [
        'id',
        'created_at',
        'length',
        'width',
        'weight',
        'cargo_note',
        'price',
        'exchange',
        'vehicle_note',
        'status',
        'auction_end_datetime',
        'min_down_bind_percentage'
    ]
    res = fields_to_string(tbl, fields)
    # Aukcija ce bit false ako je auction=True ali je istekla
    auc = f"""
        case
            when {tbl}.auction = true and (now() > {tbl}.auction_end_datetime)
        then
            false
        else
            {tbl}.auction
        end "auction"
    """
    res = f"{res}, {auc}"
    return res