def determine_loyalty(yearly_payments):
    """
    Determines loyalty if customer made >50 payments in any continuous 5-year period.
    yearly_payments: list of integers representing payments per year (length >= 5)
    """
    if len(yearly_payments) < 5:
        return False
    # Check all continuous 5-year windows
    for i in range(len(yearly_payments) - 4):
        if all(p > 50 for p in yearly_payments[i:i+5]):
            return True
    return False

def assign_badge(active_months):
    if active_months >= 60:
        return "Pro"
    elif active_months >= 24:
        return "Experience"
    elif active_months > 3:
        return "Newbie"
    else:
        return "No badge"

def calculate_cash_coins(payments_in_month, total_payment_amount, loyalty=False):
    coins = payments_in_month  # 1 coin per payment
    if payments_in_month > 5 and total_payment_amount > 10000:
        coins += 2  # bonus coins
    if loyalty:
        coins += 50  # loyalty bonus coins
    return coins

def tax_and_credit_decision(payments_in_month, loyalty, badge):
    if payments_in_month > 5:
        return "Cash Loans"
    elif loyalty:
        return f"Badges - {badge}"
    else:
        return "No rewards"

def chatbot():
    print("Welcome to the Tax & Credit chatbot!")
    
    try:
        payments_in_month = int(input("How many payments have you made this month? "))
        total_payment_amount = float(input("What is the total amount (in ₹) for these payments this month? "))
        
        years = int(input("How many years of payment data do you want to enter? (At least 5) "))
        yearly_payments = []
        for i in range(1, years + 1):
            payments = int(input(f"Payments made in year {-i}: "))
            yearly_payments.append(payments)
        yearly_payments.reverse()
        
        active_months = int(input("How many months have you been actively connected to the website? "))
        
        loyalty = determine_loyalty(yearly_payments)
        badge = assign_badge(active_months)
        coins = calculate_cash_coins(payments_in_month, total_payment_amount, loyalty)
        
        reward = tax_and_credit_decision(payments_in_month, loyalty, badge)
        
        while True:
            user_choice = input("\nWould you like to (1) Make a payment or (2) See your rewards? Enter 1 or 2: ").strip()
            if user_choice == '1':
                amount = float(input("Enter payment amount in ₹: "))
                payments_in_month += 1
                total_payment_amount += amount
                coins = calculate_cash_coins(payments_in_month, total_payment_amount, loyalty)
                print(f"Payment recorded! Total payments this month: {payments_in_month}, Total amount: ₹{total_payment_amount:.2f}")
            elif user_choice == '2':
                print(f"\nYour current status:")
                print(f"Loyal Customer: {'Yes' if loyalty else 'No'}")
                print(f"Badge: {badge}")
                print(f"Payments this month: {payments_in_month}")
                print(f"Total Payment Amount this month: ₹{total_payment_amount:.2f}")
                print(f"Cash Coins earned: {coins}")
                print(f"Reward: {reward}")
                break
            else:
                print("Invalid input. Please enter 1 or 2.")
        
        print("Thank you for using the Tax & Credit chatbot!")
    
    except ValueError:
        print("Invalid input. Please enter numbers only.")

if __name__ == "__main__":
    chatbot()
