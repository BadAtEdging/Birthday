import sqlite3
import config
import os
import pytz
from datetime import *

path = os.path.dirname(os.path.abspath(__file__))


def db():
    conn = sqlite3.connect(os.path.join(path,'birthday.db'), detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    return (conn,c)
def drop_table(table_name):
    conn, c = db()
    c.execute(f'drop table {table_name}')
    conn.commit()

def create_tables():
    def create_birthdays():
        conn, c = db()
        c.execute("""
                    create table if not exists birthdays(
                    guild_id integer not null,
                    member_id integer not null,
                    any_birthday_local timestamp,
                    next_birthday_utc timestamp,
                    last_announced_utc timestamp,
                    region text,
                    timezone text,
                    is_verified integer default 0,
                    primary key (guild_id,member_id)
                    );
                    """)
        conn.commit()
    create_birthdays()
class Data:
    def next_birthday():
        conn, c = db()
        c.execute("select guild_id, member_id, next_birthday_utc from birthdays where is_verified = 1 and next_birthday_utc is not null order by datetime(next_birthday_utc) limit 1")
        items = c.fetchone()
        return items
    def all_verified(guild_id):
        conn, c = db()
        c.execute("select member_id from birthdays where guild_id = ? and is_verified = 1",(guild_id,))
        items = c.fetchall()
        res = []
        for (member_id,) in items:
            res.append(member_id)
        return res
    def all_birthdays(guild_id):
        conn, c = db()
        c.execute("select member_id,next_birthday_utc from birthdays where guild_id = ? and is_verified = 1 and next_birthday_utc is not null order by datetime(next_birthday_utc)",(guild_id,))
        items = c.fetchall()
        return items
    def get_last_announced_utc(guild_id,member_id):
        conn, c = db()
        c.execute("select last_announced_utc from birthdays where guild_id = ? and member_id = ?",(guild_id,member_id))
        last_announced_utc = c.fetchone()
        if last_announced_utc is None:
            return None
        (last_announced_utc,) = last_announced_utc
        return last_announced_utc
    def get_any_birthday_local(guild_id,member_id):
        conn, c = db()
        c.execute("select any_birthday_local from birthdays where guild_id = ? and member_id = ?",(guild_id,member_id))
        any_birthday_local = c.fetchone()
        if any_birthday_local is None:
            return None
        (any_birthday_local,) = any_birthday_local
        return any_birthday_local
    def get_timezone(guild_id,member_id):
        conn, c = db()
        c.execute("select region, timezone from birthdays where guild_id = ? and member_id = ?",(guild_id,member_id))
        tzinfo = c.fetchone()
        if tzinfo is None:
            return pytz.utc
        region,timezone = tzinfo
        if timezone is None:
            if region is None:
                return pytz.utc
            return pytz.timezone(config.REGION_TZ[region])
        return pytz.timezone(timezone)
    def ensure_member_id(guild_id,member_id):
        conn, c = db()
        c.execute("select * from birthdays where guild_id = ? and member_id = ?",(guild_id,member_id))
        item = c.fetchone()
        if item is None:
            c.execute("insert into birthdays (guild_id, member_id) values (?,?)",(guild_id,member_id))
        conn.commit()
    def unset_roles(guild_id):
        conn, c = db()
        c.execute("update birthdays set region = null, is_verified = 0 where guild_id = ?", (guild_id,))
        conn.commit()
    def delete_member(guild_id,member_id):
        conn, c = db()
        c.execute("delete from birthdays where guild_id = ? and member_id = ?",(guild_id,member_id))
        conn.commit()

    def delete_timezone(guild_id,member_id):
        conn, c = db()
        c.execute("update birthdays set timezone = null where guild_id = ? and member_id = ?",(guild_id,member_id))
        conn.commit()

    def delete_region(guild_id,member_id):
        conn, c = db()
        c.execute("update birthdays set region = null where guild_id = ? and member_id = ?",(guild_id,member_id))
        conn.commit()
    def set_elem(guild_id,member_id, name, value):
        assert name in ['any_birthday_local','next_birthday_utc','last_announced_utc','region','timezone','is_verified'],\
                f'Invalid field: {name}'
        conn, c = db()
        Data.ensure_member_id(guild_id,member_id)
        c.execute("update birthdays set " + name + " = ? where guild_id = ? and member_id = ?", (value,guild_id,member_id))
        conn.commit()
def scary_test0():
    drop_table('birthdays')
    create_tables()
    gid = 739681700539531285
    mid = 723072794665025597
    Data.ensure_member_id(gid,mid)
    conn,c = db()
    c.execute('select * from birthdays')
    items = c.fetchone()
    assert items is not None
def scary_test1():
    drop_table('birthdays')
    create_tables()
    gid = 739681700539531285
    mid = 723072794665025597
    Data.set_elem(gid,mid,'any_birthday_local',datetime.now())
    res = Data.all_birthdays(gid)
    assert res == list(), res
    Data.set_elem(gid,mid,'is_verified',1)
    res = Data.all_birthdays(gid)
    assert len(res) == 1,res
def scary_test():
    scary_test0()
    scary_test1()
if __name__ == '__main__':
    create_tables()
    gid = 739681700539531285
    mid = 723072794665025597
    conn, c = db()
    # c.execute('select next_birthday_utc from birthdays where next_birthday_utc is not null and is_verified = 1 order by datetime(next_birthday_utc);')
    # print(Data.all_birthdays(gid))

    # print(Data.next_birthday())


