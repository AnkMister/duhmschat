"""
Price fetcher for stock and options data.

Uses yfinance for free stock/options quotes.
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import yfinance as yf
except ImportError:
    yf = None  # Will raise error on use

logger = logging.getLogger(__name__)


class PriceFetcherError(Exception):
    """Error fetching price data."""
    pass


class PriceFetcher:
    """
    Fetches real-time stock and options price data.

    Uses Yahoo Finance API (yfinance) for free price quotes.
    """

    def __init__(self, cache_ttl_seconds: int = 60):
        """
        Initialize the price fetcher.

        Args:
            cache_ttl_seconds: How long to cache prices (default 60s)
        """
        if yf is None:
            raise ImportError(
                "yfinance is required for price fetching. "
                "Install it with: pip install yfinance"
            )

        self._cache: dict[str, tuple[datetime, dict]] = {}
        self._cache_ttl = timedelta(seconds=cache_ttl_seconds)

    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data for symbol is still valid."""
        if symbol not in self._cache:
            return False
        cache_time, _ = self._cache[symbol]
        return datetime.now() - cache_time < self._cache_ttl

    def _get_from_cache(self, symbol: str) -> Optional[dict]:
        """Get data from cache if valid."""
        if self._is_cache_valid(symbol):
            _, data = self._cache[symbol]
            return data
        return None

    def _set_cache(self, symbol: str, data: dict) -> None:
        """Store data in cache."""
        self._cache[symbol] = (datetime.now(), data)

    def get_stock_price(self, symbol: str) -> Decimal:
        """
        Get the current stock price for a symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Current stock price as Decimal

        Raises:
            PriceFetcherError: If price cannot be fetched
        """
        symbol = symbol.upper().strip()

        # Check cache
        cached = self._get_from_cache(symbol)
        if cached and 'price' in cached:
            return cached['price']

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Try multiple price fields in order of preference
            price = None
            for field in ['regularMarketPrice', 'currentPrice', 'previousClose', 'ask', 'bid']:
                if field in info and info[field]:
                    price = Decimal(str(info[field]))
                    break

            if price is None:
                # Try fast_info as fallback
                try:
                    fast = ticker.fast_info
                    if hasattr(fast, 'last_price') and fast.last_price:
                        price = Decimal(str(fast.last_price))
                except Exception:
                    pass

            if price is None:
                raise PriceFetcherError(f"Could not get price for {symbol}")

            # Cache the result
            self._set_cache(symbol, {'price': price, 'info': info})

            return price

        except PriceFetcherError:
            raise
        except Exception as e:
            raise PriceFetcherError(f"Error fetching price for {symbol}: {e}")

    def get_stock_prices_batch(self, symbols: list[str]) -> dict[str, Decimal]:
        """
        Get stock prices for multiple symbols efficiently.

        Args:
            symbols: List of stock ticker symbols

        Returns:
            Dict mapping symbol to price
        """
        results = {}
        symbols = [s.upper().strip() for s in symbols]

        # Check cache first
        uncached = []
        for symbol in symbols:
            cached = self._get_from_cache(symbol)
            if cached and 'price' in cached:
                results[symbol] = cached['price']
            else:
                uncached.append(symbol)

        if not uncached:
            return results

        # Fetch uncached symbols in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(self.get_stock_price, symbol): symbol
                for symbol in uncached
            }

            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    results[symbol] = future.result()
                except Exception as e:
                    logger.warning(f"Failed to fetch price for {symbol}: {e}")

        return results

    def get_stock_info(self, symbol: str) -> dict:
        """
        Get detailed stock information.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict with stock information
        """
        symbol = symbol.upper().strip()

        cached = self._get_from_cache(symbol)
        if cached and 'info' in cached:
            return cached['info']

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Cache the result
            price = None
            for field in ['regularMarketPrice', 'currentPrice', 'previousClose']:
                if field in info and info[field]:
                    price = Decimal(str(info[field]))
                    break

            if price:
                self._set_cache(symbol, {'price': price, 'info': info})

            return info

        except Exception as e:
            raise PriceFetcherError(f"Error fetching info for {symbol}: {e}")

    def get_options_chain(
        self,
        symbol: str,
        expiration_date: Optional[date] = None
    ) -> dict:
        """
        Get options chain data for a symbol.

        Args:
            symbol: Stock ticker symbol
            expiration_date: Specific expiration date (optional)

        Returns:
            Dict with 'calls' and 'puts' DataFrames
        """
        symbol = symbol.upper().strip()

        try:
            ticker = yf.Ticker(symbol)

            # Get available expiration dates
            expirations = ticker.options

            if not expirations:
                raise PriceFetcherError(f"No options available for {symbol}")

            # Select expiration date
            if expiration_date:
                exp_str = expiration_date.strftime("%Y-%m-%d")
                if exp_str not in expirations:
                    # Find closest date
                    exp_dates = [datetime.strptime(e, "%Y-%m-%d").date() for e in expirations]
                    closest = min(exp_dates, key=lambda d: abs((d - expiration_date).days))
                    exp_str = closest.strftime("%Y-%m-%d")
            else:
                exp_str = expirations[0]

            # Get options chain
            chain = ticker.option_chain(exp_str)

            return {
                'expiration': exp_str,
                'calls': chain.calls,
                'puts': chain.puts,
                'available_expirations': expirations
            }

        except PriceFetcherError:
            raise
        except Exception as e:
            raise PriceFetcherError(f"Error fetching options for {symbol}: {e}")

    def get_option_quote(
        self,
        symbol: str,
        option_type: str,
        strike_price: Decimal,
        expiration_date: date
    ) -> Optional[dict]:
        """
        Get quote for a specific option contract.

        Args:
            symbol: Underlying stock symbol
            option_type: 'call' or 'put'
            strike_price: Strike price
            expiration_date: Option expiration date

        Returns:
            Dict with option data or None if not found
        """
        try:
            chain = self.get_options_chain(symbol, expiration_date)

            # Select calls or puts
            options_df = chain['calls'] if option_type.lower() == 'call' else chain['puts']

            if options_df.empty:
                return None

            # Find matching strike
            strike_float = float(strike_price)
            matches = options_df[abs(options_df['strike'] - strike_float) < 0.01]

            if matches.empty:
                return None

            row = matches.iloc[0]

            return {
                'contract_symbol': row.get('contractSymbol', ''),
                'last_price': Decimal(str(row.get('lastPrice', 0))),
                'bid': Decimal(str(row.get('bid', 0))),
                'ask': Decimal(str(row.get('ask', 0))),
                'volume': int(row.get('volume', 0) or 0),
                'open_interest': int(row.get('openInterest', 0) or 0),
                'implied_volatility': float(row.get('impliedVolatility', 0) or 0),
                'in_the_money': bool(row.get('inTheMoney', False)),
            }

        except Exception as e:
            logger.warning(f"Error getting option quote: {e}")
            return None

    def get_historical_prices(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> list[dict]:
        """
        Get historical price data.

        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            List of price data dicts
        """
        symbol = symbol.upper().strip()

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)

            results = []
            for idx, row in hist.iterrows():
                results.append({
                    'date': idx.to_pydatetime(),
                    'open': Decimal(str(row['Open'])),
                    'high': Decimal(str(row['High'])),
                    'low': Decimal(str(row['Low'])),
                    'close': Decimal(str(row['Close'])),
                    'volume': int(row['Volume']),
                })

            return results

        except Exception as e:
            raise PriceFetcherError(f"Error fetching history for {symbol}: {e}")

    def clear_cache(self, symbol: Optional[str] = None) -> None:
        """
        Clear the price cache.

        Args:
            symbol: Specific symbol to clear, or None to clear all
        """
        if symbol:
            symbol = symbol.upper().strip()
            if symbol in self._cache:
                del self._cache[symbol]
        else:
            self._cache.clear()
