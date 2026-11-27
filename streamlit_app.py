import streamlit as st
from datetime import date

st.set_page_config(page_title="Pocket Tracker", page_icon="💳", layout="wide")

# Theme: navy, emerald and light background
st.markdown("""
<style>
.stApp { background: #F8FAFC; color: #0F172A; }
.block-container { padding-top: 2rem; }
[data-testid="stSidebar"] { background: #0F172A; }
[data-testid="stSidebar"] * { color: #F8FAFC !important; }
h1, h2, h3 { color: #0F172A; }
.stButton > button, [data-testid="stFormSubmitButton"] button {
    background: #0D9488; color: white; border: 0;
    border-radius: 10px; font-weight: 600;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
    background: #0F766E; color: white;
}
[data-testid="stMetric"], [data-testid="stForm"] {
    background: white; border: 1px solid #E2E8F0;
    border-radius: 14px; padding: 16px;
}
.stTextInput input, .stNumberInput input, .stDateInput input,
.stTextArea textarea, [data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background: white !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    border-radius: 8px;
}
[data-baseweb="select"] div, [data-baseweb="select"] span,
[role="option"] { color: #0F172A !important; }
input::placeholder, textarea::placeholder {
    color: #64748B !important; opacity: 1;
}
[data-testid="stMetricValue"] { color: #0F172A; font-weight: 700; }
[data-testid="stProgressBar"] > div > div { background: #0D9488; }
hr { border-color: #E2E8F0; }
</style>
""", unsafe_allow_html=True)


# Each expense stores its details in an object
class Expense:
    def __init__(self, number, amount, category, day, payment, note):
        self.number = number
        self.amount = amount
        self.category = category
        self.day = day
        self.payment = payment
        self.note = note


# Stores and manages expenses
class ExpenseTracker:
    def __init__(self):
        self.expenses = []
        self.next_number = 1

    def add(self, amount, category, day, payment, note):
        item = Expense(self.next_number, amount, category, day, payment, note)
        self.expenses.append(item)
        self.next_number += 1

    def delete(self, number):
        for item in self.expenses:
            if item.number == number:
                self.expenses.remove(item)
                return

    def total(self):
        return sum(item.amount for item in self.expenses)

    def category_total(self, category):
        return sum(item.amount for item in self.expenses
                   if item.category == category)

    def month_total(self, month, year):
        return sum(item.amount for item in self.expenses
                   if item.day.month == month and item.day.year == year)


# Keep data during the current Streamlit session (no file/database storage)
if "tracker" not in st.session_state:
    st.session_state.tracker = ExpenseTracker()
if "monthly_budget" not in st.session_state:
    st.session_state.monthly_budget = 10000.0
if "category_budgets" not in st.session_state:
    st.session_state.category_budgets = {}
if "savings_goal" not in st.session_state:
    st.session_state.savings_goal = 5000.0
if "saved_amount" not in st.session_state:
    st.session_state.saved_amount = 0.0

tracker = st.session_state.tracker
categories = ["Food", "Transport", "Shopping", "Education",
              "Entertainment", "Bills", "Health", "Other"]
payments = ["UPI", "Cash", "Debit Card", "Credit Card",
             "Net Banking", "Other"]
today = date.today()
month_spend = tracker.month_total(today.month, today.year)


# Sidebar navigation
with st.sidebar:
    st.title("💳 Pocket Tracker")
    st.caption("Your money. Your control.")
    page = st.radio("NAVIGATION", ["Dashboard", "Add Expense",
                                  "Expense History", "Budget Planner",
                                  "Insights"])
    st.divider()
    st.metric("This Month", f"₹{month_spend:,.2f}")


# Dashboard
if page == "Dashboard":
    st.title("Welcome to Pocket Tracker 👋")
    st.write("A simple and smarter way to manage your money.")
    a, b, c = st.columns(3)
    a.metric("Total Expenses", f"₹{tracker.total():,.2f}")
    b.metric("Monthly Spending", f"₹{month_spend:,.2f}")
    remaining = st.session_state.monthly_budget - month_spend
    c.metric("Budget Remaining", f"₹{remaining:,.2f}")

    st.subheader("Monthly Budget")
    budget = st.session_state.monthly_budget
    if budget > 0:
        st.progress(min(month_spend / budget, 1.0))
        st.write(f"₹{month_spend:,.2f} spent out of ₹{budget:,.2f}")
        if month_spend > budget:
            st.warning("You have exceeded your monthly budget.")
        elif month_spend >= budget * 0.8:
            st.warning("You are close to your budget limit.")
        else:
            st.success("You are within your budget.")

    st.subheader("Recent Transactions")
    for item in reversed(tracker.expenses[-5:]):
        st.write(f"**{item.category}** — ₹{item.amount:,.2f}")
        st.caption(f"{item.day:%d %b %Y} | {item.note or 'No description'}")
        st.divider()
    if not tracker.expenses:
        st.info("No expenses yet. Add your first expense!")


# Add expense
elif page == "Add Expense":
    st.title("➕ Add New Expense")
    with st.form("expense_form"):
        amount = st.number_input("Amount (₹)", min_value=0.01, step=10.0)
        category = st.selectbox("Category", categories)
        day = st.date_input("Expense Date", value=today)
        payment = st.selectbox("Payment Method", payments)
        note = st.text_input("Description", placeholder="Example: Lunch with friends")
        submit = st.form_submit_button("Add Expense", use_container_width=True)

    if submit:
        if amount <= 0:
            st.error("Enter a valid amount.")
        else:
            tracker.add(amount, category, day, payment, note)
            st.success("Expense added successfully!")
            st.balloons()


# Search, filter and delete expenses
elif page == "Expense History":
    st.title("📋 Expense History")
    if tracker.expenses:
        search = st.text_input("Search description or category").lower()
        chosen = st.selectbox("Filter by Category", ["All"] + categories)
        shown = [item for item in tracker.expenses
                 if search in item.note.lower() or search in item.category.lower()]
        if chosen != "All":
            shown = [item for item in shown if item.category == chosen]
        st.write(f"Showing {len(shown)} transactions")

        for item in reversed(shown):
            with st.container(border=True):
                left, middle, right = st.columns([3, 2, 1])
                left.write(f"**{item.category}**")
                left.caption(item.note or "No description")
                left.caption(item.day.strftime("%d %B %Y"))
                middle.write(f"**₹{item.amount:,.2f}**")
                middle.caption(item.payment)
                if right.button("Delete", key=f"delete_{item.number}"):
                    tracker.delete(item.number)
                    st.rerun()
    else:
        st.info("Your expense history is empty.")


# Monthly and category budgets
elif page == "Budget Planner":
    st.title("🎯 Budget Planner")
    new_budget = st.number_input("Monthly Budget (₹)", min_value=0.0,
                                value=float(st.session_state.monthly_budget),
                                step=500.0)
    if st.button("Save Monthly Budget"):
        st.session_state.monthly_budget = new_budget
        st.success("Monthly budget updated!")

    st.divider()
    chosen = st.selectbox("Choose Category", categories)
    old_limit = st.session_state.category_budgets.get(chosen, 0.0)
    limit = st.number_input("Category Budget (₹)", min_value=0.0,
                            value=float(old_limit), step=100.0)
    if st.button("Save Category Budget"):
        st.session_state.category_budgets[chosen] = limit
        st.success("Category budget saved!")

    st.subheader("Category Budget Overview")
    for category in categories:
        limit = st.session_state.category_budgets.get(category, 0.0)
        if limit > 0:
            spent = tracker.category_total(category)
            st.write(f"**{category}**")
            st.progress(min(spent / limit, 1.0))
            st.write(f"₹{spent:,.2f} spent out of ₹{limit:,.2f}")
            if spent > limit:
                st.warning(f"{category} budget exceeded!")


# Charts and savings goal
elif page == "Insights":
    st.title("📊 Spending Insights")
    if tracker.expenses:
        category_data = {name: tracker.category_total(name)
                         for name in categories
                         if tracker.category_total(name) > 0}
        st.subheader("Category-wise Spending")
        if category_data:
            st.bar_chart(category_data)

        monthly_data = {}
        for item in tracker.expenses:
            name = item.day.strftime("%b %Y")
            monthly_data[name] = monthly_data.get(name, 0) + item.amount
        st.subheader("Monthly Spending")
        st.bar_chart(monthly_data)

        st.divider()
        st.subheader("Savings Goal")
        goal = st.number_input("Savings Target (₹)", min_value=0.0,
                               value=float(st.session_state.savings_goal),
                               step=500.0)
        saved = st.number_input("Amount Saved (₹)", min_value=0.0,
                                value=float(st.session_state.saved_amount),
                                step=100.0)
        if st.button("Update Savings"):
            st.session_state.savings_goal = goal
            st.session_state.saved_amount = saved
            st.success("Savings updated!")

        if goal > 0:
            st.progress(min(saved / goal, 1.0))
            st.write(f"₹{saved:,.2f} saved out of ₹{goal:,.2f}")
            st.metric("Amount Left to Save", f"₹{max(goal - saved, 0):,.2f}")

        if category_data:
            biggest = max(category_data, key=category_data.get)
            st.info(f"Your highest spending category is **{biggest}**.")
        st.write(f"Total recorded spending: ₹{tracker.total():,.2f}")
    else:
        st.info("Add expenses first to see your insights.")

st.divider()
st.caption("Pocket Tracker | Smart spending starts here.")
