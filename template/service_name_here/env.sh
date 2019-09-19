export RABBITURL=amqp://terraPorta:terraPorta@localhost:5672/terraPorta/
export NOTIFY_EXCHANGE=notification
export MONGO_DB_FIRE=fireservice # replace with correct DB | 
export MONGO_PASSWORD=fireservice1! # replace with correct DB password | 
export MONGO_USER=fireservice # replace with correct DB user | 
export MONGO_ADDR=127.0.0.1
export MONGO_PORT=27017

export POSTGRES_ADDR=127.0.0.1
export POSTGRES_PORT=5432
export POSTGRES_USER=terraporta
export POSTGRES_PASSWORD=terraPorta
export POSTGRES_DB=terraporta_db

export SCHEDULE_TIME_FIRE=5 # replace with correct time
export SCHEDULE_DELETE_DAYS_FIRE=7 # replace with correct time

# replace as necessary
export FIRE_EVENT_ID=FireService

export FIRE_URL=https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/csv/VNP14IMGTDL_NRT_Global_24h.csv
