import os
from app.models import user_datastore, Player, GoServer, Game, User
from app import app, db
from flask.ext.security.utils import encrypt_password 
import random
import datetime

# Create data for testing
def create_test_data():
    role_user = user_datastore.create_role(
        name='user',
        description='default role'
    )
    role_gs_admin = user_datastore.create_role(
        name='server_admin',
        description='Admin of a Go Server'
    )
    role_aga_admin = user_datastore.create_role(
        name='ratings_admin',
        description='Admin of AGA-Online Ratings'
    )

    u = user_datastore.create_user(email='admin@usgo.org',
                                   password=encrypt_password('usgo'),
                                   id=1)
    user_datastore.add_role_to_user(u, role_aga_admin)

    kgs_admin = user_datastore.create_user(email='admin@kgs.com',
                                           password=encrypt_password('kgs'),
                                           id=2)
    user_datastore.add_role_to_user(kgs_admin, role_gs_admin)

    u = user_datastore.create_user(email='foo@foo.com',
                                   aga_id=10,
                                   password=encrypt_password('foo'),
                                   id=3)
    db.session.add(Player(id=1,name="FooPlayerKGS",server_id=1,user_id=3,token="secret_foo_KGS"))
    db.session.add(Player(id=4,name="FooPlayerIGS",server_id=2,user_id=3,token="secret_foo_IGS"))
    user_datastore.add_role_to_user(u, role_user)

    u = user_datastore.create_user(email='bar@bar.com',
                                   aga_id=20,
                                   password=encrypt_password('bar'),
                                   id=4)
    db.session.add(Player(id=2,name="BarPlayerKGS",server_id=1,user_id=4,token="secret_bar_KGS"))
    db.session.add(Player(id=5,name="BarPlayerIGS",server_id=2,user_id=4,token="secret_bar_IGS"))
    user_datastore.add_role_to_user(u, role_user)

    u = user_datastore.create_user(email='baz@baz.com',
                                   aga_id=30,
                                   password=encrypt_password('baz'),
                                   id=5)
    db.session.add(Player(id=3,name="BazPlayerKGS",server_id=1,user_id=5,token="secret_baz_KGS"))
    db.session.add(Player(id=6,name="BazPlayerIGS",server_id=2,user_id=5,token="secret_baz_IGS"))
    user_datastore.add_role_to_user(u, role_user)


    gs = GoServer(id=1, name='KGS', url='http://gokgs.com', token='secret_kgs')
    gs.admins.append(kgs_admin)
    db.session.add(gs)
    db.session.add(GoServer(id=2, name='IGS',
                            url='http://pandanet.com',
                            token='secret_igs'))

    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, 'tests/testsgf.sgf')) as sgf_file:
        sgf_data = "\n".join(sgf_file.readlines()).encode()

    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="B+0.5", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="W+39.5", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=2, white_id=5, black_id=4, rated=True, result="W+Resign", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=2, white_id=5, black_id=4, rated=True, result="W+Resign", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=2, white_id=6, black_id=5, rated=True, result="W+Resign", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="B+0.5", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=1, white_id=3, black_id=2, rated=True, result="W+39.5", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=2, white_id=5, black_id=6, rated=True, result="W+Resign", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))

    db.session.commit()

    db.engine.execute("SELECT setval('myuser_id_seq', (SELECT MAX(id) FROM myuser))")
    db.engine.execute("SELECT setval('player_id_seq', (SELECT MAX(id) FROM player))")


def create_extra_data():
    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, 'tests/testsgf.sgf')) as sgf_file:
        sgf_data = "\n".join(sgf_file.readlines()).encode()
    role_user = user_datastore.find_role('user')
    for i in range(60):
        u = User(email='bla%d@example.com'%i, aga_id = 100000+i, password=encrypt_password('test'))
        user_datastore.add_role_to_user(u,role_user)
        db.session.add(u)
        db.session.commit()

        for j in range(2):
            db.session.add(Player(name="Player-%d-%d" % (i,j), server_id=1, user_id=u.id, token="Player-%d-%d" % (i,j)))

        db.session.commit()

    users = User.query.all()
    players = Player.query.all()
    p_priors = {user.id: random.randint(0,40) for user in users}
    for p, r in p_priors.items():
        print(p,r)

    from rating.math import expect
    def choose_pair():
        while True:
            pair = random.sample(users, 2)
            diff = abs(p_priors[pair[0].id] - p_priors[pair[1].id])
            if len(pair[0].players) > 0 and len(pair[1].players) > 0 and diff < 10:
                break
        return pair

    def make_game():
        user_pair = choose_pair()
        ps = (random.choice(user_pair[0].players).id, random.choice(user_pair[1].players).id)
        result = "B+5" if random.random() < expect(p_priors[user_pair[0].id], p_priors[user_pair[1].id]) else "W+5"
        g = Game(server_id=1, white_id=ps[0], black_id=ps[1],
                rated=False, result=result, game_record=sgf_data,
                date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,10000000)))
        return g

    print("Games...")
    games = [make_game() for i in range(1000)]
    print("Saving games...")
    for g in games:
        db.session.add(g)
    db.session.commit() 


if __name__ == '__main__': 
    import argparse
    random.seed(datetime.datetime.now().timestamp())

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--service", help="The DB service")
    args = parser.parse_args()
    app.config.from_object('config.DebugConfiguration')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')
    DB_SERVICE = args.service or os.environ.get('DB_SERVICE')
    DB_PORT = os.environ.get('DB_PORT')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI 
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.get_engine(app).dispose()
        print('Creating tables...')
        db.create_all()
        print('Creating test data...')
        create_test_data()
        print('Creating extra data...')
        create_extra_data()
