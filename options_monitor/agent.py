"""
AI Agent for intelligent options monitoring and insights.

Uses LLM to provide personalized recommendations and natural language insights.
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from .models import (
    OptionPosition,
    OptionType,
    MoneyStatus,
    PortfolioSummary,
    ActionInsight,
    Alert,
)
from .portfolio import PortfolioManager

logger = logging.getLogger(__name__)


# Try to import OpenAI, but make it optional
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class OptionsAgent:
    """
    AI-powered agent for options portfolio monitoring.

    Provides:
    - Natural language portfolio summaries
    - Intelligent action recommendations
    - Market context awareness
    - Personalized insights based on user preferences
    """

    def __init__(
        self,
        portfolio_manager: PortfolioManager,
        openai_api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
    ):
        """
        Initialize the options agent.

        Args:
            portfolio_manager: Portfolio manager instance
            openai_api_key: OpenAI API key (optional, uses env var if not provided)
            model: LLM model to use
        """
        self.portfolio = portfolio_manager
        self.model = model
        self.client = None

        if OPENAI_AVAILABLE and openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        elif OPENAI_AVAILABLE:
            try:
                self.client = OpenAI()  # Uses OPENAI_API_KEY env var
            except Exception:
                logger.warning("OpenAI client not configured - AI features disabled")

    def _build_portfolio_context(self) -> str:
        """Build context string describing the current portfolio state."""
        summary = self.portfolio.get_summary()
        positions = self.portfolio.positions

        if not positions:
            return "The portfolio is empty. No options positions to analyze."

        # Build position details
        position_details = []
        for pos in positions:
            status = pos.money_status.value.upper() if pos.money_status else "UNKNOWN"
            pnl = pos.calculate_profit_loss()
            pnl_pct = pos.calculate_profit_loss_pct()
            days_left = (pos.expiration_date - date.today()).days

            detail = (
                f"- {pos.symbol} {pos.option_type.value.upper()} ${pos.strike_price} "
                f"exp {pos.expiration_date} ({days_left} days): {status}"
            )

            if pos.current_stock_price:
                detail += f", stock @ ${pos.current_stock_price:.2f}"

            if pnl is not None:
                detail += f", P/L: ${pnl:.2f} ({pnl_pct:.1f}%)"

            position_details.append(detail)

        context = f"""
PORTFOLIO SUMMARY (as of {datetime.now().strftime('%Y-%m-%d %H:%M')}):
- Total Positions: {summary.total_positions}
- Total Contracts: {summary.total_contracts}
- Calls: {summary.calls_count}, Puts: {summary.puts_count}
- Long: {summary.long_count}, Short: {summary.short_count}
- ITM: {summary.itm_count}, ATM: {summary.atm_count}, OTM: {summary.otm_count}
- Cost Basis: ${summary.total_cost_basis:.2f}
- Current Value: ${summary.total_current_value:.2f if summary.total_current_value else 'N/A'}
- Total P/L: ${summary.total_profit_loss:.2f if summary.total_profit_loss else 'N/A'} ({summary.total_profit_loss_pct:.1f}% if summary.total_profit_loss_pct else 'N/A')
- Expiring This Week: {summary.expiring_this_week}
- Expiring This Month: {summary.expiring_this_month}

POSITIONS:
{chr(10).join(position_details)}
"""
        return context

    def get_daily_briefing(self) -> str:
        """
        Generate a daily briefing of the portfolio status.

        Returns:
            Natural language briefing
        """
        # Refresh prices first
        self.portfolio.refresh_prices()

        # Check for alerts
        alerts = self.portfolio.check_alerts()

        # Generate insights
        insights = self.portfolio.generate_insights()

        # Get ITM positions
        itm_positions = self.portfolio.get_itm_positions()

        # Get expiring soon
        expiring_soon = self.portfolio.get_expiring_soon(days=7)

        if not self.client:
            # Fallback to rule-based briefing
            return self._generate_rule_based_briefing(
                alerts, insights, itm_positions, expiring_soon
            )

        # Use LLM for natural language briefing
        context = self._build_portfolio_context()

        prompt = f"""You are an expert options trading assistant. Based on the portfolio data below,
provide a concise daily briefing (2-3 paragraphs) covering:

1. Overall portfolio health and key metrics
2. CRITICAL: Any options that are IN THE MONEY (ITM) that require attention
3. Upcoming expirations that need action
4. Top recommendations (max 3)

Be specific with ticker symbols, strikes, and dates. Focus on actionable insights.
Use a professional but friendly tone.

{context}

ALERTS TRIGGERED: {len(alerts)}
ITM POSITIONS: {len(itm_positions)}
EXPIRING WITHIN 7 DAYS: {len(expiring_soon)}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert options trading assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM briefing failed: {e}")
            return self._generate_rule_based_briefing(
                alerts, insights, itm_positions, expiring_soon
            )

    def _generate_rule_based_briefing(
        self,
        alerts: list[Alert],
        insights: list[ActionInsight],
        itm_positions: list[OptionPosition],
        expiring_soon: list[OptionPosition],
    ) -> str:
        """Generate briefing without LLM."""
        summary = self.portfolio.get_summary()
        lines = []

        lines.append(f"📊 **Portfolio Briefing** - {datetime.now().strftime('%B %d, %Y')}")
        lines.append("")

        # Summary stats
        lines.append(f"**Overview:** {summary.total_positions} positions, {summary.total_contracts} contracts")
        if summary.total_profit_loss is not None:
            emoji = "📈" if summary.total_profit_loss >= 0 else "📉"
            lines.append(f"{emoji} Total P/L: ${summary.total_profit_loss:.2f} ({summary.total_profit_loss_pct:.1f}%)")
        lines.append("")

        # ITM positions - CRITICAL
        if itm_positions:
            lines.append("🎯 **IN THE MONEY - Action Required:**")
            for pos in itm_positions:
                intrinsic = pos.intrinsic_value or Decimal(0)
                days = (pos.expiration_date - date.today()).days
                lines.append(
                    f"  • {pos.symbol} {pos.option_type.value.upper()} ${pos.strike_price} "
                    f"(exp {days}d) - Intrinsic: ${intrinsic:.2f}/share"
                )
            lines.append("")

        # Expiring soon
        if expiring_soon:
            lines.append("⏰ **Expiring Within 7 Days:**")
            for pos in expiring_soon:
                days = (pos.expiration_date - date.today()).days
                status = pos.money_status.value.upper() if pos.money_status else "?"
                lines.append(
                    f"  • {pos.symbol} {pos.option_type.value.upper()} ${pos.strike_price} "
                    f"- {days} days ({status})"
                )
            lines.append("")

        # Top insights
        if insights:
            high_priority = [i for i in insights if i.priority >= 4][:3]
            if high_priority:
                lines.append("💡 **Top Recommendations:**")
                for insight in high_priority:
                    lines.append(f"  • {insight.title}: {insight.recommendation[:100]}...")
                lines.append("")

        # Alerts
        if alerts:
            lines.append(f"🔔 **{len(alerts)} New Alerts**")
            for alert in alerts[:5]:
                lines.append(f"  • {alert.message}")

        return "\n".join(lines)

    def ask(self, question: str) -> str:
        """
        Ask the agent a question about the portfolio.

        Args:
            question: Natural language question

        Returns:
            Agent's response
        """
        if not self.client:
            return (
                "AI features are not available. Please configure your OpenAI API key. "
                "You can still use the portfolio manager directly for insights."
            )

        context = self._build_portfolio_context()

        prompt = f"""You are an expert options trading assistant. Answer the user's question
based on their portfolio data below. Be specific with ticker symbols, strikes, and dates.
If the question is about something not in the portfolio data, say so.

{context}

USER QUESTION: {question}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert options trading assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return f"Sorry, I couldn't process your question. Error: {e}"

    def get_itm_summary(self) -> str:
        """
        Get a focused summary of all ITM positions.

        Returns:
            Summary of ITM positions with recommendations
        """
        self.portfolio.refresh_prices()
        itm_positions = self.portfolio.get_itm_positions()

        if not itm_positions:
            return "✅ No options are currently In The Money (ITM)."

        lines = ["🎯 **IN THE MONEY POSITIONS**", ""]

        for pos in itm_positions:
            intrinsic = pos.intrinsic_value or Decimal(0)
            days = (pos.expiration_date - date.today()).days
            total_intrinsic = intrinsic * abs(pos.quantity) * 100

            lines.append(f"**{pos.symbol} {pos.option_type.value.upper()} ${pos.strike_price}**")
            lines.append(f"  Stock Price: ${pos.current_stock_price:.2f}")
            lines.append(f"  Intrinsic Value: ${intrinsic:.2f}/share (${total_intrinsic:.2f} total)")
            lines.append(f"  Days to Expiration: {days}")

            # Recommendation based on situation
            if days <= 1:
                lines.append("  ⚠️ **URGENT**: Expires tomorrow! Exercise or sell immediately.")
            elif days <= 7:
                lines.append("  📌 **ACTION**: Consider taking profits or rolling the position.")
            else:
                lines.append("  💡 **TIP**: Monitor closely. Consider profit targets.")

            lines.append("")

        return "\n".join(lines)

    def get_action_items(self) -> list[dict]:
        """
        Get a prioritized list of action items.

        Returns:
            List of action items with priority and details
        """
        self.portfolio.refresh_prices()

        actions = []
        today = date.today()

        for pos in self.portfolio.positions:
            days = (pos.expiration_date - today).days

            # Expired
            if days < 0:
                actions.append({
                    "priority": 1,
                    "urgency": "critical",
                    "position": f"{pos.symbol} {pos.option_type.value.upper()} ${pos.strike_price}",
                    "action": "REMOVE - Position has expired",
                    "reason": f"Expired on {pos.expiration_date}",
                })

            # ITM expiring tomorrow
            elif days <= 1 and pos.money_status == MoneyStatus.ITM:
                actions.append({
                    "priority": 1,
                    "urgency": "critical",
                    "position": f"{pos.symbol} {pos.option_type.value.upper()} ${pos.strike_price}",
                    "action": "EXERCISE or SELL - ITM expiring tomorrow",
                    "reason": f"Intrinsic value: ${pos.intrinsic_value:.2f}/share",
                })

            # ITM expiring this week
            elif days <= 7 and pos.money_status == MoneyStatus.ITM:
                actions.append({
                    "priority": 2,
                    "urgency": "high",
                    "position": f"{pos.symbol} {pos.option_type.value.upper()} ${pos.strike_price}",
                    "action": "REVIEW - ITM expiring soon",
                    "reason": f"{days} days left, intrinsic: ${pos.intrinsic_value:.2f}/share",
                })

            # OTM expiring this week
            elif days <= 7 and pos.money_status == MoneyStatus.OTM:
                actions.append({
                    "priority": 3,
                    "urgency": "medium",
                    "position": f"{pos.symbol} {pos.option_type.value.upper()} ${pos.strike_price}",
                    "action": "CONSIDER CLOSING - OTM expiring soon",
                    "reason": f"{days} days left, likely to expire worthless",
                })

            # Large profit
            pnl_pct = pos.calculate_profit_loss_pct()
            if pnl_pct and pnl_pct >= 100:
                actions.append({
                    "priority": 3,
                    "urgency": "medium",
                    "position": f"{pos.symbol} {pos.option_type.value.upper()} ${pos.strike_price}",
                    "action": "TAKE PROFIT - 100%+ gain",
                    "reason": f"Currently up {pnl_pct:.1f}%",
                })

            # Large loss
            elif pnl_pct and pnl_pct <= -50:
                actions.append({
                    "priority": 4,
                    "urgency": "low",
                    "position": f"{pos.symbol} {pos.option_type.value.upper()} ${pos.strike_price}",
                    "action": "EVALUATE - Significant loss",
                    "reason": f"Currently down {abs(pnl_pct):.1f}%",
                })

        # Sort by priority
        actions.sort(key=lambda x: x["priority"])

        return actions
