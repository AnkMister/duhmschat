"""
Data models for the options monitoring system.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class OptionType(str, Enum):
    """Type of option contract."""
    CALL = "call"
    PUT = "put"


class MoneyStatus(str, Enum):
    """
    Moneyness status of an option.

    ITM (In The Money): Option has intrinsic value
    - CALL: Stock price > Strike price
    - PUT: Stock price < Strike price

    ATM (At The Money): Stock price ≈ Strike price

    OTM (Out of The Money): Option has no intrinsic value
    - CALL: Stock price < Strike price
    - PUT: Stock price > Strike price
    """
    ITM = "itm"  # In The Money
    ATM = "atm"  # At The Money
    OTM = "otm"  # Out of The Money


class RuleType(str, Enum):
    """Types of monitoring rules."""
    ITM_ALERT = "itm_alert"  # Alert when option goes ITM
    OTM_ALERT = "otm_alert"  # Alert when option goes OTM
    EXPIRATION_WARNING = "expiration_warning"  # Days before expiration
    PROFIT_TARGET = "profit_target"  # Target profit percentage
    STOP_LOSS = "stop_loss"  # Stop loss percentage
    PRICE_THRESHOLD = "price_threshold"  # Stock price threshold
    DELTA_THRESHOLD = "delta_threshold"  # Greeks-based threshold
    INTRINSIC_VALUE = "intrinsic_value"  # Intrinsic value threshold


class OptionPosition(BaseModel):
    """
    Represents a single options position in the portfolio.
    """
    id: Optional[str] = Field(default=None, description="Unique identifier")
    symbol: str = Field(..., description="Underlying stock ticker symbol")
    option_type: OptionType = Field(..., description="CALL or PUT")
    strike_price: Decimal = Field(..., gt=0, description="Strike price of the option")
    expiration_date: date = Field(..., description="Option expiration date")
    quantity: int = Field(..., description="Number of contracts (negative for short)")
    premium_paid: Decimal = Field(..., description="Premium paid per share")
    purchase_date: date = Field(default_factory=date.today, description="Date position was opened")

    # Calculated/cached fields
    current_stock_price: Optional[Decimal] = Field(default=None, description="Current underlying price")
    current_option_price: Optional[Decimal] = Field(default=None, description="Current option premium")
    money_status: Optional[MoneyStatus] = Field(default=None, description="ITM/ATM/OTM status")
    intrinsic_value: Optional[Decimal] = Field(default=None, description="Intrinsic value per share")
    time_value: Optional[Decimal] = Field(default=None, description="Time value per share")
    days_to_expiration: Optional[int] = Field(default=None, description="Days until expiration")

    # Optional Greeks (if available from data source)
    delta: Optional[float] = Field(default=None, description="Delta Greek")
    gamma: Optional[float] = Field(default=None, description="Gamma Greek")
    theta: Optional[float] = Field(default=None, description="Theta Greek")
    vega: Optional[float] = Field(default=None, description="Vega Greek")
    implied_volatility: Optional[float] = Field(default=None, description="Implied Volatility")

    @field_validator('symbol')
    @classmethod
    def uppercase_symbol(cls, v: str) -> str:
        return v.upper().strip()

    @property
    def is_long(self) -> bool:
        """True if this is a long position (bought options)."""
        return self.quantity > 0

    @property
    def is_short(self) -> bool:
        """True if this is a short position (sold options)."""
        return self.quantity < 0

    @property
    def total_cost(self) -> Decimal:
        """Total cost/credit of the position (contracts * 100 shares * premium)."""
        return self.premium_paid * abs(self.quantity) * 100

    @property
    def is_expired(self) -> bool:
        """True if the option has expired."""
        return self.expiration_date < date.today()

    def calculate_money_status(self, stock_price: Decimal, atm_threshold: Decimal = Decimal("0.02")) -> MoneyStatus:
        """
        Calculate the moneyness status based on current stock price.

        Args:
            stock_price: Current price of the underlying stock
            atm_threshold: Percentage threshold for ATM (default 2%)

        Returns:
            MoneyStatus indicating ITM, ATM, or OTM
        """
        price_diff = stock_price - self.strike_price
        pct_diff = abs(price_diff / self.strike_price)

        # Check if at-the-money (within threshold)
        if pct_diff <= atm_threshold:
            return MoneyStatus.ATM

        if self.option_type == OptionType.CALL:
            # CALL is ITM when stock price > strike price
            return MoneyStatus.ITM if stock_price > self.strike_price else MoneyStatus.OTM
        else:
            # PUT is ITM when stock price < strike price
            return MoneyStatus.ITM if stock_price < self.strike_price else MoneyStatus.OTM

    def calculate_intrinsic_value(self, stock_price: Decimal) -> Decimal:
        """
        Calculate the intrinsic value of the option.

        Returns:
            Intrinsic value per share (minimum 0)
        """
        if self.option_type == OptionType.CALL:
            return max(Decimal(0), stock_price - self.strike_price)
        else:
            return max(Decimal(0), self.strike_price - stock_price)

    def calculate_profit_loss(self) -> Optional[Decimal]:
        """
        Calculate current profit/loss for the position.

        Returns:
            Profit/loss amount (positive = profit, negative = loss)
        """
        if self.current_option_price is None:
            return None

        if self.is_long:
            # Long: profit when option price increases
            return (self.current_option_price - self.premium_paid) * self.quantity * 100
        else:
            # Short: profit when option price decreases
            return (self.premium_paid - self.current_option_price) * abs(self.quantity) * 100

    def calculate_profit_loss_pct(self) -> Optional[float]:
        """Calculate profit/loss as a percentage."""
        if self.current_option_price is None or self.premium_paid == 0:
            return None

        if self.is_long:
            return float((self.current_option_price - self.premium_paid) / self.premium_paid * 100)
        else:
            return float((self.premium_paid - self.current_option_price) / self.premium_paid * 100)


class AlertRule(BaseModel):
    """
    A rule that triggers alerts based on option conditions.
    """
    id: Optional[str] = Field(default=None, description="Unique rule identifier")
    name: str = Field(..., description="Human-readable rule name")
    rule_type: RuleType = Field(..., description="Type of rule")
    enabled: bool = Field(default=True, description="Whether rule is active")

    # Rule parameters (interpretation depends on rule_type)
    threshold_value: Optional[Decimal] = Field(default=None, description="Threshold value for comparison")
    threshold_days: Optional[int] = Field(default=None, description="Days threshold (for expiration)")
    threshold_pct: Optional[float] = Field(default=None, description="Percentage threshold")

    # Scope
    apply_to_symbols: Optional[list[str]] = Field(default=None, description="Specific symbols (None = all)")
    apply_to_option_type: Optional[OptionType] = Field(default=None, description="Specific type (None = all)")

    # Notification settings
    priority: int = Field(default=1, ge=1, le=5, description="Priority level 1-5 (5=highest)")
    notification_message: Optional[str] = Field(default=None, description="Custom notification message")

    created_at: datetime = Field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = Field(default=None)


class Alert(BaseModel):
    """
    An alert generated when a rule is triggered.
    """
    id: Optional[str] = Field(default=None)
    rule_id: str = Field(..., description="ID of the rule that triggered this")
    rule_name: str = Field(..., description="Name of the rule")
    position_id: str = Field(..., description="ID of the affected position")
    symbol: str = Field(..., description="Underlying symbol")

    alert_type: RuleType = Field(..., description="Type of alert")
    message: str = Field(..., description="Alert message")
    priority: int = Field(default=1, ge=1, le=5)

    # Context
    current_value: Optional[Decimal] = Field(default=None, description="Current relevant value")
    threshold_value: Optional[Decimal] = Field(default=None, description="Threshold that was crossed")

    created_at: datetime = Field(default_factory=datetime.now)
    acknowledged: bool = Field(default=False)
    acknowledged_at: Optional[datetime] = Field(default=None)


class PortfolioSummary(BaseModel):
    """
    Summary statistics for the entire options portfolio.
    """
    total_positions: int = 0
    total_contracts: int = 0

    # Counts by status
    itm_count: int = 0
    atm_count: int = 0
    otm_count: int = 0

    # Counts by type
    calls_count: int = 0
    puts_count: int = 0
    long_count: int = 0
    short_count: int = 0

    # Financial metrics
    total_cost_basis: Decimal = Decimal(0)
    total_current_value: Optional[Decimal] = None
    total_profit_loss: Optional[Decimal] = None
    total_profit_loss_pct: Optional[float] = None

    # Risk metrics
    total_intrinsic_value: Decimal = Decimal(0)
    total_time_value: Optional[Decimal] = None

    # Expiration analysis
    expiring_this_week: int = 0
    expiring_this_month: int = 0

    # Alert counts
    active_alerts: int = 0
    unacknowledged_alerts: int = 0

    last_updated: datetime = Field(default_factory=datetime.now)


class ActionInsight(BaseModel):
    """
    An actionable insight or recommendation for the portfolio.
    """
    id: Optional[str] = Field(default=None)
    insight_type: str = Field(..., description="Type of insight")
    title: str = Field(..., description="Short title")
    description: str = Field(..., description="Detailed description")
    recommendation: str = Field(..., description="Recommended action")

    # Related positions
    affected_positions: list[str] = Field(default_factory=list, description="Position IDs affected")
    symbols: list[str] = Field(default_factory=list, description="Symbols involved")

    # Priority and urgency
    priority: int = Field(default=1, ge=1, le=5)
    urgency: str = Field(default="low", description="low, medium, high, critical")

    # Potential impact
    potential_profit: Optional[Decimal] = Field(default=None)
    potential_loss: Optional[Decimal] = Field(default=None)
    risk_level: str = Field(default="medium", description="low, medium, high")

    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(default=None)
