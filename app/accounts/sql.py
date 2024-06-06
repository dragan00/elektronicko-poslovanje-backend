from transport.sql import sql_get_company_details

def sql_get_user(token):
    query = f'''
        select json_agg(acc) from (
        select
        (select json_agg(account_info) "account"
        from (
        select aa.id, aa.name, aa.email, aa.is_admin, aa.phone_number, aa.address, aa.panes, aa.avatar,
        (
            {sql_get_company_details(f"""
                (
                    select aa2.company_id from accounts_account aa2
                    inner join authtoken_token at2 on at2.user_id = aa2.id
                    where at2.key = '{token}'
                )
            """)}
        ),
        (
            select json_agg(accoutn_languages) "languages"
            from (
                select tl.id, tl.name, tl.native_name
                from "accounts_account_languages" aal
                inner join "transport_language" tl on aal.language_id = tl.id
                where aal.account_id = aa.id
            )accoutn_languages
        )

        from accounts_account aa 
        inner join authtoken_token at2 on at2.user_id = aa.id
        left join transport_company tcmp on tcmp.id = aa.company_id
        where at2.key = '{token}'
        ) account_info),

        ('{token}') "token",

        (select json_agg(_prepare) "prepare" from (
            select
            (
                select 
                    json_agg(_ts) "stock_types"
                from
                    (
                        select 
                            ts.id, 
                            ts.name
                        from
                            transport_stocktype ts
                    ) _ts
            ),
            (
                select 
                    json_agg(_te) "stock_equipment"
                from
                    (
                        select 
                            te.id, 
                            te.name
                        from
                            transport_stockequipment te
                    ) _te
            ),
            (select json_agg(_tg) "goods_types" from (
            select tg.id, tg.name
            from transport_goodstype tg 
            )  _tg),

            (select json_agg(_vt) "vehicle_types" from (
            select tvt.id, tvt.name
            from transport_vehicletype tvt 
            )  _vt),

            (select json_agg(_tvu) "vehicle_upgrades" from (
            select tvu.id, tvu.name
            from transport_vehicleupgrade tvu 
            )  _tvu),

            (select json_agg(_tvf) "vehicle_features" from (
            select tvf.id, tvf.name
            from transport_vehiclefeature tvf 
            )  _tvf),

            (select json_agg(_contact_accounts) "contact_accounts" from (
                select aa.id, aa.name
                from accounts_account aa 
                where aa.company_id = (
                    select aa2.company_id from accounts_account aa2
                    inner join authtoken_token at2 on at2.user_id = aa2.id
                    where at2.key = '{token}'
                )
                
            ) _contact_accounts)

        ) _prepare)

        
        ) acc
    '''
    return query


def sql_get_user_by_id(id):
    query = f'''
        select json_agg(acc) from (
        select
        (select json_agg(account_info)->0 "account"
        from (
        select aa.id, aa.name, aa.email, aa.is_admin, aa.phone_number, aa.address, aa.panes, aa.avatar,
        (
            {sql_get_company_details(f"""
                (
                    select aa2.company_id from accounts_account aa2
                    where aa2.id = {id}
                )
            """)}
        ),
        (
            select json_agg(accoutn_languages) "languages"
            from (
                select tl.id, tl.name, tl.native_name
                from "accounts_account_languages" aal
                inner join "transport_language" tl on aal.language_id = tl.id
                where aal.account_id = aa.id
            )accoutn_languages
        )

        from accounts_account aa 
        where aa.id = {id}
        ) account_info)

        ) acc
    '''
    return query

def sql_get_company_contact_accounts(company_id):
    query = f"""
        select json_agg(acc)->0 from (
        select
            (select json_agg(_contact_accounts) "contact_accounts" from (
                select 
                    aa.id,
                    aa.name,
                    aa.email,
                    aa.phone_number,
                    aa.avatar,
                    (
                        select json_agg(account_languages) "languages"
                        from (
                            select tl.id, tl.name, tl.native_name
                            from "accounts_account_languages" aal
                            inner join "transport_language" tl on aal.language_id = tl.id
                            where aal.account_id = aa.id
                        )account_languages
                    )
                from accounts_account aa 
                where aa.company_id = {company_id}
                
            ) _contact_accounts)

        
        ) acc
    """
    return query
