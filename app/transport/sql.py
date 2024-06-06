from .constants import *
from .helpers import *
from .sql_serializer import *

def sql_get_prepare():
    """
    Generira SQL za dohvatanje
    Jezika, Država
    Vraća SQL query
    """
    query = '''
        select 
            json_agg(_all) 
        from 
            (
                select 
                    COALESCE(json_agg(account_languages), '[]') "languages",
                	(
                		select 
                			COALESCE(json_agg(countries), '[]') "countries"
                		from
                			(
                				select 
                					tc.id, 
                					tc.name, 
                					tc."alpha2Code"
                				from
                					transport_country tc
                                where
                                    tc.is_active = true
                				order by
                				    tc.name
                			) countries
                	),
                    (select COALESCE(json_agg(_tg), '[]') "goods_types" from (
                    select tg.id, tg.name
                    from transport_goodstype tg 
                    )  _tg),
        
                    (select COALESCE(json_agg(_vt), '[]') "vehicle_types" from (
                    select tvt.id, tvt.name
                    from transport_vehicletype tvt 
                    )  _vt),
        
                    (select COALESCE(json_agg(_tvu), '[]') "vehicle_upgrades" from (
                    select tvu.id, tvu.name
                    from transport_vehicleupgrade tvu 
                    )  _tvu),
        
                    (select COALESCE(json_agg(_tvf), '[]') "vehicle_features" from (
                    select tvf.id, tvf.name
                    from transport_vehiclefeature tvf 
                    )  _tvf),
                    
                    (select COALESCE(json_agg(_tve), '[]') "vehicle_equipment" from (
                    select tve.id, tve.name
                    from transport_vehicleequipment tve 
                    )  _tve),
                    
                    (select COALESCE(json_agg(_tgf), '[]') "goods_forms" from (
                    select tgf.id, tgf.name
                    from transport_goodsform tgf 
                    )  _tgf),
                    
                    (select COALESCE(json_agg(_ttt), '[]') "transport_types" from (
                    select ttt.id, ttt.name
                    from transport_transporttype ttt 
                    )  _ttt),
                    
                    (select COALESCE(json_agg(_tls), '[]') "loading_systems" from (
                    select tls.id, tls.name
                    from transport_loadingsystem tls 
                    )  _tls)
                	
        from (
            select tl.id, tl.name, tl.native_name, tl."alpha2Code"
            from transport_language tl
            --from "accounts_account_languages" aal
            --inner join "transport_language" tl on aal.language_id = tl.id
        )account_languages
    ) _all	
    '''
    return query


def sql_get_vehicle_equipment_by_cargo_id(cargo_id):
    query = f"""
        --Oprema vozila pocetak
        (
            select
                COALESCE(json_agg(_oprema_vozila), '[]') "vehicle_equipment"
            from
                (
                    select
                        tveq.id, tveq.name
                    from
                        transport_cargo_vehicle_equipment tcveq
                    inner join
                        transport_vehicleequipment tveq on tveq.id = tcveq.vehicleequipment_id
                    where
                        tcveq.cargo_id = {cargo_id}
                ) _oprema_vozila
        ) 
        --Oprema vozila kraj
    """
    return query

def sql_get_vehicle_equipment_by_loading_space_id(id):
    query = f"""
        --Oprema vozila pocetak
        (
            select
                COALESCE(json_agg(_oprema_vozila), '[]') "vehicle_equipment"
            from
                (
                    select
                        tveq.id, tveq.name
                    from
                        transport_loadingspace_vehicle_equipment tcveq
                    inner join
                        transport_vehicleequipment tveq on tveq.id = tcveq.vehicleequipment_id
                    where
                        tcveq.loadingspace_id = {id}
                ) _oprema_vozila
        ) 
        --Oprema vozila kraj
    """
    return query

def sql_get_places(tbl):
    query = f'''
                (
                    		select
                    			json_agg(countries)->0 "country"
                    		from
                    			(
                    				select 
                    					tctry.id, tctry.name
                    				from 
                    					transport_country tctry
                                    where
                                        tctry.id = {tbl}.country_id
                    			)countries
                    	),
                    	(
                    		select
                    			json_agg(cities)->0 "city"
                    		from
                    			(
                    				select 
                    					tcty.id, tcty.name
                    				from 
                    					transport_city tcty
                                    where
                                        tcty.id = {tbl}.city_id
                    			)cities
                    	),
                    	(
                    		select 
                    			json_agg(zip_codes)->0 "zip_code" 
                    		from
                    			(
                    				select 
                    					tz.id, tz.code "name", tz.code
                    				from 
                    					transport_zipcode tz
                                    where
                                        tz.id = {tbl}.zip_code_id
                    			)zip_codes
                    	)
        '''
    return query

def sql_get_cities_and_zip_codes_by_country(country_id):
    """
    Generira SQL za dohvatanje
    gradova i poštanskih brojeva
    koji pripadaju određenoj državi
    """
    query = f'''
        select 
            json_agg(_all) 
        from 
            (
                select 
                	(
                		select
                			COALESCE(json_agg(cities), '[]') "cities"
                		from
                			(
                				select 
                					tc2.id, tc2.name, tc2.country_id
                				from 
                					transport_city tc2
                                where
                                    tc2.country_id = {country_id} and tc2.is_active = true
                                order by tc2.name
                			)cities
                	),
                	(
                		select 
                			COALESCE(json_agg(zip_codes), '[]') "zip_codes" 
                		from
                			(
                				select 
                					tz.id, tz.code "name", tz.code, tz.city_id, tc3.country_id 
                				from 
                					transport_zipcode tz
                				inner join
                					transport_city tc3 on tc3.id = tz.city_id
                                where
                                    tc3.country_id = {country_id} and tz.is_active = true
                                order by 
                                    tz.code
                			)zip_codes
                	)
    ) _all	
    '''
    return query

def sql_get_cargo_details(cargo_id):
    """
    SQL za dohvatanje detalja o nekom teretu
    """
    query = f'''
        (
            select
                json_agg(_tc)
            from
                (
                    --Cargo Informacije
                    select
                        {SqlCargoDetailInfo('tc')},
                        {sql_get_auctions('tc.id')},
                        {sql_get_vehicle_equipment_by_cargo_id('tc.id')},
                        --Poduzece start
                        (
                            select 
                                json_agg(_tcompany)->0 "company"
                            from
                                (
                                    select 
                                        {SqlCompanyBasicInfo('tcom')},
                                        {sql_get_places('tcom')},
                                        (
                                            select 
                                                COALESCE(array_agg(tcm.email), ARRAY[]::text[]) "emails"
                                            from
                                                transport_companymail tcm
                                            where 
                                                tcm.company_id = tcom.id
                                        ),
                                        (
                                            select 
                                                COALESCE(json_agg(_nums), '[]') "numbers"
                                            from 
                                                (
                                                    select 
                                                        tcn.number, tcn.type
                                                    from
                                                        transport_companynumber tcn
                                                    where 
                                                        tcn.company_id = tcom.id
                                                ) _nums
                                        )
                                    from
                                        transport_company tcom
                                    where 
                                        tcom.id = tc.company_id 
                                    group by 
                                        tcom.id

                                ) _tcompany
                        ),
                        --Poduzece kraj
                        -- Kontakt osobe start
                        (
                            select
                                coalesce(json_agg(_tcca), '[]') "contact_accounts"
                            from
                                (
                                    select
                                        aa.id,
                                        aa.name,
                                        aa.email,
                                        aa.phone_number,
                                        aa.avatar,
                                        (
                                        select coalesce(json_agg(account_languages), '[]') "languages"
                                        from (
                                            select tl.id, tl.name, tl.native_name
                                            from "accounts_account_languages" aal
                                            inner join "transport_language" tl on aal.language_id = tl.id
                                            where aal.account_id = aa.id
                                        )account_languages
                                    )
                                    from
                                        transport_cargo_contact_accounts tcca
                                        inner join accounts_account aa on aa.id = tcca.account_id
                                        left join accounts_account_languages aal on aal.account_id = aa.id
                                        left join transport_language tl on tl.id = aal.language_id
                                    where
                                        tcca.cargo_id = tc.id
                                    group by
                                        aa.id
                                ) _tcca
                        ),
                        --Kontakt osobe kraj
                        --Vrsta robe start 
                        (
                            select
                                coalesce(json_agg(_tcgt), '[]') "goods_types"
                            from
                                (
                                    select
                                        tgt.id, tgt.name
                                    from
                                        transport_cargo_goods_types tcgt
                                    inner join
                                        transport_goodstype tgt on tgt.id = tcgt.goodstype_id
                                    where
                                        tcgt.cargo_id = tc.id
                                ) _tcgt
                        ),
                        --Vrsta robe kraj
                        --Tipovi vozila pocetak
                        
                        (
                            select
                                coalesce(json_agg(_tcvt), '[]') "vehicle_types"
                            from
                                (
                                    select
                                        tvt.id, tvt.name
                                    from
                                        transport_cargo_vehicle_types tcvt
                                    inner join
                                        transport_vehicletype tvt on tvt.id = tcvt.vehicletype_id
                                    where 
                                        tcvt.cargo_id = tc.id
                                ) _tcvt
                        ),
                        --Tipovi vozila kraj
                        --Nadogradnje vozila pocetak
                        
                        (
                            select
                                coalesce(json_agg(_tcvu), '[]') "vehicle_upgrades"
                            from
                                (
                                    select
                                        tvu.id, tvu.name
                                    from
                                        transport_cargo_vehicle_upgrades tcvu
                                    inner join
                                        transport_vehicleupgrade tvu on tvu.id = tcvu.vehicleupgrade_id
                                    where 
                                        tcvu.cargo_id = tc.id
                                ) _tcvu
                        ),
                        --Nadogradnje vozila kraj
                        --Utovar i istovar start
                        (
                            select 
                                coalesce(json_agg(_tclu), '[]') "load_unload" 
                            from
                                (
                                    select 
                                        tclu.id, 
                                        tclu.start_datetime, 
                                        tclu.end_datetime,
                                        tclu.type,
                                        json_build_object(
                                            'id', tclu.country_id,
                                            'name', tc3.name,
                                            'alpha2Code', tc3."alpha2Code"
                                        ) "country",
                                        json_build_object(
                                            'id', tclu.city_id,
                                            'name', tc2.name
                                        ) "city",
                                        json_build_object(
                                            'id', tclu.zip_code_id,
                                            'name', tz.code,
                                            'city_id', tz.city_id 
                                        ) "zip_code"
                                    from 
                                        transport_cargoloadunload tclu
                                    left join
                                        transport_city tc2 on tc2.id = tclu.city_id 
                                    left join
                                        transport_country tc3 on tc3.id = tclu.country_id 
                                    left join
                                        transport_zipcode tz on tz.id = tclu.zip_code_id
                                    where
                                        tclu.cargo_id = tc.id
                                ) _tclu
                        )
                        --Utovar i istovar kraj
                    from
                        transport_cargo tc
                    where
                        tc.id = {cargo_id} --and tc.status = '{ACTIVE}'
                ) _tc
        )

    '''
    return query

def sql_get_auctions(cargo_id):
    query = f'''
    (
        select 
            coalesce(json_agg(_ta), '[]') "auctions"
        from 
            (
                select 
                ta.id,
                ta.price ,
                ta."timestamp" ,
                (
                    select 
                        json_agg(_aa)->0 "account"
                    from
                        (
                            select 
                                aa.id,
                                aa.name,
                                aa.phone_number,
                                aa.email ,
                                json_build_object(
                                    'id', tc.id,
                                    'name', tc.name,
                                    'address', tc.address
                                ) "company" 
                            from 
                                accounts_account aa 
                            inner join
                                transport_company tc on tc.id = aa.company_id
                            where 
                                aa.id = ta.account_id
                        ) _aa
                )
            from 
                transport_auction ta
            where 
                ta.cargo_id = {cargo_id}
            order by
                ta."timestamp" 
            ) _ta
    )
    '''
    return query

def sql_get_first_load_cargo_place():
    query = f'''
        (
            select min(tclu2.start_datetime) "sort_by"
            from 
                transport_cargoloadunload tclu2
            where
                tclu2.cargo_id = tc.id and tclu2.type = '{LOAD}'
        )
    '''
    return query

def sql_get_first_loading_space_starting_point():
    query = f'''
        (
            select min(tspd1.departure_datetime) "sort_by"
            from 
                transport_startingpointdestination tspd1
            where
                tspd1.loading_space_id = tc.id and tspd1.type = '{STARTING}'
        )
    '''
    return query

def sql_get_cargo_list(token, *args, **kwargs):
    JOIN_ARR = []
    JOIN_STRING = ''
    WHERE_ARR = []
    WHERE_STRING = ''
    LIMIT_STRING = ''
    HAVING_STRING = ''
    # previus_cursor = 'null'
    # next_cursor = f'''
    #     (select exists (select ))
    # '''
    # WHERE_ARR.append(f"tc.status = '{ACTIVE}'")
    WHERE_ARR.append(f"(tc.closed_at is null or (tc.closed_at > now() - INTERVAL '7 days'))")
    if NEXT_CURSOR in kwargs:
        WHERE_ARR.append(f"{sql_get_first_load_cargo_place()} > '{kwargs.get(NEXT_CURSOR)}'")
        previus_cursor = kwargs.get(NEXT_CURSOR)
    if LIMIT in kwargs:
        LIMIT_STRING = f'LIMIT {kwargs.get(LIMIT)}'
    lu_join, lu_where, lu_having = generate_cargo_load_unload_sql_filter(*args, **kwargs)
    if lu_join:
        JOIN_ARR.append(lu_join)
    # else:
    #     JOIN_ARR.append('inner join transport_cargoloadunload tc2 on tc2.cargo_id = tc.id')
    if lu_where:
        WHERE_ARR.append(lu_where)
    if DATE_FROM in kwargs and DATE_TO in kwargs:
        if not lu_join:
            JOIN_ARR.append('inner join transport_cargoloadunload tc2 on tc2.cargo_id = tc.id')
        WHERE_ARR.append(
            f"tc2.type='{LOAD}' and ((tc2.start_datetime <= '{kwargs.get(DATE_TO)}' and tc2.start_datetime >= '{kwargs.get(DATE_FROM)}') or (tc2.end_datetime <= '{kwargs.get(DATE_TO)}' and tc2.end_datetime >= '{kwargs.get(DATE_FROM)}'))"
        )
    print(lu_where)
    HAVING_STRING = lu_having
    # if COUNTRIES in kwargs or CITIES in kwargs or ZIP_CODES in kwargs:
    #     JOIN_ARR.append('inner join transport_cargoloadunload tclu on tclu.cargo_id = tc.id')
    # if 'from_countries' in kwargs:
    #     WHERE_ARR.append(f'tclu.country_id in {format_ids(kwargs.get(COUNTRIES))}')
    # if 'from_cities' in kwargs:
    #     WHERE_ARR.append(f'tc.city_id in {format_ids(kwargs.get(CITIES))}')
    # if 'from_zip_codes' in kwargs:
    #     WHERE_ARR.append(f'tc.zip_code_id in {format_ids(kwargs.get(ZIP_CODES))}')
    if VEHICLE_TYPES in kwargs:
        JOIN_ARR.append('left join transport_cargo_vehicle_types tcvt on tcvt.cargo_id = tc.id')
        WHERE_ARR.append(f'tcvt.vehicletype_id in {format_ids(kwargs.get(VEHICLE_TYPES))}')
    if VEHICLE_UPGRADES in kwargs:
        JOIN_ARR.append('inner join transport_cargo_vehicle_upgrades tcvu on tcvu.cargo_id = tc.id')
        WHERE_ARR.append(f'tcvu.vehicleupgrade_id in {format_ids(kwargs.get(VEHICLE_UPGRADES))}')
    if VEHICLE_EQUIPMENT in kwargs:
        JOIN_ARR.append('inner join transport_cargo_vehicle_equipment tlve on tlve.cargo_id = tc.id')
        WHERE_ARR.append(f"tlve.vehicleequipment_id in {format_ids(kwargs.get(VEHICLE_EQUIPMENT))}")
    if VEHICLE_FEATURES in kwargs:
        JOIN_ARR.append('inner join transport_cargo_vehicle_features tcvf on tcvf.cargo_id = tc.id')
        WHERE_ARR.append(f'tcvf.vehiclefeature_id in {format_ids(kwargs.get(VEHICLE_FEATURES))}')
    if MIN_LENGTH in kwargs:
        WHERE_ARR.append(f'tc.length >= {kwargs.get(MIN_LENGTH)}')
    if MAX_LENGTH in kwargs:
        WHERE_ARR.append(f'tc.length <= {kwargs.get(MAX_LENGTH)}')
    if MIN_WEIGHT in kwargs:
        WHERE_ARR.append(f'tc.weight >= {kwargs.get(MIN_WEIGHT)}')
    if MAX_WEIGHT in kwargs:
        WHERE_ARR.append(f'tc.weight <= {kwargs.get(MAX_WEIGHT)}')
    if AUCTION in kwargs and kwargs.get(AUCTION) == '1':
        # WHERE_ARR.append(f'tc.auction = true')
        WHERE_ARR.append(f"""
                (case
                when tc.auction = true and (now() > tc.auction_end_datetime)
            then
                false
            else
                tc.auction
            end = true)
        """)
    if MY_BID in kwargs and kwargs.get(MY_BID) == '1':
        WHERE_ARR.append(f"""
            (
            exists (
                select 1 from transport_auction tauc where tauc.account_id = (
                    select 
                        aa3.id 
                    from 
                        accounts_account aa3
                    inner join 
                        authtoken_token at1 on at1.user_id = aa3.id
                    where
                        at1.key = '{token}'
                ) and tauc.cargo_id = tc.id
            )
            )
        """)
    if (SHOW_BLOCKED_USERS in kwargs and kwargs.get(SHOW_BLOCKED_USERS) == '0') or not SHOW_BLOCKED_USERS in kwargs:
        WHERE_ARR.append(
            f'''
                (tc.company_id not in (
                    select 
                        tcbl.blocked_company_id
                    from 
                        transport_companyblocklist tcbl
                    where 
                        tcbl.my_company_id = (
                            select 
                                aa2.company_id 
                            from 
                                accounts_account aa2
                            inner join 
                                authtoken_token at on at.user_id = aa2.id
                            where
                                at.key = '{token}'
                        ) and unblocked_at is null
                ) )
            '''
        )
    JOIN_STRING = get_join_string(JOIN_ARR)
    WHERE_STRING = get_where_string(WHERE_ARR)
    query = f'''
        (
            select
                json_agg(_tc)
            from
                (
                    --Cargo Informacije
                    select
                        {sql_get_first_load_cargo_place()},
                        {sql_get_vehicle_equipment_by_cargo_id('tc.id')},
                        {SqlCargoDetailInfo('tc')},
                        {sql_get_auctions('tc.id')},
                        --Poduzece start
                        (
                            select 
                                json_agg(_tcompany)->0 "company"
                            from
                                (
                                    select 
                                        {SqlCompanyBasicInfo('tcom')},
                                        (
                                            select 
                                                COALESCE(array_agg(tcm.email), ARRAY[]::text[]) "emails"
                                            from
                                                transport_companymail tcm
                                            where 
                                                tcm.company_id = tcom.id
                                        ),
                                        (
                                            select 
                                                COALESCE(json_agg(_nums), '[]') "numbers"
                                            from 
                                                (
                                                    select 
                                                        tcn.number, tcn.type
                                                    from
                                                        transport_companynumber tcn
                                                    where 
                                                        tcn.company_id = tcom.id
                                                ) _nums
                                        )
                                    from
                                        transport_company tcom
                                    where 
                                        tcom.id = tc.company_id 
                                    group by 
                                        tcom.id

                                ) _tcompany
                        ),
                        --Poduzece kraj
                        -- Kontakt osobe start
                        (
                            select
                                COALESCE(json_agg(_tcca), '[]') "contact_accounts"
                            from
                                (
                                    select
                                        aa.id,
                                        aa.name,
                                        aa.email,
                                        aa.phone_number,
                                        aa.avatar,
                                        (
                                        select COALESCE(json_agg(account_languages), '[]') "languages"
                                        from (
                                            select tl.id, tl.name, tl.native_name
                                            from "accounts_account_languages" aal
                                            inner join "transport_language" tl on aal.language_id = tl.id
                                            where aal.account_id = aa.id
                                        )account_languages
                                    )
                                    from
                                        transport_cargo_contact_accounts tcca
                                        inner join accounts_account aa on aa.id = tcca.account_id
                                        left join accounts_account_languages aal on aal.account_id = aa.id
                                        left join transport_language tl on tl.id = aal.language_id
                                    where
                                        tcca.cargo_id = tc.id
                                    group by
                                        aa.id
                                ) _tcca
                        ),
                        --Kontakt osobe kraj
                        --Vrsta robe start 
                        (
                            select
                                COALESCE(json_agg(_tcgt), '[]') "goods_types"
                            from
                                (
                                    select
                                        tgt.id, tgt.name
                                    from
                                        transport_cargo_goods_types tcgt
                                    inner join
                                        transport_goodstype tgt on tgt.id = tcgt.goodstype_id
                                    where
                                        tcgt.cargo_id = tc.id
                                ) _tcgt
                        ),
                        --Vrsta robe kraj
                        --Znacajke vozila pocetak
                        (
                            select
                                COALESCE(json_agg(_tcvf), '[]') "vehicle_features"
                            from
                                (
                                    select
                                        tvf.id, tvf.name
                                    from
                                        transport_cargo_vehicle_features tcvf
                                    inner join
                                        transport_vehiclefeature tvf on tvf.id = tcvf.vehiclefeature_id
                                    where
                                        tcvf.cargo_id = tc.id
                                ) _tcvf
                        ) ,
                        --Znacajke vozila kraj
                        --Tipovi vozila pocetak
                        
                        (
                            select
                                COALESCE(json_agg(_tcvt), '[]') "vehicle_types"
                            from
                                (
                                    select
                                        tvt.id, tvt.name
                                    from
                                        transport_cargo_vehicle_types tcvt
                                    inner join
                                        transport_vehicletype tvt on tvt.id = tcvt.vehicletype_id
                                    where 
                                        tcvt.cargo_id = tc.id
                                ) _tcvt
                        ),
                        --Tipovi vozila kraj
                        --Nadogradnje vozila pocetak
                        
                        (
                            select
                                COALESCE(json_agg(_tcvu), '[]') "vehicle_upgrades"
                            from
                                (
                                    select
                                        tvu.id, tvu.name
                                    from
                                        transport_cargo_vehicle_upgrades tcvu
                                    inner join
                                        transport_vehicleupgrade tvu on tvu.id = tcvu.vehicleupgrade_id
                                    where 
                                        tcvu.cargo_id = tc.id
                                ) _tcvu
                        ),
                        --Nadogradnje vozila kraj
                        --Utovar i istovar start
                        (
                            select 
                                COALESCE(json_agg(_tclu), '[]') "load_unload" 
                            from
                                (
                                    select 
                                        tclu.id, 
                                        tclu.start_datetime, 
                                        tclu.end_datetime,
                                        tclu.type,
                                        json_build_object(
                                            'id', tclu.country_id,
                                            'name', tc3.name,
                                            'alpha2Code', tc3."alpha2Code"
                                        ) "country",
                                        json_build_object(
                                            'id', tclu.city_id,
                                            'name', tc2.name
                                        ) "city",
                                        json_build_object(
                                            'id', tclu.zip_code_id,
                                            'name', tz.code
                                        ) "zip_code"
                                    from 
                                        transport_cargoloadunload tclu
                                    left join
                                        transport_city tc2 on tc2.id = tclu.city_id 
                                    left join
                                        transport_country tc3 on tc3.id = tclu.country_id 
                                    left join
                                        transport_zipcode tz on tz.id = tclu.zip_code_id
                                    where
                                        tclu.cargo_id = tc.id
                                ) _tclu
                        )
                        --Utovar i istovar kraj
                    from
                        transport_cargo tc
                    {JOIN_STRING}
                    {WHERE_STRING}
                    group by tc.id
                    {HAVING_STRING}
                    order by status,sort_by
                    {LIMIT_STRING}
                ) _tc
        )

    '''
    return query


def sql_get_my_cargo(token, *args, **kwargs):
    WHERE_ARR = []
    WHERE_STRING = ''
    WHERE_ARR.append(f"""
        tc.company_id = (
                        select 
                            aa2.company_id 
                        from 
                            accounts_account aa2
                        inner join 
                            authtoken_token at on at.user_id = aa2.id
                        where
                            at.key = '{token}'
                    ) 
    """)
    if STATUS in kwargs:
        WHERE_ARR.append(f"tc.status in {format_string(kwargs.get(STATUS))}")
    else:
        WHERE_ARR.append(f"tc.status = '{ACTIVE}'")
    WHERE_STRING = get_where_string(WHERE_ARR)
    query = f'''
        (
            select
                json_agg(_tc)
            from
                (
                    --Cargo Informacije
                    select
                        {sql_get_first_load_cargo_place()},
                        {SqlCargoDetailInfo('tc')},
                        {sql_get_auctions('tc.id')},
                        {sql_get_vehicle_equipment_by_cargo_id('tc.id')},
                        --Poduzece start
                        (
                            select 
                                json_agg(_tcompany)->0 "company"
                            from
                                (
                                    select 
                                        {SqlCompanyBasicInfo('tcom')},
                                        (
                                            select 
                                                COALESCE(array_agg(tcm.email), ARRAY[]::text[]) "emails"
                                            from
                                                transport_companymail tcm
                                            where 
                                                tcm.company_id = tcom.id
                                        ),
                                        (
                                            select 
                                                COALESCE(json_agg(_nums), '[]') "numbers"
                                            from 
                                                (
                                                    select 
                                                        tcn.number, tcn.type
                                                    from
                                                        transport_companynumber tcn
                                                    where 
                                                        tcn.company_id = tcom.id
                                                ) _nums
                                        )
                                    from
                                        transport_company tcom
                                    where 
                                        tcom.id = tc.company_id 
                                    group by 
                                        tcom.id

                                ) _tcompany
                        ),
                        --Poduzece kraj
                        -- Kontakt osobe start
                        (
                            select
                                COALESCE(json_agg(_tcca), '[]') "contact_accounts"
                            from
                                (
                                    select
                                        aa.id,
                                        aa.name,
                                        aa.email,
                                        aa.phone_number,
                                        aa.avatar,
                                        (
                                        select COALESCE(json_agg(account_languages), '[]') "languages"
                                        from (
                                            select tl.id, tl.name, tl.native_name
                                            from "accounts_account_languages" aal
                                            inner join "transport_language" tl on aal.language_id = tl.id
                                            where aal.account_id = aa.id
                                        )account_languages
                                    )
                                    from
                                        transport_cargo_contact_accounts tcca
                                        inner join accounts_account aa on aa.id = tcca.account_id
                                        left join accounts_account_languages aal on aal.account_id = aa.id
                                        left join transport_language tl on tl.id = aal.language_id
                                    where
                                        tcca.cargo_id = tc.id
                                    group by
                                        aa.id
                                ) _tcca
                        ),
                        --Kontakt osobe kraj
                                                --Vrsta robe start 
                        (
                            select
                                COALESCE(json_agg(_tcgt), '[]') "goods_types"
                            from
                                (
                                    select
                                        tgt.id, tgt.name
                                    from
                                        transport_cargo_goods_types tcgt
                                    inner join
                                        transport_goodstype tgt on tgt.id = tcgt.goodstype_id
                                    where
                                        tcgt.cargo_id = tc.id
                                ) _tcgt
                        ),
                        --Vrsta robe kraj
                        --Znacajke vozila pocetak
                        (
                            select
                                COALESCE(json_agg(_tcvf), '[]') "vehicle_features"
                            from
                                (
                                    select
                                        tvf.id, tvf.name
                                    from
                                        transport_cargo_vehicle_features tcvf
                                    inner join
                                        transport_vehiclefeature tvf on tvf.id = tcvf.vehiclefeature_id
                                    where
                                        tcvf.cargo_id = tc.id
                                ) _tcvf
                        ) ,
                        --Znacajke vozila kraj
                        --Tipovi vozila pocetak
                        
                        (
                            select
                                COALESCE(json_agg(_tcvt), '[]') "vehicle_types"
                            from
                                (
                                    select
                                        tvt.id, tvt.name
                                    from
                                        transport_cargo_vehicle_types tcvt
                                    inner join
                                        transport_vehicletype tvt on tvt.id = tcvt.vehicletype_id
                                    where 
                                        tcvt.cargo_id = tc.id
                                ) _tcvt
                        ),
                        --Tipovi vozila kraj
                        --Nadogradnje vozila pocetak
                        
                        (
                            select
                                COALESCE(json_agg(_tcvu), '[]') "vehicle_upgrades"
                            from
                                (
                                    select
                                        tvu.id, tvu.name
                                    from
                                        transport_cargo_vehicle_upgrades tcvu
                                    inner join
                                        transport_vehicleupgrade tvu on tvu.id = tcvu.vehicleupgrade_id
                                    where 
                                        tcvu.cargo_id = tc.id
                                ) _tcvu
                        ),
                        --Nadogradnje vozila kraj
                        --Utovar i istovar start
                        (
                            select 
                                COALESCE(json_agg(_tclu), '[]') "load_unload" 
                            from
                                (
                                    select 
                                        tclu.id, 
                                        tclu.start_datetime, 
                                        tclu.end_datetime,
                                        tclu.type,
                                        json_build_object(
                                            'id', tclu.country_id,
                                            'name', tc3.name,
                                            'alpha2Code', tc3."alpha2Code"
                                        ) "country",
                                        json_build_object(
                                            'id', tclu.city_id,
                                            'name', tc2.name
                                        ) "city",
                                        json_build_object(
                                            'id', tclu.zip_code_id,
                                            'name', tz.code
                                        ) "zip_code"
                                    from 
                                        transport_cargoloadunload tclu
                                    left join
                                        transport_city tc2 on tc2.id = tclu.city_id 
                                    left join
                                        transport_country tc3 on tc3.id = tclu.country_id 
                                    left join
                                        transport_zipcode tz on tz.id = tclu.zip_code_id
                                    where
                                        tclu.cargo_id = tc.id
                                ) _tclu
                        )
                        --Utovar i istovar kraj
                    from
                        transport_cargo tc
                    {WHERE_STRING}
                    order by status, sort_by
                        
                ) _tc
        )

    '''

    return query


def sql_get_my_loading_spaces(token, *args, **kwargs):
    WHERE_ARR = []
    WHERE_STRING = ''
    WHERE_ARR.append(f"""
                    	tc.company_id = (
                            select 
                                aa2.company_id 
                            from 
                                accounts_account aa2
                            inner join 
                                authtoken_token at on at.user_id = aa2.id
                            where
                                at.key = '{token}'
                        ) 
        """)
    if STATUS in kwargs:
        WHERE_ARR.append(f"tc.status in {format_string(kwargs.get(STATUS))}")
    else:
        WHERE_ARR.append(f"tc.status = '{ACTIVE}'")
    WHERE_STRING = get_where_string(WHERE_ARR)
    query = f'''
        (select
                json_agg(_tl)
            from
                (
                    --loading space Informacije
                    select
                        {sql_get_first_loading_space_starting_point()},
                        tc.id,
                        tc.created_at,
                        tc.vehicle_length,
                        tc.vehicle_load_capacity,
                        tc.connected_vehicle_length,
                        tc.connected_vehicle_load_capacity,
                        tc.vehicle_note,
                        tc.status,
                        {sql_get_vehicle_equipment_by_loading_space_id('tc.id')},
                         (
                            select
                                COALESCE(json_agg(_tcvt), '[]') "vehicle_type"
                            from
                                (
                                    select
                                        tv.id, tv.name
                                    from
                                        transport_vehicletype tv
                                    where 
                                        tv.id = tc.vehicle_type_id 
                                ) _tcvt
                        ),
                        --Poduzece start
                        (
                            select 
                                json_agg(_tcompany)->0 "company"
                            from
                                (
                                    select 
                                        {SqlCompanyBasicInfo('tcom')},
                                        (
                                            select 
                                                COALESCE(array_agg(tcm.email), ARRAY[]::text[]) "emails"
                                            from
                                                transport_companymail tcm
                                            where 
                                                tcm.company_id = tcom.id
                                        ),
                                        (
                                            select 
                                                COALESCE(json_agg(_nums), '[]') "numbers"
                                            from 
                                                (
                                                    select 
                                                        tcn.number, tcn.type
                                                    from
                                                        transport_companynumber tcn
                                                    where 
                                                        tcn.company_id = tcom.id
                                                ) _nums
                                        )
                                    from
                                        transport_company tcom
                                    where 
                                        tcom.id = tc.company_id 
                                    group by 
                                        tcom.id

                                ) _tcompany
                        ),
                        --Poduzece kraj
                        -- Kontakt osobe start
                        (
                            select
                                COALESCE(json_agg(_tcca), '[]') "contact_accounts"
                            from
                                (
                                    select
                                        aa.id,
                                        aa.name,
                                        aa.email,
                                        aa.phone_number,
                                        aa.avatar,
                                        (
                                        select COALESCE(json_agg(account_languages), '[]') "languages"
                                        from (
                                            select tl.id, tl.name, tl.native_name
                                            from "accounts_account_languages" aal
                                            inner join "transport_language" tl on aal.language_id = tl.id
                                            where aal.account_id = aa.id
                                        )account_languages
                                    )
                                    from
                                        transport_loadingspace_contact_accounts tcca
                                        inner join accounts_account aa on aa.id = tcca.account_id
                                        left join accounts_account_languages aal on aal.account_id = aa.id
                                        left join transport_language tl on tl.id = aal.language_id
                                    where
                                        tcca.loadingspace_id = tc.id
                                    group by
                                        aa.id
                                ) _tcca
                        ),
                        --Kontakt osobe kraj
                        --Znacajke vozila pocetak
                        (
                            select
                                COALESCE(json_agg(_tcvf), '[]') "vehicle_features"
                            from
                                (
                                    select
                                        tvf.id, tvf.name
                                    from
                                        transport_loadingspace_vehicle_features tcvf
                                    inner join
                                        transport_vehiclefeature tvf on tvf.id = tcvf.vehiclefeature_id
                                    where
                                        tcvf.loadingspace_id = tc.id
                                ) _tcvf
                        ) ,
                        --Znacajke vozila kraj
                        --Nadogradnje vozila pocetak
                        
                        (
                            select
                                COALESCE(json_agg(_tcvu), '[]') "vehicle_upgrades"
                            from
                                (
                                    select
                                        tvu.id, tvu.name
                                    from
                                        transport_loadingspace_vehicle_upgrades tcvu
                                    inner join
                                        transport_vehicleupgrade tvu on tvu.id = tcvu.vehicleupgrade_id
                                    where 
                                        tcvu.loadingspace_id = tc.id
                                ) _tcvu
                        ),
                        --Nadogradnje vozila kraj
						(
                            select 
                                COALESCE(json_agg(_spd), '[]') "starting_point_destination" 
                            from
                                (
                                    select 
                                        ts.id, 
                                        ts.departure_datetime, 
                                        ts.type,
                                        json_build_object(
                                            'id', ts.country_id,
                                            'name', tc3.name,
                                            'alpha2Code', tc3."alpha2Code"
                                        ) "country",
                                        json_build_object(
                                            'id', ts.city_id,
                                            'name', tc2.name
                                        ) "city",
                                        json_build_object(
                                            'id', ts.zip_code_id,
                                            'name', tz.code
                                        ) "zip_code"
                                    from 
                                        transport_startingpointdestination ts
                                    left join
                                        transport_city tc2 on tc2.id = ts.city_id 
                                    left join
                                        transport_country tc3 on tc3.id = ts.country_id 
                                    left join
                                        transport_zipcode tz on tz.id = ts.zip_code_id
                                    where
                                        ts.loading_space_id = tc.id
                                ) _spd
                        )
                    from
                        transport_loadingspace tc
                       {WHERE_STRING}
                       order by status, sort_by
                ) _tl);
    '''
    return query


def sql_get_my_stocks(token, *args, **kwargs):
    WHERE_ARR = []
    WHERE_STRING = ''
    WHERE_ARR.append(f"""
                        ts.company_id = (
                        select 
                            aa2.company_id 
                        from 
                            accounts_account aa2
                        inner join 
                            authtoken_token at on at.user_id = aa2.id
                        where
                            at.key = '{token}'
                    ) 
            """)
    if STATUS in kwargs:
        WHERE_ARR.append(f"ts.status in {format_string(kwargs.get(STATUS))}")
    else:
        WHERE_ARR.append(f"ts.status = '{ACTIVE}'")
    WHERE_STRING = get_where_string(WHERE_ARR)
    query = f'''
        select 
            json_agg(_s)  
        from
            (
                select 
                    ts.id,
                    ts.start_datetime,
                    ts.end_datetime,
                    ts.min_area ,
                    ts.max_area,
                    ts.created_at ,
                    ts.status,
                    ts.stock_types,
                    ts.stock_equipment,
                    (
                		select 
                			json_agg(countries)->0 "country"
                		from
                			(
                				select 
                					tc.id, 
                					tc.name, 
                					tc."alpha2Code"
                				from
                					transport_country tc
                				where 
                				    tc.id = ts.country_id
                			) countries
                	),
                    -- Kontakt osobe start
                    (
                        select
                            COALESCE(json_agg(_tcca), '[]') "contact_accounts"
                        from
                            (
                                select
                                    aa.id,
                                    aa.name,
                                    aa.email,
                                    aa.phone_number,
                                    aa.avatar,
                                    (
                                        select COALESCE(json_agg(account_languages), '[]') "languages"
                                        from (
                                            select tl.id, tl.name, tl.native_name
                                            from "accounts_account_languages" aal
                                            inner join "transport_language" tl on aal.language_id = tl.id
                                            where aal.account_id = aa.id
                                        )account_languages
                                    )
                                from
                                    transport_stock_contact_accounts tcca
                                    inner join accounts_account aa on aa.id = tcca.account_id
                                    left join accounts_account_languages aal on aal.account_id = aa.id
                                    left join transport_language tl on tl.id = aal.language_id
                                where
                                    tcca.stock_id = ts.id
                                group by
                                    aa.id
                            ) _tcca
                    ),
                    --Kontakt osobe kraj
                    --Poduzece start
                    (
                        select 
                            json_agg(_tcompany)->0 "company"
                        from
                            (
                                select 
                                    {SqlCompanyBasicInfo('tcom')},
                                    (
                                        select 
                                            COALESCE(array_agg(tcm.email), ARRAY[]::text[]) "emails"
                                        from
                                            transport_companymail tcm
                                        where 
                                            tcm.company_id = tcom.id
                                    ),
                                    (
                                        select 
                                            COALESCE(json_agg(_nums), '[]') "numbers"
                                        from 
                                            (
                                                select 
                                                    tcn.number, tcn.type
                                                from
                                                    transport_companynumber tcn
                                                where 
                                                    tcn.company_id = tcom.id
                                            ) _nums
                                    )
                                from
                                    transport_company tcom
                                where 
                                    tcom.id = ts.company_id 
                                group by 
                                    tcom.id

                            ) _tcompany
                    )
                    --Poduzece kraj
                from 
                    transport_stock ts  
                {WHERE_STRING}
                order by ts.status, ts.start_datetime
                    
            )_s
    '''
    return query


def sql_get_loading_spaces_list(token, *args, **kwargs):
    JOIN_ARR = []
    JOIN_STRING = ''
    WHERE_ARR = []
    WHERE_STRING = ''
    LIMIT_STRING = ''
    HAVING_STRING = ''
    # WHERE_ARR.append(f"tc.status = '{ACTIVE}'")
    WHERE_ARR.append(f"(tc.closed_at is null or (tc.closed_at > now() - INTERVAL '7 days'))")
    if NEXT_CURSOR in kwargs:
        WHERE_ARR.append(f"{sql_get_first_loading_space_starting_point()} > '{kwargs.get(NEXT_CURSOR)}'")
        # WHERE_ARR.append(f'tc.id < {kwargs.get(NEXT_CURSOR)}')
    if LIMIT in kwargs:
        LIMIT_STRING = f'LIMIT {kwargs.get(LIMIT)}'
    lu_join, lu_where, lu_having = generate_loading_space_starting_point_destination_sql_filter(*args, **kwargs)
    if lu_join:
        JOIN_ARR.append(lu_join)
    if lu_where:
        WHERE_ARR.append(lu_where)
    if DATE_FROM in kwargs and DATE_TO in kwargs:
        if not lu_join:
            JOIN_ARR.append('inner join transport_startingpointdestination tc2 on tc2.loading_space_id = tc.id')
        WHERE_ARR.append(
            f"tc2.type='{STARTING}' and (tc2.departure_datetime <= '{kwargs.get(DATE_TO)}' and tc2.departure_datetime >= '{kwargs.get(DATE_FROM)}')"
        )
    print(lu_where)
    HAVING_STRING = lu_having
    # if COUNTRIES in kwargs:
    #     WHERE_ARR.append(f'tc.country_id in {format_ids(kwargs.get(COUNTRIES))}')
    # if CITIES in kwargs:
    #     WHERE_ARR.append(f'tc.city_id in {format_ids(kwargs.get(CITIES))}')
    # if ZIP_CODES in kwargs:
    #     WHERE_ARR.append(f'tc.zip_code_id in {format_ids(kwargs.get(ZIP_CODES))}')
    if VEHICLE_TYPE in kwargs:
        WHERE_ARR.append(f'tc.vehicle_type_id in {format_ids(kwargs.get(VEHICLE_TYPE))}')
    if VEHICLE_UPGRADES in kwargs:
        JOIN_ARR.append('inner join transport_loadingspace_vehicle_upgrades tcvu on tcvu.loadingspace_id = tc.id')
        WHERE_ARR.append(f'tcvu.vehicleupgrade_id in {format_ids(kwargs.get(VEHICLE_UPGRADES))}')
    if VEHICLE_EQUIPMENT in kwargs:
        JOIN_ARR.append('inner join transport_loadingspace_vehicle_equipment tlve on tlve.loadingspace_id = tc.id')
        WHERE_ARR.append(f"tlve.vehicleequipment_id in {format_ids(kwargs.get(VEHICLE_EQUIPMENT))}")
    if VEHICLE_FEATURES in kwargs:
        JOIN_ARR.append('inner join transport_loadingspace_vehicle_features tcvf on tcvf.loadingspace_id = tc.id')
        WHERE_ARR.append(f'tcvf.vehiclefeature_id in {format_ids(kwargs.get(VEHICLE_FEATURES))}')
    if MIN_LENGTH in kwargs:
        WHERE_ARR.append(f'tc.vehicle_length >= {kwargs.get(MIN_LENGTH)}')
    if MAX_LENGTH in kwargs:
        WHERE_ARR.append(f'tc.vehicle_length <= {kwargs.get(MAX_LENGTH)}')
    # if MIN_WEIGHT in kwargs:
    #     WHERE_ARR.append(f'tc.weight >= {kwargs.get(MIN_WEIGHT)}')
    # if MAX_WEIGHT in kwargs:
    #     WHERE_ARR.append(f'tc.weight <= {kwargs.get(MAX_WEIGHT)}')
    if (SHOW_BLOCKED_USERS in kwargs and kwargs.get(SHOW_BLOCKED_USERS) == '0') or not SHOW_BLOCKED_USERS in kwargs:
        WHERE_ARR.append(
            f'''
                (tc.company_id not in (
                    select 
                        tcbl.blocked_company_id
                    from 
                        transport_companyblocklist tcbl
                    where 
                        tcbl.my_company_id = (
                            select 
                                aa2.company_id 
                            from 
                                accounts_account aa2
                            inner join 
                                authtoken_token at on at.user_id = aa2.id
                            where
                                at.key = '{token}'
                        ) and unblocked_at is null
                ) )
            '''
        )
    JOIN_STRING = get_join_string(JOIN_ARR)
    WHERE_STRING = get_where_string(WHERE_ARR)
    query = f'''
        select
                json_agg(_tl)
            from
                (
                    --loading space Informacije
                    select
                        {sql_get_first_loading_space_starting_point()},
                        tc.id,
                        tc.created_at,
                        tc.vehicle_length,
                        tc.vehicle_load_capacity,
                        tc.connected_vehicle_length,
                        tc.connected_vehicle_load_capacity,
                        tc.vehicle_note,
                        tc.status,
                        {sql_get_vehicle_equipment_by_loading_space_id('tc.id')},
                         (
                            select
                                COALESCE(json_agg(_tcvt), '[]') "vehicle_type"
                            from
                                (
                                    select
                                        tv.id, tv.name
                                    from
                                        transport_vehicletype tv
                                    where 
                                        tv.id = tc.vehicle_type_id 
                                ) _tcvt
                        ),
                        --Poduzece start
                        (
                            select 
                                json_agg(_tcompany)->0 "company"
                            from
                                (
                                    select 
                                        {SqlCompanyBasicInfo('tcom')},
                                        (
                                            select 
                                                COALESCE(array_agg(tcm.email), ARRAY[]::text[]) "emails"
                                            from
                                                transport_companymail tcm
                                            where 
                                                tcm.company_id = tcom.id
                                        ),
                                        (
                                            select 
                                                COALESCE(json_agg(_nums), '[]') "numbers"
                                            from 
                                                (
                                                    select 
                                                        tcn.number, tcn.type
                                                    from
                                                        transport_companynumber tcn
                                                    where 
                                                        tcn.company_id = tcom.id
                                                ) _nums
                                        )
                                    from
                                        transport_company tcom
                                    where 
                                        tcom.id = tc.company_id 
                                    group by 
                                        tcom.id

                                ) _tcompany
                        ),
                        --Poduzece kraj
                        -- Kontakt osobe start
                        (
                            select
                                COALESCE(json_agg(_tcca), '[]') "contact_accounts"
                            from
                                (
                                    select
                                        aa.id,
                                        aa.name,
                                        aa.email,
                                        aa.phone_number,
                                        aa.avatar,
                                        (
                                        select COALESCE(json_agg(account_languages), '[]') "languages"
                                        from (
                                            select tl.id, tl.name, tl.native_name
                                            from "accounts_account_languages" aal
                                            inner join "transport_language" tl on aal.language_id = tl.id
                                            where aal.account_id = aa.id
                                        )account_languages
                                    )
                                    from
                                        transport_loadingspace_contact_accounts tcca
                                        inner join accounts_account aa on aa.id = tcca.account_id
                                        left join accounts_account_languages aal on aal.account_id = aa.id
                                        left join transport_language tl on tl.id = aal.language_id
                                    where
                                        tcca.loadingspace_id = tc.id
                                    group by
                                        aa.id
                                ) _tcca
                        ),
                        --Kontakt osobe kraj
                        --Nadogradnje vozila pocetak
                        
                        (
                            select
                                COALESCE(json_agg(_tcvu), '[]') "vehicle_upgrades"
                            from
                                (
                                    select
                                        tvu.id, tvu.name
                                    from
                                        transport_loadingspace_vehicle_upgrades tcvu
                                    inner join
                                        transport_vehicleupgrade tvu on tvu.id = tcvu.vehicleupgrade_id
                                    where 
                                        tcvu.loadingspace_id = tc.id
                                ) _tcvu
                        ),
                        --Nadogradnje vozila kraj
						(
                            select 
                                COALESCE(json_agg(_spd), '[]') "starting_point_destination" 
                            from
                                (
                                    select 
                                        ts.id, 
                                        ts.departure_datetime, 
                                        ts.type,
                                        ts.within_km,
                                        json_build_object(
                                            'id', ts.country_id,
                                            'name', tc3.name,
                                            'alpha2Code', tc3."alpha2Code"
                                        ) "country",
                                        json_build_object(
                                            'id', ts.city_id,
                                            'name', tc2.name
                                        ) "city",
                                        json_build_object(
                                            'id', ts.zip_code_id,
                                            'name', tz.code
                                        ) "zip_code"
                                    from 
                                        transport_startingpointdestination ts
                                    left join
                                        transport_city tc2 on tc2.id = ts.city_id 
                                    left join
                                        transport_country tc3 on tc3.id = ts.country_id 
                                    left join
                                        transport_zipcode tz on tz.id = ts.zip_code_id
                                    where
                                        ts.loading_space_id = tc.id
                                ) _spd
                        )
                    from
                        transport_loadingspace tc
                    {JOIN_STRING}
                    {WHERE_STRING}
                    group by tc.id
                    {HAVING_STRING}
                    order by status,sort_by
                    {LIMIT_STRING}
                ) _tl
    '''
    # f = open('query-test.txt', 'w+')
    # f.write(query)
    # f.close()
    return query


def sql_get_stocks_list(token, *args, **kwargs):
    JOIN_ARR = []
    JOIN_STRING = ''
    WHERE_ARR = []
    WHERE_STRING = ''
    LIMIT_STRING = ''
    # WHERE_ARR.append(f"ts.status = '{ACTIVE}'")
    WHERE_ARR.append(f"(ts.closed_at is null or (ts.closed_at > now() - INTERVAL '7 days'))")
    if NEXT_CURSOR in kwargs:
        WHERE_ARR.append(f"ts.start_datetime > '{kwargs.get(NEXT_CURSOR)}'")
        # WHERE_ARR.append(f'ts.id < {kwargs.get(NEXT_CURSOR)}')
    if LIMIT in kwargs:
        LIMIT_STRING = f'LIMIT {kwargs.get(LIMIT)}'
    if COUNTRIES in kwargs:
        WHERE_ARR.append(f'ts.country_id in {format_ids(kwargs.get(COUNTRIES))}')
    if CITIES in kwargs:
        WHERE_ARR.append(f'ts.city_id in {format_ids(kwargs.get(CITIES))}')
    if ZIP_CODES in kwargs:
        WHERE_ARR.append(f'ts.zip_code_id in {format_ids(kwargs.get(ZIP_CODES))}')
    if DATE in kwargs:
        WHERE_ARR.append(f"'{kwargs.get(DATE)}' >= ts.start_datetime and '{kwargs.get(DATE)}' <= ts.end_datetime")
    # if STOCK_TYPES in kwargs:
    #     JOIN_ARR.append('inner join transport_stock_stock_types tsst on tsst.stock_id = ts.id')
    #     WHERE_ARR.append(f'tsst.stocktype_id in {format_ids(kwargs.get(STOCK_TYPES))}')
    # if STOCK_EQUIPMENTS in kwargs:
    #     JOIN_ARR.append('inner join transport_stock_stock_equipments tsse on tsse.stock_id = ts.id')
    #     WHERE_ARR.append(f'tsse.stockequipment_id in {format_ids(kwargs.get(STOCK_EQUIPMENTS))}')
    # if MIN_AREA in kwargs:
    #     WHERE_ARR.append(f'ts.min_area <= {kwargs.get(MIN_AREA)}')
    # if MAX_AREA in kwargs:
    #     WHERE_ARR.append(f'ts.max_area >= {kwargs.get(MAX_AREA)}')
    if (SHOW_BLOCKED_USERS in kwargs and kwargs.get(SHOW_BLOCKED_USERS) == '0') or not SHOW_BLOCKED_USERS in kwargs:
        WHERE_ARR.append(
            f'''
                (ts.company_id not in (
                    select 
                        tcbl.blocked_company_id
                    from 
                        transport_companyblocklist tcbl
                    where 
                        tcbl.my_company_id = (
                            select 
                                aa2.company_id 
                            from 
                                accounts_account aa2
                            inner join 
                                authtoken_token at on at.user_id = aa2.id
                            where
                                at.key = '{token}'
                        ) and unblocked_at is null
                ) )
            '''
        )
    JOIN_STRING = get_join_string(JOIN_ARR)
    WHERE_STRING = get_where_string(WHERE_ARR)
    query = f'''
        select 
	json_agg(_s)
    from
        (
            select 
                ts.id,
                ts.start_datetime,
                ts.end_datetime,
                ts.min_area ,
                ts.max_area,
                ts.created_at ,
                ts.status,
                ts.stock_equipment,
                ts.stock_types,
                (
                		select 
                			json_agg(countries)->0 "country"
                		from
                			(
                				select 
                					tc.id, 
                					tc.name, 
                					tc."alpha2Code"
                				from
                					transport_country tc
                				where 
                				    tc.id = ts.country_id
                			) countries
                	),
                	(
                		select
                			json_agg(cities)->0 "city"
                		from
                			(
                				select 
                					tc2.id, tc2.name, tc2.country_id
                				from 
                					transport_city tc2
                				where
                				    tc2.id = ts.city_id
                			)cities
                	),
                	(
                		select 
                			json_agg(zip_codes)->0 "zip_code" 
                		from
                			(
                				select 
                					tz.id, tz.code "name", tz.code, tz.city_id
                				from 
                					transport_zipcode tz
                				where
                				    tz.id = ts.zip_code_id
                			)zip_codes
                	),
                -- Kontakt osobe start
                (
                    select
                        COALESCE(json_agg(_tcca), '[]') "contact_accounts"
                    from
                        (
                            select
                                aa.id,
                                aa.name,
                                aa.email,
                                aa.phone_number,
                                aa.avatar,
                                (
                                        select COALESCE(json_agg(account_languages), '[]') "languages"
                                        from (
                                            select tl.id, tl.name, tl.native_name
                                            from "accounts_account_languages" aal
                                            inner join "transport_language" tl on aal.language_id = tl.id
                                            where aal.account_id = aa.id
                                        )account_languages
                                    )
                            from
                                transport_stock_contact_accounts tcca
                                inner join accounts_account aa on aa.id = tcca.account_id
                                left join accounts_account_languages aal on aal.account_id = aa.id
                                left join transport_language tl on tl.id = aal.language_id
                            where
                                tcca.stock_id = ts.id
                            group by
                                aa.id
                        ) _tcca
                ),
                --Kontakt osobe kraj
                --Poduzece start
                (
                    select 
                        json_agg(_tcompany)->0 "company"
                    from
                        (
                            select 
                                {SqlCompanyBasicInfo('tcom')},
                                (
                                    select 
                                        COALESCE(array_agg(tcm.email), ARRAY[]::text[]) "emails"
                                    from
                                        transport_companymail tcm
                                    where 
                                        tcm.company_id = tcom.id
                                ),
                                (
                                    select 
                                        COALESCE(json_agg(_nums), '[]') "numbers"
                                    from 
                                        (
                                            select 
                                                tcn.number, tcn.type
                                            from
                                                transport_companynumber tcn
                                            where 
                                                tcn.company_id = tcom.id
                                        ) _nums
                                )
                            from
                                transport_company tcom
                            where 
                                tcom.id = ts.company_id 
                            group by 
                                tcom.id

                        ) _tcompany
                )
                --Poduzece kraj
            from 
                transport_stock ts  
            {JOIN_STRING}
            {WHERE_STRING}
            group by ts.id
            order by ts.status, ts.start_datetime
            {LIMIT_STRING}
        )_s
    '''
    return query

def sql_get_company_cover_countries(company_id):
    query = f"""
        (
            select 
                COALESCE(json_agg(_cover_countries), '[]') "cover_countries"
            from
                (
                    select 
                        tcoun.id,
                        tcoun.name
                    from
                        transport_company_cover_countries tccc
                    inner join
                        transport_country tcoun on tcoun.id = tccc.country_id
                    where 
                        tccc.company_id = {company_id}

                ) _cover_countries
        )
    """
    return query

def sql_get_companies_to_confirm(*args, **kwargs):
    WHERE_ARR = []
    WHERE_STRING = ''
    if STATUS in kwargs:
        WHERE_ARR.append(f"tc.status in {format_string(kwargs.get(STATUS))}")
    else:
        WHERE_ARR.append(f"tc.status = '{NEED_CONFIRM}'")
    WHERE_STRING = get_where_string(WHERE_ARR)
    query = f'''
            select
                json_agg(_all)
            from
                (
                    select 
                        {SqlCompanyBasicInfo('tc')},
                        {sql_get_company_cover_countries('tc.id')},
                        json_build_object(
                            'id', tc2.id,
                            'name', tc2.name,
                            'alpha2Code', tc2."alpha2Code"
                        ) "country",
                        json_build_object(
                            'id', tc3.id,
                            'name', tc3.name
                        ) "city",
                        json_build_object(
                            'id', tz.id,
                            'code', tz.code,
                            'name', tz.code
                        ) "zip_code"
                    from
                        transport_company tc
                    left join
                        transport_country tc2 on tc2.id = tc.country_id
                    left join
                        transport_city tc3 on tc3.id = tc.city_id
                    left join
                        transport_zipcode tz on tz.id = tc.zip_code_id
                    {WHERE_STRING}
                    order by tc.created_at
                ) _all
        '''
    return query


def sql_get_company_list(token, *args, **kwargs):
    JOIN_ARR = []
    JOIN_STRING = ''
    WHERE_ARR = []
    WHERE_STRING = ''
    LIMIT_STRING = ''
    WHERE_ARR.append('tc.is_active=true')
    # WHERE_ARR.append(f"tc.status = '{ACTIVE}'")
    if STATUS in kwargs:
        WHERE_ARR.append(f"tc.status in {format_string(kwargs.get(STATUS))}")
    else:
        WHERE_ARR.append(f"tc.status = '{ACTIVE}'")
    if NEXT_CURSOR in kwargs:
        WHERE_ARR.append(f"tc.name > '{kwargs.get(NEXT_CURSOR)}'")
    if LIMIT in kwargs:
        LIMIT_STRING = f'LIMIT {kwargs.get(LIMIT)}'
    if COUNTRIES in kwargs:
        WHERE_ARR.append(f'tc.country_id in {format_ids(kwargs.get(COUNTRIES))}')
    if CITIES in kwargs:
        WHERE_ARR.append(f'tc.city_id in {format_ids(kwargs.get(CITIES))}')
    if ZIP_CODES in kwargs:
        WHERE_ARR.append(f'tc.zip_code_id in {format_ids(kwargs.get(ZIP_CODES))}')
    if GOODS_FORMS in kwargs:
        JOIN_ARR.append(f'inner join transport_company_goods_forms tcgf on tcgf.company_id = tc.id')
        WHERE_ARR.append(f'tcgf.goodsform_id in {format_ids(kwargs.get(GOODS_FORMS))}')
    if GOODS_TYPES in kwargs:
        JOIN_ARR.append(f'inner join transport_company_goods_types tcgt on tcgt.company_id = tc.id')
        WHERE_ARR.append(f'tcgt.goodstype_id in {format_ids(kwargs.get(GOODS_TYPES))}')
    if TRANSPORT_TYPES in kwargs:
        JOIN_ARR.append(f'inner join transport_company_transport_types tctt on tctt.company_id = tc.id')
        WHERE_ARR.append(f'tctt.transporttype_id in {format_ids(kwargs.get(TRANSPORT_TYPES))}')
    if OWN_VEHICLES in kwargs:
        WHERE_ARR.append(f'tc.own_vehicles = {get_bool_from_string(kwargs.get(OWN_VEHICLES))}')
    if VEHICLE_TYPES in kwargs:
        JOIN_ARR.append(f'inner join transport_company_vehicle_types tcvt on tcvt.company_id = tc.id')
        WHERE_ARR.append(f'tcvt.vehicletype_id in {format_ids(kwargs.get(VEHICLE_TYPES))}')
    if VEHICLE_UPGRADES in kwargs:
        JOIN_ARR.append(f'inner join transport_company_vehicle_upgrades tcvu on tcvu.company_id = tc.id')
        WHERE_ARR.append(f'tcvu.vehicleupgrade_id in {format_ids(kwargs.get(VEHICLE_UPGRADES))}')
    if LOADING_SYSTEMS in kwargs:
        JOIN_ARR.append(f'inner join transport_company_loading_systems tcls on tcls.company_id = tc.id')
        WHERE_ARR.append(f'tcls.loadingsystem_id in {format_ids(kwargs.get(LOADING_SYSTEMS))}')
    WHERE_STRING = get_where_string(WHERE_ARR)
    JOIN_STRING = get_join_string(JOIN_ARR)
    query = f'''
        with account_id as ( 
            select user_id from authtoken_token where key = '{token}'
        ),
        blocked_ids as (
            select 
                tcbl.blocked_company_id
            from
                transport_companyblocklist tcbl
            where 
                tcbl.unblocked_at is null and 
                tcbl.my_company_id = (
                    select 
                        acc.company_id
                    from 
                        accounts_account acc 
                    where 
                        acc.id = (select user_id from account_id)
                )
        )
        select
            json_agg(_all)
        from
            (
                select 
                    {SqlCompanyBasicInfo('tc')},
                    {sql_get_company_cover_countries('tc.id')},
                    case 
                        when 
                            tc.id in (select blocked_company_id from blocked_ids)
                        then 
                            true
                        else
                            false
                        end "blocked",
                    
                    json_build_object(
                        'id', tc2.id,
                        'name', tc2.name,
                        'alpha2Code', tc2."alpha2Code"
                    ) "country",
                    json_build_object(
                        'id', tc3.id,
                        'name', tc3.name
                    ) "city",
                    json_build_object(
                        'id', tz.id,
                        'code', tz.code,
                        'name', tz.code
                    ) "zip_code"
                from
                    transport_company tc
                left join
                    transport_country tc2 on tc2.id = tc.country_id
                left join
                    transport_city tc3 on tc3.id = tc.city_id
                left join
                    transport_zipcode tz on tz.id = tc.zip_code_id
                {JOIN_STRING}
                {WHERE_STRING}
                order by tc.name
                {LIMIT_STRING}
            ) _all
    '''
    return query

def sql_company_places_join(tbl):
    query = f"""
        left join
            transport_country tctr on tctr.id = {tbl}.country_id
        left join
            transport_city tcty on tcty.id = {tbl}.city_id
        left join
            transport_zipcode tzip on tzip.id = {tbl}.zip_code_id
    """
    return query

def sql_get_company_places():
    query = """
    json_build_object(
        'id', tctr.id,
        'name', tctr.name,
        'alpha2Code', tctr."alpha2Code"
    ) "country",
    json_build_object(
        'id', tcty.id,
        'name', tcty.name
    ) "city",
    json_build_object(
        'id', tzip.id,
        'code', tzip.code,
        'name', tzip.code
    ) "zip_code"
    """
    return query

def sql_get_company_details(company_id):
    query = f'''
        with 
        blocked_ids as (
            select 
                tcbl.blocked_company_id
            from
                transport_companyblocklist tcbl
            where 
                tcbl.unblocked_at is null and 
                tcbl.my_company_id = {company_id}
        )
        select 
	        json_agg(_tc)->0 "company"
        from 
            (
                select 
                    {SqlCompanyBasicInfo('tc')},
                    {sql_get_company_cover_countries('tc.id')},
                    case 
                        when 
                            tc.id in (select blocked_company_id from blocked_ids)
                        then 
                            true
                        else
                            false
                        end "blocked",
                    json_build_object(
                        'id', tc2.id,
                        'name', tc2.name,
                        'alpha2Code', tc2."alpha2Code"
                    ) "country",
                    json_build_object(
                        'id', tc3.id,
                        'name', tc3.name
                    ) "city",
                    json_build_object(
                        'id', tz.id,
                        'code', tz.code,
                        'name', tz.code
                    ) "zip_code",
                    (
                        select 
                            COALESCE(json_agg(_documents), '[]') "company_documents"
                        from
                            (
                                select 
                                    tcd.id,
                                    tcd.title,
                                    tcd.path
                                from 
                                    transport_companydocument tcd 
                                where 
                                    tcd.is_active = true and tcd.company_id = tc.id 
                            ) _documents 
                    ),
                    (
                        select 
                            COALESCE(json_agg(_emails), '[]') "company_emails"
                        from
                            (
                                select 
                                    tcm.id,
                                    tcm.email
                                from 
                                    transport_companymail tcm
                                where
                                    tcm.company_id = tc.id
                            ) _emails
                    ),
                    (
                        select 
                            COALESCE(json_agg(_numbers), '[]') "company_numbers"
                        from
                            (
                                select 
                                    tcn.id,
                                    tcn.number,
                                    tcn.type
                                from 
                                    transport_companynumber tcn
                                where
                                    tcn.company_id = tc.id
                            ) _numbers
                    ),
                    (
                        select 
                            COALESCE(json_agg(_contact_accounts), '[]') "contact_accounts"
                        from
                            (
                                select 
                                    aa.id,
                                    aa.name,
                                    aa.email,
                                    aa.phone_number,
                                    aa.avatar,
                                    (
                                        select COALESCE(json_agg(account_languages), '[]') "languages"
                                        from (
                                            select tl.id, tl.name, tl.native_name
                                            from "accounts_account_languages" aal
                                            inner join "transport_language" tl on aal.language_id = tl.id
                                            where aal.account_id = aa.id
                                        )account_languages
                                    )
                                from
                                    accounts_account aa 
                                where 
                                    aa.company_id = tc.id and aa.is_active = true
                            )_contact_accounts
                    ),
                    (
                        select 
                            json_agg(_services)::json->0 "services"
                        from
                            (
                                (
                                    select 
                                        COALESCE(json_agg(_goods_forms), '[]') "goods_forms",
                                        -- Tipovi robe START
                                        (
                                            select 
                                                COALESCE(json_agg(_goods_types), '[]') "goods_types"
                                            from
                                                (
                                                    select 
                                                        tgt.id,
                                                        tgt.name
                                                    from 
                                                        transport_company_goods_types tcgf
                                                    inner join
                                                        transport_goodstype tgt on tgt.id = tcgf.goodstype_id
                                                    where
                                                        tcgf.company_id = tc.id
                                                ) _goods_types
                                        ),
                                        --Tipovi Robe END
                                        --Tipovi Transporta START
                                        (
                                            select 
                                                COALESCE(json_agg(_transport_types), '[]') "transport_types"
                                            from
                                                (
                                                    select 
                                                        ttt.id,
                                                        ttt.name
                                                    from 
                                                        transport_company_transport_types tcgf
                                                    inner join
                                                        transport_transporttype ttt on ttt.id = tcgf.transporttype_id
                                                    where
                                                        tcgf.company_id = tc.id
                                                ) _transport_types
                                        ),
                                        --Tipovi Transporta END
                                        --Tipovi Vozila START
                                        (
                                            select 
                                                COALESCE(json_agg(_vehicle_types), '[]') "vehicle_types"
                                            from
                                                (
                                                    select 
                                                        vvt.id,
                                                        vvt.name
                                                    from 
                                                        transport_company_vehicle_types tcgf
                                                    inner join
                                                        transport_vehicletype vvt on vvt.id = tcgf.vehicletype_id
                                                    where
                                                        tcgf.company_id = tc.id
                                                ) _vehicle_types
                                        ),
                                        --Tipovi Vozila END
                                        --Oprema vozila START
                                        (
                                            select 
                                                COALESCE(json_agg(_vehicle_equipment), '[]') "vehicle_equipment"
                                            from
                                                (
                                                    select 
                                                        tve.id,
                                                        tve.name
                                                    from 
                                                        transport_company_vehicle_equipment tcve
                                                    inner join
                                                        transport_vehicleequipment tve on tve.id = tcve.vehicleequipment_id
                                                    where
                                                        tcve.company_id = tc.id
                                                ) _vehicle_equipment
                                        ),
                                        --Oprema vozila END
                                        --Nadogradnje Vozila START
                                        (
                                            select 
                                                COALESCE(json_agg(_vehicle_upgrades), '[]') "vehicle_upgrades"
                                            from
                                                (
                                                    select 
                                                        vvu.id,
                                                        vvu.name
                                                    from 
                                                        transport_company_vehicle_upgrades tcgf
                                                    inner join
                                                        transport_vehicleupgrade vvu on vvu.id = tcgf.vehicleupgrade_id
                                                    where
                                                        tcgf.company_id = tc.id
                                                ) _vehicle_upgrades
                                        ),
                                        --Nadogradnje Vozila END
                                        --Utovarni sustav START
                                        (
                                            select 
                                                COALESCE(json_agg(_loading_systems), '[]') "loading_systems"
                                            from
                                                (
                                                    select 
                                                        tls.id,
                                                        tls.name
                                                    from 
                                                        transport_company_loading_systems tcgf
                                                    inner join
                                                        transport_loadingsystem tls on tls.id = tcgf.loadingsystem_id
                                                    where
                                                        tcgf.company_id = tc.id
                                                ) _loading_systems
                                        ),
                                        --Utovarni sustav END,
                                        tc.own_vehicles,
                                        tc.vehicles_num
                                    from
                                        (
                                            select 
                                                tg.id,
                                                tg.name
                                            from 
                                                transport_company_goods_forms tcgf
                                            inner join
                                                transport_goodsform tg on tg.id = tcgf.goodsform_id
                                            where
                                                tcgf.company_id = tc.id
                                        ) _goods_forms
                                )
                            ) _services
                    )
                from 
                    transport_company tc 
                left join
                    transport_country tc2 on tc2.id = tc.country_id
                left join
                    transport_city tc3 on tc3.id = tc.city_id
                left join
                    transport_zipcode tz on tz.id = tc.zip_code_id
                where tc.id = {company_id} and tc.is_active=true
            ) _tc
    '''
    return query

def sql_get_basic_backoffice_info(*args, **kwargs):
    query = f"""
        WITH
	active_cargo_num AS (
		SELECT 
			count(*) "active_cargo_num"
		FROM
			transport_cargo tc 
		WHERE 
			tc.status = 'active'
	),
	active_ls_num AS (
		SELECT 
			count(*) "active_loading_spaces_num"
		FROM
			transport_loadingspace tl
		WHERE 
			tl.status = 'active'
	),
	active_stock_num AS (
		SELECT 
			count(*) "active_stocks_num"
		FROM
			transport_stock ts
		WHERE 
			ts.status = 'active'
	),
	closed_cargo_num AS (
		SELECT 
			count(*) "closed_cargo_num"
		FROM
			transport_cargo tc 
		WHERE 
			tc.status = 'closed'
	),
	closed_ls_num AS (
		SELECT 
			count(*) "closed_loading_spaces_num"
		FROM
			transport_loadingspace tl
		WHERE 
			tl.status = 'closed'
	),
	closed_stock_num AS (
		SELECT 
			count(*) "closed_stocks_num"
		FROM
			transport_stock ts
		WHERE 
			ts.status = 'closed'
	),
	active_companies_num AS (
		SELECT 
			count(*) "active_companies_num"
		FROM
			transport_company tc2 
		WHERE 
			tc2.status = 'active'
	),
	waiting_companies_num AS (
		SELECT 
			count(*) "waiting_companies_num"
		FROM
			transport_company tc3
		WHERE 
			tc3.status = 'need_confirm'
	),
	accounts_num AS (
		SELECT 
			count(*) "accounts_num"
		FROM
			accounts_account aa 
		WHERE 
			aa.is_active = True
	)

        select 
            json_agg(_data)->0 "data"
        from 
        (
        	SELECT 
        	    (
        	        select 
        	            json_agg(_active_ads)->0 "active_ads"
        	        from (
        	            select 
        	            json_build_object(
        	                'active_stocks_num', (SELECT active_stocks_num FROM active_stock_num), 
                            'active_loading_spaces_num', (SELECT active_loading_spaces_num FROM active_ls_num),
                            'active_cargo_num', (SELECT active_cargo_num FROM active_cargo_num)
        	            ) "per_category",
        	            (SELECT active_stocks_num FROM active_stock_num) +  (SELECT active_loading_spaces_num FROM active_ls_num) + (SELECT active_cargo_num FROM active_cargo_num) "total"
        	        ) _active_ads
        	    ),
        	    (
        	        select 
        	            json_agg(_closed_ads)->0 "closed_ads"
        	        from (
        	            select 
        	            json_build_object(
        	                'closed_stocks_num', (SELECT closed_stocks_num FROM closed_stock_num), 
                            'closed_loading_spaces_num', (SELECT closed_loading_spaces_num FROM closed_ls_num),
                            'closed_cargo_num', (SELECT closed_cargo_num FROM closed_cargo_num)
        	            ) "per_category",
        	            (SELECT closed_stocks_num FROM closed_stock_num) +  (SELECT closed_loading_spaces_num FROM closed_ls_num) + (SELECT closed_cargo_num FROM closed_cargo_num) "total"
        	        ) _closed_ads
        	    ),
        	    (
        	        select 
        	            json_agg(_companies)->0 "companies"
        	        from (
        	            select 
        	            json_build_object(
        	                'active_companies_num', (SELECT active_companies_num FROM active_companies_num), 
                            'waiting_companies_num', (SELECT waiting_companies_num FROM waiting_companies_num)
        	            ) "per_category",
        	            (SELECT active_companies_num FROM active_companies_num) +  (SELECT waiting_companies_num FROM waiting_companies_num) "total"
        	        ) _companies
        	    ),
				(SELECT accounts_num FROM accounts_num)
		) _data

	
    """
    return query

def sql_get_first_page_data(company_id, *args, **kwargs):
    query = f"""
    SELECT 

	(SELECT 
		count(*)
	FROM 
		transport_cargo tc 
	),
	(SELECT 
		count(*)
	FROM 
		transport_cargo tc 
	WHERE 
		tc.company_id = {company_id}
	),
	(SELECT 
		count(*)
	FROM 
		transport_loadingspace tl 
	),
	(SELECT 
		count(*)
	FROM 
		transport_loadingspace tl 
	WHERE 
		tl.company_id = {company_id}
	),
	(SELECT 
		count(*)
	FROM 
		transport_stock ts 
	),
	(SELECT 
		count(*)
	FROM 
		transport_stock ts 
	WHERE 
		ts.company_id = {company_id}
	)
    """
    return query