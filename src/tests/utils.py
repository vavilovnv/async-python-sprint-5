TEST_DB_NAME = "test_db"
database_dsn = (f'postgresql+asyncpg://postgres:'
                f'postgres@localhost:5432/{TEST_DB_NAME}')
BASE_URL = 'http://127.0.0.1'
REDIS_URL = "redis://127.0.0.1:6379"
REDIS_KEY = 'PYTEST'
TEST_USER1 = "test_user"
TEST_USER2 = "test_user2"
TEST_PASSWORD = "password"
