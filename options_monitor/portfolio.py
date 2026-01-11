"""
Portfolio manager for options positions, analytics, and optimization insights.
"""

import json
import logging
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Optional

from .models import (
    OptionPosition,
    OptionType,
    MoneyStatus,
    PortfolioSummary,
    ActionInsight,
    AlertRule,
    Alert,
)
from .analyzer import OptionsAnalyzer
from .rules_engine import RulesEngine
from .price_fetcher import PriceFetcher

logger = logging.getLogger(__name__)


class PortfolioManager:
    """
    Manages options portfolio, provides analytics, and generates insights.

    Features:
    - Position tracking and persistence
    - Portfolio-level analytics
    - Actionable insights and optimization suggestions
    - Alert management
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        price_fetcher: Optional[PriceFetcher] = None,
    ):
        """
        Initialize the portfolio manager.

        Args:
            storage_path: Path to store portfolio data (JSON file)
            price_fetcher: Price fetcher instance
        """
        self.storage_path = storage_path or Path("portfolio_data.json")
        self.price_fetcher = price_fetcher or PriceFetcher()
        self.analyzer = OptionsAnalyzer(price_fetcher=self.price_fetcher)
        self.rules_engine = RulesEngine()

        self.positions: list[OptionPosition] = []
        self.alerts: list[Alert] = []
        self.insights: list[ActionInsight] = []

        # Load existing data
        self._load_data()

    def _load_data(self) -> None:
        """Load portfolio data from storage."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            # Load positions
            for pos_data in data.get('positions', []):
                # Convert date strings back to date objects
                if 'expiration_date' in pos_data:
                    pos_data['expiration_date'] = date.fromisoformat(pos_data['expiration_date'])
                if 'purchase_date' in pos_data:
                    pos_data['purchase_date'] = date.fromisoformat(pos_data['purchase_date'])
                # Convert Decimal strings
                for field in ['strike_price', 'premium_paid', 'current_stock_price',
                             'current_option_price', 'intrinsic_value', 'time_value']:
                    if field in pos_data and pos_data[field] is not None:
                        pos_data[field] = Decimal(str(pos_data[field]))

                self.positions.append(OptionPosition(**pos_data))

            # Load rules
            for rule_data in data.get('rules', []):
                self.rules_engine.add_rule(AlertRule(**rule_data))

            logger.info(f"Loaded {len(self.positions)} positions from storage")

        except Exception as e:
            logger.error(f"Error loading portfolio data: {e}")

    def _save_data(self) -> None:
        """Save portfolio data to storage."""
        try:
            data = {
                'positions': [],
                'rules': [],
                'last_updated': datetime.now().isoformat(),
            }

            for pos in self.positions:
                pos_dict = pos.model_dump()
                # Convert date objects to strings
                if pos_dict.get('expiration_date'):
                    pos_dict['expiration_date'] = pos_dict['expiration_date'].isoformat()
                if pos_dict.get('purchase_date'):
                    pos_dict['purchase_date'] = pos_dict['purchase_date'].isoformat()
                # Convert Decimals to strings
                for key, value in pos_dict.items():
                    if isinstance(value, Decimal):
                        pos_dict[key] = str(value)
                data['positions'].append(pos_dict)

            for rule in self.rules_engine.rules:
                rule_dict = rule.model_dump()
                # Convert datetime objects
                if rule_dict.get('created_at'):
                    rule_dict['created_at'] = rule_dict['created_at'].isoformat()
                if rule_dict.get('last_triggered'):
                    rule_dict['last_triggered'] = rule_dict['last_triggered'].isoformat()
                # Convert Decimals
                for key, value in rule_dict.items():
                    if isinstance(value, Decimal):
                        rule_dict[key] = str(value)
                data['rules'].append(rule_dict)

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.debug("Portfolio data saved")

        except Exception as e:
            logger.error(f"Error saving portfolio data: {e}")

    def add_position(self, position: OptionPosition) -> str:
        """
        Add a new position to the portfolio.

        Args:
            position: The position to add

        Returns:
            Position ID
        """
        if position.id is None:
            position.id = str(uuid.uuid4())

        self.positions.append(position)
        self._save_data()

        logger.info(
            f"Added position: {position.symbol} "
            f"{position.option_type.value} ${position.strike_price}"
        )

        return position.id

    def remove_position(self, position_id: str) -> bool:
        """
        Remove a position by ID.

        Args:
            position_id: ID of position to remove

        Returns:
            True if removed, False if not found
        """
        for i, pos in enumerate(self.positions):
            if pos.id == position_id:
                del self.positions[i]
                self._save_data()
                logger.info(f"Removed position: {position_id}")
                return True
        return False

    def get_position(self, position_id: str) -> Optional[OptionPosition]:
        """Get a position by ID."""
        for pos in self.positions:
            if pos.id == position_id:
                return pos
        return None

    def update_position(self, position: OptionPosition) -> bool:
        """
        Update an existing position.

        Args:
            position: Updated position (must have ID)

        Returns:
            True if updated, False if not found
        """
        if position.id is None:
            return False

        for i, pos in enumerate(self.positions):
            if pos.id == position.id:
                self.positions[i] = position
                self._save_data()
                return True
        return False

    def refresh_prices(self) -> list[OptionPosition]:
        """
        Refresh all positions with current market data.

        Returns:
            List of updated positions
        """
        logger.info("Refreshing portfolio prices...")
        self.positions = self.analyzer.analyze_positions(
            self.positions,
            fetch_option_prices=True
        )
        self._save_data()
        return self.positions

    def get_summary(self) -> PortfolioSummary:
        """
        Get portfolio summary statistics.

        Returns:
            PortfolioSummary with aggregated metrics
        """
        summary = PortfolioSummary()

        if not self.positions:
            return summary

        summary.total_positions = len(self.positions)
        summary.total_contracts = sum(abs(p.quantity) for p in self.positions)

        # Count by status
        for pos in self.positions:
            if pos.money_status == MoneyStatus.ITM:
                summary.itm_count += 1
            elif pos.money_status == MoneyStatus.ATM:
                summary.atm_count += 1
            elif pos.money_status == MoneyStatus.OTM:
                summary.otm_count += 1

        # Count by type
        summary.calls_count = len([p for p in self.positions if p.option_type == OptionType.CALL])
        summary.puts_count = len([p for p in self.positions if p.option_type == OptionType.PUT])
        summary.long_count = len([p for p in self.positions if p.is_long])
        summary.short_count = len([p for p in self.positions if p.is_short])

        # Financial metrics
        summary.total_cost_basis = sum(p.total_cost for p in self.positions)

        current_values = [
            (p.current_option_price or Decimal(0)) * abs(p.quantity) * 100
            for p in self.positions
            if p.current_option_price is not None
        ]
        if current_values:
            summary.total_current_value = sum(current_values)

        pnls = [p.calculate_profit_loss() for p in self.positions]
        pnls = [pnl for pnl in pnls if pnl is not None]
        if pnls:
            summary.total_profit_loss = sum(pnls)
            if summary.total_cost_basis > 0:
                summary.total_profit_loss_pct = float(
                    summary.total_profit_loss / summary.total_cost_basis * 100
                )

        # Intrinsic value
        summary.total_intrinsic_value = sum(
            (p.intrinsic_value or Decimal(0)) * abs(p.quantity) * 100
            for p in self.positions
        )

        # Expiration analysis
        today = date.today()
        week_end = today + timedelta(days=7)
        month_end = today + timedelta(days=30)

        summary.expiring_this_week = len([
            p for p in self.positions
            if today <= p.expiration_date <= week_end
        ])
        summary.expiring_this_month = len([
            p for p in self.positions
            if today <= p.expiration_date <= month_end
        ])

        # Alert counts
        summary.active_alerts = len(self.alerts)
        summary.unacknowledged_alerts = len([a for a in self.alerts if not a.acknowledged])

        summary.last_updated = datetime.now()

        return summary

    def get_itm_positions(self) -> list[OptionPosition]:
        """Get all In The Money positions."""
        return self.analyzer.get_itm_positions(self.positions)

    def get_otm_positions(self) -> list[OptionPosition]:
        """Get all Out of The Money positions."""
        return self.analyzer.get_otm_positions(self.positions)

    def get_expiring_soon(self, days: int = 7) -> list[OptionPosition]:
        """Get positions expiring within specified days."""
        return self.analyzer.get_expiring_soon(self.positions, days)

    def check_alerts(self) -> list[Alert]:
        """
        Check all rules and generate alerts.

        Returns:
            List of new alerts generated
        """
        new_alerts = self.rules_engine.evaluate_positions(self.positions)
        self.alerts.extend(new_alerts)
        return new_alerts

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now()
                return True
        return False

    def clear_alerts(self, acknowledged_only: bool = True) -> int:
        """
        Clear alerts.

        Args:
            acknowledged_only: If True, only clear acknowledged alerts

        Returns:
            Number of alerts cleared
        """
        if acknowledged_only:
            original_count = len(self.alerts)
            self.alerts = [a for a in self.alerts if not a.acknowledged]
            return original_count - len(self.alerts)
        else:
            count = len(self.alerts)
            self.alerts = []
            return count

    def generate_insights(self) -> list[ActionInsight]:
        """
        Generate actionable insights for the portfolio.

        Returns:
            List of insights and recommendations
        """
        self.insights = []

        # ITM positions that may need action
        self._generate_itm_insights()

        # Expiration warnings
        self._generate_expiration_insights()

        # Profit/loss insights
        self._generate_pnl_insights()

        # Portfolio optimization
        self._generate_optimization_insights()

        return self.insights

    def _generate_itm_insights(self) -> None:
        """Generate insights for ITM positions."""
        itm_positions = self.get_itm_positions()

        for pos in itm_positions:
            intrinsic = pos.intrinsic_value or Decimal(0)
            days_left = (pos.expiration_date - date.today()).days

            if days_left <= 7 and intrinsic > 0:
                # ITM and expiring soon - high priority
                insight = ActionInsight(
                    id=str(uuid.uuid4()),
                    insight_type="itm_expiring",
                    title=f"{pos.symbol} ITM - Action Required",
                    description=(
                        f"Your {pos.option_type.value.upper()} option on {pos.symbol} "
                        f"at ${pos.strike_price} strike is IN THE MONEY with "
                        f"${intrinsic:.2f}/share intrinsic value. "
                        f"It expires in {days_left} days."
                    ),
                    recommendation=(
                        f"Consider: (1) Exercise the option to capture intrinsic value, "
                        f"(2) Sell to close and collect premium + intrinsic value, or "
                        f"(3) Roll to a later expiration to maintain the position."
                    ),
                    affected_positions=[pos.id],
                    symbols=[pos.symbol],
                    priority=5 if days_left <= 3 else 4,
                    urgency="critical" if days_left <= 1 else "high",
                    potential_profit=intrinsic * abs(pos.quantity) * 100,
                )
                self.insights.append(insight)

            elif intrinsic > pos.premium_paid:
                # Significant profit potential
                profit = (intrinsic - pos.premium_paid) * abs(pos.quantity) * 100
                insight = ActionInsight(
                    id=str(uuid.uuid4()),
                    insight_type="itm_profitable",
                    title=f"{pos.symbol} - Take Profit Opportunity",
                    description=(
                        f"Your {pos.option_type.value.upper()} on {pos.symbol} "
                        f"has ${intrinsic:.2f} intrinsic value vs "
                        f"${pos.premium_paid:.2f} premium paid."
                    ),
                    recommendation=(
                        f"You could lock in approximately ${profit:.2f} profit by closing this position. "
                        f"Consider your outlook on {pos.symbol} before deciding."
                    ),
                    affected_positions=[pos.id],
                    symbols=[pos.symbol],
                    priority=3,
                    urgency="medium",
                    potential_profit=profit,
                )
                self.insights.append(insight)

    def _generate_expiration_insights(self) -> None:
        """Generate insights for expiring positions."""
        today = date.today()

        for pos in self.positions:
            days_left = (pos.expiration_date - today).days

            if days_left < 0:
                # Already expired
                insight = ActionInsight(
                    id=str(uuid.uuid4()),
                    insight_type="expired",
                    title=f"{pos.symbol} - Expired Position",
                    description=(
                        f"Your {pos.option_type.value.upper()} on {pos.symbol} "
                        f"expired on {pos.expiration_date}."
                    ),
                    recommendation=(
                        "Remove this position from your tracking. "
                        "Check your brokerage for final settlement details."
                    ),
                    affected_positions=[pos.id],
                    symbols=[pos.symbol],
                    priority=2,
                    urgency="low",
                )
                self.insights.append(insight)

            elif days_left <= 1 and pos.money_status == MoneyStatus.OTM:
                # OTM and expiring tomorrow - likely to expire worthless
                insight = ActionInsight(
                    id=str(uuid.uuid4()),
                    insight_type="otm_expiring",
                    title=f"{pos.symbol} - Expiring Worthless",
                    description=(
                        f"Your {pos.option_type.value.upper()} on {pos.symbol} "
                        f"at ${pos.strike_price} is OTM and expires in {days_left} day(s). "
                        f"It will likely expire worthless."
                    ),
                    recommendation=(
                        "If there's any remaining premium, consider selling to close. "
                        "Otherwise, let it expire and record the loss for tax purposes."
                    ),
                    affected_positions=[pos.id],
                    symbols=[pos.symbol],
                    priority=3,
                    urgency="medium",
                    potential_loss=pos.total_cost,
                )
                self.insights.append(insight)

    def _generate_pnl_insights(self) -> None:
        """Generate profit/loss insights."""
        for pos in self.positions:
            pnl_pct = pos.calculate_profit_loss_pct()
            pnl = pos.calculate_profit_loss()

            if pnl_pct is None or pnl is None:
                continue

            if pnl_pct >= 100:
                # Doubled or more
                insight = ActionInsight(
                    id=str(uuid.uuid4()),
                    insight_type="large_gain",
                    title=f"{pos.symbol} - 100%+ Gain",
                    description=(
                        f"Your {pos.option_type.value.upper()} on {pos.symbol} "
                        f"is up {pnl_pct:.1f}% (${pnl:.2f}). "
                        f"This is more than 100% return on your investment!"
                    ),
                    recommendation=(
                        "Consider taking profits or selling a portion to lock in gains. "
                        "You could also sell enough to cover your original cost basis "
                        "and let the rest ride risk-free."
                    ),
                    affected_positions=[pos.id],
                    symbols=[pos.symbol],
                    priority=4,
                    urgency="medium",
                    potential_profit=pnl,
                )
                self.insights.append(insight)

            elif pnl_pct <= -50:
                # Significant loss
                insight = ActionInsight(
                    id=str(uuid.uuid4()),
                    insight_type="large_loss",
                    title=f"{pos.symbol} - Significant Loss",
                    description=(
                        f"Your {pos.option_type.value.upper()} on {pos.symbol} "
                        f"is down {abs(pnl_pct):.1f}% (${abs(pnl):.2f})."
                    ),
                    recommendation=(
                        "Consider: (1) Close to limit further losses, "
                        "(2) Roll to a different strike/expiration, or "
                        "(3) Hold if you believe the stock will move in your favor. "
                        "Be cautious of holding losing options to expiration."
                    ),
                    affected_positions=[pos.id],
                    symbols=[pos.symbol],
                    priority=4,
                    urgency="high",
                    potential_loss=abs(pnl),
                    risk_level="high",
                )
                self.insights.append(insight)

    def _generate_optimization_insights(self) -> None:
        """Generate portfolio optimization insights."""
        if len(self.positions) < 2:
            return

        summary = self.get_summary()

        # Check for concentration
        symbols = [p.symbol for p in self.positions]
        symbol_counts = {}
        for sym in symbols:
            symbol_counts[sym] = symbol_counts.get(sym, 0) + 1

        for sym, count in symbol_counts.items():
            if count >= 3:
                insight = ActionInsight(
                    id=str(uuid.uuid4()),
                    insight_type="concentration",
                    title=f"High Concentration in {sym}",
                    description=(
                        f"You have {count} positions in {sym}, "
                        f"representing significant concentration risk."
                    ),
                    recommendation=(
                        f"Consider diversifying by reducing exposure to {sym} "
                        "and spreading across other opportunities."
                    ),
                    symbols=[sym],
                    priority=2,
                    urgency="low",
                    risk_level="medium",
                )
                self.insights.append(insight)

        # Check long/short balance
        if summary.long_count > 0 and summary.short_count == 0:
            insight = ActionInsight(
                id=str(uuid.uuid4()),
                insight_type="directional_bias",
                title="All Long Positions",
                description=(
                    "Your portfolio consists entirely of long options. "
                    "This means you're paying time decay on all positions."
                ),
                recommendation=(
                    "Consider selling some covered calls or cash-secured puts "
                    "to collect premium and offset time decay on long positions."
                ),
                priority=2,
                urgency="low",
            )
            self.insights.append(insight)

        # Check call/put balance
        if summary.calls_count > 0 and summary.puts_count == 0:
            insight = ActionInsight(
                id=str(uuid.uuid4()),
                insight_type="directional_bias",
                title="Only Call Options",
                description=(
                    "Your portfolio only has call options, "
                    "meaning you're entirely bullish."
                ),
                recommendation=(
                    "Consider adding put options for downside protection "
                    "or to profit from potential pullbacks."
                ),
                priority=2,
                urgency="low",
            )
            self.insights.append(insight)

    def setup_default_rules(self) -> list[str]:
        """Set up default monitoring rules."""
        return self.rules_engine.create_default_rules()

    def get_positions_by_symbol(self, symbol: str) -> list[OptionPosition]:
        """Get all positions for a specific symbol."""
        symbol = symbol.upper()
        return [p for p in self.positions if p.symbol == symbol]

    def get_positions_by_type(self, option_type: OptionType) -> list[OptionPosition]:
        """Get all positions of a specific type."""
        return [p for p in self.positions if p.option_type == option_type]

    def import_positions(self, positions_data: list[dict]) -> int:
        """
        Import positions from a list of dicts.

        Args:
            positions_data: List of position data dicts

        Returns:
            Number of positions imported
        """
        count = 0
        for data in positions_data:
            try:
                position = OptionPosition(**data)
                self.add_position(position)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to import position: {e}")

        return count

    def export_positions(self) -> list[dict]:
        """
        Export all positions as a list of dicts.

        Returns:
            List of position data dicts
        """
        return [p.model_dump() for p in self.positions]
