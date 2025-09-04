import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()


def init_database():
    try:
        # Подключение к БД
        conn = psycopg2.connect(
            host=os.getenv("HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("USER"),
            password=os.getenv("DB_PASSWORD")
        )
        conn.autocommit = True  # Включаем autocommit для DDL команд
        cur = conn.cursor()

        print("✅ Connected to database")

        # 1. Удаляем таблицы если существуют (в правильном порядке из-за foreign keys)
        cur.execute("DROP TABLE IF EXISTS grades;")
        cur.execute("DROP TABLE IF EXISTS users;")
        print("✅ Dropped existing tables")

        # 2. Создаем таблицу users
        cur.execute("""
            CREATE TABLE users (
                telegram_id bigint NOT NULL PRIMARY KEY,
                login text NOT NULL,
                password text NOT NULL,
                last_change timestamp without time zone,
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created users table")

        # 3. Создаем последовательность для grades
        cur.execute("DROP SEQUENCE IF EXISTS grades_id_seq;")
        cur.execute("CREATE SEQUENCE grades_id_seq;")
        print("✅ Created sequence")

        # 4. Создаем таблицу grades
        cur.execute("""
            CREATE TABLE grades (
                id integer NOT NULL DEFAULT nextval('grades_id_seq'),
                telegram_id bigint,
                data jsonb NOT NULL,
                changed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT grades_pkey PRIMARY KEY (id),
                CONSTRAINT grades_telegram_id_fkey FOREIGN KEY (telegram_id)
                    REFERENCES users (telegram_id)
                    ON DELETE CASCADE
            );
        """)
        print("✅ Created grades table")

        # 5. Создаем индексы ОТДЕЛЬНЫМИ командами
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_grades_changed_at 
            ON grades USING btree (changed_at DESC NULLS FIRST);
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_grades_telegram_id 
            ON grades USING btree (telegram_id ASC NULLS LAST);
        """)
        print("✅ Created indexes")

        # 6. Создаем функцию для триггера (если не существует)
        cur.execute("""
            CREATE OR REPLACE FUNCTION update_user_last_change()
            RETURNS TRIGGER AS $$
            BEGIN
                UPDATE users 
                SET last_change = CURRENT_TIMESTAMP 
                WHERE telegram_id = NEW.telegram_id;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("✅ Created trigger function")

        # 7. Создаем триггер
        cur.execute("""
            DROP TRIGGER IF EXISTS grades_update_trigger ON grades;
            CREATE TRIGGER grades_update_trigger
                AFTER INSERT OR UPDATE 
                ON grades
                FOR EACH ROW
                EXECUTE FUNCTION update_user_last_change();
        """)
        print("✅ Created trigger")

        print("🎉 Database initialization completed successfully!")

    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
        print("✅ Database connection closed")


if __name__ == "__main__":
    init_database()