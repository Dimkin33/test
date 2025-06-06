import sqlite3

from dto import CurrencyDTO
from errors import CurrencyAlreadyExistsError, CurrencyNotFoundError

from .base import BaseModel


class CurrencyModel(BaseModel):
    """Модель для работы с валютами в базе данных."""

    def get_currency_by_code(self, code: str) -> dict:
        conn, cursor = self._get_connection_and_cursor()
        cursor.execute(
            'SELECT id, code, name, sign FROM currencies WHERE code = ?', (code,)
        )
        row = cursor.fetchone()
        if not row:
            raise CurrencyNotFoundError(code)
        return CurrencyDTO(*row).to_dict()

    def get_currencies(self) -> list[dict]:
        conn, cursor = self._get_connection_and_cursor()

        cursor.execute('SELECT id, code, name, sign FROM currencies')
        rows = cursor.fetchall()
        return [CurrencyDTO(*row).to_dict() for row in rows]

    def add_currency(self, code: str, name: str, sign: str) -> dict:
        code = code.upper()
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute(
                'INSERT INTO currencies (code, name, sign) VALUES (?, ?, ?)',
                (code, name, sign),
            )
            conn.commit()
            currency_id = cursor.lastrowid
            return CurrencyDTO(currency_id, code, name, sign).to_dict()
        except sqlite3.IntegrityError as e:
            raise CurrencyAlreadyExistsError(code) from e

    def delete_all_currencies(self):
        conn, cursor = self._get_connection_and_cursor()
        cursor.executescript("""
            DELETE FROM exchange_rates;
            DELETE FROM currencies;
            DELETE FROM sqlite_sequence WHERE name='exchange_rates';
            DELETE FROM sqlite_sequence WHERE name='currencies';
        """)
        conn.commit()
        return {'message': 'All currencies and exchange rates deleted, ids reset'}
