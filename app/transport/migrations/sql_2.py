from django.db import migrations

SQL = """
CREATE or REPLACE FUNCTION get_loading_space(loading_space_id integer) RETURNS json
    LANGUAGE plpgsql
AS
$$
begin
		if loading_space_id != 0 then
		return (select
                json_agg(_tl)->0
            from
                (
                    --loading space Informacije
                    select
                        tc.id,
                        tc.created_at,
                        tc.vehicle_length,
                        tc.vehicle_load_capacity,
                        tc.connected_vehicle_length,
                        tc.connected_vehicle_load_capacity,
                        tc.vehicle_note,
                        tc.status,
                         (
                            select
                                json_agg(_tcvt)->0 "vehicle_type"
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
                                        tcom.id,
                                        tcom.name,
                                        tcom."OIB",
                                        tcom.web,
                                        tcom.address,
                                        tcom.year,
                                        tcom.avatar,
                                        tcom.number,
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
				                                        tctry.id = tcom.country_id
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
				                                        tcty.id = tcom.city_id
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
				                                        tz.id = tcom.zip_code_id
				                    			)zip_codes
				                    	),
                                        (
                                            select 
                                                coalesce (array_agg(tcm.email), ARRAY[]::text[]) "emails"
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
				                        tcveq.loadingspace_id = tc.id
				                ) _oprema_vozila
				        ) ,
                        --Nadogradnje vozila pocetak
                        
                        (
                            select
                                coalesce(json_agg(_tcvu), '[]') "vehicle_upgrades"
                            from
                                (
                                    select
                                        tv.id, tv.name
                                    from
                                        transport_loadingspace_vehicle_upgrades tcvu
                                    inner join
                                    	transport_vehicleupgrade tv on tv.id = tcvu.vehicleupgrade_id
                                    where 
                                        tcvu.loadingspace_id = tc.id
                                ) _tcvu
                        ),
                        --Nadogradnje vozila kraj
						(
                            select 
                                coalesce(json_agg(_spd), '[]') "starting_point_destination" 
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
                    where 
                    	tc.id = loading_space_id --and tc.status = 'active'
                ) _tl);
        else
        	return (select
                json_agg(_tl)
            from
                (
                    --loading space Informacije
                    select
                        tc.id,
                        tc.created_at,
                        tc.vehicle_length,
                        tc.vehicle_load_capacity,
                        tc.connected_vehicle_length,
                        tc.connected_vehicle_load_capacity,
                        tc.vehicle_note,
                        tc.status,
                         (
                            select
                                json_agg(_tcvt)->0 "vehicle_type"
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
                                        tcom.id,
                                        tcom.name,
                                        tcom."OIB",
                                        tcom.web,
                                        tcom.address,
                                        tcom.year,
                                        tcom.avatar,
                                        tcom.number,
                                        (
                                            select 
                                                coalesce (array_agg(tcm.email), ARRAY[]::text[]) "emails"
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
				                        tcveq.loadingspace_id = tc.id
				                ) _oprema_vozila
				        ) ,
				        --Oprema vozila kraj
                        --Nadogradnje vozila pocetak
                        
                        (
                            select
                                coalesce(json_agg(_tcvu), '[]') "vehicle_upgrades"
                            from
                                (
                                    select
                                        tv.id, tv.name
                                    from
                                        transport_loadingspace_vehicle_upgrades tcvu
                                    inner join
                                    	transport_vehicleupgrade tv on tv.id = tcvu.vehicleupgrade_id
                                    where 
                                        tcvu.loadingspace_id = tc.id
                                ) _tcvu
                        ),
                        --Nadogradnje vozila kraj
						(
                            select 
                                coalesce(json_agg(_spd), '[]') "starting_point_destination" 
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
                                            'name', tz.code,
                                            'city_id', tz.city_id 
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
                    where
                    	tc.status = 'active'
                ) _tl);
        end if;
	END;
$$;



"""

class Migration(migrations.Migration):
    dependencies = [
        ('transport', 'sql_1')
    ]

    operations = [migrations.RunSQL(SQL)]
