create or replace function fix_parent(tabla text, campo_padre text, campo_nombre text) RETURNS varchar as $$
DECLARE
    abuelo record;
    padre record;
    hijo record;
    c integer; 
    mx integer; 
    p integer; 
    r varchar; 
    nivel_a integer; 
    padre_a integer;
BEGIN
    c := 0;
    for abuelo in execute 'select id from '||tabla||' where '||campo_padre||' is null order by id' loop
        nivel_a := 0;
        for hijo in execute 'with recursive r(d,path,id,parent) as (select 1,''/'',id,'||campo_padre||' from '||tabla||' where id='||abuelo.id||' union all select r.d+1,r.path || CASE r.path WHEN ''/'' THEN '''' ELSE ''/'' END || t.'||campo_nombre||',t.id,t.'||campo_padre||' from r,'||tabla||' t where r.id=t.'||campo_padre||') select * from r order by path' loop
            while nivel_a > hijo.d loop 
                execute 'update '||tabla||' set parent_right='||c||' where id='||padre_a;
                c := c + 1;
                
                execute 'select '||campo_padre||' from '||tabla||' where id='||padre_a into padre_a;
                nivel_a := nivel_a - 1;
            end loop;
            
            execute 'select count(*) from '||tabla||' where '||campo_padre||'='||hijo.id into p;
            if p > 0 then
                execute 'update '||tabla||' set parent_left='||c||' where id='||hijo.id;
            else 
                execute 'update '||tabla||' set parent_left='||c||' where id='||hijo.id;
                c := c + 1;
                execute 'update '||tabla||' set parent_right='||c||' where id='||hijo.id;
            end if;
            c := c + 1;
            nivel_a := hijo.d;
            padre_a := hijo.parent;
        end loop;

        while nivel_a > 1 loop 
            execute 'update '||tabla||' set parent_right='||c||' where id='||padre_a;
            c := c + 1;

            execute 'select '||campo_padre||' from '||tabla||' where id='||padre_a into padre_a;
            nivel_a := nivel_a - 1;
        end loop;
        
     
    end loop;

    execute 'select count(*)*2 from '||tabla into mx;
    r := 'SUCCESS';
    if c<>mx then
        r := 'ERROR';
    end if;
    return r;
END;
$$ LANGUAGE plpgsql;