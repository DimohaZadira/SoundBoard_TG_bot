set -e

DOCKER="podman"
PG_VERSION="17"
IMAGE_NAME="docker.io/library/postgres:$PG_VERSION"
PG_HOME="$PWD/.postgres_data"

PG_PASSWORD="insecure1111"
PG_USER="test_user"
PG_DATABASE="test_database"

mkdir -p "$PG_HOME/"

$DOCKER run \
	  --env POSTGRES_USER="$PG_USER" \
	  --env POSTGRES_PASSWORD="$PG_PASSWORD" \
	  --env POSTGRES_DB="$PG_DATABASE" \
	  --env PGDATA="/var/lib/postgresql/data/pgdata" \
	  --volume "$PG_HOME:/var/lib/postgresql/data/pgdata" \
	  --publish 5432:5432 \
	  $IMAGE_NAME
