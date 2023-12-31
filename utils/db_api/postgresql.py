from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config

class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        favorite_books JSONB NULL,
        date_of_registration date
        );
        """
        await self.execute(sql, execute=True)
    

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id):
        sql = "INSERT INTO users (full_name, username, telegram_id, date_of_registration) VALUES($1, $2, $3, NOW()::DATE) returning *"
        return await self.execute(sql, full_name, username, telegram_id, fetchrow=True)
    
    async def get_favorite_books(self, telegram_id):
        sql = f"SELECT favorite_books FROM USERS WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchrow=True) 
    
    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)
    
    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)
        
    async def count_users_by_month(self):
        sql = "SELECT DATE_TRUNC('MONTH', date_of_registration)::date m, COUNT(*) FROM Users GROUP BY m"
        return await self.execute(sql, fetch=True)
    
    async def count_users_by_day(self):
        sql = "SELECT DATE_TRUNC('DAY', date_of_registration)::date d, COUNT(*) FROM Users GROUP BY d"
        return await self.execute(sql, fetch=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def count_active_users(self):
        sql = "SELECT active_users FROM Details"
        return await self.execute(sql, fetchval=True)

    async def count_deactive_users(self):
        sql = "SELECT deactive_users FROM Details"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def update_user_favorite_books(self, favorite_books, telegram_id):
        sql = "UPDATE Users SET favorite_books=$1 WHERE telegram_id=$2"
        return await self.execute(sql, favorite_books, telegram_id, execute=True)

    async def update_active_users(self, active_users, id):
        sql = "UPDATE Details SET active_users=$1 WHERE id=$2"
        return await self.execute(sql, active_users, id, execute=True)

    async def update_deactive_users(self, deactive_users, id):
        sql = "UPDATE Details SET deactive_users=$1 WHERE id=$2"
        return await self.execute(sql, deactive_users, id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)