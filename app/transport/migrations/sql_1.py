from django.db import migrations

SQL = """

CREATE OR REPLACE FUNCTION public.account_auth(tok character varying)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
declare
	id integer;
	BEGIN
		select user_id into id from authtoken_token at2 where key = tok;
		return id;
	END;
$function$
;
CREATE OR REPLACE FUNCTION public.insert_many_to_many(tab_name character varying, static_col character varying, dynamic_col character varying, dynamic_data character varying, static_id integer, is_update boolean)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
	declare 
	str_arr varchar;
	arr varchar[];
	begin
		str_arr = replace(dynamic_data, '[', '');
		str_arr = replace(str_arr, ']', '');
		if str_arr = '' then
			return 0;
		end if;
		arr = string_to_array(str_arr, ',')::integer[];
	
		if is_update = true then
			execute (
		   		format (
			   		'delete from %s 
			   		where %s = %s', tab_name, static_col, static_id
		   		)
		   	);
		end if;
		
		FOR i IN 1..array_length(arr, 1)
	   	LOOP 
	   	execute (
	   		format (
		   		'insert into %s (%s, %s)
		   		values (%s, %s)', tab_name, static_col, dynamic_col, static_id, arr[i]
	   		)
	   	);
	   	
	   	end loop;
	   return 1;
	END;
$function$
;
CREATE OR REPLACE FUNCTION public.get_cargo_details(cargo_id integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
BEGIN
		return (
            select
                json_agg(_tc)->0
            from
                (
                    --Cargo Informacije
                    select
                        tc.id,
                        tc.created_at,
                        tc.length,
                        tc.width,
                        tc.weight,
                        tc.cargo_note,
                        tc.price,
                        tc.exchange,
                        tc.vehicle_note,
                        tc.status,
                        tc.auction_end_datetime,
                        tc.min_down_bind_percentage,
						case
							when tc.auction = true and (now() > tc.auction_end_datetime)
						then
							false
						else
							tc.auction
						end "auction",
                        (
                        	select 
								coalesce (json_agg(_ta), '[]') "auctions"
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
													aa.avatar,
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
									ta.cargo_id = tc.id
								order by
									ta."timestamp" 
								) _ta
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
                                        (
                                            select 
                                                coalesce(array_agg(tcm.email), ARRAY[]::text[]) "emails"
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
                                coalesce (json_agg(_tcca), '[]') "contact_accounts"
                            from
                                (
                                    select
                                        aa.id,
                                        aa.name,
                                        aa.email,
                                        aa.phone_number,
                                        aa.avatar,
                                        (
                                        select coalesce (json_agg(account_languages), '[]') "languages"
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
                                coalesce (json_agg(_tcgt), '[]') "goods_types"
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
                                coalesce (json_agg(_tcvf), '[]') "vehicle_features"
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
				                        tcveq.cargo_id = tc.id
				                ) _oprema_vozila
				        ),
				        --Oprema vozila kraj
                        --Tipovi vozila pocetak
                        
                        (
                            select
                                coalesce (json_agg(_tcvt), '[]') "vehicle_types"
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
                                coalesce (json_agg(_tcvu), '[]') "vehicle_upgrades"
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
                                coalesce (json_agg(_tclu), '[]') "load_unload" 
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
                        tc.id = cargo_id --and tc.status = 'active'
                ) _tc
        );
	END;
$function$
;
CREATE OR REPLACE FUNCTION public.get_stock(stock_id integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
	BEGIN
	if stock_id = 0 then 
	return (
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
                    coalesce(json_agg(_tcca), '[]') "contect_accounts"
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
                            tcom.id,
                            tcom.name,
                            tcom."OIB",
                            tcom.web,
                            tcom.address,
                            tcom.year,
                            tcom.avatar,
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
                            tcom.id = ts.company_id 
                        group by 
                            tcom.id

                    ) _tcompany
            )
            --Poduzece kraj
		from 
			transport_stock ts  
		where 
			ts.status = 'active'
	)_s
	);
	else 
	return (
	select 
	json_agg(_s)->0
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
			(
				select 
					coalesce(json_agg(_si), '[]') "images"
				from 
					(
						select 
							si.id,
							si.title,
							si.path
						from
							transport_stockimage si 
						where 
							si.is_active = true and si.stock_id = ts.id 
					) _si
			),
            -- Kontakt osobe start
            (
                select
                    coalesce(json_agg(_tcca), '[]') "contect_accounts"
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
                            tcom.id,
                            tcom.name,
                            tcom."OIB",
                            tcom.web,
                            tcom.address,
                            tcom.year,
                            tcom.avatar,
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
                            tcom.id = ts.company_id 
                        group by 
                            tcom.id

                    ) _tcompany
            )
            --Poduzece kraj
		from 
			transport_stock ts  
		where 
			ts.id = stock_id --and ts.status = 'active'
	)_s
	);
	end if;
	END;
$function$
;
CREATE OR REPLACE FUNCTION public.insert_update_stock(json_data json, tok character varying, is_update boolean, _stock_id integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
	declare 
		account_id integer;
		stock json;
		stock_status varchar;
		stock_id integer;
		tmp integer;
		company_id integer;
	begin
		--AUTENTIFIKACIJA
			account_id = account_auth(tok);
			if account_id is null then
				return 401;
			end if;
		--AUTENTIFIKACIJ KRAJ
		
		if is_update = true then
			if not exists (select 1 from transport_stock ts where ts.id = _stock_id) then 
				return 404;	
		end if;
		end if;
		
		stock = json_data -> 'stock';
		stock_status = 'active';
	
		if is_update = false then
		--DOdaj
		
	
			select aa.company_id into company_id from accounts_account aa where aa.id = account_id;
			
			insert into 
				transport_stock 
				(
					country_id, 
					city_id, 
					zip_code_id, 
					start_datetime, 
					end_datetime, 
					min_area, 
					max_area,
					status, 
					created_at, 
					created_by_id,
					company_id,
					stock_types,
					stock_equipment 
				)
			values
				(
					(stock ->> 'country')::integer,
					(stock ->> 'city')::integer,
					(stock ->> 'zip_code')::integer,
					(stock ->> 'start_datetime')::timestamp,
					(stock ->> 'end_datetime')::timestamp,
					(stock ->> 'min_area')::float4,
					(stock ->> 'max_area')::float4,
					stock_status,
					now(),
					account_id,
					company_id,
					(stock ->> 'stock_types'),
					(stock ->> 'stock_equipment')
				)
			returning id into stock_id;
		
			--select into tmp insert_many_to_many('transport_stock_stock_equipments'::varchar,'stock_id'::varchar,'stockequipment_id'::varchar,(stock ->> 'stock_equipments'),stock_id, false);
			--select into tmp insert_many_to_many('transport_stock_stock_types'::varchar,'stock_id'::varchar,'stocktype_id'::varchar,(stock ->> 'stock_types'),stock_id, false);
			select into tmp insert_many_to_many('transport_stock_contact_accounts'::varchar,'stock_id'::varchar,'account_id'::varchar,(stock ->> 'contact_accounts'),stock_id, false);
		else
		--Updateaj
			stock_id = _stock_id;
			update 
				transport_stock 
			set
				country_id = (stock ->> 'country')::integer,
				city_id = (stock ->> 'city')::integer,
				zip_code_id = (stock ->> 'zip_code')::integer,
				start_datetime = (stock ->> 'start_datetime')::timestamp,
				end_datetime = (stock ->> 'end_datetime')::timestamp,
				min_area = (stock ->> 'min_area')::float4,
				max_area = (stock ->> 'max_area')::float4,
				stock_types = (stock ->> 'stock_types'),
				stock_equipment = (stock ->> 'stock_equipment')
			where 
				id = _stock_id;
			--select into tmp insert_many_to_many('transport_stock_stock_equipments'::varchar,'stock_id'::varchar,'stockequipment_id'::varchar,(stock ->> 'stock_equipments'),stock_id, true);
			--select into tmp insert_many_to_many('transport_stock_stock_types'::varchar,'stock_id'::varchar,'stocktype_id'::varchar,(stock ->> 'stock_types'),stock_id, true);
			select into tmp insert_many_to_many('transport_stock_contact_accounts'::varchar,'stock_id'::varchar,'account_id'::varchar,(stock ->> 'contact_accounts'),stock_id, true);
		
			--delete from transport_stockimage a where a.stock_id = stock_id;
		end if;
	
		FOR i IN 0..json_array_length(json_data -> 'files') -1 
		LOOP 
			insert into 
				transport_stockimage 
				(path, title, stock_id)
			values (
				(json_data -> 'files' -> i ->> 'path'),
				json_data -> 'files' -> i ->> 'title',
				stock_id
			);
		end loop;
		
		return get_stock(stock_id);
	END;
$function$
;
CREATE OR REPLACE FUNCTION public.get_auctions(_cargo_id integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
	BEGIN
		return (
			select 
				json_agg(_data)
			from
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
							ta.cargo_id = _cargo_id
						order by
							ta."timestamp" 
						) _ta
				)_data
		);
	END;
$function$
;
CREATE OR REPLACE FUNCTION public.get_loading_space(loading_space_id integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
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
$function$
;
CREATE OR REPLACE FUNCTION public.update_cargo(json_data json, tok character varying)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
declare 
		account_id integer;
		load_unload json;
		cargo json;
		_auction json;
		vehicle json;
		cargo_status varchar;
		tmp integer;
		_cargo_id integer;
		res json;
	BEGIN
		--AUTENTIFIKACIJA
			account_id = account_auth(tok);
			if account_id is null then
				return 401;
			end if;
		--AUTENTIFIKACIJ KRAJ
		
		cargo = json_data -> 'cargo';
		_cargo_id = json_data ->> 'cargo_id';
		load_unload = json_data -> 'load_unload';
		_auction = json_data -> 'auction';
		vehicle = json_data -> 'vehicle';
		
		--CHECK PERMISSION
		if (select tc.created_by_id from transport_cargo tc where tc.id = _cargo_id) != account_id then
			return 403;
		end if;
		--CHECK PERMISSION KRAJ
		
		if not exists (select 1 from transport_cargo tc where tc.id = _cargo_id) then 
			return 404;	
		end if;
		
		
		--UPDATE TERETA
		update 
			transport_cargo 
		set 
			length = (cargo ->> 'length')::float4, 
			width = (cargo ->> 'width')::float4, 
			weight = (cargo ->> 'weight')::float4,
			cargo_note = (cargo -> 'cargo_note'), 
			price = (cargo ->> 'price')::float4, 
			exchange = (cargo ->> 'exchange')::bool, 
			auction = (_auction ->> 'auction')::boolean,
			vehicle_note = (vehicle -> 'vehicle_note'), 
			auction_end_datetime = (_auction ->> 'auction_end_datetime')::timestamp,
			min_down_bind_percentage = (_auction ->> 'min_down_bind_percentage')::float4
		where 
			id = _cargo_id;
		--KRAJ UPDATEA TERETA
		select into tmp insert_many_to_many('transport_cargo_goods_types'::varchar,'cargo_id'::varchar,'goodstype_id'::varchar,(cargo ->> 'goods_types'),_cargo_id, true);
		select into tmp insert_many_to_many('transport_cargo_vehicle_types'::varchar,'cargo_id'::varchar,'vehicletype_id'::varchar,(vehicle ->> 'vehicle_types'),_cargo_id, true);
		select into tmp insert_many_to_many('transport_cargo_vehicle_upgrades'::varchar,'cargo_id'::varchar,'vehicleupgrade_id'::varchar,(vehicle ->> 'vehicle_upgrades'),_cargo_id, true);
		--select into tmp insert_many_to_many('transport_cargo_vehicle_features'::varchar,'cargo_id'::varchar,'vehiclefeature_id'::varchar,(vehicle ->> 'vehicle_features'),_cargo_id, true);
		select into tmp insert_many_to_many('transport_cargo_contact_accounts'::varchar,'cargo_id'::varchar,'account_id'::varchar,(vehicle ->> 'contact_accounts'),_cargo_id, true);
		select into tmp insert_many_to_many('transport_cargo_vehicle_equipment'::varchar,'cargo_id'::varchar,'vehicleequipment_id'::varchar,(vehicle ->> 'vehicle_equipment'),_cargo_id, true);
		
		delete from transport_cargoloadunload 
		where transport_cargoloadunload.cargo_id = _cargo_id;
		--Dodavanje Utovara i Istovara
		FOR i IN 0..json_array_length(json_data -> 'load_unload') -1 
	   	LOOP 
	   		raise notice '%', load_unload -> i -> 'country';
	   		insert into transport_cargoloadunload 
	   		("country_id", "city_id", "zip_code_id", "type", start_datetime, end_datetime, cargo_id)
	   		values (
	   			(load_unload -> i ->> 'country')::integer,
	   			(load_unload -> i ->> 'city')::integer,
	   			(load_unload -> i ->> 'zip_code')::integer,
	   			load_unload -> i ->> 'type',
	   			(load_unload -> i ->> 'start_datetime')::timestamp,
	   			(load_unload -> i ->> 'end_datetime')::timestamp,
	   			_cargo_id
	   		);
	   	end loop;
	   res = get_cargo_details(_cargo_id);
	  	return res;
	END;
$function$
;
CREATE OR REPLACE FUNCTION public.insert_auction(tok character varying, cargo_id integer, price real)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
declare 
		perc float4;
		last_price float4;
		to_datetime timestamp;
		account_id integer;
		is_auction boolean;
		_cargo_id integer;
	begin
		_cargo_id = cargo_id;
		--AUTENTIFIKACIJA
			account_id = account_auth(tok);
			if account_id is null then
				return 401;
			end if;
		--AUTENTIFIKACIJ KRAJ
		--Dohvati podatke o aukciji
		select 
			tc.min_down_bind_percentage, tc.auction_end_datetime , tc.auction
		into
			perc, to_datetime, is_auction
		from 
			transport_cargo tc
		where 
			tc.id = cargo_id;
		if is_auction = false or is_auction is null then
			return 0;
		end if;
		--Dohvati krajnji datum (Provjerit moze li ovako i tesitrat pa onda pustit)
		if now() > to_datetime then
			raise notice '% > %', now(), to_datetime;
			return 0;
		end if;
		--Dohvati zadnju cijenu
		select 
			ta.price
		into 
			last_price
		from 
			transport_auction ta
		where 
			ta.cargo_id = _cargo_id
		order by
			ta."timestamp" desc
		limit 
			1;
		raise notice 'Zadnja cijena %', last_price;
		
		if perc is null or perc = 0 then 
			if price > last_price then
				return 0;
			end if;
		
		elseif price > (last_price - perc) then
			return 0;
		end if;
	
		insert into transport_auction ("account_id", "cargo_id", "price", "timestamp", "is_active")
	   	values (account_id, cargo_id, price, now(), true);
		return get_auctions(cargo_id);
	END;
$function$
;
CREATE OR REPLACE FUNCTION public.insert_cargo(json_data json, tok character varying)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
declare
	i integer;
	l float4;
	load_unload json;
	cargo json;
	auction json;
	vehicle json;
	cargo_status varchar;
	cargo_id integer;
	tmp integer;
	str_arr varchar;
	account_id integer;
	company_id integer;
	res json;
	begin
		
		--AUTENTIFIKACIJA
			account_id = account_auth(tok);
			if account_id is null then
				return 401;
			end if;
		--AUTENTIFIKACIJ KRAJ

		
		cargo_status = 'active';
		cargo = json_data -> 'cargo';
		load_unload = json_data -> 'load_unload';
		auction = json_data -> 'auction';
		vehicle = json_data -> 'vehicle';
		
		select aa.company_id into company_id from accounts_account aa where aa.id = account_id;
		
		--Dodavanje Tereta
		insert into transport_cargo 
		(length, width, weight, cargo_note, price, exchange, created_at, auction, vehicle_note, status, auction_end_datetime, created_by_id, company_id, min_down_bind_percentage,
		auction_notification_sent)
		values (
			(cargo ->> 'length')::float4, (cargo ->> 'width')::float4, (cargo ->> 'weight')::float4,
			(cargo -> 'cargo_note'), (cargo ->> 'price')::float4, (cargo ->> 'exchange')::bool, now(), (auction ->> 'auction')::boolean,
			(vehicle -> 'vehicle_note'), cargo_status, (auction ->> 'auction_end_datetime')::timestamp, account_id, company_id, (auction ->> 'min_down_bind_percentage')::float4,
			false
		)
		returning id into cargo_id;
		--Kraj dodavanja tereta
		select into tmp insert_many_to_many('transport_cargo_goods_types'::varchar,'cargo_id'::varchar,'goodstype_id'::varchar,(cargo ->> 'goods_types'),cargo_id, false);
		select into tmp insert_many_to_many('transport_cargo_vehicle_types'::varchar,'cargo_id'::varchar,'vehicletype_id'::varchar,(vehicle ->> 'vehicle_types'),cargo_id, false);
		select into tmp insert_many_to_many('transport_cargo_vehicle_upgrades'::varchar,'cargo_id'::varchar,'vehicleupgrade_id'::varchar,(vehicle ->> 'vehicle_upgrades'),cargo_id, false);
		--select into tmp insert_many_to_many('transport_cargo_vehicle_features'::varchar,'cargo_id'::varchar,'vehiclefeature_id'::varchar,(vehicle ->> 'vehicle_features'),cargo_id, false);
		select into tmp insert_many_to_many('transport_cargo_contact_accounts'::varchar,'cargo_id'::varchar,'account_id'::varchar,(vehicle ->> 'contact_accounts'),cargo_id, false);
		select into tmp insert_many_to_many('transport_cargo_vehicle_equipment'::varchar,'cargo_id'::varchar,'vehicleequipment_id'::varchar,(vehicle ->> 'vehicle_equipment'),cargo_id, false);
	
		--Dodavanje Utovara i Istovara
		FOR i IN 0..json_array_length(json_data -> 'load_unload') -1 
	   	LOOP 
	   		raise notice '%', load_unload -> i -> 'country';
	   		insert into transport_cargoloadunload 
	   		("country_id", "city_id", "zip_code_id", "type", start_datetime, end_datetime, cargo_id)
	   		values (
	   			(load_unload -> i ->> 'country')::integer,
	   			(load_unload -> i ->> 'city')::integer,
	   			(load_unload -> i ->> 'zip_code')::integer,
	   			load_unload -> i ->> 'type',
	   			(load_unload -> i ->> 'start_datetime')::timestamp,
	   			(load_unload -> i ->> 'end_datetime')::timestamp,
	   			cargo_id
	   		);
	   	end loop;
	   
	   --Dodavanje aukcije
	   if (auction ->> 'auction')::boolean = true then
	   	insert into transport_auction ("account_id", "cargo_id", "price", "timestamp", "is_active")
	   	values (account_id, cargo_id, (auction ->> 'start_price')::float4, now(), true);
	   end if;
		res = get_cargo_details(cargo_id);
		return res;
	END;
$function$
;
CREATE OR REPLACE FUNCTION public.insert_update_account_and_company(update_company boolean, json_data json, tok character varying)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
DECLARE
	company_id integer;
	account_id integer;
	is_active boolean;
	tmp integer;
	auth_account_id integer;
begin
	
	is_active = true;
	IF update_company = false then

		if json_data ->> 'company' is null then
			--Dodaj Poduzece
			select insert_update_company(null, json_data) into company_id;
			
		else
			--Ako se samo dodaje korisnik
			company_id = (json_data ->> 'company')::integer;
			--AUTENTIFIKACIJA
				auth_account_id = account_auth(tok);
				if auth_account_id is null then
					return 401;
				end if;
			--AUTENTIFIKACIJ KRAJ
			--CHECK PERMISSION
			if (select aa.company_id from accounts_account aa where aa.id = auth_account_id) != company_id then
				return 403;
			end if;
			if (select cmp.status from transport_company cmp where cmp.id = company_id) != 'active' then 
				return 403;
			end if;
			--CHECK PERMISSION KRAJ
		end if;
		
		
		--Dodaj korisnika
		insert into
			accounts_account
			(
				name, email, phone_number, password, company_id, date_joined, last_login,
				is_admin, is_staff, is_superuser, is_active
			)
		values
			(
				json_data ->> 'account_full_name',
				json_data ->> 'account_email',
				json_data ->> 'account_phone_number',
				json_data ->> 'account_password',
				company_id,
				now(),
				now(),
				false,
				false,
				false,
				is_active
			)
		returning id into account_id;
	
		--Dodat kreatora poduzeća
		if json_data ->> 'company' is null then
			update transport_company 
			set creator_id = account_id
			where id = company_id;
			
			if json_data -> 'fcm_token' is not null then
				insert into fcm_django_fcmdevice 
				(active, date_created, registration_id, type, user_id)
				values
				(true, now(), json_data ->> 'fcm_token', 'web', account_id);
			end if;
		end if;
		
		FOR i IN 0..json_array_length(json_data -> 'account_languages') -1 
	   	LOOP 
	   		insert into 
				accounts_account_languages 
	   			(language_id, account_id)
	   		values (
	   			(json_data -> 'account_languages' ->> i)::integer,
	   			account_id
	   			);
	   	end loop;
		
		return account_id;
	else
		--UPDATE COMPANY
		company_id = (json_data ->> 'company')::integer;
		--AUTENTIFIKACIJA
				auth_account_id = account_auth(tok);
				if auth_account_id is null then
					return 401;
				end if;
			--AUTENTIFIKACIJ KRAJ
			--CHECK PERMISSION
			if (select aa.company_id from accounts_account aa where aa.id = auth_account_id) != company_id then
				return 403;
			end if;
			--CHECK PERMISSION KRAJ
		select insert_update_company(company_id, json_data) into tmp;
		return company_id;
	end if;
END;
$function$
;
CREATE OR REPLACE FUNCTION public.ukraine_to_latin(json_data json)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
	BEGIN
		FOR i IN 0..json_array_length(json_data) -1 
		LOOP 
			RAISE NOTICE 'fsadfsd';
		end loop;
		RETURN 1;
	END;
$function$
;
CREATE OR REPLACE FUNCTION public.insert_loading_space(json_data json, tok character varying, is_update boolean, _loading_space_id integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
	declare 
		account_id integer;
		vehicle json;
		starting_point_destination json;
		loadning_space_status varchar;
		loading_space_id integer;
		tmp integer;
		company_id integer;
	begin
		--AUTENTIFIKACIJA
			account_id = account_auth(tok);
			if account_id is null then
				return 401;
			end if;
		--AUTENTIFIKACIJ KRAJ
		
		if is_update = true then
			if not exists (select 1 from transport_loadingspace tl where tl.id = _loading_space_id) then 
				return 404;	
		end if;
		end if;
		
		vehicle = json_data -> 'vehicle';
		starting_point_destination = json_data -> 'starting_point_destination';
		loadning_space_status = 'active';
	
		if is_update = false then
		--DOdaj
		
	
			select aa.company_id into company_id from accounts_account aa where aa.id = account_id;
			
			insert into 
				transport_loadingspace 
				(
					vehicle_type_id, 
					vehicle_length, 
					vehicle_load_capacity, 
					connected_vehicle_length, 
					connected_vehicle_load_capacity,
					vehicle_note, 
					status, 
					created_at, 
					created_by_id,
					company_id
				)
			values
				(
					(vehicle ->> 'vehicle_type')::integer,
					(vehicle ->> 'vehicle_length')::float4,
					(vehicle ->> 'vehicle_load_capacity')::float4,
					(vehicle ->> 'connected_vehicle_length')::float4,
					(vehicle ->> 'connected_vehicle_load_capacity')::float4,
					(vehicle -> 'vehicle_note'),
					loadning_space_status,
					now(),
					account_id,
					company_id
				)
			returning id into loading_space_id;
		
			select into tmp insert_many_to_many('transport_loadingspace_vehicle_upgrades'::varchar,'loadingspace_id'::varchar,'vehicleupgrade_id'::varchar,(vehicle ->> 'vehicle_upgrades'),loading_space_id, false);
			--select into tmp insert_many_to_many('transport_loadingspace_vehicle_features'::varchar,'loadingspace_id'::varchar,'vehiclefeature_id'::varchar,(vehicle ->> 'vehicle_features'),loading_space_id, false);
			select into tmp insert_many_to_many('transport_loadingspace_contact_accounts'::varchar,'loadingspace_id'::varchar,'account_id'::varchar,(vehicle ->> 'contact_accounts'),loading_space_id, false);
			select into tmp insert_many_to_many('transport_loadingspace_vehicle_equipment'::varchar,'loadingspace_id'::varchar,'vehicleequipment_id'::varchar,(vehicle ->> 'vehicle_equipment'),loading_space_id, false);
		else
		--Updateaj
			loading_space_id = _loading_space_id;
			update 
				transport_loadingspace 
			set
				vehicle_type_id = (vehicle ->> 'vehicle_type')::integer,
				vehicle_length = (vehicle ->> 'vehicle_length')::float4,
				vehicle_load_capacity =	(vehicle ->> 'vehicle_load_capacity')::float4,
				connected_vehicle_length = (vehicle ->> 'connected_vehicle_length')::float4,
				connected_vehicle_load_capacity = (vehicle ->> 'connected_vehicle_load_capacity')::float4,
				vehicle_note = (vehicle -> 'vehicle_note'),
				status = loadning_space_status
			where 
				id = _loading_space_id;
			select into tmp insert_many_to_many('transport_loadingspace_vehicle_upgrades'::varchar,'loadingspace_id'::varchar,'vehicleupgrade_id'::varchar,(vehicle ->> 'vehicle_upgrades'),loading_space_id, true);
			--select into tmp insert_many_to_many('transport_loadingspace_vehicle_features'::varchar,'loadingspace_id'::varchar,'vehiclefeature_id'::varchar,(vehicle ->> 'vehicle_features'),loading_space_id, true);
			select into tmp insert_many_to_many('transport_loadingspace_contact_accounts'::varchar,'loadingspace_id'::varchar,'account_id'::varchar,(vehicle ->> 'contact_accounts'),loading_space_id, true);
			select into tmp insert_many_to_many('transport_loadingspace_vehicle_equipment'::varchar,'loadingspace_id'::varchar,'vehicleequipment_id'::varchar,(vehicle ->> 'vehicle_equipment'),loading_space_id, true);
			
			delete from transport_startingpointdestination 
			where transport_startingpointdestination.loading_space_id = _loading_space_id;
		end if;
		
		
	
		FOR i IN 0..json_array_length(json_data -> 'starting_point_destination') -1 
	   	LOOP 
	   		insert into transport_startingpointdestination 
	   		("country_id", "city_id", "zip_code_id", "type", departure_datetime, within_km, loading_space_id)
	   		values (
	   			(starting_point_destination -> i ->> 'country')::integer,
	   			(starting_point_destination -> i ->> 'city')::integer,
	   			(starting_point_destination -> i ->> 'zip_code')::integer,
	   			starting_point_destination -> i ->> 'type',
	   			(starting_point_destination -> i ->> 'departure_datetime')::timestamp,
	   			(starting_point_destination -> i ->> 'within_km')::float4,
	   			loading_space_id
	   		);
	   	end loop;
		
		return get_loading_space(loading_space_id);
	END;
$function$
;
CREATE OR REPLACE FUNCTION public.insert_update_company(company_id integer, json_data json)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
	_company_id integer;
	company_services json;
	_own_vehicles boolean;
	_vehicles_num integer;
	company_avatar varchar;
	company_status varchar;
	_company_number integer;
begin
	company_status = 'need_confirm';
	company_avatar = 'images/default_company.png';
	company_services = json_data -> 'company_services';
	if company_services -> 'own_vehicles' is not null then
		_own_vehicles = (company_services ->> 'own_vehicles')::boolean;
	else
		_own_vehicles = null;
	end if;
	if company_services -> 'vehicles_num' is not null then
		_vehicles_num = (company_services ->> 'vehicles_num')::integer;
	else
		_vehicles_num = null;
	end if;
	
	
	if company_id is not null then
		--UPDATE
		_company_id = company_id;
		delete from transport_companynumber a where a.company_id = _company_id;
		delete from transport_companymail a where a.company_id = _company_id;
		delete from transport_company_goods_forms a where a.company_id = _company_id;
		delete from transport_company_goods_types a where a.company_id = _company_id;
		delete from transport_company_transport_types a where a.company_id = _company_id;
		delete from transport_company_vehicle_types a where a.company_id = _company_id;
		delete from transport_company_vehicle_upgrades a where a.company_id = _company_id;
		delete from transport_company_loading_systems a where a.company_id = _company_id;
		delete from transport_companydocument a where a.company_id = _company_id;
		delete from transport_company_cover_countries a where a.company_id = _company_id;
		delete from transport_company_vehicle_equipment a where a.company_id = _company_id;
		
		update transport_company
		set name = json_data ->> 'company_name',
			"OIB" = json_data ->> 'company_OIB',
			year = (json_data ->> 'company_year')::integer,
			web = json_data ->> 'company_web',
			country_id = (json_data ->> 'company_country')::integer,
			city_id = (json_data ->> 'company_city')::integer,
			zip_code_id = (json_data ->> 'company_zip_code')::integer,
			own_vehicles = _own_vehicles,
			vehicles_num = _vehicles_num,
			address = (json_data ->> 'company_address')
		where id = _company_id;
		
	ELSE
		--Dohvati zanji Broj Poduzeca
		SELECT COALESCE (tc.number, 1000) INTO _company_number FROM transport_company tc ORDER BY tc.id DESC LIMIT 1;
		if _company_number is null then
			_company_number = 1000;
		end if;
	
		insert into 
			transport_company 
			(name, "OIB", year, web, country_id, city_id, zip_code_id, own_vehicles, vehicles_num, avatar, is_active, address, status, created_at, number)
		values
			(
				json_data ->> 'company_name',
				json_data ->> 'company_OIB',
				(json_data ->> 'company_year')::integer,
				json_data ->> 'company_web',
				(json_data ->> 'company_country')::integer,
				(json_data ->> 'company_city')::integer,
				(json_data ->> 'company_zip_code')::integer,
				_own_vehicles,
				_vehicles_num,
				company_avatar,
				true,
				(json_data ->> 'company_address'),
				company_status,
				now(),
				_company_number + 1
			)
		returning id into _company_id;
	end if; --Kraj IF company_id is not null then
	
	FOR i IN 0..json_array_length(json_data -> 'files') -1 
	LOOP 
		insert into 
			transport_companydocument 
			(path, title, company_id, is_active)
		values (
			(json_data -> 'files' -> i ->> 'path'),
			json_data -> 'files' -> i ->> 'title',
			_company_id, 
			true
		);
	end loop;

	FOR i IN 0..json_array_length(json_data -> 'company_numbers') -1 
	LOOP 
		insert into 
			transport_companynumber 
			(number, type, company_id)
		values (
			(json_data -> 'company_numbers' -> i ->> 'number'),
			json_data -> 'company_numbers' -> i ->> 'type',
			_company_id
		);
	end loop;

	FOR i IN 0..json_array_length(json_data -> 'company_emails') -1 
	LOOP 
		insert into 
			transport_companymail 
			(email, company_id)
		values (
			(json_data -> 'company_emails' ->> i),
			_company_id
		);
	end loop;
	
	if (json_data -> 'company_cover_countries') is not null then
		FOR i IN 0..json_array_length(json_data -> 'company_cover_countries') -1 
		LOOP 
			insert into 
				transport_company_cover_countries
				(country_id, company_id)
			values (
				(json_data -> 'company_cover_countries' ->> i)::integer,
				_company_id
			);
		end loop;
	end if;

	if company_services is not null then

		if company_services -> 'goods_forms' is not null then
			FOR i IN 0..json_array_length(company_services -> 'goods_forms') -1 
			LOOP 
				insert into 
					transport_company_goods_forms 
					(goodsform_id, company_id)
				values (
					(company_services -> 'goods_forms' ->> i)::integer,
					_company_id
				);
			end loop;
		end if;

		if company_services -> 'goods_types' is not null then
			FOR i IN 0..json_array_length(company_services -> 'goods_types') -1 
			LOOP 
				insert into 
					transport_company_goods_types
					(goodstype_id, company_id)
				values (
					(company_services -> 'goods_types' ->> i)::integer,
					_company_id
				);
			end loop;
		end if;

		if company_services -> 'transport_types' is not null then
			FOR i IN 0..json_array_length(company_services -> 'transport_types') -1 
			LOOP 
				insert into 
					transport_company_transport_types
					(transporttype_id, company_id)
				values (
					(company_services -> 'transport_types' ->> i)::integer,
					_company_id
				);
			end loop;
		end if;

		if company_services -> 'vehicle_types' is not null then
			FOR i IN 0..json_array_length(company_services -> 'vehicle_types') -1 
			LOOP 
				insert into 
					transport_company_vehicle_types
					(vehicletype_id, company_id)
				values (
					(company_services -> 'vehicle_types' ->> i)::integer,
					_company_id
				);
			end loop;
		end if;

		if company_services -> 'vehicle_upgrades' is not null then
			FOR i IN 0..json_array_length(company_services -> 'vehicle_upgrades') -1 
			LOOP 
				insert into 
					transport_company_vehicle_upgrades
					(vehicleupgrade_id, company_id)
				values (
					(company_services -> 'vehicle_upgrades' ->> i)::integer,
					_company_id
				);
			end loop;
		end if;
	
		if company_services -> 'vehicle_equipment' is not null then
			FOR i IN 0..json_array_length(company_services -> 'vehicle_equipment') -1 
			LOOP 
				insert into 
					transport_company_vehicle_equipment
					(vehicleequipment_id, company_id)
				values (
					(company_services -> 'vehicle_equipment' ->> i)::integer,
					_company_id
				);
			end loop;
		end if;

		if company_services -> 'loading_systems' is not null then
			FOR i IN 0..json_array_length(company_services -> 'loading_systems') -1 
			LOOP 
				insert into 
					transport_company_loading_systems
					(loadingsystem_id, company_id)
				values (
					(company_services -> 'loading_systems' ->> i)::integer,
					_company_id
				);
			end loop;
		end if;

	end if;
		
	return _company_id;
END;
$function$


"""

class Migration(migrations.Migration):
    dependencies = [
        ('transport', '0041_company_number')
    ]

    operations = [migrations.RunSQL(SQL)]
