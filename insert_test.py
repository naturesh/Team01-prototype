from src.database import db, Query


db.upsert({'agent_request' : True}, Query.roll_number==3)
