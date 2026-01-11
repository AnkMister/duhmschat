"""
Options Portfolio Monitor - Streamlit Dashboard

A comprehensive dashboard for monitoring options positions,
tracking ITM status, and receiving actionable insights.
"""

import os
import streamlit as st
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our options monitoring system
from options_monitor import (
    OptionPosition,
    OptionType,
    MoneyStatus,
    AlertRule,
    RuleType,
    PortfolioManager,
)
from options_monitor.agent import OptionsAgent

# Page configuration
st.set_page_config(
    page_title="Options Portfolio Monitor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .itm-card {
        background-color: #d4edda;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .otm-card {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .atm-card {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .alert-critical {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 10px;
        margin: 5px 0;
    }
    .alert-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 5px 0;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'portfolio_manager' not in st.session_state:
        storage_path = Path("portfolio_data.json")
        st.session_state.portfolio_manager = PortfolioManager(storage_path=storage_path)
        # Set up default rules on first load
        if not st.session_state.portfolio_manager.rules_engine.rules:
            st.session_state.portfolio_manager.setup_default_rules()

    if 'agent' not in st.session_state:
        api_key = os.getenv("OPENAI_API_KEY")
        st.session_state.agent = OptionsAgent(
            portfolio_manager=st.session_state.portfolio_manager,
            openai_api_key=api_key,
        )

    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None

    if 'alerts' not in st.session_state:
        st.session_state.alerts = []


def refresh_portfolio():
    """Refresh all portfolio prices and check alerts."""
    with st.spinner("Refreshing prices..."):
        st.session_state.portfolio_manager.refresh_prices()
        st.session_state.alerts = st.session_state.portfolio_manager.check_alerts()
        st.session_state.last_refresh = datetime.now()


def render_sidebar():
    """Render the sidebar navigation and controls."""
    st.sidebar.title("📈 Options Monitor")

    # Refresh button
    if st.sidebar.button("🔄 Refresh Prices", use_container_width=True):
        refresh_portfolio()
        st.rerun()

    if st.session_state.last_refresh:
        st.sidebar.caption(f"Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}")

    st.sidebar.divider()

    # Navigation
    page = st.sidebar.radio(
        "Navigate",
        ["Dashboard", "Positions", "Add Position", "Alerts & Rules", "AI Assistant"],
        label_visibility="collapsed",
    )

    st.sidebar.divider()

    # Quick stats
    pm = st.session_state.portfolio_manager
    summary = pm.get_summary()

    st.sidebar.metric("Total Positions", summary.total_positions)
    st.sidebar.metric("ITM Positions", summary.itm_count)
    st.sidebar.metric("Expiring This Week", summary.expiring_this_week)

    if summary.total_profit_loss is not None:
        pnl_delta = f"{summary.total_profit_loss_pct:.1f}%" if summary.total_profit_loss_pct else None
        st.sidebar.metric(
            "Total P/L",
            f"${summary.total_profit_loss:.2f}",
            delta=pnl_delta,
        )

    return page


def render_dashboard():
    """Render the main dashboard view."""
    st.title("📊 Portfolio Dashboard")

    pm = st.session_state.portfolio_manager
    agent = st.session_state.agent

    # Auto-refresh on first load
    if st.session_state.last_refresh is None and pm.positions:
        refresh_portfolio()

    # Top metrics row
    summary = pm.get_summary()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Positions", summary.total_positions)
    with col2:
        st.metric("🎯 ITM", summary.itm_count)
    with col3:
        st.metric("⚪ ATM", summary.atm_count)
    with col4:
        st.metric("⭕ OTM", summary.otm_count)
    with col5:
        if summary.total_profit_loss is not None:
            color = "green" if summary.total_profit_loss >= 0 else "red"
            st.metric(
                "Total P/L",
                f"${summary.total_profit_loss:.2f}",
                delta=f"{summary.total_profit_loss_pct:.1f}%",
            )
        else:
            st.metric("Total P/L", "N/A")

    st.divider()

    # Two-column layout
    left_col, right_col = st.columns([2, 1])

    with left_col:
        # ITM Positions - Most Important
        st.subheader("🎯 In The Money Positions")

        itm_positions = pm.get_itm_positions()

        if not itm_positions:
            st.info("No positions are currently ITM.")
        else:
            for pos in itm_positions:
                intrinsic = pos.intrinsic_value or Decimal(0)
                days = (pos.expiration_date - date.today()).days
                total_intrinsic = intrinsic * abs(pos.quantity) * 100

                with st.container():
                    st.markdown(f"""
                    <div class="itm-card">
                        <h4>{pos.symbol} {pos.option_type.value.upper()} ${pos.strike_price}</h4>
                        <p>
                            <strong>Stock:</strong> ${pos.current_stock_price:.2f} |
                            <strong>Intrinsic:</strong> ${intrinsic:.2f}/share (${total_intrinsic:.2f} total) |
                            <strong>Expires:</strong> {pos.expiration_date} ({days} days)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

        # Expiring Soon
        st.subheader("⏰ Expiring Within 7 Days")

        expiring = pm.get_expiring_soon(days=7)

        if not expiring:
            st.info("No positions expiring within 7 days.")
        else:
            for pos in expiring:
                days = (pos.expiration_date - date.today()).days
                status = pos.money_status.value.upper() if pos.money_status else "?"

                card_class = "itm-card" if pos.money_status == MoneyStatus.ITM else (
                    "atm-card" if pos.money_status == MoneyStatus.ATM else "otm-card"
                )

                urgency = "🚨" if days <= 1 else ("⚠️" if days <= 3 else "⏰")

                st.markdown(f"""
                <div class="{card_class}">
                    {urgency} <strong>{pos.symbol}</strong> {pos.option_type.value.upper()} ${pos.strike_price}
                    - Expires in <strong>{days} days</strong> ({status})
                </div>
                """, unsafe_allow_html=True)

    with right_col:
        # Action Items
        st.subheader("📋 Action Items")

        actions = agent.get_action_items()

        if not actions:
            st.success("No urgent actions required!")
        else:
            for action in actions[:5]:
                urgency_icon = {
                    "critical": "🚨",
                    "high": "⚠️",
                    "medium": "📌",
                    "low": "💡",
                }.get(action["urgency"], "📌")

                alert_class = "alert-critical" if action["urgency"] in ["critical", "high"] else "alert-warning"

                st.markdown(f"""
                <div class="{alert_class}">
                    {urgency_icon} <strong>{action['position']}</strong><br/>
                    {action['action']}<br/>
                    <small>{action['reason']}</small>
                </div>
                """, unsafe_allow_html=True)

        # Portfolio Breakdown
        st.subheader("📊 Breakdown")

        if summary.total_positions > 0:
            # Calls vs Puts
            st.write("**By Type:**")
            st.progress(summary.calls_count / summary.total_positions if summary.total_positions > 0 else 0)
            st.caption(f"Calls: {summary.calls_count} | Puts: {summary.puts_count}")

            # Long vs Short
            st.write("**By Direction:**")
            st.progress(summary.long_count / summary.total_positions if summary.total_positions > 0 else 0)
            st.caption(f"Long: {summary.long_count} | Short: {summary.short_count}")


def render_positions():
    """Render the positions list view."""
    st.title("📋 All Positions")

    pm = st.session_state.portfolio_manager

    if not pm.positions:
        st.info("No positions yet. Add your first position to get started!")
        return

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_status = st.selectbox("Status", ["All", "ITM", "ATM", "OTM"])
    with col2:
        filter_type = st.selectbox("Type", ["All", "CALL", "PUT"])
    with col3:
        filter_symbol = st.text_input("Symbol", placeholder="Filter by symbol...")

    # Apply filters
    positions = pm.positions

    if filter_status != "All":
        status_map = {"ITM": MoneyStatus.ITM, "ATM": MoneyStatus.ATM, "OTM": MoneyStatus.OTM}
        positions = [p for p in positions if p.money_status == status_map.get(filter_status)]

    if filter_type != "All":
        type_map = {"CALL": OptionType.CALL, "PUT": OptionType.PUT}
        positions = [p for p in positions if p.option_type == type_map.get(filter_type)]

    if filter_symbol:
        positions = [p for p in positions if filter_symbol.upper() in p.symbol]

    st.divider()

    # Display positions
    for pos in positions:
        status_emoji = {
            MoneyStatus.ITM: "🎯",
            MoneyStatus.ATM: "⚪",
            MoneyStatus.OTM: "⭕",
        }.get(pos.money_status, "❓")

        with st.expander(
            f"{status_emoji} {pos.symbol} {pos.option_type.value.upper()} ${pos.strike_price} | "
            f"Exp: {pos.expiration_date}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Symbol:** {pos.symbol}")
                st.write(f"**Type:** {pos.option_type.value.upper()}")
                st.write(f"**Strike:** ${pos.strike_price}")
                st.write(f"**Expiration:** {pos.expiration_date}")
                st.write(f"**Quantity:** {pos.quantity} contracts")
                st.write(f"**Premium Paid:** ${pos.premium_paid}/share")
                st.write(f"**Total Cost:** ${pos.total_cost:.2f}")

            with col2:
                st.write(f"**Status:** {pos.money_status.value.upper() if pos.money_status else 'Unknown'}")
                if pos.current_stock_price:
                    st.write(f"**Stock Price:** ${pos.current_stock_price:.2f}")
                if pos.intrinsic_value:
                    st.write(f"**Intrinsic Value:** ${pos.intrinsic_value:.2f}/share")
                if pos.current_option_price:
                    st.write(f"**Current Option Price:** ${pos.current_option_price:.2f}")

                pnl = pos.calculate_profit_loss()
                pnl_pct = pos.calculate_profit_loss_pct()
                if pnl is not None:
                    color = "green" if pnl >= 0 else "red"
                    st.markdown(f"**P/L:** <span style='color:{color}'>${pnl:.2f} ({pnl_pct:.1f}%)</span>",
                               unsafe_allow_html=True)

            # Delete button
            if st.button(f"🗑️ Remove", key=f"del_{pos.id}"):
                pm.remove_position(pos.id)
                st.success(f"Removed {pos.symbol} position")
                st.rerun()


def render_add_position():
    """Render the add position form."""
    st.title("➕ Add New Position")

    pm = st.session_state.portfolio_manager

    with st.form("add_position_form"):
        col1, col2 = st.columns(2)

        with col1:
            symbol = st.text_input("Stock Symbol", placeholder="AAPL").upper()
            option_type = st.selectbox("Option Type", ["CALL", "PUT"])
            strike_price = st.number_input("Strike Price", min_value=0.01, step=0.50, value=100.0)
            expiration_date = st.date_input("Expiration Date", min_value=date.today())

        with col2:
            quantity = st.number_input("Quantity (contracts)", min_value=-100, max_value=100, value=1,
                                       help="Positive for long, negative for short")
            premium_paid = st.number_input("Premium Paid (per share)", min_value=0.0, step=0.05, value=1.0)
            purchase_date = st.date_input("Purchase Date", value=date.today())

        submitted = st.form_submit_button("Add Position", use_container_width=True)

        if submitted:
            if not symbol:
                st.error("Please enter a stock symbol")
            elif quantity == 0:
                st.error("Quantity cannot be zero")
            else:
                position = OptionPosition(
                    symbol=symbol,
                    option_type=OptionType.CALL if option_type == "CALL" else OptionType.PUT,
                    strike_price=Decimal(str(strike_price)),
                    expiration_date=expiration_date,
                    quantity=quantity,
                    premium_paid=Decimal(str(premium_paid)),
                    purchase_date=purchase_date,
                )

                pm.add_position(position)
                st.success(f"Added {symbol} {option_type} ${strike_price} position!")

                # Refresh to get current prices
                refresh_portfolio()
                st.rerun()

    st.divider()

    # Bulk import
    st.subheader("📥 Bulk Import")

    st.write("Paste CSV data (symbol, type, strike, expiration, quantity, premium):")

    csv_data = st.text_area("CSV Data", height=150, placeholder="""AAPL,CALL,180,2024-12-20,5,3.50
MSFT,PUT,400,2024-12-27,2,5.25
TSLA,CALL,250,2025-01-17,3,8.00""")

    if st.button("Import Positions"):
        if csv_data.strip():
            lines = csv_data.strip().split("\n")
            imported = 0

            for line in lines:
                try:
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 6:
                        position = OptionPosition(
                            symbol=parts[0].upper(),
                            option_type=OptionType.CALL if parts[1].upper() == "CALL" else OptionType.PUT,
                            strike_price=Decimal(parts[2]),
                            expiration_date=date.fromisoformat(parts[3]),
                            quantity=int(parts[4]),
                            premium_paid=Decimal(parts[5]),
                        )
                        pm.add_position(position)
                        imported += 1
                except Exception as e:
                    st.warning(f"Failed to parse line: {line} - {e}")

            if imported > 0:
                st.success(f"Imported {imported} positions!")
                refresh_portfolio()
                st.rerun()


def render_alerts():
    """Render the alerts and rules management view."""
    st.title("🔔 Alerts & Rules")

    pm = st.session_state.portfolio_manager

    tab1, tab2 = st.tabs(["Active Alerts", "Monitoring Rules"])

    with tab1:
        st.subheader("Active Alerts")

        if not st.session_state.alerts:
            st.info("No active alerts. Your portfolio is looking good!")
        else:
            for alert in st.session_state.alerts:
                icon = "🚨" if alert.priority >= 4 else ("⚠️" if alert.priority >= 3 else "📌")

                with st.expander(f"{icon} {alert.rule_name} - {alert.symbol}"):
                    st.write(alert.message)
                    st.caption(f"Triggered: {alert.created_at.strftime('%Y-%m-%d %H:%M')}")

                    if not alert.acknowledged:
                        if st.button("Acknowledge", key=f"ack_{alert.id}"):
                            pm.acknowledge_alert(alert.id)
                            st.rerun()

            if st.button("Clear Acknowledged Alerts"):
                cleared = pm.clear_alerts(acknowledged_only=True)
                st.success(f"Cleared {cleared} alerts")
                st.rerun()

    with tab2:
        st.subheader("Monitoring Rules")

        rules = pm.rules_engine.rules

        if not rules:
            if st.button("Set Up Default Rules"):
                pm.setup_default_rules()
                st.success("Default rules created!")
                st.rerun()
        else:
            for rule in rules:
                status = "✅" if rule.enabled else "❌"

                with st.expander(f"{status} {rule.name} ({rule.rule_type.value})"):
                    st.write(f"**Type:** {rule.rule_type.value}")
                    st.write(f"**Priority:** {rule.priority}/5")

                    if rule.threshold_days:
                        st.write(f"**Days Threshold:** {rule.threshold_days}")
                    if rule.threshold_pct:
                        st.write(f"**Percentage Threshold:** {rule.threshold_pct}%")
                    if rule.threshold_value:
                        st.write(f"**Value Threshold:** ${rule.threshold_value}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if rule.enabled:
                            if st.button("Disable", key=f"dis_{rule.id}"):
                                pm.rules_engine.disable_rule(rule.id)
                                st.rerun()
                        else:
                            if st.button("Enable", key=f"en_{rule.id}"):
                                pm.rules_engine.enable_rule(rule.id)
                                st.rerun()

                    with col2:
                        if st.button("Remove", key=f"rem_{rule.id}"):
                            pm.rules_engine.remove_rule(rule.id)
                            st.rerun()

        st.divider()

        # Add new rule
        st.subheader("Add New Rule")

        with st.form("add_rule_form"):
            rule_name = st.text_input("Rule Name")
            rule_type = st.selectbox("Rule Type", [
                ("ITM Alert", RuleType.ITM_ALERT),
                ("OTM Alert", RuleType.OTM_ALERT),
                ("Expiration Warning", RuleType.EXPIRATION_WARNING),
                ("Profit Target", RuleType.PROFIT_TARGET),
                ("Stop Loss", RuleType.STOP_LOSS),
                ("Price Threshold", RuleType.PRICE_THRESHOLD),
            ], format_func=lambda x: x[0])

            priority = st.slider("Priority", 1, 5, 3)

            col1, col2 = st.columns(2)
            with col1:
                threshold_days = st.number_input("Days Threshold (for expiration)", min_value=0, value=7)
            with col2:
                threshold_pct = st.number_input("Percentage Threshold", min_value=0.0, value=50.0)

            submitted = st.form_submit_button("Add Rule")

            if submitted and rule_name:
                new_rule = AlertRule(
                    name=rule_name,
                    rule_type=rule_type[1],
                    priority=priority,
                    threshold_days=threshold_days if threshold_days > 0 else None,
                    threshold_pct=threshold_pct if threshold_pct > 0 else None,
                )
                pm.rules_engine.add_rule(new_rule)
                st.success(f"Added rule: {rule_name}")
                st.rerun()


def render_ai_assistant():
    """Render the AI assistant chat interface."""
    st.title("🤖 AI Assistant")

    agent = st.session_state.agent

    # Daily briefing
    st.subheader("📋 Daily Briefing")

    if st.button("Generate Daily Briefing", use_container_width=True):
        with st.spinner("Generating briefing..."):
            briefing = agent.get_daily_briefing()
            st.markdown(briefing)

    st.divider()

    # ITM Summary
    st.subheader("🎯 ITM Summary")

    if st.button("Show ITM Summary", use_container_width=True):
        with st.spinner("Analyzing ITM positions..."):
            summary = agent.get_itm_summary()
            st.markdown(summary)

    st.divider()

    # Ask a question
    st.subheader("💬 Ask About Your Portfolio")

    question = st.text_input("Ask a question...", placeholder="Which positions should I close?")

    if st.button("Ask", use_container_width=True) and question:
        with st.spinner("Thinking..."):
            response = agent.ask(question)
            st.markdown(response)

    # Sample questions
    st.caption("Sample questions:")
    sample_questions = [
        "Which of my positions are most profitable?",
        "What should I do about my expiring options?",
        "How can I hedge my portfolio?",
        "What's my risk exposure to AAPL?",
    ]

    for q in sample_questions:
        if st.button(q, key=f"sample_{q[:20]}"):
            with st.spinner("Thinking..."):
                response = agent.ask(q)
                st.markdown(response)


def main():
    """Main application entry point."""
    init_session_state()

    page = render_sidebar()

    if page == "Dashboard":
        render_dashboard()
    elif page == "Positions":
        render_positions()
    elif page == "Add Position":
        render_add_position()
    elif page == "Alerts & Rules":
        render_alerts()
    elif page == "AI Assistant":
        render_ai_assistant()


if __name__ == "__main__":
    main()
