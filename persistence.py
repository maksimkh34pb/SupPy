import pickle

USERS_DB_PATH = "users.pkl"


# def append(obj, path=USERS_DB_PATH):
#     with open(path, 'ab') as outp:
#         try:
#             pickle.dump(obj=obj, file=outp, protocol=pickle.HIGHEST_PROTOCOL)
#         except FileNotFoundError:
#             open(path, 'a').close()
#             pickle.dump(obj=obj, file=outp, protocol=pickle.HIGHEST_PROTOCOL)

#
# def load(path=USERS_DB_PATH) -> []:
#     db = []
#     try:
#         with open(path, 'rb') as inp:
#             while data := pickle.load(inp):
#                 db.append(data)
#     except EOFError:
#         return db
#     except FileNotFoundError:
#         return []

def append(obj, path=USERS_DB_PATH) -> None:
    with open(path, 'ab') as outp:
        try:
            pickle.dump(obj=obj, file=outp, protocol=pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            open(path, 'a').close()
            pickle.dump(obj=obj, file=outp, protocol=pickle.HIGHEST_PROTOCOL)


def read_by_item(path=USERS_DB_PATH) -> []:
    db = []
    try:
        with open(path, 'rb') as inp:
            while data := pickle.load(inp):
                db.append(data)
    except EOFError:
        return db
    except FileNotFoundError:
        return []


def write(obj: [], path=USERS_DB_PATH):
    with open(path, 'wb') as outp:
        try:
            pickle.dump(obj=obj, file=outp, protocol=pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            open(path, 'a').close()
            pickle.dump(obj=obj, file=outp, protocol=pickle.HIGHEST_PROTOCOL)


def read_list(path=USERS_DB_PATH):
    try:
        with open(path, 'rb') as inp:
            return pickle.load(inp)
    except EOFError:
        return []
    except FileNotFoundError:
        return []
