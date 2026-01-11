"""
Options analyzer for calculating ITM/OTM/ATM status and other metrics.
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Optional

from .models import OptionPosition, OptionType, MoneyStatus
from .price_fetcher import PriceFetcher

logger = logging.getLogger(__name__)


class OptionsAnalyzer:
    """
    Analyzes options positions for moneyness, value, and other metrics.

    Key Definitions:
    - ITM (In The Money):
        - CALL: Stock price > Strike price (option has intrinsic value)
        - PUT: Stock price < Strike price (option has intrinsic value)
    - ATM (At The Money):
        - Stock price ≈ Strike price (within threshold, typically 2%)
    - OTM (Out of The Money):
        - CALL: Stock price < Strike price (no intrinsic value)
        - PUT: Stock price > Strike price (no intrinsic value)
    """

    def __init__(
        self,
        price_fetcher: Optional[PriceFetcher] = None,
        atm_threshold_pct: float = 0.02
    ):
        """
        Initialize the analyzer.

        Args:
            price_fetcher: Price fetcher instance (creates new if None)
            atm_threshold_pct: Percentage threshold for ATM status (default 2%)
        """
        self.price_fetcher = price_fetcher or PriceFetcher()
        self.atm_threshold = Decimal(str(atm_threshold_pct))

    def analyze_position(
        self,
        position: OptionPosition,
        stock_price: Optional[Decimal] = None,
        fetch_option_price: bool = True
    ) -> OptionPosition:
        """
        Analyze a single option position and update its metrics.

        Args:
            position: The option position to analyze
            stock_price: Current stock price (fetches if None)
            fetch_option_price: Whether to fetch current option price

        Returns:
            Updated position with calculated metrics
        """
        # Get stock price if not provided
        if stock_price is None:
            try:
                stock_price = self.price_fetcher.get_stock_price(position.symbol)
            except Exception as e:
                logger.warning(f"Could not fetch price for {position.symbol}: {e}")
                return position

        position.current_stock_price = stock_price

        # Calculate money status
        position.money_status = self._calculate_money_status(
            option_type=position.option_type,
            strike_price=position.strike_price,
            stock_price=stock_price
        )

        # Calculate intrinsic value
        position.intrinsic_value = self._calculate_intrinsic_value(
            option_type=position.option_type,
            strike_price=position.strike_price,
            stock_price=stock_price
        )

        # Calculate days to expiration
        position.days_to_expiration = self._calculate_days_to_expiration(
            position.expiration_date
        )

        # Fetch current option price if requested
        if fetch_option_price:
            try:
                option_data = self.price_fetcher.get_option_quote(
                    symbol=position.symbol,
                    option_type=position.option_type.value,
                    strike_price=position.strike_price,
                    expiration_date=position.expiration_date
                )

                if option_data:
                    # Use mid-point of bid-ask or last price
                    bid = option_data.get('bid', Decimal(0))
                    ask = option_data.get('ask', Decimal(0))

                    if bid > 0 and ask > 0:
                        position.current_option_price = (bid + ask) / 2
                    else:
                        position.current_option_price = option_data.get('last_price')

                    # Set implied volatility if available
                    if option_data.get('implied_volatility'):
                        position.implied_volatility = option_data['implied_volatility']

                    # Calculate time value
                    if position.current_option_price:
                        position.time_value = max(
                            Decimal(0),
                            position.current_option_price - position.intrinsic_value
                        )

            except Exception as e:
                logger.debug(f"Could not fetch option quote: {e}")

        return position

    def analyze_positions(
        self,
        positions: list[OptionPosition],
        fetch_option_prices: bool = True
    ) -> list[OptionPosition]:
        """
        Analyze multiple positions efficiently.

        Args:
            positions: List of positions to analyze
            fetch_option_prices: Whether to fetch option prices

        Returns:
            List of updated positions
        """
        if not positions:
            return []

        # Get unique symbols
        symbols = list(set(p.symbol for p in positions))

        # Batch fetch stock prices
        try:
            prices = self.price_fetcher.get_stock_prices_batch(symbols)
        except Exception as e:
            logger.warning(f"Error fetching batch prices: {e}")
            prices = {}

        # Analyze each position
        results = []
        for position in positions:
            stock_price = prices.get(position.symbol)
            analyzed = self.analyze_position(
                position=position,
                stock_price=stock_price,
                fetch_option_price=fetch_option_prices
            )
            results.append(analyzed)

        return results

    def get_itm_positions(self, positions: list[OptionPosition]) -> list[OptionPosition]:
        """
        Filter positions that are In The Money.

        Args:
            positions: List of positions (should be pre-analyzed)

        Returns:
            List of ITM positions
        """
        return [p for p in positions if p.money_status == MoneyStatus.ITM]

    def get_otm_positions(self, positions: list[OptionPosition]) -> list[OptionPosition]:
        """
        Filter positions that are Out of The Money.

        Args:
            positions: List of positions (should be pre-analyzed)

        Returns:
            List of OTM positions
        """
        return [p for p in positions if p.money_status == MoneyStatus.OTM]

    def get_atm_positions(self, positions: list[OptionPosition]) -> list[OptionPosition]:
        """
        Filter positions that are At The Money.

        Args:
            positions: List of positions (should be pre-analyzed)

        Returns:
            List of ATM positions
        """
        return [p for p in positions if p.money_status == MoneyStatus.ATM]

    def get_expiring_soon(
        self,
        positions: list[OptionPosition],
        days: int = 7
    ) -> list[OptionPosition]:
        """
        Get positions expiring within specified days.

        Args:
            positions: List of positions
            days: Number of days threshold

        Returns:
            List of positions expiring soon
        """
        today = date.today()
        return [
            p for p in positions
            if (p.expiration_date - today).days <= days and p.expiration_date >= today
        ]

    def get_profitable_positions(
        self,
        positions: list[OptionPosition]
    ) -> list[OptionPosition]:
        """
        Get positions that are currently profitable.

        Args:
            positions: List of positions (should be pre-analyzed with option prices)

        Returns:
            List of profitable positions
        """
        return [
            p for p in positions
            if p.calculate_profit_loss() is not None and p.calculate_profit_loss() > 0
        ]

    def get_losing_positions(
        self,
        positions: list[OptionPosition]
    ) -> list[OptionPosition]:
        """
        Get positions that are currently losing money.

        Args:
            positions: List of positions (should be pre-analyzed with option prices)

        Returns:
            List of losing positions
        """
        return [
            p for p in positions
            if p.calculate_profit_loss() is not None and p.calculate_profit_loss() < 0
        ]

    def _calculate_money_status(
        self,
        option_type: OptionType,
        strike_price: Decimal,
        stock_price: Decimal
    ) -> MoneyStatus:
        """
        Calculate the moneyness status of an option.

        ITM (In The Money):
        - CALL: Stock price > Strike price
        - PUT: Stock price < Strike price

        OTM (Out of The Money):
        - CALL: Stock price < Strike price
        - PUT: Stock price > Strike price

        ATM (At The Money):
        - Stock price ≈ Strike price (within threshold)
        """
        price_diff = stock_price - strike_price
        pct_diff = abs(price_diff / strike_price)

        # Check if at-the-money (within threshold)
        if pct_diff <= self.atm_threshold:
            return MoneyStatus.ATM

        if option_type == OptionType.CALL:
            # CALL is ITM when stock price > strike price
            return MoneyStatus.ITM if stock_price > strike_price else MoneyStatus.OTM
        else:
            # PUT is ITM when stock price < strike price
            return MoneyStatus.ITM if stock_price < strike_price else MoneyStatus.OTM

    def _calculate_intrinsic_value(
        self,
        option_type: OptionType,
        strike_price: Decimal,
        stock_price: Decimal
    ) -> Decimal:
        """
        Calculate the intrinsic value of an option.

        Intrinsic value is the amount by which the option is ITM.
        - CALL: max(0, stock_price - strike_price)
        - PUT: max(0, strike_price - stock_price)
        """
        if option_type == OptionType.CALL:
            return max(Decimal(0), stock_price - strike_price)
        else:
            return max(Decimal(0), strike_price - stock_price)

    def _calculate_days_to_expiration(self, expiration_date: date) -> int:
        """Calculate days until option expiration."""
        return (expiration_date - date.today()).days

    def calculate_breakeven(self, position: OptionPosition) -> Decimal:
        """
        Calculate the breakeven price for a position.

        For long positions:
        - CALL: Strike + Premium paid
        - PUT: Strike - Premium paid

        For short positions:
        - CALL: Strike + Premium received
        - PUT: Strike - Premium received
        """
        if position.option_type == OptionType.CALL:
            return position.strike_price + position.premium_paid
        else:
            return position.strike_price - position.premium_paid

    def calculate_max_profit(self, position: OptionPosition) -> Optional[Decimal]:
        """
        Calculate maximum potential profit.

        Returns None for unlimited profit potential (long calls).
        """
        if position.is_long:
            if position.option_type == OptionType.CALL:
                return None  # Unlimited upside
            else:
                # Long put: max profit = strike - premium (if stock goes to 0)
                return (position.strike_price - position.premium_paid) * abs(position.quantity) * 100
        else:
            # Short positions: max profit = premium received
            return position.premium_paid * abs(position.quantity) * 100

    def calculate_max_loss(self, position: OptionPosition) -> Optional[Decimal]:
        """
        Calculate maximum potential loss.

        Returns None for unlimited loss potential (short calls).
        """
        if position.is_long:
            # Long positions: max loss = premium paid
            return position.premium_paid * abs(position.quantity) * 100
        else:
            if position.option_type == OptionType.CALL:
                return None  # Unlimited downside for naked short calls
            else:
                # Short put: max loss = strike - premium (if stock goes to 0)
                return (position.strike_price - position.premium_paid) * abs(position.quantity) * 100

    def get_status_summary(self, position: OptionPosition) -> str:
        """
        Get a human-readable status summary for a position.
        """
        if position.money_status is None:
            return "Status unknown (price data unavailable)"

        status_map = {
            MoneyStatus.ITM: "IN THE MONEY",
            MoneyStatus.ATM: "AT THE MONEY",
            MoneyStatus.OTM: "OUT OF THE MONEY",
        }

        status = status_map.get(position.money_status, "Unknown")

        parts = [
            f"{position.symbol} {position.option_type.value.upper()}",
            f"${position.strike_price} strike",
            f"exp {position.expiration_date}",
            f"→ {status}"
        ]

        if position.current_stock_price:
            parts.append(f"(stock @ ${position.current_stock_price:.2f})")

        if position.intrinsic_value and position.intrinsic_value > 0:
            parts.append(f"Intrinsic: ${position.intrinsic_value:.2f}")

        return " | ".join(parts)
