"""
Rules engine for monitoring options and generating alerts.
"""

import logging
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Callable, Optional

from .models import (
    OptionPosition,
    OptionType,
    MoneyStatus,
    AlertRule,
    RuleType,
    Alert,
)

logger = logging.getLogger(__name__)


class RulesEngine:
    """
    Evaluates monitoring rules against options positions and generates alerts.

    Supports rules for:
    - ITM/OTM status changes
    - Expiration warnings
    - Profit/loss thresholds
    - Price thresholds
    - Custom rules
    """

    def __init__(self):
        """Initialize the rules engine."""
        self.rules: list[AlertRule] = []
        self._rule_evaluators: dict[RuleType, Callable] = {
            RuleType.ITM_ALERT: self._evaluate_itm_rule,
            RuleType.OTM_ALERT: self._evaluate_otm_rule,
            RuleType.EXPIRATION_WARNING: self._evaluate_expiration_rule,
            RuleType.PROFIT_TARGET: self._evaluate_profit_target_rule,
            RuleType.STOP_LOSS: self._evaluate_stop_loss_rule,
            RuleType.PRICE_THRESHOLD: self._evaluate_price_threshold_rule,
            RuleType.INTRINSIC_VALUE: self._evaluate_intrinsic_value_rule,
        }

    def add_rule(self, rule: AlertRule) -> str:
        """
        Add a monitoring rule.

        Args:
            rule: The rule to add

        Returns:
            Rule ID
        """
        if rule.id is None:
            rule.id = str(uuid.uuid4())
        self.rules.append(rule)
        logger.info(f"Added rule: {rule.name} ({rule.rule_type})")
        return rule.id

    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove a rule by ID.

        Args:
            rule_id: ID of rule to remove

        Returns:
            True if removed, False if not found
        """
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                del self.rules[i]
                logger.info(f"Removed rule: {rule_id}")
                return True
        return False

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get a rule by ID."""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule."""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule."""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = False
            return True
        return False

    def evaluate_position(self, position: OptionPosition) -> list[Alert]:
        """
        Evaluate all rules against a single position.

        Args:
            position: The position to evaluate

        Returns:
            List of alerts generated
        """
        alerts = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            # Check if rule applies to this position
            if not self._rule_applies_to_position(rule, position):
                continue

            # Evaluate the rule
            evaluator = self._rule_evaluators.get(rule.rule_type)
            if evaluator:
                alert = evaluator(rule, position)
                if alert:
                    alerts.append(alert)

        return alerts

    def evaluate_positions(self, positions: list[OptionPosition]) -> list[Alert]:
        """
        Evaluate all rules against multiple positions.

        Args:
            positions: List of positions to evaluate

        Returns:
            List of all alerts generated
        """
        all_alerts = []
        for position in positions:
            alerts = self.evaluate_position(position)
            all_alerts.extend(alerts)
        return all_alerts

    def _rule_applies_to_position(self, rule: AlertRule, position: OptionPosition) -> bool:
        """Check if a rule should be applied to a position."""
        # Check symbol filter
        if rule.apply_to_symbols:
            if position.symbol not in rule.apply_to_symbols:
                return False

        # Check option type filter
        if rule.apply_to_option_type:
            if position.option_type != rule.apply_to_option_type:
                return False

        return True

    def _create_alert(
        self,
        rule: AlertRule,
        position: OptionPosition,
        message: str,
        current_value: Optional[Decimal] = None,
        threshold_value: Optional[Decimal] = None
    ) -> Alert:
        """Create an alert from a triggered rule."""
        rule.last_triggered = datetime.now()

        return Alert(
            id=str(uuid.uuid4()),
            rule_id=rule.id,
            rule_name=rule.name,
            position_id=position.id or "",
            symbol=position.symbol,
            alert_type=rule.rule_type,
            message=rule.notification_message or message,
            priority=rule.priority,
            current_value=current_value,
            threshold_value=threshold_value,
        )

    def _evaluate_itm_rule(
        self,
        rule: AlertRule,
        position: OptionPosition
    ) -> Optional[Alert]:
        """Evaluate ITM alert rule."""
        if position.money_status != MoneyStatus.ITM:
            return None

        intrinsic = position.intrinsic_value or Decimal(0)

        message = (
            f"🎯 {position.symbol} {position.option_type.value.upper()} "
            f"${position.strike_price} is IN THE MONEY! "
            f"Stock: ${position.current_stock_price:.2f}, "
            f"Intrinsic value: ${intrinsic:.2f}/share"
        )

        return self._create_alert(
            rule=rule,
            position=position,
            message=message,
            current_value=position.current_stock_price,
            threshold_value=position.strike_price
        )

    def _evaluate_otm_rule(
        self,
        rule: AlertRule,
        position: OptionPosition
    ) -> Optional[Alert]:
        """Evaluate OTM alert rule."""
        if position.money_status != MoneyStatus.OTM:
            return None

        message = (
            f"⚠️ {position.symbol} {position.option_type.value.upper()} "
            f"${position.strike_price} is OUT OF THE MONEY. "
            f"Stock: ${position.current_stock_price:.2f}"
        )

        return self._create_alert(
            rule=rule,
            position=position,
            message=message,
            current_value=position.current_stock_price,
            threshold_value=position.strike_price
        )

    def _evaluate_expiration_rule(
        self,
        rule: AlertRule,
        position: OptionPosition
    ) -> Optional[Alert]:
        """Evaluate expiration warning rule."""
        if rule.threshold_days is None:
            return None

        days_left = (position.expiration_date - date.today()).days

        if days_left > rule.threshold_days or days_left < 0:
            return None

        urgency = "🚨" if days_left <= 3 else "⏰"

        message = (
            f"{urgency} {position.symbol} {position.option_type.value.upper()} "
            f"${position.strike_price} expires in {days_left} days! "
            f"Expiration: {position.expiration_date}"
        )

        return self._create_alert(
            rule=rule,
            position=position,
            message=message,
            current_value=Decimal(days_left),
            threshold_value=Decimal(rule.threshold_days)
        )

    def _evaluate_profit_target_rule(
        self,
        rule: AlertRule,
        position: OptionPosition
    ) -> Optional[Alert]:
        """Evaluate profit target rule."""
        if rule.threshold_pct is None:
            return None

        pnl_pct = position.calculate_profit_loss_pct()
        if pnl_pct is None:
            return None

        if pnl_pct < rule.threshold_pct:
            return None

        pnl = position.calculate_profit_loss() or Decimal(0)

        message = (
            f"💰 PROFIT TARGET HIT! {position.symbol} {position.option_type.value.upper()} "
            f"${position.strike_price} is up {pnl_pct:.1f}% (${pnl:.2f})"
        )

        return self._create_alert(
            rule=rule,
            position=position,
            message=message,
            current_value=Decimal(str(pnl_pct)),
            threshold_value=Decimal(str(rule.threshold_pct))
        )

    def _evaluate_stop_loss_rule(
        self,
        rule: AlertRule,
        position: OptionPosition
    ) -> Optional[Alert]:
        """Evaluate stop loss rule."""
        if rule.threshold_pct is None:
            return None

        pnl_pct = position.calculate_profit_loss_pct()
        if pnl_pct is None:
            return None

        # Stop loss triggers when loss exceeds threshold (pnl_pct is negative)
        if pnl_pct > -rule.threshold_pct:
            return None

        pnl = position.calculate_profit_loss() or Decimal(0)

        message = (
            f"🛑 STOP LOSS! {position.symbol} {position.option_type.value.upper()} "
            f"${position.strike_price} is down {abs(pnl_pct):.1f}% (${pnl:.2f})"
        )

        return self._create_alert(
            rule=rule,
            position=position,
            message=message,
            current_value=Decimal(str(pnl_pct)),
            threshold_value=Decimal(str(-rule.threshold_pct))
        )

    def _evaluate_price_threshold_rule(
        self,
        rule: AlertRule,
        position: OptionPosition
    ) -> Optional[Alert]:
        """Evaluate stock price threshold rule."""
        if rule.threshold_value is None or position.current_stock_price is None:
            return None

        if position.current_stock_price < rule.threshold_value:
            return None

        message = (
            f"📈 {position.symbol} crossed ${rule.threshold_value}! "
            f"Current: ${position.current_stock_price:.2f}"
        )

        return self._create_alert(
            rule=rule,
            position=position,
            message=message,
            current_value=position.current_stock_price,
            threshold_value=rule.threshold_value
        )

    def _evaluate_intrinsic_value_rule(
        self,
        rule: AlertRule,
        position: OptionPosition
    ) -> Optional[Alert]:
        """Evaluate intrinsic value threshold rule."""
        if rule.threshold_value is None or position.intrinsic_value is None:
            return None

        if position.intrinsic_value < rule.threshold_value:
            return None

        message = (
            f"💎 {position.symbol} {position.option_type.value.upper()} "
            f"${position.strike_price} intrinsic value: ${position.intrinsic_value:.2f}/share "
            f"(threshold: ${rule.threshold_value})"
        )

        return self._create_alert(
            rule=rule,
            position=position,
            message=message,
            current_value=position.intrinsic_value,
            threshold_value=rule.threshold_value
        )

    def create_default_rules(self) -> list[str]:
        """
        Create a set of default monitoring rules.

        Returns:
            List of created rule IDs
        """
        default_rules = [
            AlertRule(
                name="ITM Alert",
                rule_type=RuleType.ITM_ALERT,
                priority=4,
                notification_message=None,  # Use dynamic message
            ),
            AlertRule(
                name="Expiration 7 Days",
                rule_type=RuleType.EXPIRATION_WARNING,
                threshold_days=7,
                priority=3,
            ),
            AlertRule(
                name="Expiration 3 Days",
                rule_type=RuleType.EXPIRATION_WARNING,
                threshold_days=3,
                priority=5,
            ),
            AlertRule(
                name="Expiration Tomorrow",
                rule_type=RuleType.EXPIRATION_WARNING,
                threshold_days=1,
                priority=5,
            ),
            AlertRule(
                name="Profit Target 50%",
                rule_type=RuleType.PROFIT_TARGET,
                threshold_pct=50.0,
                priority=3,
            ),
            AlertRule(
                name="Profit Target 100%",
                rule_type=RuleType.PROFIT_TARGET,
                threshold_pct=100.0,
                priority=4,
            ),
            AlertRule(
                name="Stop Loss 50%",
                rule_type=RuleType.STOP_LOSS,
                threshold_pct=50.0,
                priority=4,
            ),
        ]

        rule_ids = []
        for rule in default_rules:
            rule_id = self.add_rule(rule)
            rule_ids.append(rule_id)

        return rule_ids

    def get_active_rules(self) -> list[AlertRule]:
        """Get all enabled rules."""
        return [r for r in self.rules if r.enabled]

    def get_rules_by_type(self, rule_type: RuleType) -> list[AlertRule]:
        """Get all rules of a specific type."""
        return [r for r in self.rules if r.rule_type == rule_type]
