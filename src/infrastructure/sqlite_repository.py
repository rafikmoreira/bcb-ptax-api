import sqlite3
import os
from typing import List
from src.domain.entities import CurrencyQuotation
from src.domain.ports import QuotationRepository

class SQLiteQuotationRepository(QuotationRepository):
    def __init__(self, db_path: str = "data/db/quotations.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quotations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency TEXT NOT NULL,
                    target_date TEXT NOT NULL,
                    buy_rate_brl REAL NOT NULL,
                    sell_rate_brl REAL NOT NULL,
                    usd_parity_buy REAL NOT NULL,
                    usd_parity_sell REAL NOT NULL,
                    UNIQUE(currency, target_date)
                )
            """)
            conn.commit()

    def save_quotations(self, target_date: str, quotations: List[CurrencyQuotation]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for q in quotations:
                cursor.execute("""
                    INSERT OR REPLACE INTO quotations (
                        currency, target_date, buy_rate_brl, sell_rate_brl, usd_parity_buy, usd_parity_sell
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    q.currency, q.date, q.buy_rate_brl, q.sell_rate_brl, q.usd_parity_buy, q.usd_parity_sell
                ))
            conn.commit()

    def get_quotations_by_date(self, target_date: str) -> List[CurrencyQuotation]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT currency, target_date, buy_rate_brl, sell_rate_brl, usd_parity_buy, usd_parity_sell
                FROM quotations
                WHERE target_date = ?
            """, (target_date,))
            rows = cursor.fetchall()
            
            quotations = []
            for row in rows:
                q = CurrencyQuotation(
                    currency=row[0],
                    date=row[1],
                    buy_rate_brl=row[2],
                    sell_rate_brl=row[3],
                    usd_parity_buy=row[4],
                    usd_parity_sell=row[5]
                )
                quotations.append(q)
            return quotations
