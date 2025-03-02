import sqlalchemy
from sqlalchemy.ext.automap import automap_base
import warnings
from sqlalchemy.exc import SAWarning

warnings.filterwarnings("ignore", category=SAWarning, message="Did not recognize type*")

url = sqlalchemy.engine.URL.create(
    drivername="postgresql",
    username="fire_user",
    password="fire_pass",
    host="127.0.0.1",
    database="",
)

engine = sqlalchemy.create_engine(url)

Base = automap_base()
Base.prepare(autoload_with=engine, schema="")

SessionLocal = sqlalchemy.orm.sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
