rpsh_sql = (
'''SELECT cp.month_year,
                      cp.mso,
                      cp.network,
                      nid.offering_detail,
                      nid.offering,
                      --ah.offering_rollup,       
                      nid.provider,
                      nid.content_type,
                      nid.resolution,       

                      
                      --This replaces the Nationwide values to be normal if they are not from Comcast
                      case 
                      when cp.mso != 'Comcast' then replace(nid.content_type || '-' ||nid.resolution, 'NW ', '')
                      else nid.content_type || '-' ||nid.resolution
                      end content_type_res,
                      cp.txns,
                      
                      --This gives me a default avg_price if our providers does not have the same type
                      case 
                      when avg_price.avg_price is null then default_avg_price
                      else avg_price.avg_price
                      end avg_price,
                      
                      
                      --last statement multiplied by txns for revenue
                      case 
                      when avg_price.avg_price is null then default_avg_price
                      else avg_price.avg_price
                      end * txns revenue,
                      
                      allotted_hours/*,
                      

                      round(case 
                      when avg_price.avg_price is null then default_avg_price
                      else avg_price.avg_price
                      end * txns / allotted_hours) rpsh*/
                      
                      
                      

            from comp_perf cp


            left join network_id nid on nid.network = cp.network

            left join(

            select month_year,
                      mso,
                      avg(avg_price) avg_price,
                      content_type || '-' ||resolution content_type, heat

            from provider_perf pp


            left join network_id nid on nid.network = pp.network

            group by month_year, mso,  content_type || '-' ||resolution, heat
            ) avg_price on (avg_price.content_type = content_type_res
                                  and cp.month_year = avg_price.month_year  
                                  and cp.mso = avg_price.mso
                                  and nid.heat = avg_price.heat
                                 
            )

            left join (select mso, content_type, resolution, default_avg_price
                            from  default_avg_price
                            )dap on (dap.mso = cp.mso 
                                         and dap.content_type = nid.content_type 
                                         and dap.resolution = nid.resolution)
                                                                                                                     

                                                                                                                     
            left join (select 
                        month_year,
                        mso,
                        offering_rollup, 
                        sum(allotted_hours) allotted_hours

                        from allotted_hours

                        group by month_year, mso, offering_rollup) ah on (ah.mso = cp.mso
                                                                         and ah.month_year = cp.month_year  
                                                                         and ah.offering_rollup = nid.offering)
                                                                                                                                 
                        --where avg_price is null and default_avg_price is null
                        where (cp.month_year like '%2016%' or cp.month_year like '%2015%') and not (nid.content_type = 'Uncen')

                        --and cp.mso = 'Charter' --and allotted_hours is null

            order by cp.month_year, cp.mso, nid.provider, nid.offering_detail
''')
