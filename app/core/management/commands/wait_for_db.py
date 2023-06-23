"""
Django command to wait for the database to be available to connect.
"""
import time

from MySQLdb import OperationalError as MySqlError
from django.db.utils import OperationalError

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Django command to wait for database
    """

    def handle(self, *args, **options):
        """
        Entrypoint for command.
        """
        self.stdout.write('Waiting for database...')
        db_active = False

        while db_active is False:
            try:
                self.check(databases=['default'])
                db_active = True
            except (MySqlError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
