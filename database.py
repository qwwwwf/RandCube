import os
import asyncio

from sqlalchemy import and_
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, insert, update, MetaData, Table, Column, Integer, Boolean, String, JSON

load_dotenv()
data_url = 'sqlite+aiosqlite'

engine = create_async_engine(f'{data_url}:///{os.getenv("DB_URI")}')
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
metadata = MetaData()


users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('uid', Integer, nullable=False, unique=True),
              Column('allowSeeFacts', Boolean, nullable=False, default=False),
              Column('lastGenerationNumber', JSON, nullable=False, default={
                  'generation_count': 1,
                  'min_value': 1,
                  'max_value': 100
              }),
              Column('lastGenerationPassword', JSON, nullable=False, default={
                  'generation_count': 1,
                  'password_size': 8,
                  'has_punctuation': True
              })
              )

events = Table('events', metadata,
               Column('id', Integer, primary_key=True),
               Column('secretId', String, nullable=False, unique=True),
               Column('creatorId', Integer, nullable=False),
               Column('active', Boolean, nullable=False, default=True),
               Column('prizesCount', Integer, nullable=False),
               Column('membersCount', Integer, nullable=False),
               Column('description', String, nullable=False, default='отсутствует'),
               Column('winners', JSON, nullable=False, default=[]),
               Column('members', JSON, default=[])
               )


async def create_tables():
    async with async_session() as session:
        try:
            await session.execute(CreateTable(users))
            await session.execute(CreateTable(events))
        except OperationalError:
            pass


class Event:
    def __init__(self, uid):
        self.uid = uid

    async def create_event(self, secret_id: str, prizes_count: int, members_count: int) -> None:
        try:
            async with async_session() as session:
                await session.execute(
                    insert(events)
                    .values(
                        secretId=secret_id,
                        creatorId=self.uid,
                        prizesCount=prizes_count,
                        membersCount=members_count
                    ))
                await session.commit()
        except SQLAlchemyError as error:
            print(error)

    async def get_user_event(self) -> dict:
        try:
            async with async_session() as session:
                if (await session.execute(
                        select(events.columns.id)
                        .where(and_(events.columns.creatorId == self.uid, events.columns.active.is_(True)))))\
                        .scalars().first() is not None:

                    data = (await session.execute(
                        select(events)
                        .where(and_(events.columns.creatorId == self.uid, events.columns.active.is_(True))))).one()

                    return {
                        'secret_id': data[1],
                        'description': data[6],
                        'prizes_count': data[4],
                        'members_count': data[5],
                        'members': data[8]
                    }
                else:
                    return {}
        except SQLAlchemyError as error:
            print(error)

    async def add_user_into_event(self, secret_id: str) -> bool:
        try:
            async with async_session() as session:
                if (await session.execute(
                        select(events.columns.secretId)
                        .where(events.columns.secretId == secret_id))).scalars().first() is not None:

                    data = (await session.execute(
                        select(events)
                        .where(events.columns.secretId == secret_id))).one()

                    if data[3] is True and len(data[7]) < data[5]:
                        event_members = (await session.execute(
                            select(events.columns.members)
                            .where(events.columns.secretId == secret_id))).scalars().first()

                        if self.uid not in event_members:
                            event_members.append(self.uid)

                            await session.execute(
                                update(events)
                                .where(events.columns.secretId == secret_id)
                                .values(members=event_members))
                            await session.commit()

                            return True

                return False
        except SQLAlchemyError as error:
            print(error)

    async def get_users_events(self) -> list:
        try:
            async with async_session() as session:
                return (await session.execute(
                    select(events)
                    .where(and_(events.columns.active.is_(True), events.columns.members.contains(self.uid))))).all()
        except SQLAlchemyError as error:
            print(error)

    async def get_event_members(self, secret_id: str) -> list:
        try:
            async with async_session() as session:
                return (await session.execute(
                            select(events.columns.members)
                            .where(events.columns.secretId == secret_id))).scalars().first()
        except SQLAlchemyError as error:
            print(error)

    async def cancel_event(self, secret_id: str) -> None:
        try:
            async with async_session() as session:
                await session.execute(
                    update(events)
                    .where(events.columns.secretId == secret_id)
                    .values(
                        active=False
                    ))
                await session.commit()
        except SQLAlchemyError as error:
            print(error)

    async def update_event_description(self, secret_id: str, new_description: str) -> None:
        try:
            async with async_session() as session:
                await session.execute(
                    update(events).
                    where(events.columns.secretId == secret_id)
                    .values(
                        description=new_description
                    ))
                await session.commit()
        except SQLAlchemyError as error:
            print(error)

    async def update_event_winners(self, secret_id: str, winners: list) -> None:
        try:
            async with async_session() as session:
                await session.execute(
                    update(events).
                    where(events.columns.secretId == secret_id)
                    .values(
                        winners=winners
                    ))
                await session.commit()
        except SQLAlchemyError as error:
            print(error)


class User:
    def __init__(self, uid):
        self.uid = uid

    async def user_exists(self) -> bool:
        try:
            async with async_session() as session:
                if (await session.execute(
                        select(users.columns.id)
                        .where(users.columns.uid.contains(self.uid)))).scalars().first() is not None:
                    return True
                else:
                    return False
        except SQLAlchemyError as error:
            print(error)

    async def create_user(self) -> None:
        try:
            async with async_session() as session:
                await session.execute(insert(users).values(uid=self.uid))
                await session.commit()
        except SQLAlchemyError as error:
            print(error)

    async def user_is_allow_see_facts(self) -> bool:
        try:
            async with async_session() as session:
                return (await session.execute(
                    select(users.columns.allowSeeFacts)
                    .where(users.columns.uid.contains(self.uid)))).scalars().first()
        except SQLAlchemyError as error:
            print(error)

    async def change_allow_see_facts(self, boolean: bool) -> None:
        try:
            async with async_session() as session:
                await session.execute(
                    update(users)
                    .where(users.columns.uid.contains(self.uid))
                    .values(
                        allowSeeFacts=boolean
                    ))
                await session.commit()
        except SQLAlchemyError as error:
            print(error)

    async def get_last_generation_number(self) -> dict:
        try:
            async with async_session() as session:
                return (await session.execute(
                    select(users.columns.lastGenerationNumber)
                    .where(users.columns.uid.contains(self.uid)))).scalars().first()
        except SQLAlchemyError as error:
            print(error)

    async def get_last_generation_password(self) -> dict:
        try:
            async with async_session() as session:
                return (await session.execute(
                    select(users.columns.lastGenerationPassword)
                    .where(users.columns.uid.contains(self.uid)))).scalars().first()
        except SQLAlchemyError as error:
            print(error)

    async def update_generation_number_params(self, new_params: dict) -> None:
        try:
            async with async_session() as session:
                await session.execute(
                    update(users)
                    .where(users.columns.uid.contains(self.uid))
                    .values(
                        lastGenerationNumber=new_params
                    ))
                await session.commit()
        except SQLAlchemyError as error:
            print(error)

    async def update_generation_password_params(self, new_params: dict) -> None:
        try:
            async with async_session() as session:
                await session.execute(
                    update(users)
                    .where(users.columns.uid.contains(self.uid))
                    .values(
                        lastGenerationPassword=new_params
                    ))
                await session.commit()
        except SQLAlchemyError as error:
            print(error)


asyncio.run(create_tables())
