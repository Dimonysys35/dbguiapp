def select(cur, table):
    res = cur.execute(f"select * from '{table}'")
    res = res.fetchall()
    return res 

def get_one(cur, table, id):
    req = f"SELECT * FROM {table} WHERE id = {id}"
    res = cur.execute(req)
    res = res.fetchone()
    return res

def get_id(cur, table):
    res = cur.execute(f"select id from '{table}'")
    res = res.fetchall()
    res = [re[0] for re in res]
    return res 

def get_headers(cur, table):
    req = f"PRAGMA table_info({table});"
    res = cur.execute(req)
    res = res.fetchall()
    res = [ar[1] for ar in res]
    return res

def get_tables(cur):
    req = f"SELECT name FROM sqlite_master WHERE type='table'"
    res = cur.execute(req)
    res = res.fetchall()
    rez = []
    for i in res:
        if i[0] != 'sqlite_sequence':
            rez.append(i[0])
    return rez

def update(cur, table, fields, values, id):
    req = f"UPDATE {table} SET "
    for i in range(len(values)):    
        req += "'" +str(fields[i]) + "' = '" + str(values[i]) + "'"
        if i != len(values)-1:
            req += " , "
    req += f" WHERE id = {id};"
    cur.execute(req)

def delete(cur, table, id):
    req = f"DELETE FROM {table} WHERE id = {id}"
    cur.execute(req)

def insert(cur, table, fields, values):
    fields = ['\''+str(field)+'\'' for field in fields]
    values = ['\''+str(value)+'\'' for value in values]
    req = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join(values)})"
    cur.execute(req)

