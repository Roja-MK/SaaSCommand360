
import pandas as pd
import random
from pathlib import Path
from datetime import datetime, date, timedelta
from faker import Faker

# --------------------------------------------------
# 1. INITIAL SETUP
# --------------------------------------------------

fake = Faker()
random.seed(42)
Faker.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent

# Separate development dataset
DATA_DIR = BASE_DIR / "data" / "dev" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

NOW = datetime.now()
TODAY = date.today()

# Record configuration - TOTAL 10,000
NUM_ACCOUNTS = 500
NUM_USERS = 1000
NUM_SUBSCRIPTIONS = 500
NUM_INVOICES = 2000
NUM_SUPPORT_TICKETS = 1000
NUM_PRODUCT_EVENTS = 5000

BATCH_SIZE = 1000

print("Starting SaaSCommand360 10K data generation...")


# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

def random_datetime(start, end):
    difference = int((end - start).total_seconds())

    if difference <= 0:
        return start

    return start + timedelta(seconds=random.randint(0, difference))


def random_date(start, end):
    difference = (end - start).days

    if difference <= 0:
        return start

    return start + timedelta(days=random.randint(0, difference))


# --------------------------------------------------
# 3. ACCOUNTS - 500 RECORDS
# --------------------------------------------------

print("\nGenerating accounts...")

accounts = []

for i in range(1, NUM_ACCOUNTS + 1):

    accounts.append({
        "account_id": f"A{i:04}",
        "company_name": fake.company(),
        "industry": random.choice([
            "IT", "Healthcare", "Finance",
            "Retail", "Manufacturing", "Education"
        ]),
        "size": random.choice(["Small", "Medium", "Large"]),
        "region": random.choice([
            "India", "USA", "UK", "Germany", "Canada"
        ]),
        "owner": fake.name()
    })

accounts_df = pd.DataFrame(accounts)

accounts_df.to_csv(
    DATA_DIR / "accounts.csv",
    index=False
)

account_ids = [a["account_id"] for a in accounts]


# --------------------------------------------------
# 4. USERS - 1,000 RECORDS
# --------------------------------------------------

print("Generating users...")

users = []

for i in range(1, NUM_USERS + 1):

    users.append({
        "user_id": f"U{i:05}",
        "account_id": random.choice(account_ids),
        "role": random.choice(["Admin", "Manager", "User"]),
        "created_at": random_datetime(
            NOW - timedelta(days=730), NOW
        )
    })

users_df = pd.DataFrame(users)

users_df.to_csv(
    DATA_DIR / "users.csv",
    index=False
)

user_details = {
    user["user_id"]: user["created_at"]
    for user in users
}

user_ids = list(user_details.keys())


# --------------------------------------------------
# 5. SUBSCRIPTIONS - 500 RECORDS
# --------------------------------------------------

print("Generating subscriptions...")

subscriptions = []

plan_prices = {
    "Basic": 2000,
    "Premium": 5000,
    "Enterprise": 10000
}

for i in range(1, NUM_SUBSCRIPTIONS + 1):

    plan = random.choice(list(plan_prices.keys()))
    billing_cycle = random.choice(["Monthly", "Yearly"])

    start_date = random_date(
        TODAY - timedelta(days=730), TODAY
    )

    status = random.choices(
        ["Active", "Cancelled", "Past Due"],
        weights=[70, 20, 10]
    )[0]

    end_date = None

    if status == "Cancelled":
        end_date = random_date(start_date, TODAY)

    subscriptions.append({
        "subscription_id": f"S{i:05}",
        "account_id": random.choice(account_ids),
        "plan": plan,
        "start_date": start_date,
        "end_date": end_date,
        "billing_cycle": billing_cycle,
        "status": status
    })

subscriptions_df = pd.DataFrame(subscriptions)

subscriptions_df.to_csv(
    DATA_DIR / "subscriptions.csv",
    index=False
)


# --------------------------------------------------
# 6. INVOICES - 2,000 RECORDS
# --------------------------------------------------

print("Generating invoices...")

invoices = []

for i in range(1, NUM_INVOICES + 1):

    subscription = random.choice(subscriptions)

    invoice_date = random_date(
        subscription["start_date"], TODAY
    )

    due_date = invoice_date + timedelta(days=15)

    if due_date > TODAY:

        status = random.choice(["Pending", "Paid"])

    else:

        status = random.choices(
            ["Paid", "Overdue", "Failed"],
            weights=[75, 18, 7]
        )[0]

    paid_date = None

    if status == "Paid":

        last_paid_day = min(due_date, TODAY)

        paid_date = random_date(
            invoice_date, last_paid_day
        )

    monthly_price = plan_prices[subscription["plan"]]

    if subscription["billing_cycle"] == "Yearly":
        amount = monthly_price * 12 * 0.90
    else:
        amount = monthly_price

    invoices.append({
        "invoice_id": f"I{i:06}",
        "account_id": subscription["account_id"],
        "subscription_id": subscription["subscription_id"],
        "amount": amount,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "paid_date": paid_date,
        "status": status
    })

invoices_df = pd.DataFrame(invoices)

invoices_df.to_csv(
    DATA_DIR / "invoices.csv",
    index=False
)


# --------------------------------------------------
# 7. SUPPORT TICKETS - 1,000 RECORDS
# --------------------------------------------------

print("Generating support tickets...")

support = []

for i in range(1, NUM_SUPPORT_TICKETS + 1):

    created_at = random_datetime(
        NOW - timedelta(days=365), NOW
    )

    is_resolved = random.choice([True, False])

    resolved_at = None

    if is_resolved:
        resolved_at = random_datetime(
            created_at, NOW
        )

    status = (
        "Resolved" if is_resolved
        else random.choice(["Open", "In Progress"])
    )

    support.append({
        "ticket_id": f"T{i:05}",
        "account_id": random.choice(account_ids),
        "severity": random.choice([
            "Low", "Medium", "High", "Critical"
        ]),
        "status": status,
        "created_at": created_at,
        "resolved_at": resolved_at
    })

support_df = pd.DataFrame(support)

support_df.to_csv(
    DATA_DIR / "support.csv",
    index=False
)


# --------------------------------------------------
# 8. PRODUCT EVENTS - 5,000 RECORDS
# --------------------------------------------------

print("Generating product events...")

features = [
    "Login",
    "Dashboard",
    "Reports",
    "Analytics",
    "Export",
    "Settings"
]

events_file = DATA_DIR / "product_events.csv"

for batch_number, start in enumerate(
    range(0, NUM_PRODUCT_EVENTS, BATCH_SIZE),
    start=1
):

    events = []

    current_batch_size = min(
        BATCH_SIZE,
        NUM_PRODUCT_EVENTS - start
    )

    for i in range(
        start + 1,
        start + current_batch_size + 1
    ):

        user_id = random.choice(user_ids)

        user_created = user_details[user_id]

        event_timestamp = random_datetime(
            user_created, NOW
        )

        events.append({
            "event_id": f"E{i:07}",
            "user_id": user_id,
            "feature": random.choice(features),
            "event_timestamp": event_timestamp
        })

    events_df = pd.DataFrame(events)

    events_df.to_csv(
        events_file,
        mode="w" if batch_number == 1 else "a",
        header=(batch_number == 1),
        index=False
    )

    print(
        f"Product events generated: "
        f"{start + current_batch_size:,}/"
        f"{NUM_PRODUCT_EVENTS:,}"
    )


# --------------------------------------------------
# 9. FINAL SUMMARY
# --------------------------------------------------

total_records = (
    NUM_ACCOUNTS
    + NUM_USERS
    + NUM_SUBSCRIPTIONS
    + NUM_INVOICES
    + NUM_SUPPORT_TICKETS
    + NUM_PRODUCT_EVENTS
)

print("\n====================================")
print("SAASCOMMAND360 DATA GENERATION DONE")
print("====================================")

print(f"Accounts:         {NUM_ACCOUNTS:,}")
print(f"Users:            {NUM_USERS:,}")
print(f"Subscriptions:    {NUM_SUBSCRIPTIONS:,}")
print(f"Invoices:         {NUM_INVOICES:,}")
print(f"Support Tickets:  {NUM_SUPPORT_TICKETS:,}")
print(f"Product Events:   {NUM_PRODUCT_EVENTS:,}")

print("------------------------------------")
print(f"Total Records:    {total_records:,}")
print("------------------------------------")

print(f"\nOutput directory: {DATA_DIR}")
print("\nAll six development datasets generated successfully!")
