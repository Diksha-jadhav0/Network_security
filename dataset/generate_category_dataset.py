import os
import csv
import random

DATASET_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_CSV = os.path.join(DATASET_DIR, "phishing_categories.csv")

CATEGORIES = {
    "BANKING_FRAUD": [
        "URGENT: Your {bank} account has been suspended due to unauthorized login attempts. Verify banking credentials now.",
        "Security Alert: Your debit card is blocked. Click here to confirm your identity and unblock your {bank} credit card.",
        "Unauthorized transaction of ${amount} detected on your {bank} online banking account. Verify your account credentials immediately.",
        "Your {bank} credit card has been temporarily locked due to suspicious activity. Update security questions to restore access.",
        "Notice: Account suspension warning for your {bank} account. Re-verify your mobile banking pin to maintain service.",
        "Action required: Suspicious withdrawal attempt on your {bank} account. Confirm your account details to cancel transaction.",
        "Alert: Your {bank} netbanking password will expire today. Update credentials to avoid permanent account block.",
        "We noticed unusual account activity in your {bank} checking account. Please log in to verify your identity.",
        "Critical update: {bank} security breach alert. Update your online banking credentials immediately to protect funds.",
        "Your {bank} credit card limit increase requires immediate identity verification. Submit your SSN and account number."
    ],
    "TRANSACTION_FRAUD": [
        "Payment Failed: Your recent online transaction of ${amount} could not be processed. Update payment method now.",
        "Invoice Overdue: Your invoice #{invoice_num} is overdue. Please process payment immediately to avoid service termination.",
        "Transaction verification required for order #{order_num}. Confirm your payment details to release shipment.",
        "UPI payment blocked: Your recent transfer of ${amount} failed. Click here to re-authorize payment.",
        "Billing Notice: Automatic monthly payment of ${amount} failed due to card decline. Update billing info.",
        "Urgent Payment Alert: Transaction #{tx_id} requires secondary authorization. Confirm transaction details.",
        "Vendor Invoice Overdue: Immediate settlement of ${amount} required for invoice #{invoice_num}.",
        "Payment Error: Unable to complete your online purchase. Verify your credit card details to proceed.",
        "Security verification needed for incoming bank transfer of ${amount}. Approve payment in app.",
        "Failed payment warning: Subscription auto-renewal failed. Update payment details to keep your service active."
    ],
    "LOTTERY_SCAM": [
        "Congratulations! You won ${prize} in the Mega Millions Lucky Draw lottery. Claim your prize reward today.",
        "Jackpot Winner Alert: Your email was selected for the $500,000 international sweepstakes prize.",
        "Claim your prize: You have been chosen as the lucky winner of ${prize} cash reward in our anniversary raffle.",
        "Lucky Draw Winner: You won a brand new luxury vehicle and ${prize} cash reward. Submit claim form now.",
        "Official Notification: You are the grand prize winner of the International Tech Giveaway. Claim reward immediately.",
        "Prize Claim Confirmation: Unclaimed jackpot reward of ${prize} waiting in your name. Pay processing fee to claim.",
        "Exclusive Contest Alert: You won first place in our annual subscriber lucky draw lottery!",
        "Winner Notice: ${prize} funds allocated to your email address. Verify identity to receive wire transfer.",
        "Congratulations! You are selected for the $1,000,000 global lottery pool. Click link to redeem gift.",
        "Jackpot reward approved: Confirm your contact details and bank details to receive your winnings."
    ],
    "JOB_FRAUD": [
        "Remote Job Offer: You have been selected for a High Pay Work From Home Data Entry position ($50/hr).",
        "Interview Selected: Your resume was accepted for Senior Project Manager position. Registration fee required to start.",
        "Salary Package Confirmation: Offer letter ready for Executive Director role. Pay onboarding background check fee.",
        "Urgent Hiring: Exclusive remote job offer with flexible hours. Register now by paying processing registration fee.",
        "Job Application Approved: Accept your offer letter for Virtual Assistant position and claim signing bonus.",
        "Career Opportunity: Selected for online customer service job. Equipment deposit payment required before training.",
        "Interview Invitation: Your background profile matches our freelance consultant opening. Confirm interview slot.",
        "Job Offer Alert: Guaranteed $4,000 monthly income. Complete registration fee payment to receive starter kit.",
        "Employment Notice: Offer of employment from Global Tech Corp. Submit personal identity details and payment.",
        "Selected for Remote Position: Download job agreement contract and send registration processing fee."
    ],
    "ENTERTAINMENT_SCAM": [
        "Netflix subscription expired: Update payment method now to continue watching your favorite movies.",
        "Streaming account suspended: Your Disney+ premium membership was revoked due to billing failure.",
        "Gaming Reward Claim: Exclusive 5,000 V-Bucks / Free Skins reward waiting for your gaming account.",
        "Premium Membership Renewal: Spotify Premium account cancelled. Claim 12 months free subscription now.",
        "Account Suspended: Hulu streaming access suspended. Re-activate membership by verifying billing info.",
        "Entertainment Pass Winner: Free 1-year HBO Max VIP subscription reward available. Click to redeem.",
        "Gaming Account Alert: Steam account flag detected. Verify credentials to avoid permanent game ban.",
        "Special Gift: Claim your Playstation Store $100 gift card code before expiration.",
        "Stream Pass Expiration: Amazon Prime Video account payment declined. Update card to resume streaming.",
        "VIP Membership Reward: YouTube Premium 6-month trial upgrade available for your email."
    ],
    "CRYPTO_INVESTMENT_SCAM": [
        "Wallet Recovery Alert: Verify seed phrase now to protect your crypto assets from unauthorized access.",
        "Crypto Bonus Claim: You received 0.5 BTC welcome bonus in your crypto wallet. Deposit 0.01 BTC to withdraw.",
        "Bitcoin Investment Return: Guaranteed 300% weekly return on your crypto staking investment pool.",
        "Staking Reward Approved: Claim your Ethereum staking rewards of 2.4 ETH before time expires.",
        "MetaMask Alert: Critical security update required for your decentralized wallet. Re-enter 12-word recovery phrase.",
        "Trust Wallet Notice: Account migration required. Verify private keys to keep crypto tokens safe.",
        "Binance Security: Unauthorized withdrawal of 10,000 USDT initiated. Click to freeze funds.",
        "Crypto Giveaway: Elon Musk 5,000 BTC giveaway promotion! Send 0.1 BTC to receive double return.",
        "Airdrop Notification: 1,000 free tokens credited to your Web3 wallet address. Connect wallet to claim.",
        "High Yield Crypto Pool: Double your Bitcoin in 24 hours with our automated arbitrage trading bot."
    ],
    "ACCOUNT_VERIFICATION_SCAM": [
        "Verify your email address immediately or your account will be permanently deactivated in 24 hours.",
        "Reset password immediately: Suspicious login attempt detected from unknown IP address in Russia.",
        "Microsoft account locked: Unauthorized activity detected on your Office 365 Outlook account.",
        "University account suspension notice: Re-validate student email credentials to avoid portal lockout.",
        "Google Workspace Alert: Security policy violation detected. Verify identity to unlock email inbox.",
        "Security Alert: Your Apple ID has been locked for security reasons. Click link to verify identity.",
        "Action Required: Confirm your account security settings to avoid service interruption.",
        "Two-factor authentication failure: Verify your phone number and backup security codes immediately.",
        "Cloud SSO Lockout Warning: Multi-Factor Authentication disabled. Re-authenticate credentials now.",
        "Domain Admin Notice: Email account quota exceeded. Verify password to upgrade mailbox space."
    ]
}

BANKS = ["PayPal", "Chase Bank", "Wells Fargo", "Bank of America", "Citibank", "Capital One"]

def generate():
    random.seed(42)
    rows = []
    
    for category, templates in CATEGORIES.items():
        # Generate 60 distinct samples for each category -> 420 total
        for i in range(60):
            tmpl = random.choice(templates)
            bank = random.choice(BANKS)
            amount = str(random.randint(50, 2500))
            prize = str(random.choice(["$50,000", "$100,000", "$500,000", "$1,000,000"]))
            invoice_num = str(random.randint(1000, 9999))
            order_num = str(random.randint(100000, 999999))
            tx_id = f"TX-{random.randint(10000, 99999)}"
            
            text = tmpl.format(
                bank=bank,
                amount=amount,
                prize=prize,
                invoice_num=invoice_num,
                order_num=order_num,
                tx_id=tx_id
            )
            # Add slight random variations for variety
            variations = [
                f"Subject: Important Notice. {text}",
                f"{text} Click http://secure-verify-{random.randint(10,99)}.com to proceed.",
                f"Dear Customer, {text} Contact support immediately if this was not you.",
                f"ATTENTION: {text} Reference ID: #{random.randint(10000,99999)}.",
                f"{text}"
            ]
            final_text = random.choice(variations)
            rows.append({"text": final_text, "label": category})

    random.shuffle(rows)

    os.makedirs(DATASET_DIR, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully generated {len(rows)} samples across 7 categories into {OUTPUT_CSV}")

if __name__ == "__main__":
    generate()
