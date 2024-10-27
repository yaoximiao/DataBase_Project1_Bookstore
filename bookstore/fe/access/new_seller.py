from fe import conf
from fe.access import seller, auth


def register_new_seller(user_id, password) -> seller.Seller:
    a = auth.Auth(conf.URL)
    print("uid="+str(user_id))
    print("password="+str(password))
    code = a.register(user_id, password)
    print("code="+str(code))
    print("验证断言")
    print(code == 200)
    assert code == 200
    s = seller.Seller(conf.URL, user_id, password)
    return s
